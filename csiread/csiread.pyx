from libc.stdlib cimport realloc, free, malloc
from libc.stdio cimport fopen, fread, fclose, fseek, ftell, FILE, SEEK_END, SEEK_SET, SEEK_CUR
from libc.stddef cimport size_t
from libc.stdint cimport uint16_t, uint32_t, uint8_t, int8_t
from libc.string cimport strcpy, strlen

import os
import struct
import numpy as np 
cimport numpy as np

__all__ = ['CSI']

cdef packed struct iwl5000_bfee_notif:
    uint32_t timestamp_low;
    uint16_t bfee_count;
    uint16_t reserved;
    uint8_t Nrx, Ntx;
    uint8_t rssiA, rssiB, rssiC;
    int8_t noise;
    uint8_t agc, antenna_sel;
    uint16_t len;
    uint16_t fake_rate_n_flags;
    uint8_t payload[0];

cdef extern from "complex.h":
    float complex I

cdef class CSI:
    """
        It's a tool to parse channel state infomation received from Intel 5300NIC by csi-tool

        CSI(self, filepath, Nrxnum, Ntxnum):
            filepath: the file name of csi .dat
            Nrxnum  : the set number of receive antennas, default=3
            Nrxnum  : the set number of transmit antennas, default=2
            return  : csidata
        
        read(self):
            解析数据

            读取文件中的所有数据, 比纯净的python版速度提升很多,目前比matlab读取
            速度快４倍

            一次解析出所有的数据可能有些失策, 应该有返回值

            csi初始化的值是numpy.nan, plot不会绘制numpy.nan

        readstp(self):
            解析时间戳, 返回第一个数据包的时间

            获取时间戳请使用修改过的`log_to_file.c`. 并确保`.dat`和`.datstp`
            文件在同一目录下. 不然请不要使用该方法.
            (因为数据量不算大, 使用纯净python实现)
    """
    cdef readonly str filepath
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
    cdef int Nrxnum
    cdef int Ntxnum

    def __init__(self, filepath, int Nrxnum = 3, int Ntxnum = 2):
        self.filepath = filepath
        self.Nrxnum = Nrxnum
        self.Ntxnum = Ntxnum
        
    cpdef read(self):
        cdef FILE *f

        filepath_b = self.filepath.encode(encoding="utf-8")
        cdef char *filepath_c = filepath_b

        f = fopen(filepath_c, "rb")
        if f is NULL:
            print("打开失败\n")
            fclose(f)
            return -1
        
        fseek(f, 0, SEEK_END);
        cdef long len = ftell(f);
        fseek(f, 0, SEEK_SET);

        self.timestamp_low = np.zeros([len//95, 1], dtype = np.int64)
        self.bfee_count = np.zeros([len//95, 1], dtype = np.int64)
        self.Nrx = np.zeros([len//95, 1], dtype = np.int64)
        self.Ntx = np.zeros([len//95, 1], dtype = np.int64)
        self.rssiA = np.zeros([len//95, 1], dtype = np.int64)
        self.rssiB = np.zeros([len//95, 1], dtype = np.int64)
        self.rssiC = np.zeros([len//95, 1], dtype = np.int64)
        self.noise = np.zeros([len//95, 1], dtype = np.int64)
        self.agc = np.zeros([len//95, 1], dtype = np.int64)
        self.perm = np.zeros([len//95, 3], dtype = np.int64)
        self.rate = np.zeros([len//95, 1], dtype = np.int64)
        # self.csi = np.full([len//95, 30, self.Nrxnum, self.Ntxnum], np.nan, dtype = np.complex128)
        self.csi = np.zeros([len//95, 30, self.Nrxnum, self.Ntxnum], dtype = np.complex128)

        cdef long cur = 0
        cdef int count = 0
        cdef unsigned short field_len
        cdef unsigned char code
        cdef unsigned char buf[400]
        cdef unsigned char temp[3]
        cdef size_t l
        cdef iwl5000_bfee_notif *bfee

        cdef long [:, :] timestamp_low_mem = self.timestamp_low
        cdef long [:, :] bfee_count_mem = self.bfee_count
        cdef long [:, :] Nrx_mem = self.Nrx
        cdef long [:, :] Ntx_mem = self.Ntx
        cdef long [:, :] rssiA_mem = self.rssiA
        cdef long [:, :] rssiB_mem = self.rssiB
        cdef long [:, :] rssiC_mem = self.rssiC
        cdef long [:, :] noise_mem = self.noise
        cdef long [:, :] agc_mem = self.agc
        cdef long [:, :] perm_mem = self.perm
        cdef long [:, :] rate_mem = self.rate
        cdef complex [:, :, :, :] csi_mem = self.csi

        cdef int index
        cdef int i, j, k
        cdef int remainder = 0

        while cur < (len-3):
            if fread(&temp, sizeof(unsigned char), 3, f) == False:
                print("打开失败\n")
                fclose(f)
                return -1

            field_len = temp[1]+(temp[0]<<8)
            code = temp[2]
            cur = cur +3
            if code == 187:
                l = fread(buf, sizeof(unsigned char), field_len-1, f)
                cur = cur + field_len -1
                if l != (field_len-1):
                    # 读取完毕, 跳出循环
                    break
                bfee = <iwl5000_bfee_notif*> &buf

                timestamp_low_mem[count, 0] = bfee.timestamp_low
                bfee_count_mem[count, 0] = bfee.bfee_count
                Nrx_mem[count, 0] = bfee.Nrx
                Ntx_mem[count, 0] = bfee.Ntx
                rssiA_mem[count, 0] = bfee.rssiA
                rssiB_mem[count, 0] = bfee.rssiB
                rssiC_mem[count, 0] = bfee.rssiC
                noise_mem[count, 0] = bfee.noise
                agc_mem[count, 0] = bfee.agc
                rate_mem[count, 0] = bfee.fake_rate_n_flags

                perm_mem[count, 0] = (bfee.antenna_sel & 0x3)
                perm_mem[count, 1] = ((bfee.antenna_sel >> 2) & 0x3)
                perm_mem[count, 2] = ((bfee.antenna_sel >> 4) & 0x3)
                csi_mem[count] = np.nan

                index = 0
                for i in range(30):
                    index = index + 3
                    remainder = index % 8
                    for j in range(bfee.Nrx):
                        for k in range(bfee.Ntx):
                            tmp = (bfee.payload[index/8] >> remainder) | (bfee.payload[index/8+1] << (8-remainder))
                            a = <double>tmp
                            a = <char>a

                            tmp = (bfee.payload[index/8+1] >> remainder) | (bfee.payload[index/8+2] << (8-remainder))
                            b = <double>tmp
                            b = <char>b
                            
                            csi_mem[count, i, perm_mem[count,j], k] =  a + b * I
                            index = index +16
                count = count + 1
            else:
                fseek(f, field_len, SEEK_CUR)
                count = count +1
                cur = cur + field_len -1   
        
        fclose(f)
        print(str(count) + " packets\n" + "读取完毕")
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
        self.timestamp_low = self.timestamp_low[:count, :]
        self.bfee_count = self.bfee_count[:count, :]
        self.Nrx = self.Nrx[:count, :]
        self.Ntx = self.Ntx[:count, :]
        self.rssiA = self.rssiA[:count, :]
        self.rssiB = self.rssiB[:count, :]
        self.rssiC = self.rssiC[:count, :]
        self.noise = self.noise[:count, :]
        self.agc = self.agc[:count, :]
        self.perm = self.perm[:count, :]
        self.rate = self.rate[:count, :]
        self.csi = self.csi[:count, :, :, :]
        self.count = count

    def readstp(self):
        stppath = self.filepath + "stp"
        f = open(stppath, "rb")
        if f is None:
            f.close()
            raise Exception("error: file does not exist\n")
        f.seek(0, os.SEEK_END)
        len = f.tell()
        f.seek(0, os.SEEK_SET)
        self.stp = np.zeros(len//8 - 1)
        for i in range(len//8 - 1):
            a = struct.unpack("<L", f.read(4))[0]
            b = struct.unpack("<L", f.read(4))[0]
            self.stp[i] = a + b / 1000000
        f.close()
        return self.stp[0]
