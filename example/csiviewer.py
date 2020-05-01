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
        Finally, you need change `Exec` manually.

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
    3. Timer should stop when the GetDataThread is blocked
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
from scipy.fftpack import ifft, ifftshift

os.environ['QT_SCALE_FACTOR'] = '1'

carriers_seq_30 = np.array([-28, -26, -24, -22, -20, -18, -16, -14, -12,
                            -10, -8, -6, -4, -2, -1, 1, 3, 5, 7, 9, 11, 13,
                            15, 17, 19, 21, 23, 25, 27, 28])

cache_amptiA = np.zeros([30, 800])       # [subcarriers, packets]
cache_amptiB = np.zeros([30, 10, 3])     # [subcarriers, packets, Nrx]
cache_phaseC = np.zeros([30, 10, 3])     # [subcarriers, packets, Nrx]
cache_cirD = np.zeros([30, 10, 3])       # [subcarriers, packets, Nrx]

mutex = QMutex()

def calib(phase):
    """Phase calibration

    ref: [Enabling Contactless Detection of Moving Humans with Dynamic Speeds
    Using CSI](http://tns.thss.tsinghua.edu.cn/wifiradar/papers/QianKun-TECS2017.pdf)
    """
    k_n = carriers_seq_30[-1]
    k_1 = carriers_seq_30[0]
    a = ((phase[:, -1:] - phase[:, :1])/(k_n - k_1))
    b = np.mean(phase, axis=1, keepdims=True)
    carriers = carriers_seq_30.reshape([30] + [1] * (len(phase.shape) - 2))
    phase_calib = phase - a*carriers - b
    return phase_calib


class GetDataThread(QThread):
    def __init__(self, parent):
        super(GetDataThread, self).__init__(parent)

    def run(self):
        """get data in real time

        Note:
            If you want to run this script on the host with Intel 5300 NIC, rewrite code as
            csiuserspace.py
        """
        csidata = csiread.CSI(None, 3, 2)

        # config
        count = 0
        address_src = ('127.0.0.1', 10086)
        address_des = ('127.0.0.1', 10010)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(address_des)
            while True:
                data, address_src = s.recvfrom(4096)
                msg_len = len(data)

                code = csidata.pmsg(data)
                if code == 0xbb:
                    csi = csidata.get_scaled_csi_sm()
                    mutex.lock()
                    cache_amptiA[:, :-1] = cache_amptiA[:, 1:]
                    cache_amptiB[:, :-1] = cache_amptiB[:, 1:]
                    cache_phaseC[:, :-1] = cache_phaseC[:, 1:]
                    cache_cirD[:, :-1] = cache_cirD[:, 1:]
                    cache_amptiA[:, -1] = np.abs(csi[0, :, 0, 0])
                    cache_amptiB[:, -1] = np.abs(csi[0, :, :, 0])
                    cache_phaseC[:, -1] = calib(np.unwrap(np.angle(csi), axis=1))[0, :, :, 0]
                    cache_cirD[:, -1] = ifftshift(np.abs(ifft(csi[0, :, :, 0], axis=0)))
                    mutex.unlock()
                    count += 1
                    if count % 100 == 0:
                        print('receive %d bytes [msgcnt=%u], seq=%d' % (msg_len, count, csidata.seq))


class MainWindow(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super(MainWindow, self).__init__(parent=parent, flags=flags)
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
        sc_num = cache_amptiA.shape[0]
        p = self.plot.addPlot(title="Amplitude of CSI_800_30_0_0")
        p.showGrid(x=False, y=True)
        p.setLabel('left', "Amplitude")
        p.setLabel('bottom', "Packets", units='')
        p.enableAutoRange('xy', False)
        p.setXRange(-int(pk_num/2), int(pk_num/2), padding=0.01)
        p.setYRange(0, 50, padding=0.01)

        self.curvesA = []
        for i in range(sc_num):
            color = self.color_define(i)
            self.curvesA.append(p.plot(pen=color, name='subcarrier=%d' % (i)))
        # x axis
        self.X = np.linspace(-int(pk_num/2), int(pk_num/2), pk_num)

        # csi amplitude (subcarriers view) ===============================================
        p2 = self.plot.addPlot(title="CFR of CSI_10_30_3_0")
        p2.showGrid(x=False, y=True)
        p2.setLabel('left', "Amplitude")
        p2.setLabel('bottom', "Subcarriers", units='')
        p2.enableAutoRange('xy', False)
        p2.setXRange(-30, 30, padding=0.01)
        p2.setYRange(0, 50, padding=0.01)

        self.curvesB = []
        for i in range(30):
            color = self.color_define(i)
            self.curvesB.append(p2.plot(pen=color))

        self.plot.nextRow()
        # csi phase (subcarriers view) ===================================================
        p3 = self.plot.addPlot(title="Phase of CSI_10_30_3_0")
        p3.showGrid(x=False, y=True)
        p3.setLabel('left', "Phase")
        p3.setLabel('bottom', "Subcarriers", units='')
        p3.enableAutoRange('xy', False)
        p3.setXRange(-30, 30, padding=0.01)
        p3.setYRange(-np.pi, np.pi, padding=0.01)

        self.curvesC = []
        for i in range(30):
            color = self.color_define(i)
            self.curvesC.append(p3.plot(pen=color))

        # cir csi (time view) ============================================================
        p4 = self.plot.addPlot(title="CIR of CSI_10_30_3_0")
        p4.showGrid(x=False, y=True)
        p4.setLabel('left', "Amplitude")
        p4.setLabel('bottom', "Time", units='?ns')
        p4.enableAutoRange('xy', False)
        p4.setXRange(-30, 30, padding=0.01)
        p4.setYRange(0, 30, padding=0.01)

        self.curvesD = []
        for i in range(30):
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
        self.timer.start(1000/30)

    @pyqtSlot()
    def updatePlot(self):
        global cache_amptiA, cache_amptiB, cache_phaseC
        mutex.lock()
        for i in range(cache_amptiA.shape[0]):
            self.curvesA[i].setData(self.X, cache_amptiA[i])
            self.curvesB[i].setData(carriers_seq_30, cache_amptiB[:, i%10 , i//10])
            self.curvesC[i].setData(carriers_seq_30, cache_phaseC[:, i%10 , i//10])
            self.curvesD[i].setData(carriers_seq_30, cache_cirD[:, i%10 , i//10])
        mutex.unlock()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            self.setWindowState(self.windowState() ^ Qt.WindowFullScreen)
        if event.key() == Qt.Key_F1:
            self.ctrl.setVisible(not self.ctrl.isVisible())
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())
