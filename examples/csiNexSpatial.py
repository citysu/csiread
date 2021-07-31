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


def get_frames_index(seq, ant_num=16):
    """Get the index of the frames

    Adjacent packets with the same sequence number are from the same frame

    Args:
        seq: sequence number
        ant_num: antennas count

    Attributes:
        count: the count of packets corresponding to one frame. we only keep
            frames where `count == ant_num`

    Returns:
        ndarray: offset, the position of frames. shape=[frame_count, ant_num]
    """
    seq_diff = np.diff(seq)
    offset = np.where(seq_diff != 0)[0]
    offset = np.r_[0, offset + 1]
    count = np.diff(np.r_[offset, len(seq)])
    offset = offset[count == ant_num]
    offset = [np.r_[o:o+ant_num] for o in offset]
    offset = np.asarray(offset)
    return offset


def rearrange(offset, csi):
    """Rearrange antennas by shortest distance of amplitudes

    Args:
        offset: returned by `get_frames_index`, shape=[frame_count, ant_num]
        csi: csidata.csi, shape=[packets_num, subcarriers]

    Returns:
        ndarray: offset_new, the position of frames after rearranging antennas.
            shape=[frame_count, ant_num]
    """
    offset_new = np.empty_like(offset)
    packet_num, ant_num = offset.shape
    amp = np.abs(csi[offset])
    index_ant = np.r_[:ant_num]
    for i in range(packet_num):
        d = np.linalg.norm(amp[i, np.newaxis] - amp[0, :, np.newaxis], axis=-1)
        d_max = d.max()
        for j in range(ant_num):
            p = np.argmin(d)
            px, py = p // ant_num, p % ant_num
            d[px, :], d[:, py] = d_max, d_max
            index_ant[px] = py
        offset_new[i, :] = offset[i, index_ant]
    return offset_new


def plotting(csidata):
    s_index = scidx(80, 1, 'ac')

    offset_0 = get_frames_index(csidata.seq, 16)
    offset = rearrange(offset_0, csidata.csi)

    t = csidata.sec + csidata.usec * 1e-6
    t = t[offset[:, 0]]
    t = t - t[0]
    amp = np.abs(csidata.csi[offset])

    plt.figure(figsize=(8, 4))
    plt.imshow(offset.T - offset_0[:, :1].T, cmap='jet', aspect='auto',
               interpolation='antialiased', origin='lower')
    plt.xlabel('packets')
    plt.ylabel('antennas')
    plt.tight_layout()

    fig, axes = plt.subplots(4, 4, sharex=True, sharey=True, figsize=(8, 4))
    for i in range(4):
        for j in range(4):
            axes[i, j].imshow(amp[:, 4 * i + j].T, cmap='jet', aspect='auto',
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
