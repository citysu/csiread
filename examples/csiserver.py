#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CSI server: simulation of real-time packet sending

Usage:
    Intel5300: python3 csiserver.py ../material/5300/dataset/sample_0x5_64_3000.dat 3000 1000
    Atheros: python3 csiserver.py ../material/atheros/dataset/ath_csi_1.dat 100 100000
    Nexmon: python3 csiserver.py ../material/nexmon/dataset/example.pcap 12 10000
    ESP32-CSI-Tool: python3 csiserver.py ../material/esp32/dataset/example_csi.csv 3000 100000
"""

import argparse
import os
import socket
import time
from utils import infer_device


def intel_server(csifile, number, delay):
    """intel server

    Args:
        csifile: csi smaple file
        number: packets number, unlimited if number=0
        delay: packets rate(us), the sending rate is inaccurate due to `sleep`

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
                print(count//1000, 'K', flush=True)
            if number != 0 and count >= number:
                break

    s.close()
    f.close()
    print()


def atheros_server(csifile, number, delay, endian):
    """atheros server

    Args:
        csifile: csi smaple file
        number: packets number, unlimited if number=0
        delay: packets rate(us), the sending rate is inaccurate due to `sleep`
        endian: the endian of csifile.

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
        if cur >= (lens - 4):
            f.seek(0, os.SEEK_SET)
            cur = 0

        # data
        field_len = int.from_bytes(f.read(2), byteorder=endian)
        data = bytearray(f.read(field_len))

        # set timestamp_low
        time.sleep(delay/1000000)
        timestamp_low = int(time.time() * 1000000) & 0xFFFFFFFFFFFFFFFF
        data[:8] = timestamp_low.to_bytes(8, endian)

        s.sendto(data, address_des)

        cur += (field_len + 2)

        count += 1
        if count % 1000 == 0:
            print(".", end="", flush=True)
        if count % 50000 == 0:
            print(count//1000, 'K', flush=True)
        if number != 0 and count >= number:
            break

    s.close()
    f.close()
    print()


def nexmon_server(csifile, number, delay):
    """nexmon server

    Args:
        csifile: csi smaple file
        number: packets number, unlimited if number=0
        delay: packets rate(us), the sending rate is inaccurate due to `sleep`

    Note:
        set address for remoting connection
    """
    # config
    address_src = ('127.0.0.1', 10086)
    address_des = ('127.0.0.1', 10010)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(address_src)

    f = open(csifile, 'rb')
    magic = f.read(4)
    f.seek(20, os.SEEK_CUR)
    lens = os.path.getsize(csifile)
    endian = 'big' if magic in [b"\xa1\xb2\xc3\xd4", b"\xa1\xb2\x3c\x4d"] else "little"
    cur = 24
    count = 0

    while True:
        if cur >= (lens - 4):
            f.seek(24, os.SEEK_SET)
            cur = 0

        caplen = int.from_bytes(f.read(16)[8:12], byteorder=endian)
        if f.read(42)[6:12] == b'NEXMON':
            time.sleep(delay/1000000)
            data = f.read(caplen - 42)
            s.sendto(data, address_des)

            count += 1
            if count % 1000 == 0:
                print(".", end="", flush=True)
            if count % 50000 == 0:
                print(count//1000, 'K', flush=True)
            if number != 0 and count >= number:
                break
        else:
            f.seek(caplen - 42, os.SEEK_CUR)
        cur += (caplen + 16)

    f.close()
    s.close()
    print()


def nexmon_server_2(csifile, number, delay):
    """nexmon server 2

    Args:
        csifile: csi smaple file
        number: packets number, unlimited if number=0
        delay: packets rate(us), the sending rate is inaccurate due to `sleep`

    Note:
        - This function only works on Linux. It needs root or sudo permissions.
        - Client cannot receive data if you run the client and server 2 on the
            same computer.
    """
    from scapy.all import rdpcap, sendp
    data = rdpcap(csifile)
    data[0].display()
    sendp(data, inter=delay/1e6, count=number//len(data))
    sendp(data[:number%len(data)], inter=delay/1e6)


def esp32_server(csifile, number, delay):
    """nexmon server

    Args:
        csifile: csi smaple file
        number: packets number, unlimited if number=0
        delay: packets rate(us), the sending rate is inaccurate due to `sleep`
    """
    assert number >= 0
    count = 0
    with open(csifile) as f:
        while True:
            time.sleep(delay/1000000)
            line = f.readline().strip('\n')
            if line:
                print(line)
                count += 1
            else:
                f.seek(0, os.SEEK_SET)
            if number != 0 and count >= number:
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('csifile', type=str, help='csi smaple file')
    parser.add_argument('number', type=int, help='packets number')
    parser.add_argument('delay', type=int, help='delay in us')
    p = parser.parse_args()

    device = infer_device(p.csifile)

    if device == "Intel":
        intel_server(p.csifile, p.number, p.delay)
    elif device == "Atheros":
        atheros_server(p.csifile, p.number, p.delay, 'little')
    elif device == "Nexmon":
        nexmon_server(p.csifile, p.number, p.delay)
    else:
        esp32_server(p.csifile, p.number, p.delay)
