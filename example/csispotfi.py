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


c = 3e8		# light speed


# >>>>>>>>>>>>>>>>>>>>> classic MUSIC <<<<<<<<<<<<<<<<<<<<< 
def signalG(N, d, f, M, L):
    """Signal generation"""
    # 阵元位置(线阵)
    array_space = np.arange(M).reshape(-1, 1) * d
    # 角度(DOA)
    angle_space = np.random.randint(-90, 90, L).reshape(-1, 1, 1) / 180 * np.pi
    # 导向矢量
    a = np.exp(-1.j * 2 * np.pi * f * array_space * np.sin(angle_space) / c).squeeze().T
    s = 10 * np.random.randn(L, N)
    n = 0.1*np.random.randn(M, N)

    x = a @ s + n

    print("signalG - doa:", sorted(angle_space.squeeze() / np.pi * 180))
    return x


def music(X, N, d, f, M, L):
    """Classic MUSIC Algorithm

    Args:
        X: 复信号
        N: 快拍数
        d: 天线间距
        f: 中心频率
        M: 阵元个数
        L: 信源个数
    """
    R = X@X.conj().T / X.shape[-1]
    w, v = LA.eig(R)
    indices = w.argsort()[::-1]
    w, v = w[indices], v[indices]

    # 噪声子空间
    u = v[:, L:]

    # 阵元位置(线阵)
    array_space = np.arange(M).reshape(-1, 1) * d
    # 角度扫面空间
    angle_space = np.linspace(-np.pi / 2, np.pi / 2, 180).reshape(-1, 1, 1)

    # 导向矢量
    a = np.exp(-1.j * 2 * np.pi * f * array_space * np.sin(angle_space) / c)
    # MUSCI谱
    p = LA.norm(a) / LA.norm(u.conj().T @ a, axis=1).squeeze()
    p = 10 * np.log10(p/p.max())

    # DOA
    peak, _ = find_peaks(p)
    doa = sorted(peak[p[peak].argsort()][-L:] - 90)

    print("MUSIC  - doa: ", doa)
    return p, doa
# >>>>>>>>>>>>>>>>>>>>>>> classic MUSIC <<<<<<<<<<<<<<<<<<<<<<


def get_subcarriers_index(bw, ng):
    """subcarriers index

    Args:
        bw: bandwitdh(20, 40)
        ng: grouping(1, 2, 4)
    """
    if bw not in [20, 40] or ng not in [1, 2, 4]:
        return None
    if bw == 20:
        a = [i for i in range(-28, -1, ng)] + [-1]
        b = [i for i in range(1, 28, ng)] + [28]
    if bw == 40:
        a = [i for i in range(-58, -2, ng)] + [-2]
        b = [i for i in range(2, 58, ng)] + [58]
    return np.array(a + b)


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


if __name__ == "__main__":
    x = signalG(N=100, d=6.25e-2, f=2.417e9, M=4, L=3)
    p, doa = music(X=x, N=100, d=6.25e-2, f=2.417e9, M=4, L=3)

    x = np.linspace(-90, 90, 180)
    plt.plot(x, p)
    plt.show()
