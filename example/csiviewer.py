#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CSI viewer: Advanced version of csishow.py

> Matplotlib is a Python 2D plotting library which produces publication quality figures
> in a variety of hardcopy formats and interactive environments across platforms

> If you are doing anything requiring rapid plot updates, video, or realtime
> interactivity, matplotlib is not the best choice.

Usage:
    1. python3 csiviewer.py
    2. python3 csiserver.py ../material/5300/dataset/sample_0x5_64_3000.dat 3000 2000
    3. F11: show fullscreen, F1: show menu bar.

Note:
    1. Functions such as np.angle() will take some time, so csiserver.py uses 
        a larger value of delay. downsampling would be better.
    2. If you want to start it quickly on Linux, create a file named 'csiviewer.desktop'. 
        Copy the following code to 'csiviewer.desktop', and give it executable permissions.
        Finally, you need set `Exec` manually.

        ```bash
        [Desktop Entry]
        Name=CSIViewer
        Comment=CSI Plot
        Keywords=CSI;
        StartupNotify=true
        Terminal=false
        Type=Application
        Categories=Application;
        Icon=/opt/csiread/csiviewer.png
        Exec=python3 /opt/csiread/csiviewer.py %F
        Name[en_US]=csiviewer.desktop
        ```

    3. If the GetDataThread was blocked, Timer should stop.
