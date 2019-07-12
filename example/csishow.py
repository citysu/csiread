# ！/usr/bin/python3
"""
Plot csi of Linux 802.11n CSI Tool
"""
import argparse

import csiread
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from scipy.fftpack import ifft, fftshift, ifftshift
import scipy.signal as signal


carriers_seq_30 = np.array([-28, -26, -24, -22, -20, -18, -16, -14, -12,
                            -10, -8, -6, -4, -2, -1, 1, 3, 5, 7, 9, 11, 13,
                            15, 17, 19, 21, 23, 25, 27, 28])


def calib(csi):
    phase = np.unwrap(np.angle(csi))
    k_n = carriers_seq_30[-1]
    k_1 = carriers_seq_30[0]
    a = ((phase[:, -1:] - phase[:, :1])/(k_n - k_1))
    b = np.mean(phase, axis=1, keepdims=True)
    phase_calib = phase - a*carriers_seq_30 - b
    return phase_calib


def func_1(csidata):
    s_index = 15    # 选择绘制的子载波
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

    plt.figure()
    plt.plot(carriers_seq_30, np.transpose(amplitude[:100, :, 0, 0]), 'r-', linewidth=0.3)
    plt.plot(carriers_seq_30, np.transpose(amplitude[:100, :, 1, 0]), 'g-', linewidth=0.3)
    plt.plot(carriers_seq_30, np.transpose(amplitude[:100, :, 2, 0]), 'y-', linewidth=0.3)

    patch_1 = mpatches.Patch(color='red', label=':100_r0t0')
    patch_2 = mpatches.Patch(color='green', label=':100_r1t0')
    patch_3 = mpatches.Patch(color='yellow', label=':100_r2t0')
    plt.legend(handles=[patch_1, patch_2, patch_3])

    plt.title('csi-amplitude')
    plt.xlabel('subcarriers')
    plt.ylabel('amplitude')
    plt.show()


def func_3(csidata):
    s_index = 15
    csi = csidata.get_scaled_csi()
    t = csidata.timestamp_low/1000000 - csidata.timestamp_low[0]/1000000
    phase1 = calib(csi[:, :, 0, 0])
    phase2 = calib(csi[:, :, 1, 0])
    phase3 = calib(csi[:, :, 2, 0])

    plt.figure()
    plt.plot(t, phase1[:, s_index], linewidth=0.3, label='subcarrier_15_0_0')
    plt.plot(t, phase2[:, s_index], linewidth=0.3, label='subcarrier_15_1_0')
    plt.plot(t, phase3[:, s_index], linewidth=0.3, label='subcarrier_15_2_0')
    plt.legend()
    plt.title('csi-phase')
    plt.xlabel('time(s)')
    plt.ylabel('phase')
    plt.show()


def func_4(csidata):
    csi = csidata.get_scaled_csi()

    phase1 = calib(csi[:, :, 0, 0])
    phase2 = calib(csi[:, :, 1, 0])
    phase3 = calib(csi[:, :, 2, 0])

    plt.figure(4)
    plt.plot(carriers_seq_30, np.transpose(phase1[:100]), 'r-', linewidth=0.3)
    plt.plot(carriers_seq_30, np.transpose(phase2[:100]), 'g-', linewidth=0.3)
    plt.plot(carriers_seq_30, np.transpose(phase3[:100]), 'y-', linewidth=0.3)

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


def func_6(csidata):
    csi = csidata.get_scaled_csi()

    amplitude1 = ifftshift(np.abs(ifft(np.transpose(csi[:100, :, 0, 0]), axis=0)))
    amplitude2 = ifftshift(np.abs(ifft(np.transpose(csi[:100, :, 1, 0]), axis=0)))
    amplitude3 = ifftshift(np.abs(ifft(np.transpose(csi[:100, :, 2, 0]), axis=0)))
    t = np.linspace(-15, 15, 30)

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


def func_7(csidata):
    csi = csidata.get_scaled_csi()
    phase_unwrap = np.unwrap(np.angle(csi[:100, :, 0, 0]))
    phase_unwrap_diff = np.diff(np.transpose(phase_unwrap))
    phase_unwrap_diff -= np.mean(phase_unwrap_diff, axis=0)
    phase_mean_0 = np.mean(phase_unwrap_diff, axis=-1)

    plt.figure(7)
    plt.plot(carriers_seq_30, phase_unwrap_diff, 'y+', linewidth=0.3)
    plt.plot(carriers_seq_30, phase_mean_0, 'r-', linewidth=2.0)

    patch_1 = mpatches.Patch(color='yellow', label=':100_r0t0')
    patch_2 = mpatches.Patch(color='red', label=':100_r0t0_phase_mean_0')
    plt.legend(handles=[patch_1, patch_2])

    plt.title('csi-phase_diff')
    plt.xlabel('subcarriers')
    plt.ylabel('phase_diff')
    plt.show()


