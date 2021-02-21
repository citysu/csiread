"""Common module"""

import os

import numpy as np


def scidx(bw, ng):
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


def calib(phase, bw=20, ng=2, axis=1):
    """Phase calibration

    Note:
        phase: it must be unwrapped, it should be a 2-D, 3-D or 4-D array and
            the second dimension must be subcarriers
        bw, ng: the same as `scidx`

    ref:
        [Enabling Contactless Detection of Moving Humans with Dynamic Speeds Using CSI]
        (http://tns.thss.tsinghua.edu.cn/wifiradar/papers/QianKun-TECS2017.pdf)
    """
    p = np.asarray(phase)
    s = scidx(bw, ng)

    slice1 = [slice(None, None)] * p.ndim
    slice1[axis] = slice(-1, None)
    slice1 = tuple(slice1)
    slice2 = [slice(None, None)] * p.ndim
    slice2[axis] = slice(None, 1)
    slice2 = tuple(slice2)
    shape1 = [1] * p.ndim
    shape1[axis] = s.shape[0]
    shape1 = tuple(shape1)

    k_n, k_1 = s[-1], s[1]
    a = (p[slice1] - p[slice2]) / (k_n - k_1)
    b = p.mean(axis=axis, keepdims=True)
    s = s.reshape(shape1)

    phase_calib = p - a * s - b
    return phase_calib


def phy_ifft(x, bw=20, ng=2, axis=1):
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
    k = scidx(bw, ng)

    n = 64 * (bw / 20)
    delta_f = bw * 1e6 / n
    t = np.arange(n).reshape(-1, 1) / (bw * 1e6)

    out = (x * np.exp(1.j * 2 * np.pi * k * delta_f * t)).mean(axis=-1).swapaxes(-1, axis)
    return out


def phy_fft(x, bw=20, ng=2, axis=1):
    """802.11n FFT

    Return discrete Fourier transform of real or complex sequence.
    """
    assert bw == 20, "Only bw=20 is allowed"

    x = np.expand_dims(x.swapaxes(-1, axis), -1)
    k = scidx(bw, ng)

    n = 64 * (bw / 20)
    delta_f = bw * 1e6 / n
    t = np.arange(n).reshape(-1, 1) / (bw * 1e6)

    scale = k.size / n
    out = (x * np.exp(1.j * -2 * np.pi * k * delta_f * t)).sum(axis=-2).swapaxes(-1, axis) * scale
    return out


def infer_device(csifile):
    """Infer the CSI file format simplely

    Args:
        csifile (str): csi data file

    Returns:
        str:
            Intel: intel 5300 csi file
            Atheros: atheros csi file
            Nexmon: nexmon csi file
            AtherosPull10: `atheros pull 10 <https://github.com/xieyaxiongfly/Atheros-CSI-Tool-UserSpace-APP/pull/10/files>`_
            NexmonPull46: `nexmon_csi pull 46 <https://github.com/seemoo-lab/nexmon_csi/pull/46/files>`_
            Unknown: Unknown file format
    Note:
        This function cannot work for some nexmon csi file formats defined by
        projects derived from nexmon_csi
    """
    with open(csifile, 'rb') as f:
        buf = f.read(4)
        if buf[2] in [0xc1, 0xbb]:
            return 'Intel'
        elif buf in [b"\xa1\xb2\xc3\xd4", b"\xd4\xc3\xb2\xa1",
                     b"\xa1\xb2\x3c\x4d", b"\x4d\x3c\xb2\xa1"]:
            f.seek(20 + 16 + 42, os.SEEK_CUR)
            buf = f.read(4)
            if buf == b'\x11\x11\x11\x11':
                return 'Nexmon'
            if buf[:2] == b'\x11\x11' and buf[2:] != b'\x11\x11':
                return 'NexmonPull46'
        elif buf[0] in [0xff, 0x00]:
            return 'AtherosPull10'
        else:
            f.seek(2 + 16 - 4, os.SEEK_CUR)
            buf = f.read(1)
            if buf[0] == 56 or buf[0] == 114:
                return 'Atheros'
            else:
                return 'Unknown'


def infer_tones(csifile, device):
    """Infer the argument `tones` of Atheros and AtherosPull10
    
    Args:
        csifile (str): atheros csi file
        device (str): Atheros or AtherosPull10
    
    Returns:
        int: tones
    
    Examples:

        >>> tones = infer_tones(csifile, 'Atheros')
        >>> csidata = csiread.Atheros(csifile, nrxnum=3, ntxnum=3,
        >>>                           if_report=False, tones=tones)
    """
    with open(csifile, 'rb') as f:
        if device == "Atheros":
            f.seek(18, os.SEEK_CUR)
        elif device == 'AtherosPull10':
            f.seek(19, os.SEEK_CUR)
        else:
            raise Exception("It is not a Atheros file")
        tones = f.read(1)[0]
    return tones


def infer_chip_bw(csifile):
    """Infer chip, bandwidth and band of nexmon csi file.

    This function may be failed on some nexmon csi files.

    Args:
        csifile (str): nexmon csi file

    Returns:
        tuple (chip, bw, band):
            str: chip
            int: bw, MHz
            int: band, GHz 

    Examples:

        >>> csifile = "../material/nexmon/dataset/example.pcap"
        >>> chip, bw, band = nexchan(csifile)
        >>> csidata = csiread.Nexmon(csifile, chip=chip, bw=bw)
        >>> csidata.read()

    References:
        1. `D11AC_IOTYPES lines 172-188 <https://github.com/seemoo-lab/nexmon/blob/master/patches/include/bcmwifi_channels.h#L172>`_
    """
    csidata = csiread.Nexmon(None, 'none', 0, False, bufsize=1)
    csidata.seek(csifile, 24, 1)
    chan_spec = csidata.chan_spec[0]
    chip_version = csidata.chip_version[0]

    CHIP_LIST = {0x0065: '43455c0', 0xdead: '4358', 0xe834: '4366c0'}
    WL_CHANSPEC_BW = chan_spec & 0x3800
    WL_CHANSPEC_BAND = chan_spec & 0xc000
    if WL_CHANSPEC_BW in [0x2800, 0x3000]:
        raise Exception("csiread.Nexmon doesn't support WL_CHANSPEC_BW_160 "
                        "and WL_CHANSPEC_BW_8080")
    if WL_CHANSPEC_BAND == 255:
        raise Exception("INVCHANSPEC")

    chip = CHIP_LIST[chip_version]
    bw = (1 << (WL_CHANSPEC_BW // 0x0800)) * 5
    band = WL_CHANSPEC_BAND // 0x4000 + 2

    return chip, bw, band