"""

import os
import socket
import sys

import csiread
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import QMutex, Qt, QThread, QTimer, pyqtSlot
from PyQt5.QtGui import QApplication
from PyQt5.QtWidgets import QLabel, QMenuBar, QPushButton, QVBoxLayout, QWidget

os.environ['QT_SCALE_FACTOR'] = '1'

Device = 'Intel' # Intel or Atheros

if Device == 'Intel':
    csidata = csiread.CSI(None, 3, 2)
    SUBCARRIERS_NUM = 30
    BW = 20
    NG = 2
    YRange_A = 70
    YRange_B = 70
    YRange_D = 40
elif Device == 'Atheros':
    csidata = csiread.Atheros(None, 3, 2)
    SUBCARRIERS_NUM = 56
    BW = 20
    NG = 1
    YRange_A = 300
    YRange_B = 300
    YRange_D = 200
else:
    raise ValueError("Device = 'Intel' or 'Atheros'")



cache_amptiA = np.zeros([SUBCARRIERS_NUM, 800])       # [subcarriers, packets]
cache_amptiB = np.zeros([SUBCARRIERS_NUM, 10, 3])     # [subcarriers, packets, Nrx]
cache_phaseC = np.zeros([SUBCARRIERS_NUM, 10, 3])     # [subcarriers, packets, Nrx]
cache_cirD = np.zeros([64, 10, 3])       # [time(samples), packets, Nrx]

mutex = QMutex()


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


def phy_ifft(x, axis=0, bw=20, ng=2):
    """802.11n IFFT
    
    Return discrete inverse Fourier transform of real or complex sequence. it
    is based on Equation (19-25)(P2373)

    Note:
        1. No ifftshift
        2. Don't use scipy.fftpack.ifft, it is different from Equation (19-25)
            and Equation (17-9)
    """
    x = np.expand_dims(x.swapaxes(-1, axis), -2)
    k = get_subcarriers_index(bw, ng)
    delta_f = 20e6 / 64
    t = np.arange(64).reshape(-1, 1) / 20e6

    out = (x * np.exp(1.j * 2 * np.pi * k * delta_f * t)).mean(axis=-1).swapaxes(-1, axis)
    return out


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


class GetDataThread(QThread):
    def __init__(self, parent):
        super(GetDataThread, self).__init__(parent)

    def stop(self):
        self.requestInterruption()
        self.exit()

    def run(self):
        """get data in real time

        Note:
            If you want to run this script on the host with Intel 5300 NIC, rewrite code as
            csiuserspace.py
        """

        # config
        count = 0
        address_src = ('127.0.0.1', 10086)
        address_des = ('127.0.0.1', 10010)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(address_des)
            s.settimeout(1/30)
            # while True:       # `QThread: Destroyed while thread is still running`
            while not self.isInterruptionRequested():
                try:
                    data, address_src = s.recvfrom(4096)
                except socket.timeout:
                    continue
                msg_len = len(data)

                code = csidata.pmsg(data)  # Notice: endian
                if code == 0xbb:            # Intel
                    csi = csidata.get_scaled_csi_sm(True)
                elif code == None:          # Atheros
                    csi = csidata.csi
                else:
                    continue

                mutex.lock()
                cache_amptiA[:, :-1] = cache_amptiA[:, 1:]
                cache_amptiB[:, :-1] = cache_amptiB[:, 1:]
                cache_phaseC[:, :-1] = cache_phaseC[:, 1:]
                cache_cirD[:, :-1] = cache_cirD[:, 1:]
                cache_amptiA[:, -1] = np.abs(csi[0, :, 0, 0])
                cache_amptiB[:, -1] = np.abs(csi[0, :, :, 0])
                cache_phaseC[:, -1] = calib(np.unwrap(np.angle(csi), axis=1), bw=BW, ng=NG)[0, :, :, 0]
                cache_cirD[:, -1] = np.abs(phy_ifft(csi[0, :, :, 0], axis=0, bw=BW, ng=NG))
                mutex.unlock()
                count += 1
                if count % 100 == 0:
                    print('receive %d bytes [msgcnt=%u]' % (msg_len, count))


class MainWindow(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super(MainWindow, self).__init__(parent=parent, flags=flags)
        self.subcarriers_index = get_subcarriers_index(bw=BW, ng=NG)
        self.configUI()
        self.configLayout()
        self.show()

    def configUI(self):
        self.setWindowTitle("CSIVIEWER")
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.resize(800, 450)
        self.move(100, 100)
        self.setStyleSheet("border:0;background-color:#e8e8e8")

        # pygtgrapg global config
        pg.setConfigOptions(antialias=True)                 # Antialiasing
        pg.setConfigOptions(background=(232, 232, 232))     # White
        pg.setConfigOptions(foreground=(25, 25, 25))        # Black

        # plot area
        self.plot = pg.GraphicsWindow()
        self.initPlot()

        # ctrl area
        self.ctrl = QMenuBar(self)
        self.initCtrl()

        # update cache
        self.task = GetDataThread(self)
        self.task.start()

        # plot refresh
        self.PlotTimer()

    def configLayout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.plot)
        layout.addWidget(self.ctrl)

    @staticmethod
    def color_define(index):
        return (int(np.sin(index * (2 * np.pi) / 30 + 2) * 127 + 128),
                int(np.cos(index * (2 * np.pi) / 30 - 1) * 127 + 128),
                int(np.sin(index * (2 * np.pi) / 30 - 2) * 127 + 128),
                127)

    def initPlot(self):
        """Plot here"""
        # csi amplitude (time view) ======================================================
        pk_num = cache_amptiA.shape[1]
        p = self.plot.addPlot(title="Amplitude of CSI_800_%s_0_0" % (SUBCARRIERS_NUM))
        p.showGrid(x=False, y=True)
        p.setLabel('left', "Amplitude")
        p.setLabel('bottom', "Packets", units='')
        p.enableAutoRange('xy', False)
        p.setXRange(-int(pk_num/2), int(pk_num/2), padding=0.01)
        p.setYRange(0, YRange_A, padding=0.01)

        self.curvesA = []
        for i in range(SUBCARRIERS_NUM):
            color = self.color_define(i)
            self.curvesA.append(p.plot(pen=color, name='subcarrier=%d' % (i)))
        # x axis
        self.X = np.linspace(-int(pk_num/2), int(pk_num/2), pk_num)

        # csi amplitude (subcarriers view) ===============================================
        p2 = self.plot.addPlot(title="CFR of CSI_10_%s_3_0" % (SUBCARRIERS_NUM))
        p2.showGrid(x=False, y=True)
        p2.setLabel('left', "Amplitude")
        p2.setLabel('bottom', "Subcarriers", units='')
        p2.enableAutoRange('xy', False)
        p2.setXRange(-30, 30, padding=0.01)
        p2.setYRange(0, YRange_B, padding=0.01)

        self.curvesB = []
        for i in range(10*3):
            color = self.color_define(i)
            self.curvesB.append(p2.plot(pen=color))

        self.plot.nextRow()
        # csi phase (subcarriers view) ===================================================
        p3 = self.plot.addPlot(title="Phase of CSI_10_%s_3_0" % (SUBCARRIERS_NUM))
        p3.showGrid(x=False, y=True)
        p3.setLabel('left', "Phase")
        p3.setLabel('bottom', "Subcarriers", units='')
        p3.enableAutoRange('xy', False)
        p3.setXRange(-30, 30, padding=0.01)
        p3.setYRange(-np.pi, np.pi, padding=0.01)

        self.curvesC = []
        for i in range(10*3):
            color = self.color_define(i)
            self.curvesC.append(p3.plot(pen=color))

        # cir csi (time view) ============================================================
        p4 = self.plot.addPlot(title="CIR of CSI_10_%s_3_0" % (SUBCARRIERS_NUM))
        p4.showGrid(x=False, y=True)
        p4.setLabel('left', "Amplitude")
        p4.setLabel('bottom', "Time", units='50ns')
        p4.enableAutoRange('xy', False)
        p4.setXRange(0, 64, padding=0.01)
        p4.setYRange(0, YRange_D, padding=0.01)

        self.curvesD = []
        for i in range(10*3):
            color = self.color_define(i)
            self.curvesD.append(p4.plot(pen=color))

    def initCtrl(self):
        """Write your control here."""
        self.ctrl.addMenu("&File")
        self.ctrl.addMenu("&Edit")
        self.ctrl.addMenu("&Help")
        self.ctrl.setVisible(False)

    def PlotTimer(self):
        self.timer = QTimer()
        self.timer.setTimerType(0)
        self.timer.timeout.connect(self.updatePlot)
        self.timer.start(1000//30)

    @pyqtSlot()
    def updatePlot(self):
        global cache_amptiA, cache_amptiB, cache_phaseC
        mutex.lock()
        for i in range(SUBCARRIERS_NUM):
            self.curvesA[i].setData(self.X, cache_amptiA[i])
        for i in range(10*3):
            self.curvesB[i].setData(self.subcarriers_index, cache_amptiB[:, i%10 , i//10])
            self.curvesC[i].setData(self.subcarriers_index, cache_phaseC[:, i%10 , i//10])
            self.curvesD[i].setData(np.arange(64), cache_cirD[:, i%10 , i//10])
        mutex.unlock()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            self.setWindowState(self.windowState() ^ Qt.WindowFullScreen)
        if event.key() == Qt.Key_F1:
            self.ctrl.setVisible(not self.ctrl.isVisible())
        event.accept()

    def closeEvent(self, event):
        self.task.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())
