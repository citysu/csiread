from libc.stdio cimport (fopen, fread, fclose, fseek, ftell, printf, FILE,
                         SEEK_END, SEEK_SET, SEEK_CUR)
from libc.stdint cimport (uint16_t, int16_t, uint32_t, int32_t, uint8_t,
                          int8_t, uint64_t)
from libc.math cimport pi, log10, pow, sqrt
from libc.stdlib cimport exit
import os
import struct

import numpy as np
cimport numpy as np
cimport cython


cdef class Intel:
    def __cinit__(self, file, nrxnum=3, ntxnum=2, pl_size=0, if_report=True,
                  bufsize=0, *argv, **kw):
        self.file = file
        self.nrxnum = nrxnum
        self.ntxnum = ntxnum
        self.pl_size = pl_size
        self.if_report = if_report

        if bufsize == 0:
            if file is None:
                self.count = 1
                pk_num = 1
            else:
                lens = os.path.getsize(file)
                pk_num = lens // (35 + 60 * 1 * 1)
        else:
            pk_num = bufsize

        btype = np.intp

        self.buf_timestamp_low = np.zeros([pk_num], dtype=np.uint32)
        self.buf_bfee_count = np.zeros([pk_num], dtype=btype)
        self.buf_Nrx = np.zeros([pk_num], dtype=btype)
        self.buf_Ntx = np.zeros([pk_num], dtype=btype)
        self.buf_rssi_a = np.zeros([pk_num], dtype=btype)
        self.buf_rssi_b = np.zeros([pk_num], dtype=btype)
        self.buf_rssi_c = np.zeros([pk_num], dtype=btype)
        self.buf_noise = np.zeros([pk_num], dtype=btype)
        self.buf_agc = np.zeros([pk_num], dtype=btype)
        self.buf_perm = np.zeros([pk_num, 3], dtype=btype)
        self.buf_rate = np.zeros([pk_num], dtype=btype)
        self.buf_csi = np.zeros([pk_num, 30, self.nrxnum, self.ntxnum],
                                dtype=np.complex128)
        self.buf_total_rss = np.zeros([pk_num], dtype=np.float64)

        self.buf_fc = np.zeros([pk_num], dtype=btype)
        self.buf_dur = np.zeros([pk_num], dtype=btype)
        self.buf_addr_des = np.zeros([pk_num, 6], dtype=btype)
        self.buf_addr_src = np.zeros([pk_num, 6], dtype=btype)
        self.buf_addr_bssid = np.zeros([pk_num, 6], dtype=btype)
        self.buf_seq = np.zeros([pk_num], dtype=btype)
        self.buf_payload = np.zeros([pk_num, self.pl_size], dtype=np.uint8)

        self.buf_timestamp_low_mem = self.buf_timestamp_low
        self.buf_bfee_count_mem = self.buf_bfee_count
        self.buf_Nrx_mem = self.buf_Nrx
        self.buf_Ntx_mem = self.buf_Ntx
        self.buf_rssi_a_mem = self.buf_rssi_a
        self.buf_rssi_b_mem = self.buf_rssi_b
        self.buf_rssi_c_mem = self.buf_rssi_c
        self.buf_noise_mem = self.buf_noise
        self.buf_agc_mem = self.buf_agc
        self.buf_perm_mem = self.buf_perm
        self.buf_rate_mem = self.buf_rate
        self.buf_csi_mem = self.buf_csi
        self.buf_total_rss_mem = self.buf_total_rss

        self.buf_fc_mem = self.buf_fc
        self.buf_dur_mem = self.buf_dur
        self.buf_addr_des_mem = self.buf_addr_des
        self.buf_addr_src_mem = self.buf_addr_src
        self.buf_addr_bssid_mem = self.buf_addr_bssid
        self.buf_seq_mem = self.buf_seq
        self.buf_payload_mem = self.buf_payload

        #  Conjugate Transpose
        sm_2_20 = np.array([[1,  1],
                            [1, -1]],
                           dtype=np.complex128) / np.sqrt(2)
        sm_2_40 = np.array([[ 1, -1j],
                            [-1j, 1]],
                           dtype=np.complex128) / np.sqrt(2)
        sm_3_20 = np.array([[-2*pi/16,      2*pi/(80/23), -2*pi/(80/13)],
                            [-2*pi/(80/33), 2*pi/(48/13),  2*pi/(240/37)],
                            [ 2*pi/(80/3),  2*pi/(240/13), 2*pi/(48/13)]],
                           dtype=np.complex128)
        sm_3_20 = np.power(np.e, -1j * sm_3_20) / np.sqrt(3)
        sm_3_40 = np.array([[-2*pi/16,      -2*pi/(80/37),    2*pi/(80/7)],
                            [-2*pi/(80/13), -2*pi/(48/11),   -2*pi/(240/83)],
                            [ 2*pi/(80/23), -2*pi/(240/107), -2*pi/(48/11)]],
                           dtype=np.complex128)
        sm_3_40 = np.power(np.e, -1j * sm_3_40) / np.sqrt(3)

        self.sm_2_20_mem = sm_2_20
        self.sm_2_40_mem = sm_2_40
        self.sm_3_20_mem = sm_3_20
        self.sm_3_40_mem = sm_3_40

    def __init__(self, file, nrxnum=3, ntxnum=2, pl_size=0, if_report=True,
                 bufsize=0):
        pass

    cpdef read(self):
        self.seek(self.file, 0, 0)

    cpdef seek(self, file, long pos, long num):
        tempfile = file.encode(encoding="utf-8")
        cdef char *datafile = tempfile
        cdef FILE *f = fopen(datafile, "rb")
        if f is NULL:
            printf("Open failed!\n")
            exit(-1)

        fseek(f, 0, SEEK_END)
        cdef long lens = ftell(f)
        fseek(f, pos, SEEK_SET)

        cdef int count_0xbb = 0
        cdef int count_0xc1 = 0
        cdef unsigned short field_len
        cdef unsigned char code
        cdef unsigned char buf[1024]
        cdef unsigned char *payload
        cdef int l

        cdef int index, index_step
        cdef int i, j, k, g, perm_j
        cdef uint8_t remainder = 0
        cdef double a, b

        if num == 0:
            num = lens

        while pos < (lens-3):
            l = <int>fread(&buf, sizeof(unsigned char), 3, f)
            field_len = buf[1] + (buf[0] << 8)
            code = buf[2]

            if code == 0xbb:
                l = <int>fread(buf, sizeof(unsigned char), field_len - 1, f)
                if l != (field_len - 1):
                    break  # finished

                self.buf_timestamp_low_mem[count_0xbb] = cu32l(buf[0], buf[1],
                                                               buf[2], buf[3])
                self.buf_bfee_count_mem[count_0xbb] = cu16l(buf[4], buf[5])
                self.buf_Nrx_mem[count_0xbb] = buf[8]
                self.buf_Ntx_mem[count_0xbb] = buf[9]
                self.buf_rssi_a_mem[count_0xbb] = buf[10]
                self.buf_rssi_b_mem[count_0xbb] = buf[11]
                self.buf_rssi_c_mem[count_0xbb] = buf[12]
                self.buf_noise_mem[count_0xbb] = <int8_t>buf[13]
                self.buf_agc_mem[count_0xbb] = buf[14]
                self.buf_rate_mem[count_0xbb] = cu16l(buf[18], buf[19])

                self.buf_perm_mem[count_0xbb, 0] = (buf[15] & 0x3)
                self.buf_perm_mem[count_0xbb, 1] = ((buf[15] >> 2) & 0x3)
                self.buf_perm_mem[count_0xbb, 2] = ((buf[15] >> 4) & 0x3)

                if buf[8] > self.nrxnum:
                    fclose(f)
                    raise ValueError("nrxnum=%d is too small!\n" % self.nrxnum)
                if buf[9] > self.ntxnum:
                    fclose(f)
                    raise ValueError("ntxnum=%d is too small!\n" % self.ntxnum)
                if buf[16] | (buf[17] << 8) != 60 * buf[8] * buf[9] + 12:
                    fclose(f)
                    raise Exception("Wrong beamforming matrix size"
                                    ", %dth packet is broken!" % count_0xbb)

                payload = &buf[20]
                index = 0
                for i in range(30):
                    index = index + 3
                    remainder = index & 0x7
                    for j in range(buf[8]):
                        with cython.boundscheck(False):
                            perm_j = <int>self.buf_perm_mem[count_0xbb, j]
                        for k in range(buf[9]):
                            index_step = index >> 3
                            a = ccsi(payload[index_step + 0],
                                     payload[index_step + 1], remainder)
                            b = ccsi(payload[index_step + 1],
                                     payload[index_step + 2], remainder)

                            set_csi_mem(self.buf_csi_mem, count_0xbb,
                                        i, perm_j, k, a, b)
                            index += 16
                count_0xbb += 1

            elif code == 0xc1:
                l = <int>fread(buf, sizeof(unsigned char), field_len - 1, f)
                if l != (field_len - 1):
                    break  # finished

                self.buf_fc_mem[count_0xc1] = cu16l(buf[0], buf[1])
                self.buf_dur_mem[count_0xc1] = cu16l(buf[2], buf[3])

                for g in range(6):
                    self.buf_addr_des_mem[count_0xc1, g] = buf[4+g]
                    self.buf_addr_src_mem[count_0xc1, g] = buf[10+g]
                    self.buf_addr_bssid_mem[count_0xc1, g] = buf[16+g]

                self.buf_seq_mem[count_0xc1] = cu16l(buf[22], buf[23])

                for g in range(min(self.pl_size, field_len - 1)):
                    self.buf_payload_mem[count_0xc1, g] = buf[g]

                count_0xc1 += 1

            else:
                fseek(f, field_len - 1, SEEK_CUR)
            pos += (field_len + 2)
            if count_0xbb >= num:
                break

        fclose(f)

        if self.if_report:
            self.__report(count_0xbb, count_0xc1)

        self.timestamp_low = self.buf_timestamp_low[:count_0xbb]
        self.bfee_count = self.buf_bfee_count[:count_0xbb]
        self.Nrx = self.buf_Nrx[:count_0xbb]
        self.Ntx = self.buf_Ntx[:count_0xbb]
        self.rssi_a = self.buf_rssi_a[:count_0xbb]
        self.rssi_b = self.buf_rssi_b[:count_0xbb]
        self.rssi_c = self.buf_rssi_c[:count_0xbb]
        self.noise = self.buf_noise[:count_0xbb]
        self.agc = self.buf_agc[:count_0xbb]
        self.perm = self.buf_perm[:count_0xbb, :]
        self.rate = self.buf_rate[:count_0xbb]
        self.csi = self.buf_csi[:count_0xbb, :, :, :]
        self.count = count_0xbb

        self.fc = self.buf_fc[:count_0xc1]
        self.dur = self.buf_dur[:count_0xc1]
        self.addr_des = self.buf_addr_des[:count_0xc1]
        self.addr_src = self.buf_addr_src[:count_0xc1]
        self.addr_bssid = self.buf_addr_bssid[:count_0xc1]
        self.seq = self.buf_seq[:count_0xc1]
        self.payload = self.buf_payload[:count_0xc1]

    cpdef pmsg(self, unsigned char *data):
        cdef unsigned char code
        cdef unsigned char *buf
        cdef unsigned char *payload

        cdef int index, index_step
        cdef int i, j, k, g, perm_j
        cdef uint8_t remainder = 0
        cdef double a, b

        code = data[0]
        buf = data
        buf += 1

        if code == 0xbb:
            self.buf_timestamp_low_mem[0] = cu32l(buf[0], buf[1],
                                                  buf[2], buf[3])
            self.buf_bfee_count_mem[0] = cu16l(buf[4], buf[5])
            self.buf_Nrx_mem[0] = buf[8]
            self.buf_Ntx_mem[0] = buf[9]
            self.buf_rssi_a_mem[0] = buf[10]
            self.buf_rssi_b_mem[0] = buf[11]
            self.buf_rssi_c_mem[0] = buf[12]
            self.buf_noise_mem[0] = <int8_t>buf[13]
            self.buf_agc_mem[0] = buf[14]
            self.buf_rate_mem[0] = cu16l(buf[18], buf[19])

            self.buf_perm_mem[0, 0] = (buf[15] & 0x3)
            self.buf_perm_mem[0, 1] = ((buf[15] >> 2) & 0x3)
            self.buf_perm_mem[0, 2] = ((buf[15] >> 4) & 0x3)

            if buf[8] > self.nrxnum:
                raise ValueError("nrxnum=%d is too small!\n" % self.nrxnum)
            if buf[9] > self.ntxnum:
                raise ValueError("ntxnum=%d is too small!\n" % self.ntxnum)
            if buf[16] | (buf[17] << 8) != 60 * buf[8] * buf[9] + 12:
                printf("Wrong beamforming matrix size, the packet is broken!\n")
                return code

            payload = &buf[20]
            index = 0
            for i in range(30):
                index = index + 3
                remainder = index & 0x7
                for j in range(buf[8]):
                    with cython.boundscheck(False):
                        perm_j = <int>self.buf_perm_mem[0, j]
                    for k in range(buf[9]):
                        index_step = index >> 3
                        a = ccsi(payload[index_step + 0],
                                 payload[index_step + 1], remainder)
                        b = ccsi(payload[index_step + 1],
                                 payload[index_step + 2], remainder)

                        set_csi_mem(self.buf_csi_mem, 0, i, perm_j, k, a, b)
                        index += 16
        if code == 0xc1:
            self.buf_fc_mem[0] = cu16l(buf[0], buf[1])
            self.buf_dur_mem[0] = cu16l(buf[2], buf[3])

            for g in range(6):
                self.buf_addr_des_mem[0, g] = buf[4+g]
                self.buf_addr_src_mem[0, g] = buf[10+g]
                self.buf_addr_bssid_mem[0, g] = buf[16+g]

            self.buf_seq_mem[0] = cu16l(buf[22], buf[23])

            for g in range(min(self.pl_size, len(data) - 1)):
                self.buf_payload_mem[0, g] = buf[g]

        self.timestamp_low = self.buf_timestamp_low
        self.bfee_count = self.buf_bfee_count
        self.Nrx = self.buf_Nrx
        self.Ntx = self.buf_Ntx
        self.rssi_a = self.buf_rssi_a
        self.rssi_b = self.buf_rssi_b
        self.rssi_c = self.buf_rssi_c
        self.noise = self.buf_noise
        self.agc = self.buf_agc
        self.perm = self.buf_perm
        self.rate = self.buf_rate
        self.csi = self.buf_csi

        self.fc = self.buf_fc
        self.dur = self.buf_dur
        self.addr_des = self.buf_addr_des
        self.addr_src = self.buf_addr_src
        self.addr_bssid = self.buf_addr_bssid
        self.seq = self.buf_seq
        self.payload = self.buf_payload

        return code

    def readstp(self, endian='little'):
        self.stp = read_stpfile(self.file + "stp", endian)
        return self.stp[0]

    cpdef get_total_rss(self):
        cdef int i
        cdef double temp
        for i in range(self.count):
            if self.buf_rssi_a_mem[i]:
                temp = pow(10, self.buf_rssi_a_mem[i] / 10)
                self.buf_total_rss_mem[i] += temp
            if self.buf_rssi_b_mem[i]:
                temp = pow(10, self.buf_rssi_b_mem[i] / 10)
                self.buf_total_rss_mem[i] += temp
            if self.buf_rssi_c_mem[i]:
                temp = pow(10, self.buf_rssi_c_mem[i] / 10)
                self.buf_total_rss_mem[i] += temp
            if self.buf_total_rss_mem[i]:
                temp = 10 * log10(self.buf_total_rss_mem[i]) - 44
                temp -= self.buf_agc_mem[i]
                self.buf_total_rss_mem[i] = temp
        return self.buf_total_rss[:self.count]

    cpdef get_scaled_csi(self, inplace=False):
        cdef int i, j, k, g
        cdef double constant2 = 2
        cdef double constant4_5 = pow(10, 0.45)
        cdef double temp, quant_error_pwr, thermal_noise_pwr
        cdef double total_noise_pwr, scale

        self.get_total_rss()

        if inplace:
            scaled_csi = self.csi
        else:
            scaled_csi = np.zeros_like(self.csi)
        cdef np.complex128_t[:, :, :, :] scaled_csi_mem = scaled_csi

        for i in range(self.count):
            temp = 0
            for j in range(30):
                for k in range(self.nrxnum):
                    for g in range(self.ntxnum):
                        with cython.boundscheck(False):
                            temp += (self.buf_csi_mem[i, j, k, g].real * \
                                     self.buf_csi_mem[i, j, k, g].real + \
                                     self.buf_csi_mem[i, j, k, g].imag * \
                                     self.buf_csi_mem[i, j, k, g].imag)
            scale = pow(10, self.buf_total_rss_mem[i] / 10) / (temp / 30)
            if self.buf_noise_mem[i] == -127:
                thermal_noise_pwr = pow(10, -9.2)
            else:
                thermal_noise_pwr = pow(10, self.buf_noise_mem[i] / 10)
            quant_error_pwr = scale * (self.buf_Nrx_mem[i] * self.buf_Ntx_mem[i])
            total_noise_pwr = thermal_noise_pwr + quant_error_pwr
            if self.buf_Ntx_mem[i] == 2:
                total_noise_pwr /= constant2
            if self.buf_Ntx_mem[i] == 3:
                total_noise_pwr /= constant4_5
            scale = sqrt(scale / total_noise_pwr)
            for j in range(30):
                for k in range(self.nrxnum):
                    for g in range(self.ntxnum):
                        with cython.boundscheck(False):
                            scaled_csi_mem[i, j, k, g].real = \
                                self.buf_csi_mem[i, j, k, g].real * scale
                            scaled_csi_mem[i, j, k, g].imag = \
                                self.buf_csi_mem[i, j, k, g].imag * scale
        return scaled_csi

    def get_scaled_csi_sm(self, inplace=False):
        return self.__remove_sm(self.get_scaled_csi(inplace), True)

    def apply_sm(self, scaled_csi):
        return self.__remove_sm(scaled_csi)

    cdef __remove_sm(self, scaled_csi, inplace=False):
        """Actually undo the input spatial mapping

        Args:
            scaled_csi (ndarray): Channel matrix H.
            inplace (bool): Optionally do the operation in-place. Default: False

        Returns:
            ndarray: The pure MIMO channel matrix H.
        """
        # Ntx is not a constant array
        if inplace:
            ret = scaled_csi
        else:
            ret = np.zeros_like(self.csi)

        cdef int i, N, M, B
        cdef np.complex128_t[:, :, :, :] scaled_csi_mem = scaled_csi
        cdef np.complex128_t[:, :, :, :] ret_mem = ret
 
        for i in range(self.count):
            M = <int>self.buf_Ntx_mem[i]
            N = <int>self.buf_Nrx_mem[i]
            B = (self.buf_rate_mem[i] & 0x800) == 0x800
            if B:
                if M == 3:
                    intel_mm_o3(ret_mem[i], scaled_csi_mem[i],
                                self.sm_3_40_mem, N, M)
                elif M == 2:
                    intel_mm_o3(ret_mem[i], scaled_csi_mem[i],
                                self.sm_2_40_mem, N, M)
                else:
                    if inplace is False:
                        ret_mem[i] = scaled_csi_mem[i]
            else:
                if M == 3:
                    intel_mm_o3(ret_mem[i], scaled_csi_mem[i],
                                self.sm_3_20_mem, N, M)
                elif M == 2:
                    intel_mm_o3(ret_mem[i], scaled_csi_mem[i],
                                self.sm_2_20_mem, N, M)
                else:
                    if inplace is False:
                        ret_mem[i] = scaled_csi_mem[i]
        del scaled_csi_mem
        del ret_mem

        return ret

    def __report(self, int count_0xbb, int count_0xc1):
        """Report parsed result."""
        if count_0xbb == 0:
            printf("connector_log=0x%x\n", 4)
            printf("%d 0xc1 packets parsed\n", count_0xc1)
        elif count_0xc1 == 0:
            printf("connector_log=0x%x\n", 1)
            printf("%d 0xbb packets parsed\n", count_0xbb)
        else:
            printf("connector_log=0x%x\n", 1 | 4)
            printf("%d 0xc1 packets parsed\n", count_0xc1)
            printf("%d 0xbb packets parsed\n", count_0xbb)


