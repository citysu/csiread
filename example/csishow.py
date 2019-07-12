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
    """Phase calibration

    ref: [Enabling Contactless Detection of Moving Humans with Dynamic Speeds
    Using CSI](http://tns.thss.tsinghua.edu.cn/wifiradar/papers/QianKun-TECS2017.pdf)
    """
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


helpinfo = r"""绘制图像的类型

1   CSI-时间-振幅
2   CSI-子载波-振幅
3   CSI-时间-相位
4   CSI-子载波-相位
5   时间戳-数据包-时间差
"""

others = r"""功能不完善，可能存在错误。

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
    """example
    
    python3 csishow.py ../material/5300/dataset/sample_0x1_ap.dat -t 1
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('file', type=str, help='data file')
    parser.add_argument('-t', type=int, default=0, help=helpinfo)
    p = parser.parse_args()

    csidata = csiread.CSI(p.file, Nrxnum=3, Ntxnum=3)
    csidata.read()
    if p.t > 5 :
        raise ValueError('the value of t can be 1, 2, 3, 4, 5')
    func = eval('func_' + str(p.t))
    func(csidata)
