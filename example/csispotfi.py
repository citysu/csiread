#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""SpotFi: `SpotFi: Decimeter Level Localization Using WiFi`

Usage:
    python3 csispotfi.py

Note:
    work with Linux 802.11n CSI Tool

Important:
    Unfinished.

Ref:
    1. <<空间谱估计理论与算法>> 王永良
    2. [SpotFi: Decimeter Level Localization Using WiFi](http://conferences.sigcomm.org/sigcomm/2015/pdf/papers/p269.pdf)
"""

import numpy as np
from numpy import linalg as LA
import scipy.signal as ss
from scipy.signal import find_peaks
import csiread
import matplotlib.pyplot as plt
from music import signalG, music
from utils import get_subcarriers_index


def remove_sto(csi, carriers):
    """Algorithm 1: SpotFi’s ToF sanitization algorithm
	
	Args:
		carriers: subcarriers index
	"""
    freq_delta = 312500                     # frequency space
    radius = np.abs(csi)					# amplitude
    theta = np.unwrap(np.angle(csi))		# phase

    # In the paper, step 1 is least squares
    tau = np.polyfit(np.arange(30), theta, 1)[0]
    n = (carriers - carriers[0]).reshape(-1, 1)
    theta = theta - 2 * np.pi * freq_delta * n * tau

    csi = radius * np.exp(1j * theta)
    return csi


def smooth_csi(csi):
    """Fig.4: CSI smoothing"""
    smoothed_csi = np.zeros([30, 32], dtype=np.complex_)
    for i in range(15):
        smoothed_csi[i] = csi[i:i+16, 0:2].flatten('F')
        smoothed_csi[i+15] = csi[i:i+16:, 1:3].flatten('F')
    return smoothed_csi


def spotfi(csi):
    carriers = get_subcarriers_index(20, 2)
    smoothed_csi = smooth_csi(csi)
    smoothed_csi = remove_sto(smoothed_csi, carriers)
    p, doa = music(X=smoothed_csi, N=32, d=6.25e-2, f=5.327e9, M=30, L=1)
    return p
