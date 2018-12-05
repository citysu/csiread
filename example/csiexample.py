#!/usr/bin python3
# -*- coding: utf-8 -*-

"""
csiread example
"""

import csiread


def example():
    """
    A example of csiread
    """
    csipath1 = "../material/sample_0x1_ap.dat"
    csidata1 = csiread.CSI(csipath1)
    csidata1.read()
    csidata1.readstp()

    print([s for s in csidata1.__dir__() if s[:2] != "__"])

    print("csi shape: ", csidata1.csi.shape)
    print("rssiA[:10]: ", csidata1.rssiA[:10])

    csipath2 = "../material/sample_0x5_64_3000.dat"
    csidata2 = csiread.CSI(csipath2)
    csidata2.read()

    addr_src = ''
    for per_addr in csidata2.addr_src[0]:
        addr_src = addr_src + hex(per_addr)[2:] + ":"
    print("addr_src: ", addr_src)
    print("seq: ", csidata2.seq[:10])
    print("count: ", csidata2.count)


if __name__ == "__main__":
    example()
