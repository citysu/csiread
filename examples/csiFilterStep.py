#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""filter step

Usage of scipy.signal.lfilter, an example of real-time filter.


Usage:
    python3 csiFilterStep.py
"""

import csiread
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter, lfilter_zi


def load_csi(csifile):
    csidata = csiread.Intel(csifile)
    csidata.read()
    csi = csidata.get_scaled_csi_sm(True)
    tpl = np.diff(csidata.timestamp_low).view(np.int32)
    rate = np.floor(1e6 / tpl.mean()).astype(int)
    return csi, rate


def filter_once(amp, fs, winsize=40):
    b, a = butter(4, [2, 60], 'bandpass', fs=fs, output='ba')
    return lfilter(b, a, amp, axis=0)[:-winsize]


def filter_step(amp, fs, winsize=40):
    b, a = butter(4, [2, 60], 'bandpass', fs=fs, output='ba')
    zi = lfilter_zi(b, a)
    zi = zi[:, np.newaxis]
    amp_new = list()
    for i in range(0, amp.shape[0] - winsize, winsize):
        amp_now, zi = lfilter(b, a, amp[i:i+winsize], axis=0, zi=zi)
        amp_new.append(amp_now)
    return np.concatenate(amp_new, axis=0)


def smooth_line(csidata, fs=1000):
    amp = np.abs(csi[:3000, :, 0, 0])
    amp_once = filter_once(amp, fs, 40)
    amp_step = filter_step(amp, fs, 40)
    t_once = np.linspace(0, amp_once.shape[0]/fs, amp_once.shape[0])
    t_step = np.linspace(0, amp_step.shape[0]/fs, amp_step.shape[0])

    plt.style.use(['ggplot'])
    plt.figure(figsize=(8, 4.5))
    plt.subplot(2, 1, 1)
    plt.plot(t_once, amp_once)
    plt.title('filter once')
    plt.xlabel('time [s]')
    plt.subplot(2, 1, 2)
    plt.plot(t_step, amp_step)
    plt.title('filter step')
    plt.xlabel('time [s]')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    csifile = "../material/5300/dataset/sample_0x5_64_3000.dat"
    csi, fs = load_csi(csifile)

    smooth_line(csi, fs)
