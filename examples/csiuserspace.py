#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CSI userspace: Implement log_to_file in pure Python(Linux 802.11n CSI Tool)

Usage:
    sudo python3 csiuserspace.py

Note:
    I tested the example with the following code on Ubuntu18.04LTS without
    Intel 5300 NIC. The code hasn't been tested on the host equipped with
    Intel 5300 NIC.

    In Ubuntu18.04, CN_NETLINK_USERS = 11, but CN_NETLINK_USERS = 10 in the linux-80211n-csitool

    `csikernel.c` is based on[linux/samples/connector/cn_test.c]
    (https://github.com/torvalds/linux/blob/master/samples/connector/cn_test.c).

    ```bash
    make
    sudo insmod csikernel.ko
    dmesg
    ```

    Don't forget to remove csikernel after playing.

    ```bash
    sudo rmmod csikernel
    make clean
    ```

Ref: 
	1. [Kernel Connector](https://www.kernel.org/doc/html/latest/driver-api/connector.html)
	2. [connector.h](https://github.com/dhalperi/linux-80211n-csitool/blob/csitool-stable/include/linux/connector.h)
"""

import os
import socket
import struct


def log_to_file(csifile='csifile.dat'):
    """Implement log_to_file in Python"""
    f = open(csifile, 'wb')

    # show frequency
    count = 0
    SLOW_MSG_CNT = 1

    # /usr/include/linux/connector.h
    # #define CN_NETLINK_USERS		10	/* Highest index + 1 */
    CN_NETLINK_USERS = 10
    CN_IDX_IWLAGN = CN_NETLINK_USERS + 0xf
    # CN_VAL_IWLAGN = 0x1       # useless

    # /usr/include/linux/netlink.h
    # #define NETLINK_CONNECTOR	11
    # #define NETLINK_ADD_MEMBERSHIP		1
    socket.NETLINK_CONNECTOR = 11
    NETLINK_ADD_MEMBERSHIP = 1

    with socket.socket(socket.AF_NETLINK, socket.SOCK_DGRAM, socket.NETLINK_CONNECTOR) as s:
        # proc_addr
        s.bind((os.getpid(), CN_IDX_IWLAGN))

        # kern_addr, useless, pass

        # And subscribe to netlink group
        s.setsockopt(270, NETLINK_ADD_MEMBERSHIP, CN_IDX_IWLAGN)

        while True:
            ret = s.recv(4096)

            # /usr/include/linux/netlink.h
            # struct nlmsghdr {
            #     __u32		nlmsg_len;	/* Length of message including header */
            #     __u16		nlmsg_type;	/* Message content */
            #     __u16		nlmsg_flags;	/* Additional flags */
            #     __u32		nlmsg_seq;	/* Sequence number */
            #     __u32		nlmsg_pid;	/* Sending process port ID */
            # };

            nlmsg_len, nlmsg_type, nlmsg_flags, nlmsg_seq, nlmsg_pid = struct.unpack("=LHHLL", ret[:16])

            # /usr/include/linux/connector.h
            # struct cb_id {
            #     __u32 idx;
            #     __u32 val;
            # };

            # struct cn_msg {
            #     struct cb_id id;

            #     __u32 seq;
            #     __u32 ack;

            #     __u16 len;		/* Length of the following data */
            #     __u16 flags;
            #     __u8 data[0];
            # };

            cnmsg_idx, cnmsg_val, cnmsg_seq, cnmsg_ack, cnmsg_len, cnmsg_flag = struct.unpack("=LLLLHH", ret[16:36])
            
            # linux-80211n-csitool: /drivers/net/wireless/iwlwifi/iwl-connector.c
            # /**
            #  * Sends the message over the kernel connector to a userspace program.
            #  */
            # void connector_send_msg(const u8 *data, const u32 size, const u8 code)
            # {
            #     struct cn_msg *m;
            #     u8 *buf;
            #     u32 payload_size;

            #     /* Payload + 1-byte "code" */
            #     payload_size = size + 1 + sizeof(struct cn_msg);
            #     m = kmalloc(payload_size, GFP_ATOMIC);
            #     if (m == NULL) {
            #         printk(KERN_ERR "%s: malloc failed\n", __func__);
            #         return;
            #     }
            #     buf = ((u8 *) m) + sizeof(struct cn_msg);

            #     /* Set up message */
            #     memcpy(&m->id, &connector_id, sizeof(struct cb_id));
            #     m->seq = 0;
            #     m->len = size + 1;
            #     buf[0] = code;
            #     memcpy(&buf[1], data, size);

            #     /* Enqueue message -- may free on failure */
            #     connector_enqueue_msg(m);

            #     return;
            # }

            cnmsg_data = ret[36:]

            if count % SLOW_MSG_CNT == 0:
                print("received %d bytes: id: %d val: %d seq: %d clen: %d" % (cnmsg_len, cnmsg_idx, cnmsg_val, cnmsg_seq, cnmsg_len))
                # print("data: %s", bytes.decode(cnmsg_data))

            l2 = struct.pack('!H', cnmsg_len)
            f.write(l2)
            ret = f.write(cnmsg_data)

            if count % 100 == 0:
                print('wrote %d bytes [msgcnt=%u]' % (ret, count))
            count += 1
    f.close()


if __name__ == "__main__":
    log_to_file(csifile="csiuserspace.dat")
