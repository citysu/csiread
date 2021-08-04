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
    3. Alternate pseudocode for Nexmon with multiple spatial stream:

        ```python
        last_seq = None
        cache_csi = np.zeros([frame_num, s_num, c_num, subcarrier])
        ...
        if csidata.seq[0] != last_seq:
            last_seq = csidata.seq[0]
            cache_csi[:-1] = cache_csi[1:]
        cache_csi[-1:, csidata.core[0], csidata.spatial[0], :] = csidata.csi[0]
        ```
"""

import os
import socket
import sys

import csiread
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import QMutex, Qt, QThread, QTimer, pyqtSlot
from PyQt5.QtGui import QApplication
from PyQt5.QtWidgets import QMenuBar, QVBoxLayout, QWidget
from utils import scidx, phy_ifft, calib


os.environ['QT_SCALE_FACTOR'] = '1'

Device = 'Intel'    # Intel, Atheros, Nexmon

if Device == 'Intel':
    csidata = csiread.Intel(None, 3, 2)
    PK_COUNT = 800
    RX_NUM = 3
    PK_NUM = 10
    BW = 20
    NG = 2
    YRange_A = 70
    YRange_B = 70
    YRange_D = 40
    S_INDEX = scidx(BW, NG, 'n')
elif Device == 'Atheros':
    csidata = csiread.Atheros(None, 3, 2)
    PK_COUNT = 800
    RX_NUM = 3
    PK_NUM = 10
    BW = 20
    NG = 1
    YRange_A = 300
    YRange_B = 300
    YRange_D = 200
    S_INDEX = scidx(BW, NG, 'n')
elif Device == 'Nexmon':
    csidata = csiread.Nexmon(None, '4358', 80)
    PK_COUNT = 100
    RX_NUM = 1
    PK_NUM = 10
    BW = 80
    NG = 1
    YRange_A = 2000
    YRange_B = 2000
    YRange_D = 1000
    S_INDEX = scidx(BW, NG, 'ac')
else:
    raise ValueError("Device = 'Intel', 'Atheros', 'Nexmon'")

SUBCARRIERS_NUM = S_INDEX.size
T = np.r_[:64 * (BW / 20)]

cache_amptiA = np.zeros([SUBCARRIERS_NUM, PK_COUNT])            # [subcarriers, packets]
cache_amptiB = np.zeros([SUBCARRIERS_NUM, PK_NUM, RX_NUM])      # [subcarriers, packets, Nrx]
cache_phaseC = np.zeros([SUBCARRIERS_NUM, PK_NUM, RX_NUM])      # [subcarriers, packets, Nrx]
cache_cirD = np.zeros([len(T), PK_NUM, RX_NUM])                 # [time(samples), packets, Nrx]

mutex = QMutex()
state = True


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
        global cache_amptiA, cache_amptiB, cache_phaseC, cache_cirD, mutex, state
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
                elif code == 0xff00:        # Atheros
                    csi = csidata.csi
                elif code == 0xf100:        # Nexmon
                    # if csidata.core != 0 or csidata.spatial != 0:
                    #     continue
                    csi = np.fft.fftshift(csidata.csi, axes=1)
                    csi = csi[:, S_INDEX + 32 * (BW // 20), np.newaxis, np.newaxis]
                else:
                    continue

                mutex.lock()
                cache_amptiA[:, :-1] = cache_amptiA[:, 1:]
                cache_amptiB[:, :-1] = cache_amptiB[:, 1:]
                cache_phaseC[:, :-1] = cache_phaseC[:, 1:]
                cache_cirD[:, :-1] = cache_cirD[:, 1:]
                cache_amptiA[:, -1] = np.abs(csi[0, :, 0, 0])
                cache_amptiB[:, -1] = np.abs(csi[0, :, :, 0])
                cache_phaseC[:, -1] = calib(np.unwrap(np.angle(csi), axis=1), S_INDEX)[0, :, :, 0]
                cache_cirD[:, -1] = np.abs(phy_ifft(csi[0, :, :, 0], S_INDEX, axis=0))
                state = True
                mutex.unlock()
                count += 1
                if count % 100 == 0:
                    print('receive %d bytes [msgcnt=%u]' % (msg_len, count))


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
        p2 = self.plot.addPlot(title="CFR of CSI_%s_%s_%s_0" % (PK_NUM, SUBCARRIERS_NUM, RX_NUM))
        p2.showGrid(x=False, y=True)
        p2.setLabel('left', "Amplitude")
        p2.setLabel('bottom', "Subcarriers", units='')
        p2.enableAutoRange('xy', False)
        p2.setXRange(S_INDEX[0] - 2, S_INDEX[-1] + 2, padding=0.01)
        p2.setYRange(0, YRange_B, padding=0.01)

        self.curvesB = []
        for i in range(PK_NUM*RX_NUM):
            color = self.color_define(i)
            self.curvesB.append(p2.plot(pen=color))

        self.plot.nextRow()
        # csi phase (subcarriers view) ===================================================
        p3 = self.plot.addPlot(title="Phase of CSI_%s_%s_%s_0" % (PK_NUM, SUBCARRIERS_NUM, RX_NUM))
        p3.showGrid(x=False, y=True)
        p3.setLabel('left', "Phase")
        p3.setLabel('bottom', "Subcarriers", units='')
        p3.enableAutoRange('xy', False)
        p3.setXRange(S_INDEX[0] - 2, S_INDEX[-1] + 2, padding=0.01)
        p3.setYRange(-np.pi * 2, np.pi * 2, padding=0.01)

        self.curvesC = []
        for i in range(PK_NUM*RX_NUM):
            color = self.color_define(i)
            self.curvesC.append(p3.plot(pen=color))

        # cir csi (time view) ============================================================
        p4 = self.plot.addPlot(title="CIR of CSI_%s_%s_%s_0" % (PK_NUM, SUBCARRIERS_NUM, RX_NUM))
        p4.showGrid(x=False, y=True)
        p4.setLabel('left', "Amplitude")
        p4.setLabel('bottom', "Time", units='%.1fns' % (1e3/BW))
        p4.enableAutoRange('xy', False)
        p4.setXRange(T[0] - 2, T[-1] + 2, padding=0.01)
        p4.setYRange(0, YRange_D, padding=0.01)

        self.curvesD = []
        for i in range(PK_NUM*RX_NUM):
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
        global cache_amptiA, cache_amptiB, cache_phaseC, cache_cirD, mutex, state
        mutex.lock()
        if state:
            for i in range(SUBCARRIERS_NUM):
                self.curvesA[i].setData(self.X, cache_amptiA[i])
            for i in range(PK_NUM*RX_NUM):
                I_PK, I_RX = np.divmod(i, PK_NUM)
                self.curvesB[i].setData(S_INDEX, cache_amptiB[:, I_RX, I_PK])
                self.curvesC[i].setData(S_INDEX, cache_phaseC[:, I_RX, I_PK])
                self.curvesD[i].setData(T, cache_cirD[:, I_RX, I_PK])
            state = False
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
