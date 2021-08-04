#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Build spatial stream index

Usage:
    python3 csiNexSpatial.py

Note:
    Dowload data file from [spatial stream index of nexmon daa #14](https://github.com/Gi-z/CSIKit/issues/14)
"""

import numpy as np
import csiread as cr
import matplotlib.pyplot as plt
import os


def loadcsi(csifile):
    if os.path.exists(csifile) is False:
        raise FileNotFoundError("%s doesn't exist" % (csifile))
    csidata = cr.Nexmon(csifile, '4366c0', 80, if_report=False)
    csidata.read()
    csidata.csi = np.fft.fftshift(csidata.csi)
    return csidata


def group_guess_1(seq, c_num=4, s_num=4):
    """Build spatial stream index roughly, step 1

    Adjacent packets with the same sequence number are from the same frame.
    To simplify processing, we'll drop the broken frames

    Args:
        seq: sequence number
        c_num: the number of core
        s_num: the number of spatial

    Returns:
        ndarray: offset, shape=[frame_count, ant_num], the position of frames. 
    """
    ant_num = c_num * s_num
    seq_diff = np.diff(seq)
    offset = np.where(seq_diff != 0)[0]
    offset = np.r_[0, offset + 1]
    count = np.diff(np.r_[offset, len(seq)])
    offset = offset[count == ant_num]
    offset = [np.r_[o:o+ant_num] for o in offset]
    offset = np.asarray(offset)
    return offset


def group_guess_2(offset, csi):
    """Build spatial stream index roughly, step 2

    Try to rearrange antennas of each frame by the shortest distance between
    csi frames. However, it cannot return the REAL spatial stream index, you
    should consider recording core and spatial first.

    Args:
        offset: returned by `group_guess_1`
        csi: csidata.csi, shape=[packets_num, subcarriers]

    Returns:
        ndarray: offset_new, shape=[frame_count, ant_num], the position of
            frames after rearranging antennas.

    Note:
        Only call this when core and spatial are unknown
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


def group(seq, core, spatial, c_num=4, s_num=4):
    """Build spatial stream index

    It works when core and spatial are known

    Args:
        seq: csidata.seq
        core: csidata.core
        spatial: csidata.spatial
        c_num: the number of core
        s_num: the number of spatial

    Returns:
        ndarray: offset, shape=[frame_count, ant_num], the position of frames.

    Examples:

        >>> offset = group(csidata.seq, csidata.core, csidata.spatial, 4)
        >>> csi = csidata.csi[offset]
        >>> sec = csidata.sec[offset]
    """
    # step 1
    ant_num = c_num * s_num
    seq_diff = np.diff(seq)
    offset = np.where(seq_diff != 0)[0]
    offset = np.r_[0, offset + 1]
    count = np.diff(np.r_[offset, len(seq)])
    offset = offset[count == ant_num]
    offset = [np.r_[o:o+ant_num] for o in offset]
    offset = np.asarray(offset)

    # step 2
    core = core[offset]
    spatial = spatial[offset]
    p = core * s_num + spatial
    p = np.argsort(p, axis=-1)
    offset = offset[:, :1] + p

    return offset


def set_core_spatial(csidata, offset, c_num=4, s_num=4):
    """Simulation: core and spatial are known"""
    ant_num = c_num * s_num
    p = np.r_[:ant_num]
    px, py = p // s_num, p % s_num
    csidata.core[offset] = px
    csidata.spatial[offset] = py


def plotting(csidata):
    offset_0 = group_guess_1(csidata.seq, c_num=4, s_num=4)
    offset_1 = group_guess_2(offset_0, csidata.csi)

    set_core_spatial(csidata, offset_1, c_num=4, s_num=4)
    offset = group(csidata.seq, csidata.core, csidata.spatial, 4, 4)

    t = csidata.sec + csidata.usec * 1e-6
    t = t[offset[:, 0]]
    t = t - t[0]
    csi = csidata.csi[offset]
    amp = np.abs(csi)
    print("csi.shape: ", csi.shape)

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
                              extent=(t[0], t[-1], -128, 128))
    fig.text(0.5, 0.005, 'time [s]', ha='center')
    fig.text(0.005, 0.5, 'subcarriers index', va='center', rotation='vertical')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    csifile = "B1.pcap"
    csidata = loadcsi(csifile)
    plotting(csidata)