cdef class Atheros:
    def __cinit__(self, file, nrxnum=3, ntxnum=2, pl_size=0, tones=56,
                  if_report=True, bufsize=0, *argv, **kw):
        self.file = file
        self.nrxnum = nrxnum
        self.ntxnum = ntxnum
        self.tones = tones
        self.pl_size = pl_size
        self.if_report = if_report

        if tones not in [56, 114]:
            raise ValueError("tones can only take 56 and 114!\n")

        if bufsize == 0:
            if file is None:
                self.count = 1
                pk_num = 1
            else:
                lens = os.path.getsize(file)
                pk_num = int(lens / 420)
        else:
            pk_num = bufsize

        btype = np.intp
        self.buf_timestamp = np.zeros([pk_num], dtype=np.uint64)
        self.buf_csi_len = np.zeros([pk_num], dtype=btype)
        self.buf_tx_channel = np.zeros([pk_num], dtype=btype)
        self.buf_err_info = np.zeros([pk_num], dtype=btype)
        self.buf_noise_floor = np.zeros([pk_num], dtype=btype)
        self.buf_Rate = np.zeros([pk_num], dtype=btype)
        self.buf_bandWidth = np.zeros([pk_num], dtype=btype)
        self.buf_num_tones = np.zeros([pk_num], dtype=btype)
        self.buf_nr = np.zeros([pk_num], dtype=btype)
        self.buf_nc = np.zeros([pk_num], dtype=btype)
        self.buf_rssi = np.zeros([pk_num], dtype=btype)
        self.buf_rssi_1 = np.zeros([pk_num], dtype=btype)
        self.buf_rssi_2 = np.zeros([pk_num], dtype=btype)
        self.buf_rssi_3 = np.zeros([pk_num], dtype=btype)
        self.buf_payload_len = np.zeros([pk_num], dtype=btype)
        self.buf_csi = np.zeros([pk_num, self.tones, self.nrxnum, self.ntxnum],
                                dtype=np.complex128)
        self.buf_payload = np.zeros([pk_num, self.pl_size], dtype=np.uint8)

        self.buf_timestamp_mem = self.buf_timestamp
        self.buf_csi_len_mem = self.buf_csi_len
        self.buf_tx_channel_mem = self.buf_tx_channel
        self.buf_err_info_mem = self.buf_err_info
        self.buf_noise_floor_mem = self.buf_noise_floor
        self.buf_Rate_mem = self.buf_Rate
        self.buf_bandWidth_mem = self.buf_bandWidth
        self.buf_num_tones_mem = self.buf_num_tones
        self.buf_nr_mem = self.buf_nr
        self.buf_nc_mem = self.buf_nc
        self.buf_rssi_mem = self.buf_rssi
        self.buf_rssi_1_mem = self.buf_rssi_1
        self.buf_rssi_2_mem = self.buf_rssi_2
        self.buf_rssi_3_mem = self.buf_rssi_3
        self.buf_payload_len_mem = self.buf_payload_len
        self.buf_csi_mem = self.buf_csi
        self.buf_payload_mem = self.buf_payload

    def __init__(self, file, nrxnum=3, ntxnum=2, pl_size=0, tones=56,
                 if_report=True, bufsize=0):
        pass

    cpdef read(self, endian='little'):
        self.seek(self.file, 0, 0, endian)

    cpdef seek(self, file, long pos, long num, endian='little'):
        cdef FILE *f

        tempfile = file.encode(encoding="utf-8")
        cdef char *datafile = tempfile

        f = fopen(datafile, "rb")
        if f is NULL:
            printf("Open failed!\n")
            exit(-1)

        fseek(f, 0, SEEK_END)
        cdef long lens = ftell(f)
        fseek(f, pos, SEEK_SET)

        cdef int count = 0
        cdef int c_len, pl_len, pl_stop
        cdef int l, field_len
        cdef uint16_t (*ath_cu16)(uint8_t, uint8_t)
        cdef uint64_t (*ath_cu64)(uint64_t, uint64_t, uint64_t, uint64_t,
                                  uint64_t, uint64_t, uint64_t, uint64_t)

        if num == 0:
            num = lens

        cdef int bits_left, bitmask, idx, h_data, current_data
        cdef int k, nc_idx, nr_idx, imag, real, i
        cdef unsigned char buf[4096]
        cdef unsigned char csi_buf[4096]
        if endian == "little":
            ath_cu16 = cu16l
            ath_cu64 = cu64l
        elif endian == "big":
            ath_cu16 = cu16b
            ath_cu64 = cu64b
        else:
            fclose(f)
            raise ValueError("endian must be either 'little' or 'big'")

        while pos < (lens - 4):
            l = <int>fread(&buf, sizeof(unsigned char), 2, f)
            field_len = ath_cu16(buf[0], buf[1])
            pos += 2
            if (pos + field_len) > lens:
                break

            l = <int>fread(&buf, sizeof(unsigned char), 25, f)
            self.buf_timestamp_mem[count] = ath_cu64(buf[0], buf[1], buf[2],
                                                     buf[3], buf[4], buf[5],
                                                     buf[6], buf[7])
            self.buf_csi_len_mem[count] = ath_cu16(buf[8], buf[9])
            self.buf_tx_channel_mem[count] = ath_cu16(buf[10], buf[11])
            self.buf_payload_len_mem[count] = ath_cu16(buf[23], buf[24])
            self.buf_err_info_mem[count] = buf[12]
            self.buf_noise_floor_mem[count] = buf[13]
            self.buf_Rate_mem[count] = buf[14]
            self.buf_bandWidth_mem[count] = buf[15]
            self.buf_num_tones_mem[count] = buf[16]
            self.buf_nr_mem[count] = buf[17]
            self.buf_nc_mem[count] = buf[18]
            self.buf_rssi_mem[count] = buf[19]
            self.buf_rssi_1_mem[count] = buf[20]
            self.buf_rssi_2_mem[count] = buf[21]
            self.buf_rssi_3_mem[count] = buf[22]
            pos += 25

            c_len = <int>self.buf_csi_len_mem[count]
            if c_len > 0:
                if buf[17] > self.nrxnum:
                    fclose(f)
                    raise ValueError("nrxnum=%d is too small!\n" % self.nrxnum)
                if buf[18] > self.ntxnum:
                    fclose(f)
                    raise ValueError("ntxnum=%d is too small!\n" % self.ntxnum)

                l = <int>fread(&csi_buf, sizeof(unsigned char), c_len, f)
                bits_left = 16
                bitmask = (1 << 10) - 1

                idx = 0
                h_data = csi_buf[idx]
                idx += 1
                h_data += (csi_buf[idx] << 8)
                idx += 1
                current_data = h_data & ((1 << 16) - 1)

                for k in range(buf[16]):
                    for nr_idx in range(buf[17]):
                        for nc_idx in range(buf[18]):
                            # imag
                            if (bits_left - 10) < 0:
                                h_data = csi_buf[idx]
                                idx += 1
                                h_data += (csi_buf[idx] << 8)
                                idx += 1
                                current_data += h_data << bits_left
                                bits_left += 16
                            imag = current_data & bitmask
                            if imag & (1 << 9):
                                imag -= (1 << 10)

                            bits_left -= 10
                            current_data = current_data >> 10
                            # real
                            if (bits_left - 10) < 0:
                                h_data = csi_buf[idx]
                                idx += 1
                                h_data += (csi_buf[idx] << 8)
                                idx += 1
                                current_data += h_data << bits_left
                                bits_left += 16
                            real = current_data & bitmask
                            if real & (1 << 9):
                                real -= (1 << 10)

                            bits_left -= 10
                            current_data = current_data >> 10
                            # csi
                            set_csi_mem(self.buf_csi_mem, count, k,
                                        nr_idx, nc_idx, real, imag)
                pos += c_len

            pl_len = <int>self.buf_payload_len_mem[count]
            pl_stop = min(pl_len, self.pl_size)
            if pl_len > 0:
                l = <int>fread(&buf, sizeof(unsigned char), pl_len, f)
                for i in range(pl_stop):
                    self.buf_payload_mem[count, i] = buf[i]
                pos += pl_len

            # In matlab, read_log_file drops the last two packets, but here we 
            # keep them.
            count += 1
            if count >= num:
                break

        fclose(f)

        if self.if_report:
            self.__report(count)

        self.timestamp = self.buf_timestamp[:count]
        self.csi_len = self.buf_csi_len[:count]
        self.tx_channel = self.buf_tx_channel[:count]
        self.err_info = self.buf_err_info[:count]
        self.noise_floor = self.buf_noise_floor[:count]
        self.Rate = self.buf_Rate[:count]
        self.bandWidth = self.buf_bandWidth[:count]
        self.num_tones = self.buf_num_tones[:count]
        self.nr = self.buf_nr[:count]
        self.nc = self.buf_nc[:count]
        self.rssi = self.buf_rssi[:count]
        self.rssi_1 = self.buf_rssi_1[:count]
        self.rssi_2 = self.buf_rssi_2[:count]
        self.rssi_3 = self.buf_rssi_3[:count]
        self.payload_len = self.buf_payload_len[:count]
        self.csi = self.buf_csi[:count]
        self.payload = self.buf_payload[:count]
        self.count = count

    cpdef pmsg(self, unsigned char *data, endian='little'):
        cdef int count = 0
        cdef int c_len, pl_len, pl_stop

        cdef int bits_left, bitmask, idx, h_data, current_data
        cdef int k, nc_idx, nr_idx, imag, real, i
        cdef unsigned char *buf
        cdef unsigned char *csi_buf
        cdef uint16_t (*ath_cu16)(uint8_t, uint8_t)
        cdef uint64_t (*ath_cu64)(uint64_t, uint64_t, uint64_t, uint64_t,
                                  uint64_t, uint64_t, uint64_t, uint64_t)

        buf = data
        if endian == "little":
            ath_cu16 = cu16l
            ath_cu64 = cu64l
        elif endian == "big":
            ath_cu16 = cu16b
            ath_cu64 = cu64b
        else:
            raise ValueError("endian must be either 'little' or 'big'")
        self.buf_timestamp_mem[count] = ath_cu64(buf[0], buf[1], buf[2],
                                                 buf[3], buf[4], buf[5],
                                                 buf[6], buf[7])
        self.buf_csi_len_mem[count] = ath_cu16(buf[8], buf[9])
        self.buf_tx_channel_mem[count] = ath_cu16(buf[10], buf[11])
        self.buf_payload_len_mem[count] = ath_cu16(buf[23], buf[24])
        self.buf_err_info_mem[count] = buf[12]
        self.buf_noise_floor_mem[count] = buf[13]
        self.buf_Rate_mem[count] = buf[14]
        self.buf_bandWidth_mem[count] = buf[15]
        self.buf_num_tones_mem[count] = buf[16]
        self.buf_nr_mem[count] = buf[17]
        self.buf_nc_mem[count] = buf[18]
        self.buf_rssi_mem[count] = buf[19]
        self.buf_rssi_1_mem[count] = buf[20]
        self.buf_rssi_2_mem[count] = buf[21]
        self.buf_rssi_3_mem[count] = buf[22]

        c_len = <int>self.buf_csi_len_mem[count]
        if c_len > 0:
            if buf[17] > self.nrxnum:
                raise ValueError("nrxnum=%d is too small!\n" % self.nrxnum)
            if buf[18] > self.ntxnum:
                raise ValueError("ntxnum=%d is too small!\n" % self.ntxnum)

            csi_buf = &buf[25]
            bits_left = 16
            bitmask = (1 << 10) - 1

            idx = 0
            h_data = csi_buf[idx]
            idx += 1
            h_data += (csi_buf[idx] << 8)
            idx += 1
            current_data = h_data & ((1 << 16) - 1)

            for k in range(buf[16]):
                for nr_idx in range(buf[17]):
                    for nc_idx in range(buf[18]):
                        # imag
                        if (bits_left - 10) < 0:
                            h_data = csi_buf[idx]
                            idx += 1
                            h_data += (csi_buf[idx] << 8)
                            idx += 1
                            current_data += h_data << bits_left
                            bits_left += 16
                        imag = current_data & bitmask
                        if imag & (1 << 9):
                            imag -= (1 << 10)

                        bits_left -= 10
                        current_data = current_data >> 10
                        # real
                        if (bits_left - 10) < 0:
                            h_data = csi_buf[idx]
                            idx += 1
                            h_data += (csi_buf[idx] << 8)
                            idx += 1
                            current_data += h_data << bits_left
                            bits_left += 16
                        real = current_data & bitmask
                        if real & (1 << 9):
                            real -= (1 << 10)

                        bits_left -= 10
                        current_data = current_data >> 10
                        # csi
                        set_csi_mem(self.buf_csi_mem, count, k,
                                    nr_idx, nc_idx, real, imag)

        pl_len = <int>self.buf_payload_len_mem[count]
        pl_stop = min(pl_len, self.pl_size)
        if pl_len > 0:
            for i in range(pl_stop):
                self.buf_payload_mem[count, i] = buf[25+c_len+i]

        self.timestamp = self.buf_timestamp
        self.csi_len = self.buf_csi_len
        self.tx_channel = self.buf_tx_channel
        self.err_info = self.buf_err_info
        self.noise_floor = self.buf_noise_floor
        self.Rate = self.buf_Rate
        self.bandWidth = self.buf_bandWidth
        self.num_tones = self.buf_num_tones
        self.nr = self.buf_nr
        self.nc = self.buf_nc
        self.rssi = self.buf_rssi
        self.rssi_1 = self.buf_rssi_1
        self.rssi_2 = self.buf_rssi_2
        self.rssi_3 = self.buf_rssi_3
        self.payload_len = self.buf_payload_len
        self.csi = self.buf_csi
        self.payload = self.buf_payload

        return 0xff00

    def readstp(self, endian='little'):
        self.stp = read_stpfile(self.file + "stp", endian)
        return self.stp[0]

    def __report(self, int count):
        """Report parsed result."""
        printf("%d packets parsed\n", count)