def func_8(csidata):
    csi = csidata.get_scaled_csi()
    phase_unwrap = np.unwrap(np.angle(csi[:1000, :, 0, 0]))
    phase_unwrap_diff = np.diff(np.transpose(phase_unwrap))
    phase_unwrap_diff -= np.mean(phase_unwrap_diff, axis=0)

    plt.figure(8)
    plt.hist(phase_unwrap_diff[12], bins=250, histtype='stepfilled', density=False, color='red', alpha=0.5)
    plt.hist(phase_unwrap_diff[13], bins=250, histtype='stepfilled', density=False, color='green', alpha=0.5)

    patch_1 = mpatches.Patch(color='red', label=':1000_s12r0t0')
    patch_2 = mpatches.Patch(color='green', label=':1000_s13r0t0')
    plt.legend(handles=[patch_1, patch_2])

    plt.title('csi-phase_diff')
    plt.xlabel('phase_diff')
    plt.ylabel('packets count')
    plt.show()


def func_9(csidata):
    csi = csidata.get_scaled_csi()
    amplitude = np.abs(csi)
    t = csidata.timestamp_low/1000000 - csidata.timestamp_low[0]/1000000

    sos = signal.butter(2, [120], 'lowpass', fs=300, output='sos')
    sfiltered = signal.sosfilt(sos, amplitude[:, 15, :, 0])

    plt.figure(9)
    plt.plot(t[50:]-t[50], sfiltered[50:, 0], '-', linewidth=0.3, label='50:1000_s15r0t0')
    plt.plot(t[50:]-t[50], sfiltered[50:, 1], '-', linewidth=0.3, label='50:1000_s15r1t0')
    plt.plot(t[50:]-t[50], sfiltered[50:, 2], '-', linewidth=0.3, label='50:1000_s15r2t0')

    plt.legend()
    plt.title("butterworth - lowpass")
    plt.xlabel('time(s)')
    plt.ylabel('amplitude')
    plt.show()


def func_10(csidata):
    index = 15
    csi = csidata.get_scaled_csi()
    amplitude = np.abs(csi)
    t = csidata.timestamp_low/1000000 - csidata.timestamp_low[0]/1000000

    kernel = np.array([[1], [2], [3], [2], [1]]) / 9
    amplitude1 = signal.convolve(amplitude[:, index:index+1, 0, 0], kernel, mode='full')
    amplitude2 = signal.convolve(amplitude[:, index:index+1, 1, 0], kernel, mode='full')
    amplitude3 = signal.convolve(amplitude[:, index:index+1, 2, 0], kernel, mode='full')

    plt.figure()
    plt.plot(t, amplitude1[2:-2], 'r-', linewidth=0.3, label=':_s15r0t0')
    plt.plot(t, amplitude2[2:-2], 'g-', linewidth=0.3, label=':_s15r1t0')
    plt.plot(t, amplitude3[2:-2], 'y-', linewidth=0.3, label=':_s15r2t0')

    plt.legend()
    plt.title('csi amplitude conv smooth')
    plt.xlabel('time(s)')
    plt.ylabel('amplitude')
    plt.show()


def func_11(csidata):
    index = 15
    csi = csidata.get_scaled_csi()
    amplitude = np.abs(csi)
    fs = 300

    newf, newt, Sxx = signal.spectrogram(amplitude[:, index, 0, 0], fs, window=('tukey', 0.25), nfft=64, nperseg=64, noverlap=8, mode='magnitude', detrend='linear', return_onesided=False, scaling='spectrum')

    plt.figure()
    plt.pcolormesh(newt, fftshift(newf), fftshift(Sxx, axes=0), cmap='jet', antialiased=True)
    plt.show()


def func_12(csidata):
    index = 15
    csi = csidata.get_scaled_csi()
    amplitude = np.abs(csi[:, index, 0, 0])
    fs = 300

    f, Pxx_den = signal.welch(amplitude, fs, nperseg=1024)
    plt.figure()
    plt.semilogy(f, Pxx_den)
    plt.xlabel('frequency [Hz]')
    plt.ylabel('PSD [V**2/Hz]')
    plt.show()


def func_13(csidata):
    index = 15
    csi = csidata.get_scaled_csi()
    amplitude = np.abs(csi)
    fs = 300

    f, Pxx = signal.csd(amplitude[:, index, 0, 0], amplitude[:, index + 10, 0, 0], fs, nperseg=1024)
    plt.figure()
    plt.semilogy(f, np.abs(Pxx))
    plt.xlabel('frequency [Hz]')
    plt.ylabel('CSD [V**2/Hz]')
    plt.show()


helpinfo = r"""绘制图像的类型

1   CSI-时间-振幅
2   CSI-子载波-振幅
3   CSI-时间-相位
4   CSI-子载波-相位
5   时间戳-数据包-时间差

6   CSI-CIR(时间轴划分有错误，需要载波编号)
7   CSI-子载波-相邻数据包做相位差
8   CSI-直方图-相邻数据包做相位差
9   CSI振幅-巴特沃思滤波器-参数没有合理设置(test)
10  CSI振幅-卷积平滑
11  CSI振幅-频谱图(正确与否未确认)
12  CSI-功率谱密度psd-Welch(正确与否未确认)
13  CSI-csd-welch(正确与否未确认)
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('file', type=str, help='数据文件')
    parser.add_argument('-t', type=int, default=0, help=helpinfo)
    p = parser.parse_args()

    csidata = csiread.CSI(p.file, Nrxnum=3, Ntxnum=3)
    csidata.read()
    func = eval('func_' + str(p.t))
    func(csidata)
