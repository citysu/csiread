"""A tool to parse channel state infomation received by 'Linux 802.11n CSI Tool'
or 'Atheros CSI Tool'."""

from libc.stdio cimport fopen, fread, fclose, fseek, ftell
from libc.stdio cimport FILE, SEEK_END, SEEK_SET, SEEK_CUR
from libc.stddef cimport size_t
from libc.stdint cimport uint16_t, uint32_t, uint8_t, int8_t

import os
import sys
import platform
import struct

import numpy as np
cimport numpy as np
cimport cython

__version__ = "1.3.4"
__all__ = ['CSI', 'Atheros']

cdef packed struct iwl5000_bfee_notif:
    uint32_t timestamp_low
    uint16_t bfee_count
    uint16_t reserved
    uint8_t Nrx, Ntx
    uint8_t rssiA, rssiB, rssiC
    int8_t noise
    uint8_t agc, antenna_sel
    uint16_t lens
    uint16_t fake_rate_n_flags
    uint8_t payload[0]

cdef packed struct lorcon_packet:
    uint16_t fc
    uint16_t dur
    uint8_t addr_des[6]
    uint8_t addr_src[6]
    uint8_t addr_bssid[6]
    uint16_t seq
    uint8_t payload[0]

cdef class CSI:
    """Parse channel state infomation received by 'Linux 802.11n CSI Tool'.

    Args:
        file: the file path of csi '.dat'
        Nrxnum: the set number of receive antennas, default=3
        Ntxnum: the set number of transmit antennas, default=2
        pl_size: the size of payload that will be used, default=0
        if_report: report the parsed result, default=True

        (file, Nrxnum=3, Ntxnum=2, pl_size=0, if_report=True)

    Attributes:
        file: data file path
        count: count of 0xbb packets parsed

        timestamp_low: timestamp
        bfee_count: packet count
        Nrx: number of receive antennas
        Ntx: number of transmit antennas
        rssiA: rssi of receive antennas A
        rssiB: rssi of receive antennas B
        rssiC: rssi of receive antennas C
        noise: noise
        agc: agc
        perm: perm
        rate: rate flag, not the real rate
        csi: channel state information
        stp: world timestamp when csi was received

        fc: frame contrl
        dur: during life
        addr_des: destination mac address
        addr_src: source mac address
        addr_bssid: bssid mac address
        seq: serial number of packet
        payload: payload

    Example:
        csidata = csiread.CSI("example.dat")
        csidata.read()
        print(csidata.count)
    """
    cdef readonly str file
    cdef readonly int count

    cdef public np.ndarray timestamp_low
    cdef public np.ndarray bfee_count
    cdef public np.ndarray Nrx
    cdef public np.ndarray Ntx
    cdef public np.ndarray rssiA
    cdef public np.ndarray rssiB
    cdef public np.ndarray rssiC
    cdef public np.ndarray noise
    cdef public np.ndarray agc
    cdef public np.ndarray perm
    cdef public np.ndarray rate
    cdef public np.ndarray csi
    cdef public np.ndarray stp

    cdef public np.ndarray fc
    cdef public np.ndarray dur
    cdef public np.ndarray addr_des
    cdef public np.ndarray addr_src
    cdef public np.ndarray addr_bssid
    cdef public np.ndarray seq
    cdef public np.ndarray payload

    cdef int Nrxnum
    cdef int Ntxnum
    cdef int pl_size
    cdef int if_report

    def __init__(self, file, Nrxnum=3, Ntxnum=2, pl_size=0, if_report=True):
        """Parameter initialization."""
        self.file = file
        self.Nrxnum = Nrxnum
        self.Ntxnum = Ntxnum
        self.pl_size = pl_size
        self.if_report = if_report

        if not os.path.isfile(file):
            raise Exception("Error: `%s` does not exist, Stop!\n" % (file))

        # Estimate the number of packets
        # ----------------------------------------------------------------------
        # | packet type | filed_len | code | header |       payload      | CRC |
        # |     0xbb    |     2     |   1  |   20   | 8 + 60 * Ntx * Nrx |  4  |
        # |     0xc1    |     2     |   1  | 4 + 20 |       pl_size      |  4  |
        # ----------------------------------------------------------------------
        # packet_number = csifile_size // packet_size

        # Important
        # ----------------------------------------------------------------------
        # packet_size is set to a constant value of 95. it is not a good choice. 
        # There are two known limitations here: 1. packet size >= 95 is necessary,
        # otherwise it will throw `IndexError: Out of bounds on buffer access
        # (axis 0)`. 2. if packet size > 95, the more packets, the more excess
        # memory allocated. Excess memory is so large that MemoryError is throwed.
        # csiread.Atheros has the same issue.

        lens = os.path.getsize(file)
        pk_num = lens // (35 + 60 * 1 * 1)
        btype = __btype()

        self.timestamp_low = np.zeros([pk_num], dtype=btype)
        self.bfee_count = np.zeros([pk_num], dtype=btype)
        self.Nrx = np.zeros([pk_num], dtype=btype)
        self.Ntx = np.zeros([pk_num], dtype=btype)
        self.rssiA = np.zeros([pk_num], dtype=btype)
        self.rssiB = np.zeros([pk_num], dtype=btype)
        self.rssiC = np.zeros([pk_num], dtype=btype)
        self.noise = np.zeros([pk_num], dtype=btype)
        self.agc = np.zeros([pk_num], dtype=btype)
        self.perm = np.zeros([pk_num, 3], dtype=btype)
        self.rate = np.zeros([pk_num], dtype=btype)
        self.csi = np.zeros([pk_num, 30, self.Nrxnum, self.Ntxnum], dtype=np.complex128)

        self.fc = np.zeros([pk_num], dtype=btype)
        self.dur = np.zeros([pk_num], dtype=btype)
        self.addr_des = np.zeros([pk_num, 6], dtype=btype)
        self.addr_src = np.zeros([pk_num, 6], dtype=btype)
        self.addr_bssid = np.zeros([pk_num, 6], dtype=btype)
        self.seq = np.zeros([pk_num], dtype=btype)
        self.payload = np.zeros([pk_num, self.pl_size], dtype=btype)

    def __getitem__(self, index):
        """Return contents of 0xbb packets"""
        ret = {
            "timestamp_low": self.timestamp_low[index],
            "bfee_count": self.bfee_count[index],
            "Nrx": self.Nrx[index],
            "Ntx": self.Ntx[index],
            "rssiA": self.rssiA[index],
            "rssiB": self.rssiB[index],
            "rssiC": self.rssiC[index],
            "noise": self.noise[index],
            "agc": self.agc[index],
            "perm": self.perm[index],
            "rate": self.rate[index],
            "csi": self.csi[index]
        }
        return ret

    cpdef read(self):
        """Parse data only if code=0xbb or code=0xc1.

        Note:
            1. All members are initialized to zero
            2. The 4 bytes after payload are CRC and will not be parsed.
        """
        cdef FILE *f

        tempfile = self.file.encode(encoding="utf-8")
        cdef char *datafile = tempfile

        f = fopen(datafile, "rb")
        if f is NULL:
            print("Open failed!\n")
            fclose(f)
            return -1

        fseek(f, 0, SEEK_END)
        cdef long lens = ftell(f)
        fseek(f, 0, SEEK_SET)

        cdef long[:] timestamp_low_mem = self.timestamp_low
        cdef long[:] bfee_count_mem = self.bfee_count
        cdef long[:] Nrx_mem = self.Nrx
        cdef long[:] Ntx_mem = self.Ntx
        cdef long[:] rssiA_mem = self.rssiA
        cdef long[:] rssiB_mem = self.rssiB
        cdef long[:] rssiC_mem = self.rssiC
        cdef long[:] noise_mem = self.noise
        cdef long[:] agc_mem = self.agc
        cdef long[:, :] perm_mem = self.perm
        cdef long[:] rate_mem = self.rate
        cdef double complex[:, :, :, :] csi_mem = self.csi

        cdef long[:] fc_mem = self.fc
        cdef long[:] dur_mem = self.dur
        cdef long[:, :] addr_des_mem = self.addr_des
        cdef long[:, :] addr_src_mem = self.addr_src
        cdef long[:, :] addr_bssid_mem = self.addr_bssid
        cdef long[:] seq_mem = self.seq
        cdef long[:, :] payload_mem = self.payload

        cdef long cur = 0
        cdef int count_0xbb = 0
        cdef int count_0xc1 = 0
        cdef unsigned short field_len
        cdef unsigned char code
        cdef unsigned char buf[1024]
        cdef unsigned char temp[3]
        cdef size_t l
        cdef iwl5000_bfee_notif *bfee
        cdef lorcon_packet *mpdu

        cdef int index, index_step
        cdef int i, j, k, g, perm_j
        cdef int remainder = 0
        cdef double a, b

        while cur < (lens-3):
            if fread(&temp, sizeof(unsigned char), 3, f) is False:
                print("Open failed!\n")
                fclose(f)
                return -1

            field_len = temp[1] + (temp[0] << 8)
            code = temp[2]
            cur = cur + 3

            if code == 0xbb:
                l = fread(buf, sizeof(unsigned char), field_len - 1, f)
                if l != (field_len - 1):
                    break  # finished
                bfee = <iwl5000_bfee_notif*> &buf

                timestamp_low_mem[count_0xbb] = bfee.timestamp_low
                bfee_count_mem[count_0xbb] = bfee.bfee_count
                Nrx_mem[count_0xbb] = bfee.Nrx
                Ntx_mem[count_0xbb] = bfee.Ntx
                rssiA_mem[count_0xbb] = bfee.rssiA
                rssiB_mem[count_0xbb] = bfee.rssiB
                rssiC_mem[count_0xbb] = bfee.rssiC
                noise_mem[count_0xbb] = bfee.noise
                agc_mem[count_0xbb] = bfee.agc
                rate_mem[count_0xbb] = bfee.fake_rate_n_flags

                perm_mem[count_0xbb, 0] = (bfee.antenna_sel & 0x3)
                perm_mem[count_0xbb, 1] = ((bfee.antenna_sel >> 2) & 0x3)
                perm_mem[count_0xbb, 2] = ((bfee.antenna_sel >> 4) & 0x3)

                if bfee.Nrx > self.Nrxnum:
                    raise Exception("Error: `Nrxnum=%d` is too small, Stop!\n" % (self.Nrxnum))
                if bfee.Ntx > self.Ntxnum:
                    raise Exception("Error: `Ntxnum=%d` is too small, Stop!\n" % (self.Ntxnum))

                index = 0
                for i in range(30):
                    index = index + 3
                    remainder = index & 0x7
                    for j in range(bfee.Nrx):
                        perm_j = perm_mem[count_0xbb, j]
                        for k in range(bfee.Ntx):
                            index_step = index >> 3

                            tmp = (bfee.payload[index_step] >> remainder) \
                                | (bfee.payload[index_step + 1] << (8 - remainder))
                            a = <int8_t>(tmp & 0xFF)

                            tmp = (bfee.payload[index_step + 1] >> remainder) \
                                | (bfee.payload[index_step + 2] << (8 - remainder))
                            b = <int8_t>(tmp & 0xFF)

                            set_csi_mem(csi_mem, count_0xbb, i, perm_j, k, a, b)
                            index = index + 16
                cur = cur + field_len - 1
                count_0xbb = count_0xbb + 1

            elif code == 0xc1:
                l = fread(buf, sizeof(unsigned char), field_len - 1, f)
                if l != (field_len - 1):
                    break  # finished
                mpdu = <lorcon_packet*>&buf

                fc_mem[count_0xc1] = mpdu.fc
                dur_mem[count_0xc1] = mpdu.dur

                for g in range(6):
                    addr_des_mem[count_0xc1, g] = mpdu.addr_des[g]
                    addr_src_mem[count_0xc1, g] = mpdu.addr_src[g]
                    addr_bssid_mem[count_0xc1, g] = mpdu.addr_bssid[g]

                seq_mem[count_0xc1] = mpdu.seq

                for g in range(min(self.pl_size, field_len - 1 - 24 - 4)):
                    payload_mem[count_0xc1, g] = mpdu.payload[g]

                cur = cur + field_len - 1
                count_0xc1 = count_0xc1 + 1

            else:
                fseek(f, field_len - 1, SEEK_CUR)
                cur = cur + field_len - 1

        fclose(f)

        if self.if_report:
            self.__report(count_0xbb, count_0xc1)

        del timestamp_low_mem
        del bfee_count_mem
        del Nrx_mem
        del Ntx_mem
        del rssiA_mem
        del rssiB_mem
        del rssiC_mem
        del noise_mem
        del agc_mem
        del perm_mem
        del rate_mem
        del csi_mem

        del fc_mem
        del dur_mem
        del addr_des_mem
        del addr_src_mem
        del addr_bssid_mem
        del seq_mem
        del payload_mem

        self.timestamp_low = self.timestamp_low[:count_0xbb]
        self.bfee_count = self.bfee_count[:count_0xbb]
        self.Nrx = self.Nrx[:count_0xbb]
        self.Ntx = self.Ntx[:count_0xbb]
        self.rssiA = self.rssiA[:count_0xbb]
        self.rssiB = self.rssiB[:count_0xbb]
        self.rssiC = self.rssiC[:count_0xbb]
        self.noise = self.noise[:count_0xbb]
        self.agc = self.agc[:count_0xbb]
        self.perm = self.perm[:count_0xbb, :]
        self.rate = self.rate[:count_0xbb]
        self.csi = self.csi[:count_0xbb, :, :, :]
        self.count = count_0xbb

        self.fc = self.fc[:count_0xc1]
        self.dur = self.dur[:count_0xc1]
        self.addr_des = self.addr_des[:count_0xc1]
        self.addr_src = self.addr_src[:count_0xc1]
        self.addr_bssid = self.addr_bssid[:count_0xc1]
        self.seq = self.seq[:count_0xc1]
        self.payload = self.payload[:count_0xc1]

    def readstp(self):
        """Parse timestamp when packet was received.

        Note:
            `file.dat` and `file.datstp` must be in the same directory.
        """
        stpfile = self.file + "stp"
        f = open(stpfile, "rb")
        if f is None:
            f.close()
            raise Exception("Error: '%s' does not exist\n" % (stpfile))
        f.seek(0, os.SEEK_END)
        lens = f.tell()
        f.seek(0, os.SEEK_SET)
        self.stp = np.zeros(lens // 8 - 1)
        for i in range(lens // 8 - 1):
            a, b = struct.unpack("<LL", f.read(8))
            self.stp[i] = a + b / 1000000
        f.close()
        return self.stp[0]

    def get_total_rss(self):
        """Calculates the Received Signal Strength [RSS] in dBm from CSI"""
        rssi_mag = np.zeros_like(self.rssiA, dtype=np.float)
        rssi_mag += self.__dbinvs(self.rssiA)
        rssi_mag += self.__dbinvs(self.rssiB)
        rssi_mag += self.__dbinvs(self.rssiC)
        ret = self.__db(rssi_mag) - 44 - self.agc
        return ret

    cpdef get_scaled_csi(self, inplace=False):
        """Converts CSI to channel matrix H

        Args:
            inplace: optionally do the operation in-place. default=False

            (inplace=False)
        """
        cdef int i, j
        cdef int flat = 30 * self.Nrxnum * self.Ntxnum
        cdef double constant2 = 2
        cdef double constant4_5 = np.power(10, 0.45)
        cdef double temp_sum

        csi = self.csi
        csi_pwr = np.zeros(self.count)
        cdef double[:] csi_pwr_mem = csi_pwr
        cdef double complex[:, :] csi_mem = csi.reshape(self.count, flat)
        for i in range(self.count):
            temp_sum = 0
            for j in range(flat):
                temp_sum = temp_sum + csi_mem[i, j].real * csi_mem[i, j].real + csi_mem[i, j].imag * csi_mem[i, j].imag
            csi_pwr_mem[i] = temp_sum
        del csi_pwr_mem
        del csi_mem
        rssi_pwr = self.__dbinv(self.get_total_rss())

        scale = rssi_pwr / (csi_pwr / 30)

        noise_db = self.noise
        noise_db[noise_db == -127] = -92
        thermal_noise_pwr = self.__dbinv(noise_db)

        quant_error_pwr = scale * (self.Nrx * self.Ntx)
        total_noise_pwr = thermal_noise_pwr + quant_error_pwr

        cdef double [:] total_noise_pwr_mem = total_noise_pwr
        cdef long[:] Ntx_mem = self.Ntx
        for i in range(self.count):
            if Ntx_mem[i] == 2:
                total_noise_pwr_mem[i] = total_noise_pwr_mem[i] / constant2
            if Ntx_mem[i] == 3:
                total_noise_pwr_mem[i] = total_noise_pwr_mem[i] / constant4_5
        del Ntx_mem
        del total_noise_pwr_mem

        if inplace:
            self.csi *= np.sqrt(scale / total_noise_pwr).reshape(-1, 1, 1, 1)
            return self.csi
        else:
            return self.csi * np.sqrt(scale / total_noise_pwr).reshape(-1, 1, 1, 1)

    def get_scaled_csi_sm(self, inplace=False):
        """Converts CSI to channel matrix H

        This version undoes Intel's spatial mapping to return the pure
        MIMO channel matrix H.

        Args:
            inplace: optionally do the operation in-place. default=False
            
            (inplace=False)
        """
        if inplace:
            return self.__remove_sm(self.get_scaled_csi(True), True)
        else:
            return self.__remove_sm(self.get_scaled_csi(False), False)

    def apply_sm(self, scaled_csi):
        """Undo the input spatial mapping

        Args:
            (scaled_csi)
        """
        return self.__remove_sm(scaled_csi)

    def __report(self, count_0xbb, count_0xc1):
        """Report parsed result."""
        if count_0xbb == 0:
            print("connector_log=" + hex(4))
            print(str(count_0xc1) + " 0xc1 packets parsed")
        elif count_0xc1 == 0:
            print("connector_log=" + hex(1))
            print(str(count_0xbb) + " 0xbb packets parsed")
        else:
            print("connector_log=" + hex(1 | 4))
            print(str(count_0xc1) + " 0xc1 packets parsed")
            print(str(count_0xbb) + " 0xbb packets parsed")
            print("0xbb packet and 0xc1 packet may be not corresponding, BE CAREFUL!")

    def __dbinvs(self, x):
        """Convert from decibels specially"""
        ret = np.power(10, x / 10)
        ret[ret == 1] = 0
        return ret

    def __dbinv(self, x):
        """Convert from decibels"""
        ret = np.power(10, x / 10)
        return ret

    def __db(self, x):
        """Calculates decibels"""
        ret = 10 * np.log10(x)
        return ret

    cdef __remove_sm(self, scaled_csi, inplace=False):
        """Actually undo the input spatial mapping"""
        sm_2_20 = np.array([[1, 1],
                            [1, -1]], dtype=np.complex128) / np.sqrt(2)
        sm_2_40 = np.array([[1, 1j],
                            [1j, 1]], dtype=np.complex128) / np.sqrt(2)
        sm_3_20 = np.array([[-2 * np.pi / 16, 2 * np.pi / (80 / 23), -2 * np.pi / (80 / 13)],
                            [-2 * np.pi / (80 / 33), 2 * np.pi * (48 / 13), 2 * np.pi * (240 / 37)],
                            [ 2 * np.pi / (80 / 3), 2 * np.pi * (240 / 13), 2 * np.pi * (48 / 13)]], dtype=np.complex128)
        sm_3_20 = np.square(np.exp(1), 1j * sm_3_20) / np.sqrt(3)
        sm_3_40 = np.array([[-2 * np.pi / 16, -2 * np.pi / (80 / 37), 2 * np.pi / (80 / 7)],
                            [-2 * np.pi / (80 / 13), -2 * np.pi * (48 / 11), -2 * np.pi * (240 / 83)],
                            [ 2 * np.pi / (80 / 23), -2 * np.pi * (240 / 107), -2 * np.pi * (48 / 11)]], dtype=np.complex128)
        sm_3_40 = np.square(np.exp(1), 1j * sm_3_40) / np.sqrt(3)

        # Ntx is not a constant array
        if inplace:
            ret = scaled_csi
        else:
            ret = np.zeros([self.count, 30, self.Nrxnum, self.Ntxnum], dtype = np.complex128)

        cdef int i, N, M, B
        cdef long[:] Ntx_mem = self.Ntx
        cdef long[:] Nrx_mem = self.Nrx
        cdef long[:] rate_mem = self.rate
        cdef double complex[:, :, :, :] scaled_csi_mem = scaled_csi
        cdef double complex[:, :, :, :] ret_mem = ret
        cdef double complex[:, :] sm_2_20_mem = sm_2_20
        cdef double complex[:, :] sm_2_40_mem = sm_2_40
        cdef double complex[:, :] sm_3_20_mem = sm_3_20
        cdef double complex[:, :] sm_3_40_mem = sm_3_40

        for i in range(self.count):
            M = Ntx_mem[i]
            N = Nrx_mem[i]
            B = (rate_mem[i] & 0x800) == 0x800
            if B:
                if M == 3:
                    intel_mm_o3(ret_mem[i, :, :N, :M], scaled_csi_mem[i, :, :N, :M], sm_3_40_mem, N, M)
                elif M == 2:
                    intel_mm_o3(ret_mem[i, :, :N, :M], scaled_csi_mem[i, :, :N, :M], sm_2_40_mem, N, M)
                else:
                    if inplace is False:
                        ret_mem[i, :, :N, :M] = scaled_csi_mem[i, :, :N, :M]
            else:
                if M == 3:
                    intel_mm_o3(ret_mem[i, :, :N, :M], scaled_csi_mem[i, :, :N, :M], sm_3_20_mem, N, M)
                elif M == 2:
                    intel_mm_o3(ret_mem[i, :, :N, :M], scaled_csi_mem[i, :, :N, :M], sm_2_20_mem, N, M)
                else:
                    if inplace is False:
                        ret_mem[i, :, :N, :M] = scaled_csi_mem[i, :, :N, :M]
        del Ntx_mem 
        del Nrx_mem
        del rate_mem
        del scaled_csi_mem
        del ret_mem
        del sm_2_20_mem
        del sm_2_40_mem
        del sm_3_20_mem
        del sm_3_40_mem

        return ret

cdef class Atheros:
    """Parse channel state infomation received by 'Atheros CSI Tool'.
    
    Args:
        (file, Nrxnum=3, Ntxnum=2, pl_size=0, Tones=56, if_report=True)
    """
    cdef readonly str file
    cdef readonly int count

    cdef public np.ndarray timestamp
    cdef public np.ndarray csi_len
    cdef public np.ndarray tx_channel
    cdef public np.ndarray err_info
    cdef public np.ndarray noise_floor
    cdef public np.ndarray Rate
    cdef public np.ndarray bandWidth
    cdef public np.ndarray num_tones
    cdef public np.ndarray nr
    cdef public np.ndarray nc
    cdef public np.ndarray rssi
    cdef public np.ndarray rssi_1
    cdef public np.ndarray rssi_2
    cdef public np.ndarray rssi_3
    cdef public np.ndarray payload_len
    cdef public np.ndarray csi
    cdef public np.ndarray payload

    cdef int Nrxnum
    cdef int Ntxnum
    cdef int Tones
    cdef int pl_size
    cdef int if_report

    def __init__(self, file, Nrxnum=3, Ntxnum=2, pl_size=0, Tones=56, if_report=True):
        """Parameter initialization."""
        self.file = file
        self.Nrxnum = Nrxnum
        self.Ntxnum = Ntxnum
        self.Tones = Tones
        self.pl_size = pl_size
        self.if_report = if_report

        if Tones not in [56, 114]:
            raise Exception("Error: Tones can only take 56 and 114, Stop!\n")

        if not os.path.isfile(file):
            raise Exception("Error: '%s' does not exist, Stop!\n" % (file))

        lens = os.path.getsize(file)
        pk_num = lens // 420
        btype = __btype()
        self.timestamp = np.zeros([pk_num])
        self.csi_len = np.zeros([pk_num], dtype=btype)
        self.tx_channel = np.zeros([pk_num], dtype=btype)
        self.err_info = np.zeros([pk_num], dtype=btype)
        self.noise_floor = np.zeros([pk_num], dtype=btype)
        self.Rate = np.zeros([pk_num], dtype=btype)
        self.bandWidth = np.zeros([pk_num], dtype=btype)
        self.num_tones = np.zeros([pk_num], dtype=btype)
        self.nr = np.zeros([pk_num], dtype=btype)
        self.nc = np.zeros([pk_num], dtype=btype)
        self.rssi = np.zeros([pk_num], dtype=btype)
        self.rssi_1 = np.zeros([pk_num], dtype=btype)
        self.rssi_2 = np.zeros([pk_num], dtype=btype)
        self.rssi_3 = np.zeros([pk_num], dtype=btype)
        self.payload_len = np.zeros([pk_num], dtype=btype)
        self.csi = np.zeros([pk_num, self.Tones, self.Nrxnum, self.Ntxnum], dtype=np.complex128)
        self.payload = np.zeros([pk_num, self.pl_size], dtype=btype)

    def __getitem__(self, index):
        """Return contents of packets"""
        ret = {
            "timestamp": self.timestamp[index],
            "csi_len": self.csi_len[index],
            "tx_channel": self.tx_channel[index],
            "err_info": self.err_info[index],
            "noise_floor": self.noise_floor[index],
            "Rate": self.Rate[index],
            "bandWidth": self.bandWidth[index],
            "num_tones": self.num_tones[index],
            "nr": self.nr[index],
            "nc": self.nc[index],
            "rssi": self.rssi[index],
            "rssi_1": self.rssi_1[index],
            "rssi_2": self.rssi_2[index],
            "rssi_3": self.rssi_3[index],
            "payload_len": self.payload_len[index],
            "csi": self.csi[index],
            "payload": self.payload[index]
        }
        return ret

    cpdef read(self, endian='little'):
        """Parse data

        Args:
            endian: ['little', 'big']

            (endian='little')
        """
        if endian not in ['little', 'big']:
            raise Exception("Error: endian can only take 'little' and 'big', Stop!\n")

        cdef FILE *f

        tempfile = self.file.encode(encoding="utf-8")
        cdef char *datafile = tempfile

        f = fopen(datafile, "rb")
        if f is NULL:
            print("Open failed!\n")
            fclose(f)
            return -1

        fseek(f, 0, SEEK_END)
        cdef long lens = ftell(f)
        fseek(f, 0, SEEK_SET)

        cdef double[:] timestamp_mem = self.timestamp
        cdef long[:] csi_len_mem = self.csi_len
        cdef long[:] tx_channel_mem = self.tx_channel
        cdef long[:] err_info_mem = self.err_info
        cdef long[:] noise_floor_mem = self.noise_floor
        cdef long[:] Rate_mem = self.Rate
        cdef long[:] bandWidth_mem = self.bandWidth
        cdef long[:] num_tones_mem = self.num_tones
        cdef long[:] nr_mem = self.nr
        cdef long[:] nc_mem = self.nc
        cdef long[:] rssi_mem = self.rssi
        cdef long[:] rssi_1_mem = self.rssi_1
        cdef long[:] rssi_2_mem = self.rssi_2
        cdef long[:] rssi_3_mem = self.rssi_3
        cdef long[:] payload_len_mem = self.payload_len
        cdef double complex[:, :, :, :] csi_mem = self.csi
        cdef long[:, :] payload_mem = self.payload

        cdef int cur = 0
        cdef int count = 0
        cdef int c_len, pl_len, pl_stop

        cdef int bits_left
        cdef int bitmask
        cdef int idx
        cdef int h_data
        cdef int curren_data
        cdef int k, nc_idx, nr_idx
        cdef int imag
        cdef int real
        cdef unsigned char buf[4096]
        cdef unsigned char csi_buf[4096]

        while cur < (lens - 4):
            fread(&buf, sizeof(unsigned char), 2, f)
            field_len = int.from_bytes(buf[:2], byteorder=endian)
            cur += 2
            if (cur + field_len) > lens:
                break
            
            fread(&buf, sizeof(unsigned char), 25, f)
            timestamp_mem[count] = int.from_bytes(buf[:8], byteorder=endian)
            csi_len_mem[count] = int.from_bytes(buf[8:10], byteorder=endian)
            tx_channel_mem[count] = int.from_bytes(buf[10:12], byteorder=endian)
            err_info_mem[count] = buf[12]
            noise_floor_mem[count] = buf[13]
            Rate_mem[count] = buf[14]
            bandWidth_mem[count] = buf[15]
            num_tones_mem[count] = buf[16]
            nr_mem[count] = buf[17]
            nc_mem[count] = buf[18]
            rssi_mem[count] = buf[19]
            rssi_1_mem[count] = buf[20]
            rssi_2_mem[count] = buf[21]
            rssi_3_mem[count] = buf[22]
            payload_len_mem[count] = int.from_bytes(buf[23:25], byteorder=endian)
            cur += 25

            if buf[17] > self.Nrxnum:
                raise Exception("Error: `Nrxnum=%d` is too small, Stop!\n" % (self.Nrxnum))
            if buf[18] > self.Ntxnum:
                raise Exception("Error: `Ntxnum=%d` is too small, Stop!\n" % (self.Ntxnum))

            c_len = csi_len_mem[count]
            if c_len > 0:
                fread(&csi_buf, sizeof(unsigned char), c_len, f)
                bits_left = 16
                bitmask = (1 << 10) - 1

                idx = 0
                h_data = csi_buf[idx]
                idx += 1
                h_data += (csi_buf[idx] << 8)
                idx += 1
                curren_data = h_data & ((1 << 16) - 1)

                for k in range(buf[16]):
                    for nr_idx in range(buf[17]):
                        for nc_idx in range(buf[18]):
                            # imag
                            if (bits_left - 10) < 0:
                                h_data = csi_buf[idx]
                                idx += 1
                                h_data += (csi_buf[idx] << 8)
                                idx += 1
                                curren_data += h_data << bits_left
                                bits_left += 16
                            imag = curren_data & bitmask
                            if imag & (1 << 9):
                                imag -= (1 << 10)

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
                            if real & (1 << 9):
                                real -= (1 << 10)

                            bits_left -= 10
                            curren_data = curren_data >> 10
                            # csi
                            set_csi_mem(csi_mem, count, k, nr_idx, nc_idx, real, imag)
                cur += c_len

            pl_len = payload_len_mem[count]
            pl_stop = min(pl_len, self.pl_size)
            if pl_len > 0:
                fread(&buf, sizeof(unsigned char), pl_len, f)
                self.payload[count, :pl_stop] = bytearray(buf[:pl_stop])
                cur += pl_len

            if (cur + 420 > lens):
                count -= 1
                break

            count += 1

        fclose(f)

        if self.if_report:
            self.__report(count)

        del timestamp_mem
        del csi_len_mem
        del tx_channel_mem
        del err_info_mem
        del noise_floor_mem
        del Rate_mem
        del bandWidth_mem
        del num_tones_mem
        del nr_mem
        del nc_mem
        del rssi_mem
        del rssi_1_mem
        del rssi_2_mem
        del rssi_3_mem
        del payload_len_mem
        del csi_mem
        del payload_mem

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
        self.count = count

    def __report(self, count):
        """report parsed result."""
        print(str(count) + " packets parsed")


@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline void intel_mm_o3(double complex[:, :, :] ret_mem,
                             double complex[:, :, :] scaled_csi_mem,
                             double complex[:, :] sm, int N, int M):
    """Matrix multiplication of O^3
    
    the function uses a trick of GEMM. It can be faster by using OPENMP and BLAS, but
    needs more dependencies.
    """
    cdef int i, j, k, g
    cdef double complex sm00, sm01, sm02, sm10, sm11, sm12, sm20, sm21, sm22
    cdef double complex r0, r1, r2

    if M == 2:
        sm00 = sm[0, 0]
        sm01 = sm[0, 1]
        sm10 = sm[1, 0]
        sm11 = sm[1, 1]
        for i in range(30):
            for j in range(N):
                r0 = scaled_csi_mem[i, j, 0]
                r1 = scaled_csi_mem[i, j, 1]
                ret_mem[i, j, 0] = r0 * sm00 + r1 * sm10
                ret_mem[i, j, 1] = r0 * sm01 + r1 * sm11
    if M == 3:
        sm00 = sm[0, 0]
        sm01 = sm[0, 1]
        sm02 = sm[0, 2]
        sm10 = sm[1, 0]
        sm11 = sm[1, 1]
        sm12 = sm[1, 2]
        sm20 = sm[2, 0]
        sm21 = sm[2, 1]
        sm22 = sm[2, 2]
        for i in range(30):
            for j in range(N):
                r0 = scaled_csi_mem[i, j, 0]
                r1 = scaled_csi_mem[i, j, 1]
                r2 = scaled_csi_mem[i, j, 2]
                ret_mem[i, j, 0] = r0 * sm00 + r1 * sm10 + r2 * sm20
                ret_mem[i, j, 1] = r0 * sm01 + r1 * sm11 + r2 * sm21
                ret_mem[i, j, 2] = r0 * sm02 + r1 * sm12 + r2 * sm22


@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline void set_csi_mem(double complex[:, :, :, :] csi_mem, int count,
							 int s, int r, int t, double real, double imag):
    csi_mem[count, s, r, t] = real + imag * 1.j


cdef __btype():
    btype = None
    if sys.platform == 'linux':
        if platform.architecture()[0] == "64bit":
            btype = np.int64
        else:
            btype = np.int32
    elif sys.platform == 'win32':
        btype = np.int32
    else:
        raise Exception("Error: Only work on linux and windows !\n")
    return btype
