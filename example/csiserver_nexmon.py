#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CSI server: simulation of real-time packet sending(nexmon_csi)

Usage:
    python3 csiserver_nexmon.py ../material/nexmon/dataset/example.pcap 12 10000
"""

import argparse
from scapy.utils import rdpcap
from scapy.all import sendp


def nexmon_server(csifile, number, delay):
	data = rdpcap(csifile)
	sendp(data, inter=delay/1e6, count=number//len(data))
	sendp(data[:number%len(data)], inter=delay/1e6)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('csifile', type=str, help='csi smaple file')
    parser.add_argument('number', type=int, help='packets number')
    parser.add_argument('delay', type=int, help='delay in us')
    p = parser.parse_args()

    nexmon_server(p.csifile, p.number, p.delay)
