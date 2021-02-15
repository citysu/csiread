#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Parse MPDU

     2          2          6        6         6         2          6         2         4      0-7955   4  
| Frame   | Duration | Address | Address | Address | Sequence | Address |   Qos   |   HT    | Frame | FCS |
| Control |   /ID    |    1    |    2    |    3    |  Control |    4    | Control | Control |  Body |     |
<-----------------------------------------MAC Header---------------------------------------->

The first three fields (Frame Control, Duration/ID, and Address 1) and the last field (FCS) 
constitute the minimal frame format and are present in all frames, including reserved types
and subtypes. The fields Address 2, Address 3, Sequence Control, Address 4, QoS Control, 
HT Control, and Frame Body are present only in **certain frame types and subtypes**.

------------------------------------------------------------------------------------------

csiread.Intel only parses MPDU defined in `random_packets.c` and csiread.Atheros does nothing
to MPDU. (MPDU defined in `random_packets.c` is not network byte order)

ref:
    1. [CWAP – MAC Header : Frame Control](https://mrncciew.com/2014/09/27/cwap-mac-header-frame-control/)
    2. IEEE 802.11n Standard
"""

import struct

import csiread
import numpy as np
from scapy.all import Dot11


class MPDU:
    def __init__(self, frame, endian='!'):
        if len(frame) < 40:
            raise Exception('Error: pl_size >= 40 is requried')
        self.frame_control, = struct.unpack(endian + 'H', frame[:2])
        self.duration, = struct.unpack(endian + 'H', frame[2:4])
        self.addr1, = struct.unpack(endian + '6s', frame[4:10])
        self.addr2, = struct.unpack(endian + '6s', frame[10:16])
        self.addr3, = struct.unpack(endian + '6s', frame[16:22])
        self.sequence_control, = struct.unpack(endian + 'H', frame[22:24])
        self.addr4, = struct.unpack(endian + '6s', frame[24:30])
        self.qos_control, = struct.unpack(endian + 'H', frame[30:32])
        self.ht_control, = struct.unpack(endian + 'L', frame[32:36])
        self.frame_body, = struct.unpack(endian + '4s', frame[36:40])

    def show(self):
        t = "{:20s}{:>12} {:<24s}\n"

        s = "-"*50 + '\n'
        s += t.format('Field', 'Hex', 'Value')
        s += "-"*50 + '\n'
        s += t.format('frame_control: ', hex(self.frame_control)[2:].zfill(4), str(self.frame_control))
        s += t.format('duration: ', hex(self.duration)[2:].zfill(4), str(self.duration))
        s += t.format('address_1: ', self.func(self.addr1, ''),  self.func(self.addr1, ':'))
        s += t.format('address_2: ',  self.func(self.addr2, ''),  self.func(self.addr2, ':'))
        s += t.format('address_3: ',  self.func(self.addr3, ''),  self.func(self.addr3, ':'))
        s += t.format('sequence_control: ', hex(self.sequence_control)[2:].zfill(4), str(self.sequence_control))
        s += t.format('address_4: ',  self.func(self.addr4, ''),  self.func(self.addr4, ':'))
        s += t.format('qos_control: ', hex(self.qos_control)[2:].zfill(4), str(self.qos_control))
        s += t.format('ht_control: ', hex(self.ht_control)[2:].zfill(8), str(self.ht_control))
        s += t.format('frame_body[:4]: ',  self.func(self.frame_body[:4], ''),  self.func(self.frame_body[:4], ' '))
        s += "-"*50
        print(s)

    @staticmethod
    def func(vlist, space):
        return space.join([hex(per)[2:].zfill(2) for per in vlist])

def AtherosMPDU(csifile, index=0):
    """Parse payload using scapy"""
    csidata = csiread.Atheros(csifile, nrxnum=3, ntxnum=2, pl_size=40, tones=56, if_report=False)
    csidata.read()
    print("=" * 20 + "Atheros MPDU" + "=" * 20)
    m = Dot11(csidata.payload[index].tobytes())
    m.show()

def Intel5300MPDU(csifile, index=0):
    """Parse payload using scapy"""
    csidata = csiread.Intel(csifile, nrxnum=3, ntxnum=2, pl_size=40, if_report=False)
    csidata.read()
    print("=" * 20 + "Intel 5300 MPDU" + "=" * 20)
    m = Dot11(csidata.payload[index].tobytes())
    m.show()

def AtherosMPDU2(csifile, index=0):
    """Parse payload without scapy"""
    csidata = csiread.Atheros(csifile, nrxnum=3, ntxnum=2, pl_size=40, tones=56, if_report=False)
    csidata.read()
    print("=" * 20 + "Atheros MPDU2" + "=" * 20)
    m = MPDU(csidata.payload[index].tobytes())
    m.show()

def Intel5300MPDU2(csifile, index=0):
    """Parse payload without scapy"""
    csidata = csiread.Intel(csifile, nrxnum=3, ntxnum=2, pl_size=40, if_report=False)
    csidata.read()
    print("=" * 20 + "Intel 5300 MPDU2" + "=" * 20)
    m = MPDU(csidata.payload[index].tobytes())
    m.show()


if __name__ == "__main__":
    AtherosMPDU("../material/atheros/dataset/ath_csi_1.dat", 10)
    Intel5300MPDU("../material/5300/dataset/sample_0x5_64_3000.dat", 10)
