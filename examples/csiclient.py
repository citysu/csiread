#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CSI client: Create a large csi data file for testing csiread's performance(Linux 802.11n CSI Tool)

Usage:
    1. python3 csiclient.py
    2. python3 csiserver.py ../material/5300/dataset/sample_0x5_64_3000.dat 3000 1000
"""

import socket


def create_large_csifile(csifile='csifile.dat', endian='big'):
    """Create a large csi data file for testing csiread's performance
    
    Note:
        5300NIC: 'endian' must be 'big'
        Atheros: 'endian' shoud be the same as csiserver.py's
    """

    # config
    address_src = ('127.0.0.1', 10086)
    address_des = ('127.0.0.1', 10010)

    count = 0
    f = open(csifile, 'wb')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(address_des)
        while True:
            data, address_src = s.recvfrom(4096)
            msg_len = len(data)
            f.write(msg_len.to_bytes(2, endian))
            f.write(data)
            count += 1
            print('received %d bytes, id: %d, seq: %d, clen: %d' % (msg_len, 0, 0, count))
            if count % 100 == 0:
                print('wrote %d bytes [msgcnt=%u]' % (msg_len, count))
    f.close()


if __name__ == "__main__":
    create_large_csifile(csifile='csiclient.dat', endian='big')
    # create_large_csifile(csifile='csiclient.dat', endian='little')