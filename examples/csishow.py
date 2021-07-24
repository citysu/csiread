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
import scipy.signal as signal
from utils import scidx, calib, phy_ifft


def func_1(csidata):
    """CSI: time-amplitude"""
    s_index = 15    # subcarrier index
    csi = csidata.get_scaled_csi_sm()
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
    """CSI: subcarrier-amplitude(CFR)"""
    csi = csidata.get_scaled_csi_sm()
    amplitude = np.abs(csi)
    s_index = scidx(20, 2)

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
    """CSI: time-phase"""
    s_index = 15    # subcarrier index
    csi = csidata.get_scaled_csi_sm()
    t = csidata.timestamp_low/1000000 - csidata.timestamp_low[0]/1000000
    phase = np.unwrap(np.angle(csi), axis=1)
    phase = calib(phase, scidx(20, 2))

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
    """CSI: subcarrier-phase"""
    csi = csidata.get_scaled_csi_sm()
    s_index = scidx(20, 2)
    phase = np.unwrap(np.angle(csi), axis=1)
    phase = calib(phase, s_index)

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
    """timestamp_low: packet-time_difference

    Tips:
        Why are Intel.timestamp_low, Nexmon.sec and Nexmon.usec stored as
        ``np.uint32``?

        We may have such timestamp_low: ``[..., 2**32 - 2000, 2**32 - 1000,0,
        1000, 2000, ...]``. If timestamp_low.dtype is ``np.unint32``, we can get
        the correct time_diff by ``np.diff(csidata.timestamp_low).view(np.int32)``
        without any concern. When timestamp_low.dtype is ``np.int64``, the
        time_diff will contain negative values, we have to correct it by
        ``time_diff[time_diff < 0] += 2**32``.
    """
    time_diff = np.diff(csidata.timestamp_low)
    plt.figure(5)
    plt.plot(time_diff, linewidth=0.3, label='time diff')
    plt.legend()
    plt.title('time-diff')
    plt.xlabel('packets')
    plt.ylabel('time(us)')
    plt.show()


def func_6(csidata):
    """CSI: time-amplitude(CIR: OFDM symbol view)"""
    csi = csidata.get_scaled_csi_sm()

    s_index = scidx(20, 2)
    amplitude1 = np.abs(phy_ifft(csi[:100, :, 0, 0], s_index, axis=1)).T
    amplitude2 = np.abs(phy_ifft(csi[:100, :, 1, 0], s_index, axis=1)).T
    amplitude3 = np.abs(phy_ifft(csi[:100, :, 2, 0], s_index, axis=1)).T
    t = np.linspace(0, 64, 64)

    plt.figure(6)
    plt.plot(t, amplitude1, 'r-', linewidth=0.3)
    plt.plot(t, amplitude2, 'g-', linewidth=0.3)
    plt.plot(t, amplitude3, 'y-', linewidth=0.3)

    patch_1 = mpatches.Patch(color='red', label=':100_r0t0')
    patch_2 = mpatches.Patch(color='green', label=':100_r1t0')
    patch_3 = mpatches.Patch(color='yellow', label=':100_r2t0')
    plt.legend(handles=[patch_1, patch_2, patch_3])

    plt.title('csi-CIR')
    plt.xlabel('time(50ns)')
    plt.ylabel('amplitude')
    plt.show()


def func_8(csidata):
    """CSI: time-amplitude(butterworth filter)"""
    print("Waring: Please set parameters(butterworth) first")

    csi = csidata.get_scaled_csi_sm()[:1000]
    amplitude = np.abs(csi)
    t = (csidata.timestamp_low/1000000 - csidata.timestamp_low[0]/1000000)[:1000]

    sos = signal.butter(4, 100.0, 'lowpass', fs=900, output='sos')
    sfiltered = signal.sosfiltfilt(sos, amplitude, axis=0)

    plt.figure(9)
    plt.plot(t, amplitude[:, 15, 0, 0], '-', linewidth=1.5, alpha=0.25, label='origin_:1000s15r0t0')
    plt.plot(t, amplitude[:, 15, 1, 0], '-', linewidth=1.5, alpha=0.25, label='origin_:1000s15r1t0')
    plt.plot(t, amplitude[:, 15, 2, 0], '-', linewidth=1.5, alpha=0.25, label='origin_:1000s15r2t0')

    plt.plot(t, sfiltered[:, 15, 0, 0], '-', linewidth=1, label='buffer_:1000s15r0t0')
    plt.plot(t, sfiltered[:, 15, 1, 0], '-', linewidth=1, label='buffer_:1000s15r1t0')
    plt.plot(t, sfiltered[:, 15, 2, 0], '-', linewidth=1, label='buffer_:1000s15r2t0')

    plt.legend()
    plt.title("butterworth - lowpass")
    plt.xlabel('time(s)')
    plt.ylabel('amplitude')
    plt.show()


def func_9(csidata):
    index = 15
    csi = csidata.get_scaled_csi_sm()
    amplitude = np.abs(csi)
    t = (csidata.timestamp_low/1000000 - csidata.timestamp_low[0]/1000000)[:1000]

    kernel = np.array([[1], [2], [3], [2], [1]]) / 9
    amplitude1 = signal.convolve(amplitude[:1000, index:index+1, 0, 0], kernel, mode='same')
    amplitude2 = signal.convolve(amplitude[:1000, index:index+1, 1, 0], kernel, mode='same')
    amplitude3 = signal.convolve(amplitude[:1000, index:index+1, 2, 0], kernel, mode='same')

    plt.figure()
    plt.plot(t, amplitude1, 'r-', linewidth=0.3, label=':_s15r0t0')
    plt.plot(t, amplitude2, 'g-', linewidth=0.3, label=':_s15r1t0')
    plt.plot(t, amplitude3, 'y-', linewidth=0.3, label=':_s15r2t0')

    plt.legend()
    plt.title('csi amplitude conv smooth')
    plt.xlabel('time(s)')
    plt.ylabel('amplitude')
    plt.show()


helpinfo = r"""Plot Type

1   CSI-time-amplitude
2   CSI-subcarrier-amplitude
3   CSI-time-phase
4   CSI-subcarrier-phase
5   timestamp-packet-timediff
6   CSI-time-amplitude(CIR: OFDM symbol view)
8   CSI-time-amplitude(butterworth filter)
9   CSI-time-amplitude(Convolve)
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('file', type=str, help='data file')
    parser.add_argument('-t', type=int, default=1, help=helpinfo)
    p = parser.parse_args()

    csidata = csiread.Intel(p.file, nrxnum=3, ntxnum=3)
    csidata.read()
    if p.t > 10:
        raise ValueError('the value of `t` can be 1 - 10')
    func = eval('func_' + str(p.t))
    func(csidata)