cdef class Nexmon:
    def __cinit__(self, file, chip, bw, if_report=True, bufsize=0,
                  *argv, **kw):
        self.file = file
        self.chip = chip
        self.bw = bw
        self.if_report = if_report

        if bufsize == 0:
            if file is None:
                self.count = 1
                pk_num = 1
            else:
                pk_num = self.get_count()
        else:
            pk_num = bufsize

        btype = np.intp
        self.buf_sec = np.zeros([pk_num], dtype=np.uint32)
        self.buf_usec = np.zeros([pk_num], dtype=np.uint32)
        self.buf_caplen = np.zeros([pk_num], dtype=btype)
        self.buf_wirelen = np.zeros([pk_num], dtype=btype)
        self.buf_magic = np.zeros([pk_num], dtype=btype)
        self.buf_src_addr = np.zeros([pk_num, 6], dtype=btype)
        self.buf_seq = np.zeros([pk_num], dtype=btype)
        self.buf_core = np.zeros([pk_num], dtype=btype)
        self.buf_spatial = np.zeros([pk_num], dtype=btype)
        self.buf_chan_spec = np.zeros([pk_num], dtype=btype)
        self.buf_chip_version = np.zeros([pk_num], dtype=btype)
        self.buf_csi = np.zeros([pk_num, int(self.bw * 3.2)],
                                dtype=np.complex128)
        self.buf_sec_mem = self.buf_sec
        self.buf_usec_mem = self.buf_usec
        self.buf_caplen_mem = self.buf_caplen
        self.buf_wirelen_mem = self.buf_wirelen
        self.buf_magic_mem = self.buf_magic
        self.buf_src_addr_mem = self.buf_src_addr
        self.buf_seq_mem = self.buf_seq
        self.buf_core_mem = self.buf_core
        self.buf_spatial_mem = self.buf_spatial
        self.buf_chan_spec_mem = self.buf_chan_spec
        self.buf_chip_version_mem = self.buf_chip_version
        self.buf_csi_mem = self.buf_csi
        self._autoscale = 1

    def __init__(self, file, chip, bw, if_report=True, bufsize=0):
        pass

    cpdef read(self):
        self.seek(self.file, 24, 0)

    cpdef seek(self, file, long pos, long num):
        cdef FILE *f

        tempfile = file.encode(encoding="utf-8")
        cdef char *datafile = tempfile

        f = fopen(datafile, "rb")
        if f is NULL:
            printf("Open failed!\n")
            exit(-1)

        pcap_endian = self.pcapheader(f)
        fseek(f, 0, SEEK_END)
        cdef long lens = ftell(f)
        fseek(f, pos, SEEK_SET)

        cdef int count = 0
        cdef unsigned char buf[4096]
        cdef int l, i
        cdef int nfft = <int>(self.bw * 3.2)
        cdef uint32_t caplen
        cdef uint16_t (*pcap_cu16)(uint8_t, uint8_t) 
        cdef uint32_t (*pcap_cu32)(uint8_t, uint8_t, uint8_t, uint8_t)

        if num == 0:
            num = lens

        if pcap_endian == "little":
            pcap_cu16 = cu16l
            pcap_cu32 = cu32l
        else:
            pcap_cu16 = cu16b
            pcap_cu32 = cu32b

        while pos < (lens - 24):
            # global header
            l = <int>fread(&buf, sizeof(unsigned char), 16, f)
            if l < 16:
                break
            caplen = pcap_cu32(buf[8], buf[9], buf[10], buf[11])
            self.buf_sec_mem[count] = pcap_cu32(buf[0], buf[1], buf[2], buf[3])
            self.buf_usec_mem[count] = pcap_cu32(buf[4], buf[5], buf[6], buf[7])
            self.buf_caplen_mem[count] = caplen
            self.buf_wirelen_mem[count] = pcap_cu32(buf[12], buf[13], buf[14],
                                                    buf[15])
            pos += (16 + caplen)

            # we don't care about enth+ip+udp header
            l = <int>fread(&buf, sizeof(unsigned char), 42, f)
            if buf[6:12] != b'NEXMON':
                fseek(f, caplen - 42, SEEK_CUR)
                continue

            # Endian of the following payload is different from
            # `pcap_endian`. Here, we assume it is always `little`.

            # nexmon header
            l = <int>fread(&buf, sizeof(unsigned char), 18, f)
            self.buf_magic_mem[count] = cu32l(buf[0], buf[1], buf[2], buf[3])
            for i in range(6):
                self.buf_src_addr_mem[count, i] = buf[4+i]
            self.buf_seq_mem[count] = cu16l(buf[10], buf[11])
            self.buf_core_mem[count] = (buf[12] | buf[13]) & 0x7
            self.buf_spatial_mem[count] = ((buf[12] | buf[13]) >> 3) & 0x7
            self.buf_chan_spec_mem[count] = cu16l(buf[14], buf[15])
            self.buf_chip_version_mem[count] = cu16l(buf[16], buf[17])

            # CSI
            l = <int>fread(&buf, sizeof(unsigned char), caplen - 42 - 18, f)
            if self.chip == '4339' or self.chip == '43455c0':
                unpack_int16(buf, self.buf_csi_mem[count], nfft, True)
            elif self.chip == '4358':
                unpack_float(buf, self.buf_csi_mem[count], nfft, 9, 5,
                             self._autoscale, True)
            elif self.chip == '4366c0':
                unpack_float(buf, self.buf_csi_mem[count], nfft, 12, 6,
                             self._autoscale, True)
            else:
                pass

            count += 1
            if count >= num:
                break
        fclose(f)
        self.count = count
        if self.if_report:
            printf("%d packets parsed\n", count)

        self.sec = self.buf_sec[:count]
        self.usec = self.buf_usec[:count]
        self.caplen = self.buf_caplen[:count]
        self.wirelen = self.buf_wirelen[:count]
        self.magic = self.buf_magic[:count]
        self.src_addr = self.buf_src_addr[:count]
        self.seq = self.buf_seq[:count]
        self.core = self.buf_core[:count]
        self.spatial = self.buf_spatial[:count]
        self.chan_spec = self.buf_chan_spec[:count]
        self.chip_version = self.buf_chip_version[:count]
        self.csi = self.buf_csi[:count]

    cpdef pmsg(self, unsigned char *data, endian='little'):
        cdef int count = 0
        cdef unsigned char *buf
        cdef int i
        cdef int nfft = <int>(self.bw * 3.2)

        buf = data

        # magic number
        if buf[:4] != b'\x11\x11\x11\x11':
            return

        # nexmon header
        self.buf_magic_mem[count] = cu32l(buf[0], buf[1], buf[2], buf[3])
        for i in range(6):
            self.buf_src_addr_mem[count, i] = buf[4+i]
        self.buf_seq_mem[count] = cu16l(buf[10], buf[11])
        self.buf_core_mem[count] = (buf[12] | buf[13]) & 0x7
        self.buf_spatial_mem[count] = ((buf[12] | buf[13]) >> 3) & 0x7
        self.buf_chan_spec_mem[count] = cu16l(buf[14], buf[15])
        self.buf_chip_version_mem[count] = cu16l(buf[16], buf[17])

        # CSI
        if self.chip == '4339' or self.chip == '43455c0':
            unpack_int16(&buf[18], self.buf_csi_mem[count], nfft, True)
        elif self.chip == '4358':
            unpack_float(&buf[18], self.buf_csi_mem[count], nfft, 9, 5,
                         self._autoscale, True)
        elif self.chip == '4366c0':
            unpack_float(&buf[18], self.buf_csi_mem[count], nfft, 12, 6,
                         self._autoscale, True)
        else:
            pass

        self.magic = self.buf_magic
        self.src_addr = self.buf_src_addr
        self.seq = self.buf_seq
        self.core = self.buf_core
        self.spatial = self.buf_spatial
        self.chan_spec = self.buf_chan_spec
        self.chip_version = self.buf_chip_version
        self.csi = self.buf_csi

        return 0xf100

    cdef get_count(self):
        cdef FILE *f
        tempfile = self.file.encode(encoding="utf-8")
        cdef char *datafile = tempfile

        f = fopen(datafile, "rb")
        if f is NULL:
            printf("Open failed!\n")
            exit(-1)

        cdef int count = 0
        cdef int l
        cdef uint32_t caplen
        cdef unsigned char buf[64]
        cdef uint32_t (*nex_cu32)(uint8_t, uint8_t, uint8_t, uint8_t)

        # pcap header: head: endian
        pcap_endian = self.pcapheader(f)
        if pcap_endian == 'little':
            nex_cu32 = cu32l
        else:
            nex_cu32 = cu32b

        # count
        while True:
            l = <int>fread(&buf, sizeof(unsigned char), 16+42, f)
            if l < 16:
                break
            if buf[22:28] == b'NEXMON':
                count += 1
            caplen = nex_cu32(buf[8], buf[9], buf[10], buf[11])
            fseek(f, caplen - 42, SEEK_CUR)
        fclose(f)
        return count

    cdef pcapheader(self, FILE *f):
        cdef unsigned char buf[16]
        cdef int l

        l = <int>fread(&buf, sizeof(unsigned char), 4, f)
        magic = buf[:4]
        if magic == b"\xa1\xb2\xc3\xd4":    # big endian
            endian = "big"
            self.nano = False
        elif magic == b"\xd4\xc3\xb2\xa1":  # little endian
            endian = "little"
            self.nano = False
        elif magic == b"\xa1\xb2\x3c\x4d":  # big endian, nanosecond
            endian = "big"
            self.nano = True
        elif magic == b"\x4d\x3c\xb2\xa1":  # little endian, nanosecond
            endian = "little"
            self.nano = True
        else:
            raise Exception("Not a pcap capture file (bad magic: %r)" % magic)

        fseek(f, 20, SEEK_CUR)
        return endian


