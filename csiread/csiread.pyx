from libc.stdlib cimport realloc, free, malloc
from libc.stdio cimport fopen, fread, fclose, fseek, ftell, FILE, SEEK_END, SEEK_SET, SEEK_CUR
from libc.stddef cimport size_t
from libc.stdint cimport uint16_t, uint32_t, uint8_t, int8_t
from libc.string cimport strcpy, strlen

import os
import sys
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

cdef packed struct lorcon_packet:
    uint16_t fc;
    uint16_t dur;
    uint8_t addr_des[6];
    uint8_t addr_src[6];
    uint8_t addr_bssid[6];
    uint16_t seq;
    uint8_t payload[0];

cdef float complex I = 1j

cdef class CSI:
    """
        A tool to parse channel state infomation received from Intel 5300 NIC by csitools

        CSI(self, filepath, Nrxnum, Ntxnum):
            filepath: the file name of csi .dat
            Nrxnum  : the set number of receive antennas, default=3
            Ntxnum  : the set number of transmit antennas, default=2
            pl_size : the payload size, default=0
            return  : csidata
        
        read(self):
            parse data if code=0xbb and code=0xc1

            1. all Initialized value of members are set zero, and csi set np.nan
            2. when `connector_log=0x4, 0x5`, the max size of payload is [500-28]
            3. read the payload or addr_src, e.g.
                >>ss = ''
                >>for s in csidata.payload[0]:
                >>    ss = ss+(chr(s))

                >>ss = ''
                >>for s in csidata.addr_src[0]:
                >>    ss = ss+(hex(s))

                the last 4 bytes are CRC and noe be parsed
                
        readstp(self):
            return the first packet's world timestamp

            `file.dat` and `file.datstp` must be in the same directory.
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

    def __init__(self, filepath, int Nrxnum = 3, int Ntxnum = 2, pl_size = 0):
        self.filepath = filepath
        self.Nrxnum = Nrxnum
        self.Ntxnum = Ntxnum
        self.pl_size = pl_size
        
        if not os.path.isfile(filepath):
            raise Exception("error: file does not exist, Stop!\n")

    cpdef read(self):
        cdef FILE *f
        
        filepath_b = self.filepath.encode(encoding="utf-8")
        cdef char *filepath_c = filepath_b

        f = fopen(filepath_c, "rb")
        if f is NULL:
            print("Open failed!\n")
            fclose(f)
            return -1
        
        fseek(f, 0, SEEK_END);
        cdef long len = ftell(f);
        fseek(f, 0, SEEK_SET);

        btype = None
        if sys.platform == 'linux':
            btype = np.int64
        elif sys.platform == 'win32':
            btype = np.int32
        else:
            raise Exception("error: Only works on linux and windows !\n")
        
        self.timestamp_low = np.zeros([len//95], dtype = btype)
        self.bfee_count = np.zeros([len//95], dtype = btype)
        self.Nrx = np.zeros([len//95], dtype = btype)
        self.Ntx = np.zeros([len//95], dtype = btype)
        self.rssiA = np.zeros([len//95], dtype = btype)
        self.rssiB = np.zeros([len//95], dtype = btype)
        self.rssiC = np.zeros([len//95], dtype = btype)
        self.noise = np.zeros([len//95], dtype = btype)
        self.agc = np.zeros([len//95], dtype = btype)
        self.perm = np.zeros([len//95, 3], dtype = btype)
        self.rate = np.zeros([len//95], dtype = btype)
        self.csi = np.zeros([len//95, 30, self.Nrxnum, self.Ntxnum], dtype = np.complex128)

        cdef long [:] timestamp_low_mem = self.timestamp_low
        cdef long [:] bfee_count_mem = self.bfee_count
        cdef long [:] Nrx_mem = self.Nrx
        cdef long [:] Ntx_mem = self.Ntx
        cdef long [:] rssiA_mem = self.rssiA
        cdef long [:] rssiB_mem = self.rssiB
        cdef long [:] rssiC_mem = self.rssiC
        cdef long [:] noise_mem = self.noise
        cdef long [:] agc_mem = self.agc
        cdef long [:, :] perm_mem = self.perm
        cdef long [:] rate_mem = self.rate
        cdef complex [:, :, :, :] csi_mem = self.csi

        self.fc = np.zeros([len//95], dtype = btype)
        self.dur = np.zeros([len//95], dtype = btype)
        self.addr_des = np.zeros([len//95, 6], dtype = btype)
        self.addr_src = np.zeros([len//95, 6], dtype = btype)
        self.addr_bssid = np.zeros([len//95, 6], dtype = btype)
        self.seq = np.zeros([len//95], dtype = btype)
        self.payload = np.zeros([len//95, self.pl_size + 4], dtype = btype)

        cdef long [:] fc_mem = self.fc
        cdef long [:] dur_mem = self.dur
        cdef long [:, :] addr_des_mem = self.addr_des
        cdef long [:, :] addr_src_mem = self.addr_src
        cdef long [:, :] addr_bssid_mem = self.addr_bssid
        cdef long [:] seq_mem = self.seq
        cdef long [:, :] payload_mem = self.payload

        cdef long cur = 0
        cdef int count_0xbb = 0
        cdef int count_0xc1 = 0
        cdef unsigned short field_len
        cdef unsigned char code
        cdef unsigned char buf[500]
        cdef unsigned char temp[3]
        cdef size_t l
        cdef iwl5000_bfee_notif *bfee
        cdef lorcon_packet *mpdu

        cdef int index
        cdef int i, j, k, g
        cdef int remainder = 0

        while cur < (len-3):
            if fread(&temp, sizeof(unsigned char), 3, f) == False:
                print("Open failed!\n")
                fclose(f)
                return -1

            field_len = temp[1]+(temp[0]<<8)
            code = temp[2]
            cur = cur +3

            if code == 0xbb:
                l = fread(buf, sizeof(unsigned char), field_len-1, f)
                if l != (field_len-1):
                    break # finished
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
                csi_mem[count_0xbb] = np.nan

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
                            
                            csi_mem[count_0xbb, i, perm_mem[count_0xbb,j], k] =  a + b * I
                            index = index +16
                cur = cur + field_len -1
                count_0xbb = count_0xbb + 1
                
            elif code == 0xc1:
                l = fread(buf, sizeof(unsigned char), field_len-1, f)
                if l != (field_len-1):
                    break # finished
                mpdu = <lorcon_packet*>&buf

                fc_mem[count_0xc1] = mpdu.fc
                dur_mem[count_0xc1] = mpdu.dur

                for g in range(6):
                    addr_des_mem[count_0xc1, g] = mpdu.addr_des[g]
                    addr_src_mem[count_0xc1, g] = mpdu.addr_src[g]
                    addr_bssid_mem[count_0xc1, g] = mpdu.addr_bssid[g]

                seq_mem[count_0xc1] = mpdu.seq

                for g in range(self.pl_size + 4):
                    payload_mem[count_0xc1, g] = mpdu.payload[g]

                cur = cur + field_len -1 
                count_0xc1 = count_0xc1 + 1

            else:
                fseek(f, field_len, SEEK_CUR)
                count_0xbb = count_0xbb + 1
                count_0xc1 = count_0xc1 + 1
                cur = cur + field_len -1   
        
        fclose(f)

        if count_0xbb == 0:
            self.count = count_0xc1
            print("connector_log=" + hex(4))
            print(str(count_0xc1) + " packets " + "parsed")
        elif count_0xc1 == 0:
            self.count = count_0xbb
            print("connector_log=" + hex(1))
            print(str(count_0xbb) + " packets " + "parsed")
        else:
            c = count_0xbb - count_0xc1
            if c < 0:
                self.count = count_0xc1
                print(str(-c)+" 0xbb packets have been lossed in user space, count:0xc1")
                print("Waring: maybe Set incorrectly, e.g. too hgih transmitter rate")
            elif c > 0:
                self.count = count_0xbb
                print(str(c)+" 0xc1 packets have been lossed in user space, count:0xbb")
                print("Waring: maybe Set incorrectly, e.g. too hgih transmitter rate")
            else:
                self.count = count_0xbb
            print("connector_log=" + hex(1 | 4))
            print(str(self.count) + " packets " + "parsed")

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
        self.bfee_count = self.bfee_count[:count_0xbb,]
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

        self.fc = self.fc[:count_0xc1]
        self.dur = self.dur[:count_0xc1]
        self.addr_des = self.addr_des[:count_0xc1]
        self.addr_src = self.addr_src[:count_0xc1]
        self.addr_bssid = self.addr_bssid[:count_0xc1]
        self.seq = self.seq[:count_0xc1]
        self.payload = self.payload[:count_0xc1]

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
