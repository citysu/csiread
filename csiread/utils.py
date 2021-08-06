import numpy as np


def scidx(bw, ng, standard='n'):
    """SubCarrier InDeX

    Table 9-54-Number of matrices and carrier grouping (in 802.11n-2016);
    Table 8-53g—Subcarriers for which a Compressed Beamforming Feedback
    Matrix subfield is sent back (in 802.11ac-2013)

    Args:
        bw (int): Bandwidth, it can be 20， 40 and 80.
        ng (int): Grouping, it can be 1, 2 and 4.
        standard (str): IEEE Std 802.11, it can be 'n' and 'ac'.

    Returns:
        ndarray: Subcarrier index

    Examples:

        >>> s_index = scidx(20, 2)

    References:
        1. `IEEE Standard for Information technology—Telecommunications and
        information exchange between systems Local and metropolitan area
        networks—Specific requirements - Part 11: Wireless LAN Medium Access
        Control (MAC) and Physical Layer (PHY) Specifications, in
        IEEE Std 802.11-2016 (Revision of IEEE Std 802.11-2012), vol., no.,
        pp.1-3534, 14 Dec. 2016, doi: 10.1109/IEEESTD.2016.7786995. <#>`_
        2. `"IEEE Standard for Information technology-- Telecommunications
        and information exchange between systemsLocal and metropolitan area
        networks-- Specific requirements--Part 11: Wireless LAN Medium Access
        Control (MAC) and Physical Layer (PHY) Specifications--Amendment 4:
        Enhancements for Very High Throughput for Operation in Bands below
        6 GHz.," in IEEE Std 802.11ac-2013 (Amendment to IEEE Std 802.11-2012,
        as amended by IEEE Std 802.11ae-2012, IEEE Std 802.11aa-2012, and IEEE
        Std 802.11ad-2012) , vol., no., pp.1-425, 18 Dec. 2013,
        doi: 10.1109/IEEESTD.2013.6687187. <#>`_
    """
    PILOT_AC = {
        20: [-21, -7, 7, 21],
        40: [-53, -25, -11, 11, 25, 53],
        80: [-103, -75, -39, -11, 11, 39, 75, 103],
        160: [-231, -203, -167, -139, -117, -89, -53, -25,
              25, 53, 89, 117, 139, 167, 203, 231]
    }
    SKIP_AC_160 = {
        1: [-129, -128, -127, 127, 128, 129],
        2: [-128, 128],
        4: []
    }
    AB = {
        20: [28, 1],
        40: [58, 2],
        80: [122, 2],
        160: [250, 6]
    }
    a, b = AB[bw]

    if standard == 'n':
        if bw not in [20, 40] or ng not in [1, 2, 4]:
            raise ValueError("bw should be [20, 40] and"
                             "ng should be [1, 2, 4]")
        k = np.r_[-a:-b:ng, -b, b:a:ng, a]
    if standard == 'ac':
        if bw not in [20, 40, 80] or ng not in [1, 2, 4]:
            raise ValueError("bw should be [20, 40, 80] and"
                             "ng should be [1, 2, 4]")
        g = np.r_[-a:-b:ng, -b]
        k = np.r_[g, -g[::-1]]
        if ng == 1:
            k = np.delete(k, np.searchsorted(k, PILOT_AC[bw]))
        if bw == 160:
            k = np.delete(k, np.searchsorted(k, SKIP_AC_160[ng]))
    return k


