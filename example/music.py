#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""MUSIC Algorithm

Usage:
    python3 csimusic.py

Ref:
   1. [MUSIC Super-Resolution DOA Estimation](https://ww2.mathworks.cn/help/phased/ug/music-super-resolution-doa-estimation.html)
   2. [Phased Array System Toolbox](https://ww2.mathworks.cn/en/products/phased-array.html)
   3. 王永良. 空间谱估计理论与算法[M]. 清华大学出版社, 2004.
"""

import numpy as np
from numpy import linalg as LA
from scipy.signal import find_peaks
import matplotlib.pyplot as plt


def signalG(N, M, L, d, f, c=3e8):
    """Signal Generation(Uncorrelated Sources)

    Args:
        N: number of snapshots
        M: number of receivers
        L: number of sources
        d: distance between receivers
        f: frequency
        c: wave speed
    """
    ula = np.c_[:M] * d                                         # uniform linear array (ULA)
    doa = np.sort(np.random.uniform(-np.pi/2, np.pi/2, L))      # directions of arrival (DOA)
    a = np.exp(-2.j * np.pi * f * ula * np.sin(doa) / c)        # steering vector
    s = np.random.randn(L, N) + np.random.randn(L, N) * 1.j     # source signal
    n = np.random.randn(M, N) + np.random.randn(M, N) * 1.j     # noise
    x = a @ s + n * 0.01                                        # signal model
    return x.T, doa


def NoSS(X, method='AIC'):
    """Number of Signal Source"""
    N, M = X.shape
    R = (X[..., np.newaxis] @ X[:, np.newaxis].conj()).mean(axis=0)
    w, v = LA.eigh(R)

    def Lambda(n):
        return 1 / (M - n) * np.sum(w[:-n]) / np.prod(w[:-n]) ** (1 / (M - n))

    def AIC(n):
        return 2 * N * (M - n) * np.log(Lambda(n)) + 2 * n * (2 * M - n)

    def MDL(n):
        return N * (M - n) * np.log(Lambda(n)) + 1/2 * n * (2 * M - n) * np.log(N)

    def HQ(n):
        return N * (M - n) * np.log(Lambda(n)) + 1/2 * n * (2 * M - n) * np.log(np.log(N))

    func = eval(method)
    L = np.argmin([func(i) for i in range(1, M)]) + 1
    return L


def music(X, L, d, f, c=3e8):
    """MUSIC Algorithm

    Args:
        X: signal received [snapshots, receivers]
        L: number of sources
        d: distance between receivers
        f: frequency
        c: wave speed
    """
    N, M = X.shape
    R = (X[..., np.newaxis] @ X[:, np.newaxis].conj()).mean(axis=0)
    w, v = LA.eigh(R)
    u = v[:, ::-1][:, L:]                                       # noise subspace

    ula = np.c_[:M] * d                                         # ULA  
    doa_space = np.linspace([[-np.pi/2]], [[np.pi/2]], 180)     # search space
    a = np.exp(-2.j * np.pi * f * ula * np.sin(doa_space) / c)  # steering vector
    p = 1 / LA.norm(u.T.conj() @ a, axis=(1, 2))                # MUSIC pseudospectrum
    # p *= LA.norm(a, axis=(1, 2))                                # optional
    p = 10 * np.log10(p/p.max())

    # DOA
    peak, _ = find_peaks(p)
    index = sorted(peak[p[peak].argsort()][-L:])
    doa = doa_space[index, 0, 0]
    return p, doa


def music_root(X, L, d, f, c=3e8):
    """Root-MUSIC(RMU) Algorithm"""
    N, M = X.shape
    R = (X[..., np.newaxis] @ X[:, np.newaxis].conj()).mean(axis=0)
    w, v = LA.eigh(R)
    u = v[:, ::-1][:, L:]

    coff = np.r_[1, (u[:L] @ LA.inv(u[L:]))[::-1, 0]]
    r = np.roots(coff)
    doa = np.sort(np.arcsin(np.angle(r) * c / f / (2 * np.pi * d)))
    return None, doa


def plotspectrum(p, doa_fake, doa_real):
    doa_real *= (180 / np.pi)
    doa_fake *= (180 / np.pi)
    print("signalG - doa: ", doa_real)
    print("MUSIC   - doa: ", doa_fake)
    
    if p is None:
        p = np.sin(np.deg2rad(np.arange(180)))
    x = np.linspace(-90, 90, p.size)
    index = [np.abs(x - a).argmin() for a in doa_fake]

    plt.figure()
    plt.plot(x, p)
    plt.plot(doa_fake, p[index], 'xr', markersize=10, label='doa fake')
    plt.vlines(doa_real, p.min(), p.max(), colors='orange', linewidth=2,
               linestyles='--', label='doa real')
    plt.legend()
    plt.title("MUSIC")
    plt.xlabel("Angle(deg)")
    plt.ylabel("Power(dB)" if p.max() != 1 else "")
    plt.show()


if __name__ == "__main__":
    x, doa_real = signalG(N=100, M=4, L=3, d=6.25e-2, f=2.4e9)
    p, doa_fake = music(X=x, L=NoSS(x), d=6.25e-2, f=2.4e9)

    plotspectrum(p, doa_fake, doa_real)
