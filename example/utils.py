"""Common module"""


import numpy as np


def get_subcarriers_index(bw, ng):
    """subcarriers index

    Args:
        bw: bandwitdh(20, 40)
        ng: grouping(1, 2, 4)
    """
    if bw not in [20, 40] or ng not in [1, 2, 4]:
        raise ValueError("bw should be [20, 40] and ng should be [1, 2, 4]")
    a, b = int(bw * 1.5 - 2), int(bw / 20)
    k = np.r_[range(-a, -b, ng), -b, range(b, a, ng), a]
    return k


def calib(phase, bw=20, ng=2):
    """Phase calibration

    Note:
        phase: it must be unwrapped, it should be a 2-D, 3-D or 4-D array and
            the second dimension must be subcarriers
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


def phy_ifft(x, axis=0, bw=20, ng=2):
    """802.11n IFFT

    Return discrete inverse Fourier transform of real or complex sequence. It
    is based on Equation (19-25)(P2373)

    Note:
        1. No ifftshift
        2. scipy.fftpack.ifft is different from Equation (19-25) and Equation (17-9)
        3. BE CAREFUL! I haven't found any code about CSI like this.

    Ref:
        IEEE Standard for Information technology—Telecommunications and information
        exchange between systems Local and metropolitan area networks—Specific 
        requirements - Part 11: Wireless LAN Medium Access Control (MAC) and Physical
        Layer (PHY) Specifications, in IEEE Std 802.11-2016 (Revision of IEEE Std
        802.11-2012), vol., no., pp.1-3534, 14 Dec. 2016, doi: 10.1109/IEEESTD.2016.7786995.
    """
    assert bw == 20, "Only bw=20 is allowed"

    x = np.expand_dims(x.swapaxes(-1, axis), -2)
    k = get_subcarriers_index(bw, ng)

    n = 64 * (bw / 20)
    delta_f = bw * 1e6 / n
    t = np.arange(n).reshape(-1, 1) / (bw * 1e6)

    out = (x * np.exp(1.j * 2 * np.pi * k * delta_f * t)).mean(axis=-1).swapaxes(-1, axis)
    return out


def phy_fft(x, axis=0, bw=20, ng=2):
    """802.11n FFT

    Return discrete Fourier transform of real or complex sequence.
    """
    assert bw == 20, "Only bw=20 is allowed"

    x = np.expand_dims(x.swapaxes(-1, axis), -1)
    k = get_subcarriers_index(bw, ng)

    n = 64 * (bw / 20)
    delta_f = bw * 1e6 / n
    t = np.arange(n).reshape(-1, 1) / (bw * 1e6)

    scale = k.size / n
    out = (x * np.exp(1.j * -2 * np.pi * k * delta_f * t)).sum(axis=-2).swapaxes(-1, axis) * scale
    return out


def check_device(csifile):
    """Check the file type simplely"""
    with open(csifile, 'rb') as f:
        buf = f.read(4)
        if buf[2] in [0xc1, 0xbb]:
            return 'Intel'
        elif buf in [b"\xa1\xb2\xc3\xd4", b"\xd4\xc3\xb2\xa1",
                     b"\xa1\xb2\x3c\x4d", b"\x4d\x3c\xb2\xa1"]:
            return 'Nexmon'
        else:
            return 'Atheros'