cdef class NexmonPull46(Nexmon):
    def __cinit__(self, file, chip, bw, if_report=True, bufsize=0,
                  *argv, **kw):
        self.file = file
        self.chip = chip
        self.bw = bw
        self.if_report = if_report

        if bufsize == 0:
            if file is None:
                self.count = 1
                pk_num = 1
            else:
                pk_num = self.get_count()
        else:
            pk_num = bufsize

        btype = np.intp
        self.buf_rssi = np.zeros([pk_num], dtype=btype)
        self.buf_fc = np.zeros([pk_num], dtype=btype)

        self.buf_rssi_mem = self.buf_rssi
        self.buf_fc_mem = self.buf_fc
        self._autoscale = 0

    cpdef seek(self, file, long pos, long num):
        cdef FILE *f

        tempfile = file.encode(encoding="utf-8")
        cdef char *datafile = tempfile

        f = fopen(datafile, "rb")
        if f is NULL:
            printf("Open failed!\n")
            exit(-1)

        pcap_endian = self.pcapheader(f)
        fseek(f, 0, SEEK_END)
        cdef long lens = ftell(f)
        fseek(f, pos, SEEK_SET)

        cdef int count = 0
        cdef unsigned char buf[4096]
        cdef int l, i
        cdef int nfft = <int>(self.bw * 3.2)
        cdef uint32_t caplen
        cdef uint16_t (*pcap_cu16)(uint8_t, uint8_t) 
        cdef uint32_t (*pcap_cu32)(uint8_t, uint8_t, uint8_t, uint8_t)

        if num == 0:
            num = lens

        if pcap_endian == "little":
            pcap_cu16 = cu16l
            pcap_cu32 = cu32l
        else:
            pcap_cu16 = cu16b
            pcap_cu32 = cu32b

        while pos < (lens - 24):
            # global header
            l = <int>fread(&buf, sizeof(unsigned char), 16, f)
            if l < 16:
                break
            caplen = pcap_cu32(buf[8], buf[9], buf[10], buf[11])
            self.buf_sec_mem[count] = pcap_cu32(buf[0], buf[1], buf[2], buf[3])
            self.buf_usec_mem[count] = pcap_cu32(buf[4], buf[5], buf[6], buf[7])
            self.buf_caplen_mem[count] = caplen
            self.buf_wirelen_mem[count] = pcap_cu32(buf[12], buf[13], buf[14],
                                                    buf[15])
            pos += (16 + caplen)

            # we don't care about enth+ip+udp header
            l = <int>fread(&buf, sizeof(unsigned char), 42, f)
            if buf[6:12] != b'NEXMON':
                fseek(f, caplen - 42, SEEK_CUR)
                continue

            # Endian of the following payload is different from
            # `pcap_endian`. Here, we assume it is always `little`.

            # nexmon header
            l = <int>fread(&buf, sizeof(unsigned char), 18, f)
            self.buf_magic_mem[count] = cu16l(buf[0], buf[1])
            self.buf_rssi_mem[count] = <int8_t>buf[2]
            self.buf_fc_mem[count] = buf[3]
            for i in range(6):
                self.buf_src_addr_mem[count, i] = buf[4+i]
            self.buf_seq_mem[count] = cu16l(buf[10], buf[11])
            self.buf_core_mem[count] = (buf[12] | buf[13]) & 0x7
            self.buf_spatial_mem[count] = ((buf[12] | buf[13]) >> 3) & 0x7
            self.buf_chan_spec_mem[count] = cu16l(buf[14], buf[15])
            self.buf_chip_version_mem[count] = cu16l(buf[16], buf[17])

            # CSI
            l = <int>fread(&buf, sizeof(unsigned char), caplen - 42 - 18, f)
            if self.chip == '4339' or self.chip == '43455c0':
                unpack_int16(buf, self.buf_csi_mem[count], nfft, True)
            elif self.chip == '4358':
                unpack_float(buf, self.buf_csi_mem[count], nfft, 9, 5,
                             self._autoscale, True)
            elif self.chip == '4366c0':
                unpack_float(buf, self.buf_csi_mem[count], nfft, 12, 6,
                             self._autoscale, True)
            else:
                pass

            count += 1
            if count >= num:
                break
        fclose(f)
        self.count = count
        if self.if_report:
            printf("%d packets parsed\n", count)

        self.sec = self.buf_sec[:count]
        self.usec = self.buf_usec[:count]
        self.caplen = self.buf_caplen[:count]
        self.wirelen = self.buf_wirelen[:count]
        self.magic = self.buf_magic[:count]
        self.rssi = self.buf_rssi[:count]
        self.fc = self.buf_fc[:count]
        self.src_addr = self.buf_src_addr[:count]
        self.seq = self.buf_seq[:count]
        self.core = self.buf_core[:count]
        self.spatial = self.buf_spatial[:count]
        self.chan_spec = self.buf_chan_spec[:count]
        self.chip_version = self.buf_chip_version[:count]
        self.csi = self.buf_csi[:count]

    cpdef pmsg(self, unsigned char *data, endian='little'):
        cdef int count = 0
        cdef unsigned char *buf
        cdef int i
        cdef int nfft = <int>(self.bw * 3.2)

        buf = data

        # magic number
        if buf[:2] != b'\x11\x11':
            return

        # nexmon header
        self.buf_magic_mem[count] = cu16l(buf[0], buf[1])
        self.buf_rssi_mem[count] = <int8_t>buf[2]
        self.buf_fc_mem[count] = buf[3]
        for i in range(6):
            self.buf_src_addr_mem[count, i] = buf[4+i]
        self.buf_seq_mem[count] = cu16l(buf[10], buf[11])
        self.buf_core_mem[count] = (buf[12] | buf[13]) & 0x7
        self.buf_spatial_mem[count] = ((buf[12] | buf[13]) >> 3) & 0x7
        self.buf_chan_spec_mem[count] = cu16l(buf[114], buf[15])
        self.buf_chip_version_mem[count] = cu16l(buf[16], buf[17])

        # CSI
        if self.chip == '4339' or self.chip == '43455c0':
            unpack_int16(&buf[18], self.buf_csi_mem[count], nfft, True)
        elif self.chip == '4358':
            unpack_float(&buf[18], self.buf_csi_mem[count], nfft, 9, 5,
                         self._autoscale, True)
        elif self.chip == '4366c0':
            unpack_float(&buf[18], self.buf_csi_mem[count], nfft, 12, 6,
                         self._autoscale, True)
        else:
            pass

        self.magic = self.buf_magic
        self.rssi = self.buf_rssi
        self.fc = self.buf_fc
        self.src_addr = self.buf_src_addr
        self.seq = self.buf_seq
        self.core = self.buf_core
        self.spatial = self.buf_spatial
        self.chan_spec = self.buf_chan_spec
        self.chip_version = self.buf_chip_version
        self.csi = self.buf_csi

        return 0xf101


