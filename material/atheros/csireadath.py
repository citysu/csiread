import numpy as np
import os
import sys
import platform


class Atheros:
    def __init__(self, filepath, Nrxnum=3, Ntxnum=2, Tones=114, pl_len=1040,
                 if_report=True):
        """Parameter initialization."""
        self.filepath = filepath
        self.Nrxnum = Nrxnum
        self.Ntxnum = Ntxnum
        self.Tones = Tones
        self.pl_len = pl_len
        self.if_report = if_report

        if not os.path.isfile(filepath):
            raise Exception("error: file does not exist, Stop!\n")

    def read(self):
        f = open(self.filepath, 'rb')
        if f is None:
            f.close()
            return -1

        len = f.seek(0, os.SEEK_END)
        f.seek(0, os.SEEK_SET)

        btype = None
        if sys.platform == 'linux':
            if platform.architecture()[0] == "64bit":
                btype = np.int64
            else:
                btype = np.int32
        elif sys.platform == 'win32':
            btype = np.int32
        else:
            raise Exception("error: Only works on linux and windows !\n")

        self.timestamp = np.zeros([len//420])
        self.csi_len = np.zeros([len//420], dtype=btype)
        self.tx_channel = np.zeros([len//420], dtype=btype)
        self.err_info = np.zeros([len//420], dtype=btype)
        self.noise_floor = np.zeros([len//420], dtype=btype)
        self.Rate = np.zeros([len//420], dtype=btype)
        self.bandWidth = np.zeros([len//420], dtype=btype)
        self.num_tones = np.zeros([len//420], dtype=btype)
        self.nr = np.zeros([len//420], dtype=btype)
        self.nc = np.zeros([len//420], dtype=btype)
        self.rssi = np.zeros([len//420], dtype=btype)
        self.rssi_1 = np.zeros([len//420], dtype=btype)
        self.rssi_2 = np.zeros([len//420], dtype=btype)
        self.rssi_3 = np.zeros([len//420], dtype=btype)
        self.payload_len = np.zeros([len//420], dtype=btype)
        self.csi = np.zeros([len//420, self.Tones, self.Nrxnum, self.Ntxnum],
                            dtype=np.complex128)
        self.payload = np.zeros([len//420, self.pl_len], dtype=btype)

        border = 'little'
        cur = 0
        count = 0
        while cur < (len - 4):
            field_len = int.from_bytes(f.read(2), byteorder=border)
            cur += 2
            if (cur + field_len) > len:
                break

            self.timestamp[count] = int.from_bytes(f.read(8), byteorder=border)
            cur += 8
            self.csi_len[count] = int.from_bytes(f.read(2), byteorder=border)
            cur += 2
            self.tx_channel[count] = int.from_bytes(f.read(2), byteorder=border)
            cur += 2
            self.err_info[count] = int.from_bytes(f.read(1), byteorder=border)
            cur += 1
            self.noise_floor[count] = int.from_bytes(f.read(1), byteorder=border)
            cur += 1
            self.Rate[count] = int.from_bytes(f.read(1), byteorder=border)
            cur += 1
            self.bandWidth[count] = int.from_bytes(f.read(1), byteorder=border)
            cur += 1
            self.num_tones[count] = int.from_bytes(f.read(1), byteorder=border)
            cur += 1
            self.nr[count] = int.from_bytes(f.read(1), byteorder=border)
            cur += 1
            self.nc[count] = int.from_bytes(f.read(1), byteorder=border)
            cur += 1
            self.rssi[count] = int.from_bytes(f.read(1), byteorder=border)
            cur += 1
            self.rssi_1[count] = int.from_bytes(f.read(1), byteorder=border)
            cur += 1
            self.rssi_2[count] = int.from_bytes(f.read(1), byteorder=border)
            cur += 1
            self.rssi_3[count] = int.from_bytes(f.read(1), byteorder=border)
            cur += 1
            self.payload_len[count] = int.from_bytes(f.read(2), byteorder=border)
            cur += 2

            c_len = self.csi_len[count]
            if c_len > 0:
                csi_buf = f.read(c_len)
                self.csi[count] = self.__read_csi(csi_buf, self.nr[count], self.nc[count], self.num_tones[count])
                cur += c_len
            else:
                self.csi[count] = None

            pl_len = self.payload_len[count]
            if pl_len > 0:
                self.payload[count, :pl_len] = bytearray(f.read(pl_len))
                cur += pl_len
            else:
                self.payload[count, :pl_len] = 0

            if (cur + 420 > len):
                count -= 1
                break
            print("cur: ", count, cur)
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
        csi = np.zeros([self.Tones, self.Nrxnum, self.Ntxnum], dtype=np.complex128)

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
