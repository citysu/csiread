#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CSI client: log_to_file(Linux 802.11n CSI Tool)"""

import socket
import struct


def create_large_csifile(csifile='csifile.dat'):
    """Create a large csi data file for testing csiread's performance"""

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
            f.write(msg_len.to_bytes(2, 'big'))
            f.write(data)
            count += 1
            print('received %d bytes, id: %d, seq: %d, clen: %d' % (msg_len, 0, 0, count))
            if count % 100 == 0:
                print('wrote %d bytes [msgcnt=%u]' % (msg_len, count))
    f.close()

def log_to_file(csifile='csifile.dat'):
    """Implement log_to_file in Python (haven't tested)"""
    count = 0
    f = open(csifile, 'wb')
    CN_NETLINK_USERS = 11
    CN_IDX_IWLAGN = CN_NETLINK_USERS + 0xf
    CN_VAL_IWLAGN = 0x1
    NETLINK_ADD_MEMBERSHIP = 1
    socket.NETLINK_CONNECT = 11
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.NETLINK_CONNECT) as s:
        s.bind(os.getpid(), CN_IDX_IWLAGN)
        s.setsockopt(270, NETLINK_ADD_MEMBERSHIP, 1)
        while True:
            ret = s.recv(4096)
            msg_len, msg_type, msg_flags, msg_seq, msg_pid = struct.unpack("=LHHLL", ret[:16])
            data = ret[32:]
            l2 = socket.htons(msg_len)      # need review
            f.write(l2)
            f.write(data)
            count += 1
            print('received %d bytes, id: %d, seq: %d, clen: %d' % (len(data), 0, 0, msg_len))
            if count % 100 == 0:
                print('wrote %d bytes [msgcnt=%u]' % (len(data), count))
    f.close()

if __name__ == "__main__":
    create_large_csifile(csifile='csifile.dat')
