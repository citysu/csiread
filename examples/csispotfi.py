#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""SpotFi: `SpotFi: Decimeter Level Localization Using WiFi`

Usage:
    python3 csispotfi.py

Important:
    Unfinished! There are many issues.

Ref:
    1. [SpotFi: Decimeter Level Localization Using WiFi](http://conferences.sigcomm.org/sigcomm/2015/pdf/papers/p269.pdf)
    2. [spotfiMusicAoaEstimation](https://bitbucket.org/mkotaru/spotfimusicaoaestimation)
"""

import numpy as np
from numpy import linalg as LA
from scipy.signal import find_peaks
import csiread
import matplotlib.pyplot as plt
from utils import scidx


def remove_sto(csi, bw=20, ng=2):
    """Algorithm 1: SpotFi’s ToF sanitization algorithm

    Args:
        csi: [30, 3] - [subcarriers, Ntx]

    Ref:
        spotfiMusicAoaEstimation: removePhsSlope.m
    """
    s_index = np.tile(scidx(bw, ng), (csi.shape[1], 1)).T

    # In the paper, step 1 is least-squares 
    m, c = np.linalg.lstsq(np.c_[s_index.flatten('F'), np.ones(csi.size)], 
                           np.unwrap(np.angle(csi), axis=0).flatten('F'),
                           rcond=None)[0]
    return csi * np.exp(-1.j * (m * s_index + c))


def smooth_csi(csi):
    """Fig.4: CSI smoothing"""
    smoothed_csi = np.zeros([30, 32], dtype=np.complex_)
    for i in range(15):
        smoothed_csi[i] = csi[i:i+16, 0:2].flatten('F')
        smoothed_csi[i+15] = csi[i:i+16:, 1:3].flatten('F')
    return smoothed_csi


def smooth_csiB(csi):
    """Fig.4: CSI smoothing(another version)"""
    from scipy.linalg import hankel
    h0 = hankel(csi[:15, 0], csi[14:, 0])
    h1 = hankel(csi[:15, 1], csi[14:, 1])
    h2 = hankel(csi[:15, 2], csi[14:, 2])
    smoothed_csi = np.c_[np.r_[h0, h1],
                         np.r_[h1, h2]]
    return smoothed_csi


def spotfi(csi):
    pass
