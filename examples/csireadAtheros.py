"""csiread.Atheros: implemented in pure Python"""

import numpy as np
import os
from timeit import default_timer


class Atheros:
    def __init__(self, file, nrxnum=3, ntxnum=2, tones=56, pl_len=0, if_report=True):
        """Parameter initialization."""
        self.file = file
        self.nrxnum = nrxnum
        self.ntxnum = ntxnum
        self.tones = tones
        self.pl_len = pl_len
        self.if_report = if_report

        if not os.path.isfile(file):
            raise Exception("error: file does not exist, Stop!\n")

    def read(self, endian='little'):
        f = open(self.file, 'rb')
        if f is None:
            f.close()
            return -1

        lens = os.path.getsize(self.file)
        btype = np.int_
        self.timestamp = np.zeros([lens//420])
        self.csi_len = np.zeros([lens//420], dtype=btype)
        self.tx_channel = np.zeros([lens//420], dtype=btype)
        self.err_info = np.zeros([lens//420], dtype=btype)
        self.noise_floor = np.zeros([lens//420], dtype=btype)
        self.Rate = np.zeros([lens//420], dtype=btype)
        self.bandWidth = np.zeros([lens//420], dtype=btype)
        self.num_tones = np.zeros([lens//420], dtype=btype)
        self.nr = np.zeros([lens//420], dtype=btype)
        self.nc = np.zeros([lens//420], dtype=btype)
        self.rssi = np.zeros([lens//420], dtype=btype)
        self.rssi_1 = np.zeros([lens//420], dtype=btype)
        self.rssi_2 = np.zeros([lens//420], dtype=btype)
        self.rssi_3 = np.zeros([lens//420], dtype=btype)
        self.payload_len = np.zeros([lens//420], dtype=btype)
        self.csi = np.zeros([lens//420, self.tones, self.nrxnum, self.ntxnum], dtype=np.complex128)
        self.payload = np.zeros([lens//420, self.pl_len], dtype=btype)

        cur = 0
        count = 0
        while cur < (lens - 4):
            field_len = int.from_bytes(f.read(2), byteorder=endian)
            cur += 2
            if (cur + field_len) > lens:
                break

            self.timestamp[count] = int.from_bytes(f.read(8), byteorder=endian)
            cur += 8
            self.csi_len[count] = int.from_bytes(f.read(2), byteorder=endian)
            cur += 2
            self.tx_channel[count] = int.from_bytes(f.read(2), byteorder=endian)
            cur += 2
            self.err_info[count] = int.from_bytes(f.read(1), byteorder=endian)
            cur += 1
            self.noise_floor[count] = int.from_bytes(f.read(1), byteorder=endian)
            cur += 1
            self.Rate[count] = int.from_bytes(f.read(1), byteorder=endian)
            cur += 1
            self.bandWidth[count] = int.from_bytes(f.read(1), byteorder=endian)
            cur += 1
            self.num_tones[count] = int.from_bytes(f.read(1), byteorder=endian)
            cur += 1
            self.nr[count] = int.from_bytes(f.read(1), byteorder=endian)
            cur += 1
            self.nc[count] = int.from_bytes(f.read(1), byteorder=endian)
            cur += 1
            self.rssi[count] = int.from_bytes(f.read(1), byteorder=endian)
            cur += 1
            self.rssi_1[count] = int.from_bytes(f.read(1), byteorder=endian)
            cur += 1
            self.rssi_2[count] = int.from_bytes(f.read(1), byteorder=endian)
            cur += 1
            self.rssi_3[count] = int.from_bytes(f.read(1), byteorder=endian)
            cur += 1
            self.payload_len[count] = int.from_bytes(f.read(2), byteorder=endian)
            cur += 2

            c_len = self.csi_len[count]
            if c_len > 0:
                csi_buf = f.read(c_len)
                self.csi[count] = self.__read_csi(csi_buf, self.nr[count], self.nc[count], self.num_tones[count])
                cur += c_len
            else:
                self.csi[count] = None

            pl_len = self.payload_len[count]
            pl_stop = min(pl_len, self.pl_len, 0)
            if pl_len > 0:
                self.payload[count, :pl_stop] = bytearray(f.read(pl_len))[:pl_stop]
                cur += pl_len
            else:
                self.payload[count, :pl_stop] = 0

            if (cur + 420 > lens):
                count -= 1
                break
            count += 1

        self.timestamp = self.timestamp[:count]
        self.csi_len = self.csi_len[:count]
        self.tx_channel = self.tx_channel[:count]
        self.err_info = self.err_info[:count]
        self.noise_floor = self.noise_floor[:count]
        self.Rate = self.Rate[:count]
        self.bandWidth = self.bandWidth[:count]
        self.num_tones = self.num_tones[:count]
        self.nr = self.nr[:count]
        self.nc = self.nc[:count]
        self.rssi = self.rssi[:count]
        self.rssi_1 = self.rssi_1[:count]
        self.rssi_2 = self.rssi_2[:count]
        self.rssi_3 = self.rssi_3[:count]
        self.payload_len = self.payload_len[:count]
        self.csi = self.csi[:count]
        self.payload = self.payload[:count]

        f.close()

    def __read_csi(self, csi_buf, nr, nc, num_tones):
        csi = np.zeros([self.tones, self.nrxnum, self.ntxnum], dtype=np.complex128)

        bits_left = 16
        bitmask = (1 << 10) - 1

        idx = 0
        h_data = csi_buf[idx]
        idx += 1
        h_data += (csi_buf[idx] << 8)
        idx += 1
        curren_data = h_data & ((1 << 16) - 1)

        for k in range(num_tones):
            for nc_idx in range(nc):
                for nr_idx in range(nr):
                    # imag
                    if (bits_left - 10) < 0:
                        h_data = csi_buf[idx]
                        idx += 1
                        h_data += (csi_buf[idx] << 8)
                        idx += 1
                        curren_data += h_data << bits_left
                        bits_left += 16
                    imag = curren_data & bitmask
                    imag = self.__signbit_convert(imag, 10)

                    bits_left -= 10
                    curren_data = curren_data >> 10
                    # real
                    if (bits_left - 10) < 0:
                        h_data = csi_buf[idx]
                        idx += 1
                        h_data += (csi_buf[idx] << 8)
                        idx += 1
                        curren_data += h_data << bits_left
                        bits_left += 16
                    real = curren_data & bitmask
                    real = self.__signbit_convert(real, 10)

                    bits_left -= 10
                    curren_data = curren_data >> 10
                    # csi
                    csi[k, nr_idx, nc_idx] = real + imag * 1j

        return csi

    def __signbit_convert(self, data, maxbit):
        if data & (1 << (maxbit - 1)):
            data -= (1 << maxbit)
        return data


if __name__ == '__main__':
    last = default_timer()
    csifile = '../material/atheros/dataset/ath_csi_1.dat'
    csidata = Atheros(csifile, nrxnum=3, ntxnum=2, pl_len=10, if_report=True)
    csidata.read()
    print(default_timer() - last, 's')
