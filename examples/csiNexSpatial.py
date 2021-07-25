#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Plot amplitude of Nexmon csi when core and spatial are unknown.

Dowload data file from [spatial stream index of nexmon daa #14](https://github.com/Gi-z/CSIKit/issues/14)

Note:
    This example cannot return the REAL core and spatial.

Usage:
    python3 csiNexSpatial.py
"""

import numpy as np
import csiread as cr
import matplotlib.pyplot as plt
from utils import scidx
import os


def loadcsi(csifile):
    if os.path.exists(csifile) is False:
        raise FileNotFoundError("%s doesn't exist" % (csifile))
    csidata = cr.Nexmon(csifile, '4366c0', 80, if_report=False)
    csidata.read()
    csidata.csi = np.fft.ifftshift(csidata.csi)
    return csidata


def group(csidata):
    seq_diff = np.diff(csidata.seq)
    offset = np.where(seq_diff != 0)[0]
    offset = np.r_[0, offset + 1]
    count = np.diff(np.r_[offset, csidata.count])
    return offset, count


def rearrange(amp, ant_num=16):
    """Rearrange antennas by shortest distance of amplitude

    Args:
        amp: amplitude, [antennas, packets_num, subcarriers]
        ant_num: antennas number

    Return:
        amp: resorted amplitude.
        idx: new antenna index
    """
    idx = list()
    for i in range(1, amp.shape[1]):
        G, J = list(), list(range(ant_num))
        for k in range(ant_num):
            d = [np.linalg.norm(amp[j, i] - amp[k, 0], axis=-1) for j in J]
            p = np.argmin(d)
            G.append(J.pop(p))
        # Rearrange
        amp[:, i] = amp[G, i]
        idx.append(G)
    idx = np.asarray(idx).T
    return amp, idx


def plotting(csidata):
    s_index = scidx(80, 1, 'ac')
    a_index = s_index + 80 // 20 * 32
    offset, count = group(csidata)
    offset, count = offset[count == 16], count[count == 16]

    amp = [np.abs(csidata.csi[offset + i][:, a_index]) for i in range(16)]
    amp = np.asarray(amp)   # [16, packets_num, subcarriers]
    amp, idx = rearrange(amp, 16)
    t = csidata.sec + csidata.usec * 1e-6
    t = t[offset]
    t = t - t[0]

    plt.figure(figsize=(8, 4))
    plt.imshow(idx, cmap='jet', aspect='auto', interpolation='antialiased',
               origin='lower')
    plt.xlabel('packets')
    plt.ylabel('antennas')
    plt.tight_layout()

    fig, axes = plt.subplots(4, 4, sharex=True, sharey=True, figsize=(8, 4))
    for i in range(4):
        for j in range(4):
            axes[i, j].imshow(amp[4 * i + j].T, cmap='jet', aspect='auto',
                              origin='lower',
                              extent=(t[0], t[-1], s_index[0], s_index[-1]))
    fig.text(0.5, 0.005, 'time [s]', ha='center')
    fig.text(0.005, 0.5, 'subcarriers index', va='center', rotation='vertical')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    csifile = "B1.pcap"
    csidata = loadcsi(csifile)
    plotting(csidata)