@cython.boundscheck(False)
@cython.wraparound(False)
cdef void intel_mm_o3(np.complex128_t[:, :, :] ret_mem,
                      np.complex128_t[:, :, :] scaled_csi_mem,
                      np.complex128_t[:, :] sm, int N, int M):
    """Matrix multiplication of O^3
    
    The function uses a trick of GEMM. It can be faster by using OPENMP and
    BLAS, but needs more dependencies.
    """
    cdef int i, j
    cdef np.complex128_t sm00, sm01, sm02, sm10, sm11, sm12, sm20, sm21, sm22
    cdef np.complex128_t r0, r1, r2

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
cdef inline void set_csi_mem(np.complex128_t[:, :, :, :] csi_mem, int count,
                             int s, int r, int t, double real, double imag):
    csi_mem[count, s, r, t].real = real
    csi_mem[count, s, r, t].imag = imag


cdef void unpack_int16(uint8_t *buf, np.complex128_t[:] csi_mem, int nfft,
                       bint flag):
    cdef int i, j
    if flag:
        for i in range(nfft):
            j = i * 4
            csi_mem[i].real = <double><int16_t>cu16l(buf[j+0], buf[j+1])
            csi_mem[i].imag = <double><int16_t>cu16l(buf[j+2], buf[j+3])
    else:
        for i in range(nfft):
            j = i * 4
            csi_mem[i].real = <double><int16_t>cu16b(buf[j+0], buf[j+1])
            csi_mem[i].imag = <double><int16_t>cu16b(buf[j+2], buf[j+3])


