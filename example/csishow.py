#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Plot csi of Linux 802.11n CSI Tool, observe csi quickly

Usage:
    python3 csishow.py ../material/5300/dataset/sample_0x1_ap.dat -t 1
"""
import argparse

import csiread
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np


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


def calib(phase, bw=20, ng=2):
    """Phase calibration

    Note:
        phase: it must be unwrapped, it should be a 2-D, 3-D
            or 4-D array and the second dimension must be subcarriers
        bw, ng: the same as `get_subcarriers_index`

    ref:
        [Enabling Contactless Detection of Moving Humans with Dynamic Speeds Using CSI]
        (http://tns.thss.tsinghua.edu.cn/wifiradar/papers/QianKun-TECS2017.pdf)
    """
    s_index = get_subcarriers_index(bw, ng)
    k_n = s_index[-1]
    k_1 = s_index[1]
    a = ((phase[:, -1:] - phase[:, :1]) / (k_n - k_1))
    b = np.mean(phase, axis=1, keepdims=True)
    s_index = s_index.reshape([len(s_index)] + [1] * (len(phase.shape) - 2))
    phase_calib = phase - a * s_index - b
    return phase_calib


def func_1(csidata):
    s_index = 15    # subcarrier index
    csi = csidata.get_scaled_csi()
    t = csidata.timestamp_low/1000000 - csidata.timestamp_low[0]/1000000

    amplitude = np.abs(csi[:, s_index])

    plt.figure()
    plt.plot(t, amplitude[:, 0, 0], linewidth=0.3, label='subcarrier_15_0_0')
    plt.plot(t, amplitude[:, 1, 0], linewidth=0.3, label='subcarrier_15_1_0')
    plt.plot(t, amplitude[:, 2, 0], linewidth=0.3, label='subcarrier_15_2_0')
    plt.legend()

    plt.title('csi-amplitude')
    plt.xlabel('time(s)')
    plt.ylabel('amplitude')
    plt.show()


def func_2(csidata):
    csi = csidata.get_scaled_csi()
    amplitude = np.abs(csi)
    s_index = get_subcarriers_index(20, 2)

    plt.figure()
    plt.plot(s_index, amplitude[:100, :, 0, 0].T, 'r-', linewidth=0.3)
    plt.plot(s_index, amplitude[:100, :, 1, 0].T, 'g-', linewidth=0.3)
    plt.plot(s_index, amplitude[:100, :, 2, 0].T, 'y-', linewidth=0.3)

    patch_1 = mpatches.Patch(color='red', label=':100_r0t0')
    patch_2 = mpatches.Patch(color='green', label=':100_r1t0')
    patch_3 = mpatches.Patch(color='yellow', label=':100_r2t0')
    plt.legend(handles=[patch_1, patch_2, patch_3])

    plt.title('csi-amplitude')
    plt.xlabel('subcarriers')
    plt.ylabel('amplitude')
    plt.show()


def func_3(csidata):
    s_index = 15    # subcarrier index
    csi = csidata.get_scaled_csi()
    t = csidata.timestamp_low/1000000 - csidata.timestamp_low[0]/1000000
    phase = np.unwrap(np.angle(csi), axis=1)
    phase = calib(phase)

    plt.figure()
    plt.plot(t, phase[:, s_index, 0, 0], linewidth=0.3, label='subcarrier_15_0_0')
    plt.plot(t, phase[:, s_index, 1, 0], linewidth=0.3, label='subcarrier_15_1_0')
    plt.plot(t, phase[:, s_index, 2, 0], linewidth=0.3, label='subcarrier_15_2_0')
    plt.legend()
    plt.title('csi-phase')
    plt.xlabel('time(s)')
    plt.ylabel('phase')
    plt.show()


def func_4(csidata):
    csi = csidata.get_scaled_csi()
    phase = np.unwrap(np.angle(csi), axis=1)
    phase = calib(phase)
    s_index = get_subcarriers_index(20, 2)

    plt.figure(4)
    plt.plot(s_index, phase[:100, :, 0, 0].T, 'r-', linewidth=0.3)
    plt.plot(s_index, phase[:100, :, 1, 0].T, 'g-', linewidth=0.3)
    plt.plot(s_index, phase[:100, :, 2, 0].T, 'y-', linewidth=0.3)

    patch_1 = mpatches.Patch(color='red', label=':100_r0t0')
    patch_2 = mpatches.Patch(color='green', label=':100_r1t0')
    patch_3 = mpatches.Patch(color='yellow', label=':100_r2t0')
    plt.legend(handles=[patch_1, patch_2, patch_3])

    plt.title('csi-phase')
    plt.xlabel('subcarriers')
    plt.ylabel('phase')
    plt.show()


def func_5(csidata):
    time_diff = np.diff(csidata.timestamp_low)
    plt.figure(5)
    plt.plot(time_diff, linewidth=0.3, label='time diff')
    plt.legend()
    plt.title('time-diff')
    plt.xlabel('packets')
    plt.ylabel('time(us)')
    plt.show()


helpinfo = r"""Plot Type

1   CSI-time-amplitude
2   CSI-subcarrier-amplitude
3   CSI-time-phase
4   CSI-subcarrier-phase
5   timestamp-packet-timediff
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('file', type=str, help='data file')
    parser.add_argument('-t', type=int, default=1, help=helpinfo)
    p = parser.parse_args()

    csidata = csiread.CSI(p.file, Nrxnum=3, Ntxnum=3)
    csidata.read()
    if p.t > 5:
        raise ValueError('the value of `t` can be 1, 2, 3, 4, 5')
    func = eval('func_' + str(p.t))
    func(csidata)
