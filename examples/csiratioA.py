#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CSI ratioA: Plot CSI ratio of two antennas in real time(Linux 802.11n CSI Tool)

Usage:
    1. python3 csiratioA.py
    2. python3 csiserver.py ../material/5300/dataset/sample_0x5_64_3000.dat 3000 1000

Note:
    1. This example is much faster than csiratioB.py, and less packets loss.
    2. You need right data to get beautiful result

Ref:
    csi ratio: [FarSense: Pushing the Range Limit of WiFi-based Respiration Sensing
        with CSI Ratio of Two Antennas](https://arxiv.org/pdf/1907.03994v1.pdf)
"""

import os
import socket
import sys

import csiread
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import QMutex, Qt, QThread, QTimer, pyqtSlot
from PyQt5.QtGui import QApplication
from PyQt5.QtWidgets import QVBoxLayout, QWidget

os.environ['QT_SCALE_FACTOR'] = '1'

cache = np.zeros([30, 800])
mutex = QMutex()


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
        csidata = csiread.Intel(None, 3, 2)

        # config
        global cache, mutex
        count = 0
        address_src = ('127.0.0.1', 10086)
        address_des = ('127.0.0.1', 10010)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(address_des)
            s.settimeout(30/1000)
            while not self.isInterruptionRequested():
                try:
                    data, address_src = s.recvfrom(4096)
                except socket.timeout:
                    continue
                msg_len = len(data)

                code = csidata.pmsg(data)
                if code == 0xbb:
                    csi = csidata.get_scaled_csi_sm()
                    scaled_csi_sm = np.abs(csi[0, :, 0, 0] / csi[0:, :, 1, 0])
                    scaled_csi_sm[scaled_csi_sm==np.inf] = 0
                    mutex.lock()
                    cache[:, :-1] = cache[:, 1:]
                    cache[:, -1] = scaled_csi_sm
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
        screen_size = QApplication.primaryScreen().size()
        self.setWindowTitle("CSIRatioA")
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.resize(800, 450)
        self.move(screen_size.width() - 800 - 100, 100)

        # pygtgrapg global config
        pg.setConfigOptions(antialias=True)                 # Antialiasing
        pg.setConfigOptions(foreground=(232, 232, 232))     # Black
        pg.setConfigOptions(background=(25, 25, 25))        # White

        # plot area
        self.win = pg.GraphicsWindow()

        # plot init
        self.initPlot()

        # update cache
        self.task = GetDataThread(self)
        self.task.start()

        # plot refresh
        self.PlotTimer()

    def configLayout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.win)

    def initPlot(self):
        lens = cache.shape[-1]

        p = self.win.addPlot(title="Ratio of CSI(30x)")
        p.showGrid(x=False, y=True)
        p.setLabel('left', "Amplitude", units='A')
        p.setLabel('bottom', "Packets", units='')
        p.enableAutoRange('xy', False)
        p.setXRange(-int(lens/2), int(lens/2), padding=0.01)
        p.setYRange(-10, 70, padding=0.01)
        p.hideAxis('left')
        # p.addLegend()

        # curves
        self.curves = []
        for i in range(len(cache)):
            color = (int(np.sin(i * (2 * np.pi) / 30 + 2) * 127 + 128),
                     int(np.cos(i * (2 * np.pi) / 30 - 1) * 127 + 128),
                     int(np.sin(i * (2 * np.pi) / 30 - 2) * 127 + 128),
                     127)
            self.curves.append(p.plot(pen=color, name='subcarrier=%d' % (i)))

        # x axis
        self.X = np.linspace(-int(lens/2), int(lens/2), lens)

    def PlotTimer(self):
        self.timer = QTimer()
        self.timer.setTimerType(0)
        self.timer.timeout.connect(self.updatePlot)
        self.timer.start(1000//30)

    @pyqtSlot()
    def updatePlot(self):
        global cache, mutex
        mutex.lock()
        for i in range(len(cache)):
            xscale = 1 - i / 200.
            self.curves[i].setData(xscale * self.X, i/2 + cache[i])
        mutex.unlock()

    def closeEvent(self, event):
        self.task.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())
