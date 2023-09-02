#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Doppler based on CSI Ratio.

Usage:
    python3 csiDoppler.py ../material/5300/dataset/sample_0x5_64_3000.dat
"""

import argparse

import csiread
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import fftshift
from scipy.signal import butter, lfilter, savgol_filter, stft

matplotlib.rcParams['lines.dash_capstyle'] = 'round'


def loadcsi(csifile):
    csidata = csiread.Intel(csifile, if_report=False)
    csidata.read()
    csi = csidata.get_scaled_csi_sm(True)
    tpl = np.diff(csidata.timestamp_low).view(np.int32)
    rate = np.floor(1e6 / tpl.mean()).astype(int)
    return csi, rate


def doppler(csi, rate=1000, hf=60, index=None):
    """Dopper

    Args:
        csi (ndarray): CSI Ratio or CSI Conjugate Multiplication
        rate (int): the sample rate of the dataset.
        hf (int): high frequency. `hf` != False means that the csi has been
            filtered, Then a mask operation will applied to the doppler spectrum
        index: which subcarrier to be used. If `None`, the mean value of
        	subcarriers will be used.
    Note:
    	The arguments of stft may be adjusted according to the data.
    """
    csi = csi.mean(axis=1) if index is None else csi[:, index]

    # stft
    newf, newt, Sxx = stft(csi, rate, nfft=rate,
                           window=('gaussian', 64), nperseg=128,
                           noverlap=127, axis=0, return_onesided=False)
    Sxx *= Sxx.conj()
    newf = fftshift(newf)
    Sxx = fftshift(np.abs(Sxx) / np.abs(Sxx).sum(axis=0), axes=0)

    # Select
    if hf:
        mask = np.abs(newf) <= hf
        newf, Sxx = newf[mask], Sxx[mask]

    return newf, newt, Sxx


def plot_spectrum(f, t, s, fit=True):
    fig = plt.figure()
    plt.imshow(s, cmap='jet', aspect='auto', origin='lower',
               extent=(0, t[-1], f[0], f[-1]), alpha=1)
    if fit:
	    pos = (np.argmax(s, axis=0) - (len(f) / 2)) * (f[-1] - f[0]) / len(f)
	    pos = savgol_filter(pos, 65, 1, mode='interp')
	    plt.plot(t, pos, 'b--', linewidth=2)

    plt.title('Doppler Shift')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.tight_layout()
    plt.show()


def plot_doppler(file, index):
    # load csi
    csi, rate = loadcsi(file)
    csi = csi[:rate * 3]	# reduce calculation, 3s.

    # csi ratio
    csi[csi == 0.0 + 0.0j] = 1 	# rare case.
    ratio = csi[:, :, 1:] / csi[:, :, :1]

    lf, hf = 2, 60
    b, a = butter(4, [lf, hf], 'bandpass', fs=rate, output='ba')
    csiratio = lfilter(b, a, ratio, axis=0)

    # doppler
    f, t, s = doppler(csiratio, rate, hf, index)
    plot_spectrum(f, t, s[:, 0, 0, :], True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str)
    parser.add_argument('-i', '--index', type=int)
    p = parser.parse_args()

    plot_doppler(p.file, p.index)
