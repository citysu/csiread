#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""WiDar3.0

Usage:
    python3 csiWiDar3.py

Important:
    I failed to get BVP with `scipy.optimize.minimize` and `cvxpy`.

Note:
    I tested the code with the sample dataset of WiDar3.0.

Ref:
    1. WiDar3.0: [Widar3.0: Zero-Effort Cross-Domain Gesture Recognition With Wi-Fi](http://tns.thss.tsinghua.edu.cn/widar3.0/data/MobiSys19_Widar3.0_paper.pdf)
    2. [BVPExtractionCode.zip](https://ieee-dataport.org/open-access/widar-30-wifi-based-activity-recognition-dataset)
    3. [Tsinghua Disk/BVPExtractionCode/Widar3.0Release-Matlab/Data/*](http://tns.thss.tsinghua.edu.cn/widar3.0/)
"""

from os import listdir
from os.path import dirname, join
from timeit import default_timer

import csiread
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as signal
from scipy.fftpack import fftshift
from scipy.optimize import Bounds, minimize
from skimage.transform import rotate


class Config:
    """Segment Settings"""
    norm = 0
    lamb = 1e-7
    sample_rate = 1000
    pos_tx = np.array([[0, 0]])
    pos_rx = np.array([[0.455, -0.455], [1.365, -0.455], [2.000, 0.000],
                       [-0.455, 0.455], [-0.455, 1.365], [0.000, 2.000]])
    ori_torso = np.array([-90, -45, 0, 45, 90])
    pos_torso = np.array([[1.365, 0.455], [0.455, 0.455],
                          [0.455, 1.365], [1.365, 1.365],
                          [0.910, 0.910], [2.275, 1.365],
                          [2.275, 2.275], [1.365, 2.275]])
    ori_select = 0
    pos_select = 0
    v_min = -2
    v_max = 2
    v_bin = 20  # M is V_BIN
    v_resolution = (v_max - v_min) / v_bin
    wave_length = 299792458 / 5.825e9
    t_stop = 1400
    segment_length = 100
    segment_number = t_stop // segment_length


def loadcsi(csifile):
    csidata = csiread.Intel(csifile, if_report=False)
    csidata.read()
    csi = csidata.get_scaled_csi_sm(True)[:, :, :, :1]
    tpl = np.diff(csidata.timestamp_low).view(np.int32)
    rate = np.floor(1e6 / tpl.mean())
    return csi, rate


def prepare_dataset(root):
    """generate_vs.m

    Args:
        root: the dataset root

    Note:
        widar3/
        ├── bvp
        │   └── (empty)
        └── csi
            ├── userA-1-1-1-1-r1.dat
            ├── userA-1-1-1-1-r2.dat
            ├── userA-1-1-1-1-r3.dat
            ├── userA-1-1-1-1-r4.dat
            ├── userA-1-1-1-1-r5.dat
            └── userA-1-1-1-1-r6.dat

    Returns:
        list: several csi files consist a group, groups consist our dataset.
    """
    csi_root = join(root, 'csi')
    csifiles = [join(csi_root, file) for file in listdir(csi_root)]
    csifiles.sort()
    dataset = [csifiles]
    return dataset


def get_doppler(csi, rate=1000):
    """get_doppler_spectrum

    Args:
        csi: csidata.csi[:, :, :, :1]
        rate: sample rate
    """
    # Filter Configuration
    half_rate = rate / 2
    upper_order, upper_stop = 6, 60
    lower_order, lower_stop = 3, 2
    lb, la = signal.butter(upper_order, upper_stop / half_rate, 'lowpass')
    hb, ha = signal.butter(lower_order, lower_stop / half_rate, 'highpass')

    # Select Antenna Pair[WiDance]
    amp = np.abs(csi)
    csi_mean = amp.mean(axis=0)
    csi_var = amp.var(axis=0)
    csi_mean_var_ratio = csi_mean / csi_var
    idx = csi_mean_var_ratio.mean(axis=0).argmax(axis=0)
    csi_ref = csi[..., idx, :]

    # Amp Adjust[IndoTrack]
    alpha = amp.min(axis=0)
    beta = 1e3 * alpha.sum() / np.prod(csi.shape[1:])
    csi_adj = (amp - alpha) * np.exp(1.j * np.angle(csi))
    csi_ref_adj = (np.abs(csi_ref) + beta) * np.exp(1.j * np.angle(csi_ref))

    # Conj Mult
    conj_mult = csi_adj * csi_ref_adj.conj()
    conj_mult = np.delete(conj_mult, idx, axis=-2)

    # Filter Out Static Component & High Frequency Component
    conj_mult = signal.lfilter(lb, la, conj_mult, axis=0)
    conj_mult = signal.lfilter(hb, ha, conj_mult, axis=0)

    # PCA analysis.
    # `sklearn.decomposition.PCA` doesn't support complex type.
    conj_mult = conj_mult.transpose(0, 2, 3, 1)             # optional
    conj_mult = conj_mult.reshape(conj_mult.shape[0], -1)
    pca_coef = pca(conj_mult, 1)
    conj_mult = conj_mult @ pca_coef

    # CWT (unimplemented)
    # I failed to run the code: `get_doppler_spectrum.m, line76`. Where are
    # `frq2scal` and `scaled_cwt` ?

    # STFT
    index = 0
    f, t, s = signal.stft(conj_mult[:, index], rate, nfft=1000,
                          window=('gaussian', 32), nperseg=128,
                          noverlap=127, axis=0, return_onesided=False)
    s *= s.conj()
    f = fftshift(f)     # Cyclic Doppler Spectrum According To frequency bin
    s = fftshift(np.abs(s) / np.abs(s).sum(axis=0), axes=0)

    # Select
    mask = np.abs(f) <= upper_stop
    f, s = f[mask], s[mask]

    return f, t, s


def get_matrix_a(pos_torso, pos_tx, pos_rx):
    """get_A_matrix.m: cos(theta)"""
    d_torso_tx = np.linalg.norm(pos_torso - pos_tx, axis=-1, keepdims=True)
    d_torso_rx = np.linalg.norm(pos_torso - pos_rx, axis=-1, keepdims=True)
    a = (pos_torso - pos_tx) / d_torso_tx + (pos_torso - pos_rx) / d_torso_rx
    return a


def get_matrix_vdm(a, wl, vv, ff):
    """get_velocity2doppler_mapping_matrix.m (faster)"""
    vdm = np.ones([len(vv), len(vv), len(a), len(ff)])
    a = a[None, None, :, None, :]
    v = np.stack(np.meshgrid(vv, vv)[::-1], -1)[..., None, :, None].conj()
    p = (a @ v / wl).round().squeeze()
    vdm[np.logical_or(p > ff.max(), p < ff.min()), :] = 1e10
    return vdm


def vdm_target_func(p, vdm, lam, ss_segment_mean, norm):
    """DVM_target_func.m"""
    V_BIN, F_BIN = vdm.shape[0], vdm.shape[3]

    # Construct Approximation Doppler Spectrum
    p = p.reshape(V_BIN, V_BIN)     # minimize will flatten p, recover it
    ss_segment_approximate = (p[..., None, None] * vdm).sum((0, 1))

    # EMD Distance
    mask = np.any(ss_segment_mean, axis=1)
    temp = (ss_segment_approximate - ss_segment_mean)[mask, :]
    floss = np.abs(temp @ np.triu(np.ones([F_BIN, F_BIN]))).sum()

    # Norm Loss, parameter: norm may be redundant.
    # floss += lam * p.sum()

    return floss


def optimize(vdm, target, lam, norm, lb, ub):
    last = default_timer()
    res = minimize(fun=vdm_target_func,
                   x0=np.zeros_like(ub).flatten(),
                   args=(vdm, lam, target, norm),
                   method='SLSQP',
                   bounds=Bounds(lb.flatten(), ub.flatten()),
                   options={'disp': True})
    print('\t    time cost: %4.4fs' % (default_timer() - last))
    return res.x.reshape(vdm.shape[0], vdm.shape[1])


def main(csifiles, show_doppler=False):
    """DVM_main.m"""
    cfg = Config()

    # Generate Doppler Spectrum
    spectrum = list()
    for csifile in csifiles:
        csi, _ = loadcsi(csifile)
        f, t, s = get_doppler(csi, cfg.sample_rate)
        spectrum.append(s[:, :cfg.t_stop])
    ff, tt, ss = f, t[:cfg.t_stop], np.asarray(spectrum)
    vv = np.linspace(cfg.v_min, cfg.v_max, cfg.v_bin + 1)[1:]

    # Display Doopler
    if show_doppler:
        for i in range(ss.shape[0]):
            plot_spectrum(ff, tt, ss[i], display=False)
        plt.show()

    # For Each Segment Do Mapping (Ready)
    u_bound = np.ones([cfg.v_bin, cfg.v_bin]) * ss.max()
    l_bound = np.zeros_like(u_bound)
    a = get_matrix_a(cfg.pos_torso[cfg.pos_select:cfg.pos_select+1],
                     cfg.pos_tx, cfg.pos_rx)
    vdm = get_matrix_vdm(a, cfg.wave_length, vv, ff)

    # Do Mapping
    bvp = np.empty([cfg.v_bin, cfg.v_bin, cfg.segment_number])
    for i in range(bvp.shape[-1]):
        # Set-up fmincon Input
        ss_segment = ss[..., i*cfg.segment_length:(i+1)*cfg.segment_length]
        ss_segment_mean = ss_segment.mean(-1)

        # Normalization Between Receivers(Compensate Path-Loss)
        mask = np.any(ss_segment_mean, axis=1)
        scale = ss_segment_mean[0].sum() / ss_segment_mean.sum(1)[mask]
        ss_segment_mean[mask, :] *= scale[:, None]

        # Notice: The following section is incorrect!

        # Apply fmincon Solver
        print("segments: %d/%d" % (i + 1, cfg.segment_number))
        bvp[..., i] = optimize(vdm, ss_segment_mean, cfg.lamb, cfg.norm, l_bound, u_bound)

    # Rotate Velocity Spectrum According to Orientation
    bvp = rotate(bvp, cfg.ori_torso[cfg.ori_select], order=0)     # get_rotated_spectrum

    # Save VS
    bvp_file = join(dirname(dirname(csifiles[0])), 'bvp', 'bvp.npy')
    np.save(bvp_file, bvp)


# Helper - PCA


def sign(x):
    """Returns an element-wise indication of the sign of a number.

    Ref:
        1. https://numpy.org/doc/stable/reference/generated/numpy.sign.html
        2. MATLAB/R2020b/toolbox/matlab/elfun/sign.m
    """
    return x / np.abs(x)


def svd_flip(u, v, u_based_decision=True):
    """Sign correction to ensure deterministic output from SVD.

    Note:
        - This function is copied from `sklearn.utils.extmath.svd_flip`. We
        only replaced `np.sign` with `sign` defined above.
        - This function corresponds to Line429-434 in pca.m (MATLAB R2020b)
    """
    if u_based_decision:
        # columns of u, rows of v
        max_abs_cols = np.argmax(np.abs(u), axis=0)
        signs = sign(u[max_abs_cols, range(u.shape[1])])
        u *= signs
        v *= signs[:, np.newaxis]
    else:
        # rows of v, columns of u
        max_abs_rows = np.argmax(np.abs(v), axis=1)
        signs = sign(v[range(v.shape[0]), max_abs_rows])
        u *= signs
        v *= signs[:, np.newaxis]
    return u, v


def pca(x, n_components):
    """PCA using Singular Value Decomposition

    Args:
        n_components (int): Number of components to keep.

    Returns:
        components_ (ndarray): principal component coefficients
    """
    x -= x.mean(0)
    U, S, V = np.linalg.svd(x, full_matrices=False)
    U, V = svd_flip(U, V, False)
    components_ = V[:, :n_components]
    return components_


# Helper - Other implementations


def get_matrix_vdm_origin(a, wl, vv, ff):
    """get_velocity2doppler_mapping_matrix.m (origin version)"""
    ff_max, ff_min, ff_len = ff.max(), ff.min(), len(ff)
    rx_cnt, v_len = len(a), len(vv)
    vdm = np.zeros([rx_cnt, v_len, v_len, ff_len])

    for i in range(rx_cnt):
        for j in range(v_len):
            for k in range(v_len):
                p = np.round(a[i] @ np.c_[vv[j], vv[k]].T.conj() / wl)
                if ff_min > p or ff_max < p:
                    vdm[i, j, k] = 1e10
                    continue
                idx = int(p - ff_min)
                vdm[i, j, k, idx] = 1
    vdm = vdm.transpose(1, 2, 0, 3)
    return vdm


def optimize_cvx(vdm, target, lam, norm, lb, ub):
    import cvxpy as cp
    V_BIN, _, NRX, F_BIN = vdm.shape
    vdm = vdm.reshape(V_BIN * V_BIN, NRX * F_BIN)

    x = cp.Variable((V_BIN, V_BIN))
    y = cp.multiply(cp.reshape(x, (V_BIN * V_BIN, 1)), vdm)
    y = cp.reshape(cp.sum(y, axis=0), (NRX, F_BIN))
    z = cp.sum(cp.abs(y - target) @ np.triu(np.ones([F_BIN, F_BIN])))
    obj = cp.Minimize(z)
    cons = [x >= lb, x <= ub]

    prob = cp.Problem(obj, cons)
    prob.solve()
    print(prob.status, prob.value)
    return x.value


# Helper - Plot


def plot_spectrum(f, t, s, method='imshow', display=True):
    fig = plt.figure()
    if method == 'pcolormesh':
        plt.pcolormesh(t, f, s, cmap='jet', antialiased=True,
                       shading='gouraud')
    elif method == 'line':
        plt.imshow(s, cmap='jet', aspect='auto', origin='lower',
                   extent=(0, t[-1], f[0], f[-1]), alpha=0.382)
        pos = (np.argmax(s, axis=0) - (len(f) / 2)) * (f[-1] - f[0]) / len(f)
        pos = signal.savgol_filter(pos, 65, 1, mode='interp')
        plt.plot(t, pos, 'b--', linewidth=2)
    elif method == 'mesh3d':
        ax = fig.add_subplot(111, projection='3d')
        ax.view_init(elev=45., azim=255)
        t = t[:1000]
        x = np.arange(len(t))
        y = np.arange(len(f))
        x, y = np.meshgrid(x, y)
        z = s[y, x]
        mesh3d = ax.plot_surface(t, f[y], z, cmap='jet', antialiased=True)
        fig.colorbar(mesh3d, shrink=0.5, aspect=10)
    else:
        plt.imshow(s, cmap='jet', aspect='auto', origin='lower',
                   extent=(0, t[-1], f[0], f[-1]))
    plt.title('Doppler Shift')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.grid()
    plt.tight_layout()
    if display:
        plt.show()


def plot_doppler(csifile):
    csi, rate = loadcsi(csifile)
    f, t, s = get_doppler(csi, rate)
    plot_spectrum(f, t, s, 'imshow', display=True)


def plot_bvp(csifiles):
    V_MIN, V_MAX, V_BIN = -2, 2, 20

    bvp_file = join(dirname(dirname(csifiles[0])), 'bvp', 'bvp.npy')
    s = np.load(bvp_file)
    v_bin = np.linspace(V_MIN, V_MAX, V_BIN + 1)[1:]

    for i in range(s.shape[-1]):
        print('segments: %d/%d' % (i + 1, s.shape[-1]), end='', flush=True)
        plot_spectrum(v_bin, v_bin, s[..., i], 'mesh3d', display=False)
        plt.title('Velocity spectrum')
        plt.xlabel('Velocity-X [m/s]')
        plt.ylabel('Velocity-Y [m/s]')
        plt.show()
        print('\b'*20, end='')


if __name__ == '__main__':
    # dataset = prepare_dataset('widar3')
    # main(dataset[0], show_doppler=True)
    # plot_bvp(dataset[0])

    plot_doppler('../material/5300/dataset/sample_0x5_64_3000.dat')