cdef void unpack_float(uint8_t *buf, np.complex128_t[:] csi_mem, int nfft,
                       int M, int E, int autoscale, bint flag):
    """N = M * R ^ E

    M: Mantissa
    R: Radix
    E: Exponent
    flag: little endian if ``True`` else big endian
    """
    cdef int i, s, e, shft, sgn
    cdef uint32_t h, m, b, x

    cdef int nbits = 10
    cdef int e_p = (1 << (E - 1))
    cdef int e_shift = 1
    cdef int e_zero = - M
    cdef int maxbit = -e_p
    cdef uint32_t k_tof_unpack_sgn_mask = (1 << 31)
    cdef uint32_t ri_mask = (1 << (M - 1)) - 1
    cdef uint32_t E_mask = (1 << E) - 1
    cdef uint32_t sgnr_mask = (1 << (E + 2 * M - 1))
    cdef uint32_t sgni_mask = sgnr_mask >> M
    cdef int8_t He[256]
    cdef int32_t Hout[512]
    cdef int32_t v_real, v_imag

    for i in range(nfft):
        if flag:
            h = cu32l(buf[4*i+0], buf[4*i+1], buf[4*i+2], buf[4*i+3])
        else:
            h = cu32b(buf[4*i+0], buf[4*i+1], buf[4*i+2], buf[4*i+3])

        v_real = <int32_t>((h >> (E + M)) & ri_mask)
        v_imag = <int32_t>((h >> E) & ri_mask)
        e = <int>(h & E_mask)
        if e >= e_p:
            e -= (e_p << 1)
        He[i] = <int8_t>e
        x = <uint32_t>v_real | <uint32_t>v_imag

        if autoscale and x:
            m = 0xffff0000
            b = 0xffff
            s = 16
            while s > 0:
                if x & m:
                    e += s
                    x >>= s
                s >>= 1
                m = (m >> s) & b
                b >>= s
            if e > maxbit:
                maxbit = e
        
        if h & sgnr_mask:
            v_real |= k_tof_unpack_sgn_mask
        if h & sgni_mask:
            v_imag |= k_tof_unpack_sgn_mask

        Hout[i<<1] = v_real
        Hout[(i<<1)+1] = v_imag

    shft = nbits - maxbit
    for i in range(nfft):
        e = He[(i*2 >> e_shift)] + shft
        sgn = 1
        v_real = Hout[i*2]
        if v_real & k_tof_unpack_sgn_mask:
            sgn = -1
            v_real &= ~k_tof_unpack_sgn_mask
        if e < e_zero:
            v_real = 0
        elif e < 0:
            e = -e
            v_real >>= e
        else:
            v_real <<= e
        v_real *= sgn

        e = He[(i*2+1 >> e_shift)] + shft
        sgn = 1
        v_imag = Hout[i*2+1]
        if v_imag & k_tof_unpack_sgn_mask:
            sgn = -1
            v_imag &= ~k_tof_unpack_sgn_mask
        if e < e_zero:
            v_imag = 0
        elif e < 0:
            e = -e
            v_imag >>= e
        else:
            v_imag <<= e
        v_imag *= sgn

        csi_mem[i].real = <double>v_real
        csi_mem[i].imag = <double>v_imag


