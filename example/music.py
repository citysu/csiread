#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""MUSIC算法

Usage:
    python3 csimusic.py

Important:
    Is it correct? I'm not sure.

Ref:
    1. <<空间谱估计理论与算法>> 王永良
"""

import numpy as np
from numpy import linalg as LA
import scipy.signal as ss
from scipy.signal import find_peaks
import matplotlib.pyplot as plt


c = 3e8		# light speed


def signalG(N, d, f, M, L):
    """Signal generation"""
    array_space = np.arange(M).reshape(-1, 1) * d                                           # 阵元位置(线阵)
    angle_space = np.random.randint(-90, 90, L).reshape(-1, 1, 1) / 180 * np.pi             # 角度(DOA) 
    a = np.exp(-1.j * 2 * np.pi * f * array_space * np.sin(angle_space) / c).squeeze().T    # 导向矢量
    s = 10 * np.random.randn(L, N)
    n = 0.1 * np.random.randn(M, N)
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
    # N is X.shape(1)
    X = np.expand_dims(X.T, -1)
    R = (X @ X.conj().transpose(0, 2, 1)).mean(axis=0)

    w, v = LA.eig(R)
    indices = w.argsort()[::-1]
    w, v = w[indices], v[indices]
    u = v[:, L:]                                                                # 噪声子空间

    array_space = np.arange(M).reshape(-1, 1) * d                               # 阵元位置(线阵)
    angle_space = np.linspace(-np.pi / 2, np.pi / 2, 180).reshape(-1, 1, 1)     # 角度扫面空间
    a = np.exp(-1.j * 2 * np.pi * f * array_space * np.sin(angle_space) / c)    # 导向矢量
    p = LA.norm(a) / LA.norm(u.conj().T @ a, axis=1).squeeze()                  # MUSIC谱
    p = 10 * np.log10(p/p.max())

    # DOA
    peak, _ = find_peaks(p)
    doa = sorted(peak[p[peak].argsort()][-L:] - 90)

    print("MUSIC  - doa: ", doa)
    return p, doa


if __name__ == "__main__":
    x = signalG(N=100, d=6.25e-2, f=2.417e9, M=4, L=3)
    p, doa = music(X=x, N=100, d=6.25e-2, f=2.417e9, M=4, L=3)

    x = np.linspace(-90, 90, 180)
    plt.plot(x, p)
    plt.show()
