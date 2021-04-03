#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""csiread.Nexmon: implemented in pure Python

Note:
    csiread.Nexmon is based on the commit of nexmon_csi(Aug 29, 2020):
    ba99ce12a6a42d7e4ec75e6f8ace8f610ed2eb60

Ref:
    [nexmon_csi](https://github.com/seemoo-lab/nexmon_csi)
    [rdpcap](https://github.com/secdev/scapy/blob/master/scapy/utils.py)
"""

import os
import struct
import numpy as np
from timeit import default_timer


def unpack_int16(buf, csi, nfft, endian):
    dt = np.dtype(np.int16).newbyteorder(endian)
    csi[:] = np.frombuffer(buf, dtype=dt, count=nfft)


def unpack_float(buf, csi, nfft, M, E, endian):
    nbits = 10
    autoscale = 1
    e_p = (1 << (E - 1))
    e_shift = 1
    e_zero = - M
    maxbit = -e_p
    k_tof_unpack_sgn_mask = (1 << 31)
    ri_mask = (1 << (M - 1)) - 1
    E_mask = (1 << E) - 1
    sgnr_mask = (1 << (E + 2 * M - 1))
    sgni_mask = sgnr_mask >> M
    He = [0] * 256
    Hout = [0] * 512
    border = 'little' if endian == '<' else 'big'

    for i in range(nfft):
        h = int.from_bytes(buf[4*i:4*i+4], border)

        v_real = (h >> (E + M)) & ri_mask
        v_imag = (h >> E) & ri_mask
        e = h & E_mask
        if (e >= e_p):
            e -= (e_p << 1)
        He[i] = e
        x = v_real | v_imag

        if (autoscale and x):
            m = 0xffff0000
            b = 0xffff
            s = 16
            while (s > 0):
                if (x & m):
                    e += s
                    x >>= s
                s >>= 1
                m = (m >> s) & b
                b >>= s
            if (e > maxbit):
                maxbit = e
        if (h & sgnr_mask):
            v_real |= k_tof_unpack_sgn_mask
        if (h & sgni_mask):
            v_imag |= k_tof_unpack_sgn_mask
        Hout[i<<1] = v_real
        Hout[(i<<1)+1] = v_imag

    shft = nbits - maxbit
    for i in range(nfft*2):
        e = He[(i >> e_shift)] + shft
        sgn = 1
        if (Hout[i] & k_tof_unpack_sgn_mask):
            sgn = -1
            Hout[i] &= ~k_tof_unpack_sgn_mask
        if (e < e_zero):
            Hout[i] = 0
        elif (e < 0):
            e = -e
            Hout[i] = (Hout[i] >> e)
        else:
            Hout[i] = (Hout[i] << e)
        Hout[i] *= sgn

    for i in range(nfft):
        csi[i] = Hout[i*2] + Hout[i*2+1] * 1.j


class Nexmon:
    def __init__(self, file, chip, bw, if_report=True):
        self.file = file
        self.chip = chip
        self.bw = bw
        self.if_report = if_report

        if file is None:
            self.count = 0
            pk_num = 1
        else:
            pk_num = self.__get_count()

        btype = np.int_
        self.sec = np.zeros([pk_num], dtype=btype)
        self.usec = np.zeros([pk_num], dtype=btype)
        self.caplen = np.zeros([pk_num], dtype=btype)
        self.wirelen = np.zeros([pk_num], dtype=btype)
        self.magic = np.zeros([pk_num], dtype=btype)
        self.src_addr = np.zeros([pk_num, 6], dtype=btype)
        self.seq = np.zeros([pk_num], dtype=btype)
        self.core = np.zeros([pk_num], dtype=btype)
        self.spatial = np.zeros([pk_num], dtype=btype)
        self.chan_spec = np.zeros([pk_num], dtype=btype)
        self.chip_version = np.zeros([pk_num], dtype=btype)
        self.csi = np.zeros([pk_num, int(self.bw * 3.2)], dtype=np.complex_)

    def read(self):
        count = 0
        nfft = int(self.bw * 3.2)

        f = open(self.file, 'rb')
        endian = self.__pcapheader(f)

        while True:
            hdr = f.read(16)
            if len(hdr) < 16:
                break
            sec, usec, caplen, wirelen = struct.unpack(endian + "IIII", hdr)
            buf = f.read(42)
            if buf[6:12] != b'NEXMON':
                f.seek(caplen - 42, os.SEEK_CUR)
                continue
            self.sec[count] = sec
            self.usec[count] = usec
            self.caplen[count] = caplen
            self.wirelen[count] = wirelen

            frame = f.read(18)
            magic, src_addr, seq, core_spatial, chan_spec, chip_version = struct.unpack(
                endian + "I6sHHHH", frame
            )
            
            self.magic[count] = magic
            for i in range(6):
                self.src_addr[count, i] = src_addr[i]
            self.seq[count] = seq
            self.core[count] = core_spatial & 0x7
            self.spatial[count] = (core_spatial >> 3) & 0x7
            self.chan_spec[count] = chan_spec
            self.chip_version[count] = chip_version

            buf = f.read(caplen - 42 - 18)
            if self.chip == '4339' or self.chip == '43455c0':
                unpack_int16(buf, self.csi[count], nfft, endian)
            elif self.chip == '4358':
                unpack_float(buf, self.csi[count], nfft, 9, 5, endian)
            elif self.chip == '4366c0':
                unpack_float(buf, self.csi[count], nfft, 12, 6, endian)
            else:
                pass
            count += 1
        f.close
        self.count = count
        if self.if_report:
            print(str(count) + " packets parsed")

    def __get_count(self):
        count = 0
        f = open(self.file, 'rb')
        endian = self.__pcapheader(f)
        while True:
            hdr = f.read(16+42)
            if len(hdr) < 16:
                break
            if hdr[22:28] == b'NEXMON':
                count += 1
            caplen, = struct.unpack(endian + "I", hdr[8:12])
            f.seek(caplen - 42, os.SEEK_CUR)
        f.close()
        return count

    def __pcapheader(self, f):
        magic = f.read(4)
        if magic == b"\xa1\xb2\xc3\xd4":  # big endian
            endian = ">"
            self.nano = False
        elif magic == b"\xd4\xc3\xb2\xa1":  # little endian
            endian = "<"
            self.nano = False
        elif magic == b"\xa1\xb2\x3c\x4d":  # big endian, nanosecond-precision
            endian = ">"
            self.nano = True
        elif magic == b"\x4d\x3c\xb2\xa1":  # little endian, nanosecond-precision
            endian = "<"
            self.nano = True
        else:
            raise Exception("Not a pcap capture file (bad magic: %r)" % magic)

        f.seek(20, os.SEEK_CUR)
        return endian


if __name__ == '__main__':
    last = default_timer()
    csifile = "../material/nexmon/dataset/example.pcap"
    csidata = Nexmon(csifile, chip='4358', bw=80, if_report=False)
    csidata.read()
    print(default_timer() - last, 's')
