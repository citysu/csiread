#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Calculate effective SNR based on CSI(Linux 802.11n CSI Tool)

Ref: [Predictable 802.11 Packet Delivery from Wireless Channel Measurements]
    (https://www.halper.in/pubs/comm356s-halperin.pdf) and [linux-80211n-csitool-supplementary]
    (https://github.com/dhalperi/linux-80211n-csitool-supplementary)
"""


import csiread
import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import inv
from scipy.special import erfc, erfcinv


def dbinv(x):
    return np.power(10, x/10)


def db(x):
    return 10 * np.log10(x)


def qfunc(x):
    return 0.5 * erfc(x/np.sqrt(2))


def qfuncinv(x):
    return np.sqrt(2) * erfcinv(2*x)


def bpsk_ber(snr):
    return qfunc(np.sqrt(2*snr))


def bpsk_berinv(ber):
    return np.power(qfuncinv(ber), 2.0) / 2


def qam16_ber(snr):
    return 3/4 * qfunc(np.sqrt(snr/5))


def qam16_berinv(ber):
    return np.power(qfuncinv(ber * 4/3), 2.0) * 5


def qam64_ber(snr):
    return 7/12*qfunc(np.sqrt(snr/21))


def qam64_berinv(ber):
    return np.power(qfuncinv(ber * 12/7), 2.0) * 21


def qpsk_ber(snr):
    return qfunc(np.sqrt(snr))


def qpsk_berinv(ber):
    return np.power(qfuncinv(ber), 2.0)


def mimo2_mmse(csi):
    """csi.shape = (Ntx(2), Nrx)"""
    M = inv(np.dot(csi.T.conjugate(), csi) + np.eye(2))
    ret = 1 / np.diag(M) - 1
    return ret.real


def mimo3_mmse(csi):
    """csi.shape = (Ntx(3), Nrx)"""
    M = inv(np.dot(csi.T.conjugate(), csi) + np.eye(3))
    ret = 1 / np.diag(M) - 1
    return ret.real


def get_simo_SNRs(csi):

    return np.sum(csi * csi.conjugate(), axis=(1), keepdims=True).real


def get_mimo2_SNRs(csi):
    S, N, M = csi.shape
    csi = csi / np.sqrt(2.0)
    if M == 2:
        ret = np.zeros([S, 2, 1])
        for i in range(S):
            ret[i, :, 0] = mimo2_mmse(csi[i])
        return ret

    ret = np.zeros([S, 2, 3])
    for i in range(S):
        ret[i, :, 0] = mimo2_mmse(csi[i, :, 0:2])
        ret[i, :, 1] = mimo2_mmse(csi[i, :, 0:3:2])
        ret[i, :, 2] = mimo2_mmse(csi[i, :, 1:3])
    return ret


def get_mimo3_SNRs(csi):
    S, N, M = csi.shape
    csi = csi / np.sqrt(dbinv(4.5))

    ret = np.zeros([S, 3, 1])
    for i in range(S):
        ret[i, :, 0] = mimo3_mmse(csi[i])
    return ret


def get_eff_SNRs(csi, csi_sm=None):
    """get_eff_SNRs

    When csi_sm is given, this function is get_eff_SNRs_sm.
    """
    if len(csi.shape) == 3:
        csi = np.array([csi])

    L, S, N, M = csi.shape
    ret = np.zeros([L, 7, 4])

    k = min(M, N)
    if k >= 1:
        for j in range(L):
            snrs = get_simo_SNRs(csi[j])
            bers = bpsk_ber(snrs)
            mean_ber = np.mean(bers, axis=(0, 1))
            ret[j, :len(mean_ber), 0] = bpsk_berinv(mean_ber)

            bers = qpsk_ber(snrs)
            mean_ber = np.mean(bers, axis=(0, 1))
            ret[j, :len(mean_ber), 1] = qpsk_berinv(mean_ber)

            bers = qam16_ber(snrs)
            mean_ber = np.mean(bers, axis=(0, 1))
            ret[j, :len(mean_ber), 2] = qam16_berinv(mean_ber)

            bers = qam64_ber(snrs)
            mean_ber = np.mean(bers, axis=(0, 1))
            ret[j, :len(mean_ber), 3] = qam64_berinv(mean_ber)

    if csi_sm is not None:
        csi = np.array([csi_sm]) if len(csi_sm.shape) == 3 else csi_sm

    if k >= 2:
        for j in range(L):
            snrs = get_mimo2_SNRs(csi[j])

            bers = bpsk_ber(snrs)
            mean_ber = np.mean(bers, axis=(0, 1))
            ret[j, 3:3+len(mean_ber), 0] = bpsk_berinv(mean_ber)

            bers = qpsk_ber(snrs)
            mean_ber = np.mean(bers, axis=(0, 1))
            ret[j, 3:3+len(mean_ber), 1] = qpsk_berinv(mean_ber)

            bers = qam16_ber(snrs)
            mean_ber = np.mean(bers, axis=(0, 1))
            ret[j, 3:3+len(mean_ber), 2] = qam16_berinv(mean_ber)

            bers = qam64_ber(snrs)
            mean_ber = np.mean(bers, axis=(0, 1))
            ret[j, 3:3+len(mean_ber), 3] = qam64_berinv(mean_ber)

    if k >= 3:
        for j in range(L):
            snrs = get_mimo3_SNRs(csi[j])

            bers = bpsk_ber(snrs)
            mean_ber = np.mean(bers, axis=(0, 1))
            ret[j, 6:6+len(mean_ber), 0] = bpsk_berinv(mean_ber)

            bers = qpsk_ber(snrs)
            mean_ber = np.mean(bers, axis=(0, 1))
            ret[j, 6:6+len(mean_ber), 1] = qpsk_berinv(mean_ber)

            bers = qam16_ber(snrs)
            mean_ber = np.mean(bers, axis=(0, 1))
            ret[j, 6:6+len(mean_ber), 2] = qam16_berinv(mean_ber)

            bers = qam64_ber(snrs)
            mean_ber = np.mean(bers, axis=(0, 1))
            ret[j, 6:6+len(mean_ber), 3] = qam64_berinv(mean_ber)
    ret[ret == np.Inf] = dbinv(40)
    return ret


def main():
    csidata = csiread.Intel('../material/5300/dataset/sample_0x5_64_3000.dat')
    csidata.read()
    scaled_csi = csidata.get_scaled_csi()
    preNrx = max(csidata.Nrx)
    preNtx = max(csidata.Ntx)
    if max(csidata.Nrx) != min(csidata.Nrx):
        print('be careful')
        preNrx = 3  # set by yourself
        scaled_csi = scaled_csi[csidata.Nrx == preNrx]
    if max(csidata.Ntx) != min(csidata.Ntx):
        print('be careful')
        preNtx = 2  # set by yourself
        scaled_csi = scaled_csi[csidata.Ntx == preNtx]
    scaled_csi = scaled_csi[:100, :, :preNrx, :preNtx]
    ret = get_eff_SNRs(scaled_csi)
    print(ret[0])
    plt.figure()
    plt.plot(ret[:, 0, :])
    plt.show()


if __name__ == "__main__":
    main()
