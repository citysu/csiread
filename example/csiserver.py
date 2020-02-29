#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CSI server: simulation of real-time packet sending(Linux 802.11n CSI Tool)

Usage:
    python3 csiserver.py ../material/5300/dataset/sample_0x5_64_3000.dat 3000 1000
"""

import argparse
import os
import random
import socket
import struct
import sys
import time


def csiserver(csifile, number, delay):
    """csi server

    Args:
        csifile: csi smaple file
        number: packets number, unlimited if number=0
        delay: packets rate(us), the sending rate is inaccurate because of `sleep`
    Note:
        set address for remoting connection
    """
    # config
    address_src = ('127.0.0.1', 10086)
    address_des = ('127.0.0.1', 10010)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(address_src)

    f = open(csifile, 'rb')
    lens = f.seek(0, os.SEEK_END)
    f.seek(0, os.SEEK_SET)

    cur = 0
    count = 0

    print("sending")
    while True:
        if cur >= (lens - 3):
            f.seek(0, os.SEEK_SET)
            cur = 0

        # data
        field_len = int.from_bytes(f.read(2), byteorder='big')
        code = int.from_bytes(f.read(1), byteorder='little')
        f.seek(-1, os.SEEK_CUR)
        data = bytearray(f.read(field_len))

        # set timestamp_low
        if code == 0xbb:
            time.sleep(delay/1000000)
            timestamp_low = int(time.time() * 1000000) & 0xFFFFFFFF
            data[1:5] = timestamp_low.to_bytes(4, 'little')

        s.sendto(data, address_des)

        cur += (field_len + 2)
        if code == 0xbb:
            count += 1
            if count % 1000 == 0:
                print(".", end="", flush=True)
            if count % 50000 == 0:
                print(count//1000, 'K',flush=True)
            if number != 0 and count >= number:
                break

    s.close()
    f.close()
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('csifile', type=str, help='csi smaple file')
    parser.add_argument('number', type=int, help='packets number')
    parser.add_argument('delay', type=int, help='delay in us')
    p = parser.parse_args()

    csiserver(p.csifile, p.number, p.delay)
