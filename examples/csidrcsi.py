#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Drcsi: `Decimeter Ranging with Channel State Information`

Usage:
    python3 csiDrcsi.py

Important:
    1. alg_3: it's not implemented. I can't understand *Algorithm 3 CFO + Weak Stream Removal*.
    2. alg_2: Is N_sto right?

Note:
    no dataset available

Ref:
    Drcsi: [Decimeter Ranging with Channel State Information](https://arxiv.org/pdf/1902.09652.pdf)
"""

import csiread
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.fftpack import fft, ifft, fftshift, ifftshift
from scipy.signal import find_peaks
from scipy.stats import mode
from utils import scidx, calib, phy_ifft, phy_fft


def fig_2(csidata, index=34):
    """fig_2

    Note:
        Fig. 2a uses data collected from a setup where transmitter and receiver arrays
        directly face each other whereas, in Fig. 2b, the receiver is rotated by 90 degrees

    Ref:
        [Power Delay Profile](https://www.gaussianwaves.com/2014/07/power-delay-profile/)
        [From Channel Impulse Response (CIR) to Power Delay Profile (PDP)](https://www.mathworks.com/matlabcentral/answers/44530-from-channel-impulse-response-cir-to-power-delay-profile-pdp)
    """
    csi = csidata.csi

    pdp = np.power(np.abs(phy_ifft(csi, scidx(20, 2), axis=1)), 2.0) / csi.shape[1]
    norm = lambda x: x / np.max(x)

    plt.figure()
    plt.plot(norm(pdp[index, :12].reshape(12, -1)))
    plt.title('Anechoic Chamber: $N_{SS}=%d$' % (sum(csi[index, 0, 0] != 0)))
    plt.xlabel('sample index')
    plt.ylabel('PDP')
    plt.tight_layout()
    plt.show()


def fig_4(athdata, index=26):
    """fig_4

    Ref:
        [FFT Length (802.11n/ac/ax)](http://rfmw.em.keysight.com/wireless/helpfiles/89600B/WebHelp/Subsystems/wlan-mimo/Content/mimo_adv_fftsze.htm)
    """
    csi = athdata.csi

    # Fig.4(a)
    phase = np.unwrap(np.angle(csi), axis=1)
    phase = calib(phase, scidx(20, 1))
    plt.subplot(3, 1, 1)
    plt.plot(phase[index].reshape(csi.shape[1], -1))

    # Fig.4(b)
    amplidute = 10 * np.log10(np.abs(csi) + 1 / 10 ** 6)    # db
    plt.subplot(3, 1, 2)
    plt.plot(amplidute[index].reshape(csi.shape[1], -1))

    # Fig.4(c)
    # scipy.fftpack.fft or phy_fft ?
    A = np.log10(np.abs(fft(csi, n=64, axis=1)))
    plt.subplot(3, 1, 3)
    plt.plot(A[index].reshape(64, -1), '*--')

    plt.tight_layout()
    plt.show()


def fig_6(csidata):
    """fig_6"""
    csi = csidata.csi
    s_index = scidx(20, 2)

    phase = np.unwrap(np.angle(csi[:1000, :, 0, 0])).T
    phase_diff = np.diff(phase)
    phase_diff -= phase_diff.mean(axis=0)
    phase_mean_0 = phase_diff.mean(axis=-1)

    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(s_index, phase_diff, 'y+', linewidth=0.3)
    plt.plot(s_index, phase_mean_0, 'r-', linewidth=2.0)
    patch_1 = mpatches.Patch(color='yellow', label=':1000_r0t0')
    patch_2 = mpatches.Patch(color='red', label=':1000_r0t0_phase_mean_0')
    plt.legend(handles=[patch_1, patch_2])
    plt.title('fig6b: csi-phase_diff')
    plt.xlabel('subcarriers')
    plt.ylabel('phase_diff')

    plt.subplot(2, 1, 2)
    plt.hist(phase_diff[12], bins=250, histtype='stepfilled', density=False, color='red', alpha=0.5)
    plt.hist(phase_diff[13], bins=250, histtype='stepfilled', density=False, color='green', alpha=0.5)
    patch_1 = mpatches.Patch(color='red', label=':1000_s12r0t0')
    patch_2 = mpatches.Patch(color='green', label=':1000_s13r0t0')
    plt.legend(handles=[patch_1, patch_2])
    plt.title('fig6c: csi-phase_diff')
    plt.xlabel('phase_diff')
    plt.ylabel('packets count')
    plt.tight_layout()
    plt.show()


def formula_14(csi, Nrx=0, Ntx=0):
    """formula_14"""
    return - np.angle(np.mean(csi[:, :-1, Nrx, Ntx] * csi[:, 1:, Nrx, Ntx].conj(), axis=1))


def formula_15(csi):
    """formula_15"""
    return - np.angle(np.mean(csi[:, :-1] * csi[:, 1:].conj(), axis=(1, 2, 3)))


def formula_16(csi):
    """formula_16"""
    k = scidx(20, 2)[:, np.newaxis, np.newaxis]
    phi = formula_15(csi)[:, np.newaxis, np.newaxis, np.newaxis]
    return np.exp(1j * phi * k) * csi


def derotate_linear(csi, bw=20, ng=2):
    """Windowing/CP removal effect compensation"""
    k = scidx(bw, ng)[:, np.newaxis, np.newaxis]
    phi = -7e-5 * k ** 3 + 3e-5 * k ** 2 + 0.05 * k
    return np.exp(-1j * phi) * csi


def derotate_formual16(csi, phi, bw=20, ng=2):
    """De-rotate CSI phase using (16)"""
    k = scidx(bw, ng)[:, np.newaxis, np.newaxis]
    phi = phi[:, np.newaxis, np.newaxis, np.newaxis]
    return np.exp(1j * phi * k) * csi


def alg_1(csi):
    """alg_1"""
    csi = derotate_linear(csi)
    phi = formula_15(csi)
    csi = derotate_formual16(csi, phi)
    return csi


def alg_2(csi):
    """alg_2

    Note: N_p = 1
    """

    p = np.power(np.abs(phy_ifft(csi, scidx(20, 2), axis=1)), 2.0)
    # find_peak() is better
    s = p[:, :20].argmax(axis=1).reshape(csi.shape[0], -1)
    N_sto = scidx(20, 2)[mode(s, axis=1)[0][:, 0]]
    N_sc = 64
    csi = derotate_formual16(csi, -2 * np.pi * N_sto / N_sc)
    return csi


def alg_3(csi, index):
    """alg_3"""
    pass
    # P = 1
    # Np = 10
    # for i in range(Np):
    #     P *= csi[index+i]
    # ret = np.power(P, 1 / Np)

    # R = np.linalg.norm(ret)
    # for jrx in range(csi.shape[2]):
    #     for jss in range(csi.shape[3]):
    #         for k in range(csi.shape[1]):
    #             if np.linalg.norm(ret[k, jrx, jss]) / R < 0.1:
    #                 ret[k, jrx, jss] = np.nan

    # return ret


def algshow(csidata):
    s_index = scidx(20, 2)
    csi = csidata.csi[:500]

    plt.figure()
    
    # alg_1
    csi = alg_1(csi)
    phase = np.unwrap(np.angle(csi), axis=1)
    phase = calib(phase, s_index)
    plt.subplot(3, 1, 1)
    plt.plot(s_index, phase[200:300, :, 0, 0].T)

    # alg_2
    csi = alg_2(csi)
    phase = np.unwrap(np.angle(csi), axis=1)
    phase = calib(phase, s_index)
    plt.subplot(3, 1, 2)
    plt.plot(s_index, phase[200:300, :, 0, 0].T)

    # alg_3
    # csicopy = csi.copy()
    # for i in range(100, 200):
    #     csicopy[i] = alg_3(csi, i)
    # phase = np.unwrap(np.angle(csicopy), axis=1)
    # phase = calib(phase, s_index)
    # plt.subplot(3, 1, 3)
    # plt.plot(s_index, phase[100:200, :, 0, 0].T)
    plt.show()


if __name__ == "__main__":
    csidata = csiread.Intel("../material/5300/dataset/sample_0x5_64_3000.dat", ntxnum=1, if_report=False)
    athdata = csiread.Atheros("../material/atheros/dataset/ath_csi_1.dat", if_report=False)
    csidata.read();csidata.get_scaled_csi(True)
    athdata.read()

    fig_2(csidata)
    fig_4(athdata)
    fig_6(csidata)
    # algshow(csidata)
