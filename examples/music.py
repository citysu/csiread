#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""MUltiple SIgnal Classification (MUSIC) Algorithm

Usage:
    python3 music.py

Ref:
   1. [MUSIC Super-Resolution DOA Estimation](https://ww2.mathworks.cn/help/phased/ug/music-super-resolution-doa-estimation.html)
   2. [Phased Array System Toolbox](https://ww2.mathworks.cn/en/products/phased-array.html)
   3. 王永良. 空间谱估计理论与算法[M]. 清华大学出版社, 2004.
"""

import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import eigh, norm, inv
from numpy.random import randn, uniform
from scipy.linalg import hankel
from scipy.signal import find_peaks
from scipy.stats import gmean


def signalG(T, M, D, d, f, c=3e8, correlated=False):
    """Signal Generation

    Args:
        T: number of snapshots
        M: number of receivers
        D: number of sources
        d: distance between receivers
        f: frequency
        c: wave speed
        correlated: correlated sources or not
    """
    ula = np.c_[:M] * d                                         # uniform linear array (ULA)
    doa = np.sort(uniform(-np.pi/2, np.pi/2, D))                # directions of arrival (DOA)
    a = np.exp(-2.j * np.pi * f * ula * np.sin(doa) / c)        # steering vector
    s = (randn(T) + randn(T) * 1.j) * np.exp(1.j * np.c_[:D]) \
        if correlated else randn(D, T) + randn(D, T) * 1.j      # sources
    n = randn(M, T) + randn(M, T) * 1.j                         # noise
    x = a @ s + n * 0.01                                        # signal model
    return x.T, doa


def smooth(X, L):
    """Spatial Smoothing of Correlated Sources

    Args:
        L: The number of elements in each subarray
    """
    T, M = X.shape
    J = M - L + 1
    X = [hankel(X[i, :L], X[i, -J:]).T for i in range(T)]
    X = np.asarray(X).reshape(-1, L)
    return X


def NoSS(X, method='MDL'):
    """Number of Signal Source"""
    T, M = X.shape
    R = (X[..., np.newaxis] @ X[:, np.newaxis].conj()).mean(axis=0)
    w, v = eigh(R)

    def Lambda(n):
        return np.mean(w[:-n]) / gmean(w[:-n])

    def AIC(n):
        return 2 * T * (M - n) * np.log(Lambda(n)) + 2 * n * (2 * M - n)

    def MDL(n):
        return T * (M - n) * np.log(Lambda(n)) + 1/2 * n * (2 * M - n) * np.log(T)

    def HQ(n):
        return T * (M - n) * np.log(Lambda(n)) + 1/2 * n * (2 * M - n) * np.log(np.log(T))

    func = eval(method)
    D = np.argmin([func(i) for i in range(1, M)]) + 1
    return D


def music(X, D, d, f, c=3e8):
    """Classic MUSIC Algorithm"""
    T, M = X.shape
    R = (X[..., np.newaxis] @ X[:, np.newaxis].conj()).mean(axis=0)
    w, v = eigh(R)
    u = v[:, ::-1][:, D:]                                       # noise subspace

    ula = np.c_[:M] * d                                         # ULA
    doa_space = np.linspace([[-np.pi/2]], [[np.pi/2]], 180)     # search space
    a = np.exp(-2.j * np.pi * f * ula * np.sin(doa_space) / c)  # steering vector
    p = 1 / norm(u.T.conj() @ a, axis=(1, 2))                   # MUSIC pseudospectrum
    p *= norm(a, axis=(1, 2))                                   # optional
    p = 10 * np.log10(p/p.max())

    # DOA
    peak, _ = find_peaks(p)
    index = sorted(peak[p[peak].argsort()][-D:])
    doa = doa_space[index, 0, 0]
    return p, doa


def music_root(X, D, d, f, c=3e8):
    """Root-MUSIC(RMU) Algorithm"""
    T, M = X.shape
    R = (X[..., np.newaxis] @ X[:, np.newaxis].conj()).mean(axis=0)
    w, v = eigh(R)
    u = v[:, ::-1][:, D:]

    coff = np.r_[1, (u[:D] @ inv(u[D:]))[::-1, 0]]
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
    x, doa_real = signalG(T=100, M=9, D=3, d=6.25e-2, f=2.4e9, correlated=True)
    x = smooth(x, L=5)
    p, doa_fake = music(X=x, D=NoSS(x), d=6.25e-2, f=2.4e9)
    plotspectrum(p, doa_fake, doa_real)