def calib(phase, k, axis=1):
    """Phase calibration

    Args:
        phase (ndarray): Unwrapped phase of CSI.
        k (ndarray): Subcarrier index
        axis (int): Axis along which is subcarrier. Default: 1

    Returns:
        ndarray: Phase calibrated

    Examples:

        >>> csi = csidata.csi[:10]
        >>> phase = np.unwrap(np.angle(csi), axis=1)
        >>> phase = calib(phase, k=scidx(20, 2), axis=1)

    References:
        1. `Enabling Contactless Detection of Moving Humans with Dynamic Speeds
        Using CSI <#>`_
    """
    p = np.asarray(phase)
    k = np.asarray(k)

    slice1 = [slice(None, None)] * p.ndim
    slice1[axis] = slice(-1, None)
    slice1 = tuple(slice1)
    slice2 = [slice(None, None)] * p.ndim
    slice2[axis] = slice(None, 1)
    slice2 = tuple(slice2)
    shape1 = [1] * p.ndim
    shape1[axis] = k.shape[0]
    shape1 = tuple(shape1)

    k_n, k_1 = k[-1], k[1]
    a = (p[slice1] - p[slice2]) / (k_n - k_1)
    b = p.mean(axis=axis, keepdims=True)
    k = k.reshape(shape1)

    phase_calib = p - a * k - b
    return phase_calib


def phy_ifft(x, k, axis=1):
    """PHY IFFT

    Return discrete inverse Fourier transform of real or complex sequence. It
    is based on Equation (19-25)(P2373) and Table 19-6—Timing-related
    constants(P2354) in 802.11n-2016, Table 22-5—Timing-related constants
    in 802.11ac-2013

    Args:
        x (ndarray): CSI (CFR)
        k (ndarray): Subcarriers index of ``x`` (returned by ``scidx``)
        axis (int): Axis along which is subcarrier. Default: 1

    Returns:
        ndarray: CIR

    Examples:

        >>> cfr = csidata.csi[:10]
        >>> cir = phy_ifft(cfr, k=scidx(20, 2), axis=1)

    Note:
        1. scipy.fftpack.ifft is different from Equation (19-25) and
            Equation (17-9)
        2. BE CAREFUL! I haven't found any code about CSI like this.

    References:
        1. IEEE Standard for Information technology—Telecommunications and
        information exchange between systems Local and metropolitan area
        networks—Specific requirements - Part 11: Wireless LAN Medium Access
        Control (MAC) and Physical Layer (PHY) Specifications, in IEEE Std
        802.11-2016 (Revision of IEEE Std 802.11-2012), vol., no., pp.1-3534,
        14 Dec. 2016, doi: 10.1109/IEEESTD.2016.7786995.
        2. "IEEE Standard for Information technology-- Telecommunications
        and information exchange between systemsLocal and metropolitan area
        networks-- Specific requirements--Part 11: Wireless LAN Medium Access
        Control (MAC) and Physical Layer (PHY) Specifications--Amendment 4:
        Enhancements for Very High Throughput for Operation in Bands below
        6 GHz.," in IEEE Std 802.11ac-2013 (Amendment to IEEE Std 802.11-2012,
        as amended by IEEE Std 802.11ae-2012, IEEE Std 802.11aa-2012, and IEEE
        Std 802.11ad-2012) , vol., no., pp.1-425, 18 Dec. 2013,
        doi: 10.1109/IEEESTD.2013.6687187.
    """
    M = x.shape[axis]
    x = x.swapaxes(-1, axis)
    k = np.asarray(k)
    bw = np.around(k[-1] / 30) * 20

    n = 64 * (bw / 20)
    delta_f = bw * 1e6 / n
    t = np.c_[:n] / (bw * 1e6)

    g = np.exp(2.j * np.pi * k * delta_f * t) / M
    out = x @ g.T

    out = out.swapaxes(-1, axis)
    return out


def phy_fft(x, k, axis=1):
    """PHY FFT

    Return discrete Fourier transform of real or complex sequence. See Also:
    ``phy_ifft``

    Args:
        x (ndarray): CSI (CIR)
        k (ndarray): Subcarriers index of ``x`` (returned by ``scidx``)
        axis (int): Axis along which is subcarrier. Default: 1

    Returns:
        ndarray: CFR
    """
    x = x.swapaxes(-1, axis)
    k = np.asarray(k)
    bw = np.around(k[-1] / 30) * 20

    n = 64 * (bw / 20)
    delta_f = bw * 1e6 / n
    t = np.c_[:n] / (bw * 1e6)

    g = np.exp(-2.j * np.pi * k * delta_f * t)
    out = x @ g

    scale = k.size / n
    out = out.swapaxes(-1, axis) * scale
    return out
