#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CSI MemoryError: Solution to the MemoryError

csiread may raise MemoryError when reading a super large file. It can be solved
by setting 'bufsize'. However, this error rarely happens.

Note:
    csiread.Intel needs to know the count of packets in the csifile before
    parsing. It estimates packets count by the following method.

    ----------------------------------------------------------------------
    | packet type | field_len | code | header |       payload       | CRC |
    |     0xbb    |     2     |   1  |   20   | 12 + 60 * Ntx * Nrx |     |
    |     0xc1    |     2     |   1  | 4 + 20 |    pl_size - 28     |  4  |
    ----------------------------------------------------------------------
    csifile_size = os.path.getsize(csifile)
    packet_number = csifile_size // packet_size

    packet_size is set to a constant value of 95. it is not a good choice.
    There are two known limitations here: 1. packet size >= 95 is necessary,
    otherwise it will throw `IndexError: Out of bounds on buffer access
    (axis 0)`. 2. if packet size > 95, the more packets, the more excess memory
    allocated. Excess memory is so large that MemoryError is throwed. 
    
    csiread.Atheros has the same issue. (Atheros.packet_size = 420). csiread.Nexmon
    does not have this issue, but it calculates the count of packets by the
    pre-read. It takes extra time.

    12 + 60 * Ntx * Nrx = (30 * (Nrx * Ntx * 8 * 2 + 3) + 7) / 8 :
    ===========================================================================
    Grouping is a method that reduces the size of the CSI Report field by
    reporting a single value for each group of Ng adjacent subcarriers. With
    grouping, the size of the CSI Report field is Nr×8+Ns×(3+2×Nb×Nc×Nr) bits,
    where the number of subcarriers sent, Ns, is a function of Ng and whether
    matrices for 40 MHz or 20 MHz are sent. The value of Ns and the specific
    carriers for which matrices are sent are shown in Table 7-25f. If the size
    of the **CSI Report field** is not an integral multiple of 8 bits, up to 7
    zeros are appended to the end of the report to make its size an integral
    multiple of 8 bits.
    ===========================================================================
ref:
    [IEEE 802.11n Standard](Link has expired)
"""

from functools import wraps

import csiread


def info(func):
    """csidata info"""
    @wraps(func)
    def wrapper(*arg, **argv):
        csidata = func(*arg, **argv)
        s = "{}: csidata.Nrx.size={} csidata.Nrx.base.size={}"
        s = s.format(func.__name__, csidata.Nrx.size, csidata.Nrx.base.size)
        print(s)
        return csidata
    return wrapper


@info
def read_bf_fileA(csifile, pk_num):
    csidata = csiread.Intel(csifile, nrxnum=3, ntxnum=2, pl_size=0, if_report=False, bufsize=pk_num)
    csidata.read()
    return csidata


@info
def read_bf_fileB(csifile):
    csidata = csiread.Intel(csifile, nrxnum=3, ntxnum=2, pl_size=0, if_report=False)
    csidata.read()
    return csidata


if __name__ == "__main__":
    csifile = "../material/5300/dataset/sample_0x1_ap.dat"
    csidataA = read_bf_fileA(csifile, pk_num=600)
    csidataB = read_bf_fileB(csifile)