cdef inline int8_t ccsi(uint8_t a, uint8_t b, uint8_t remainder):
    return ((a >> remainder) | (b << (8 - remainder))) & 0xff


cdef inline uint32_t cu32l(uint8_t a, uint8_t b, uint8_t c, uint8_t d):
    return a | (b << 8) | (c << 16) | (d << 24)


cdef inline uint32_t cu32b(uint8_t a, uint8_t b, uint8_t c, uint8_t d):
    return d | (c << 8) | (b << 16) | (a << 24)


cdef inline uint16_t cu16l(uint8_t a, uint8_t b):
    return a | (b << 8)


cdef inline uint16_t cu16b(uint8_t a, uint8_t b):
    return b | (a << 8)


cdef inline uint64_t cu64l(uint64_t a, uint64_t b, uint64_t c, uint64_t d,
                           uint64_t e, uint64_t f, uint64_t g, uint64_t h):
    return (a | (b << 8) | (c << 16) | (d << 24) |
            (e << 32) | (f << 40) | (g << 48) | (h << 56))


cdef inline uint64_t cu64b(uint64_t a, uint64_t b, uint64_t c, uint64_t d,
                           uint64_t e, uint64_t f, uint64_t g, uint64_t h):
    return (h | (g << 8) | (f << 16) | (e << 24) |
            (d << 32) | (c << 40) | (b << 48) | (a << 56))


cdef read_stpfile(stpfile, endian):
    lens = os.path.getsize(stpfile) // 8
    stp = np.empty(lens)
    format_string = '<LL' if endian == 'little' else '>LL'
    cdef int i, a, b
    f = open(stpfile, "rb")
    for i in range(lens):
        a, b = struct.unpack(format_string, f.read(8))
        stp[i] = a + b / 1000000
    f.close()
    return stp
