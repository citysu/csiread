#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CSI viewer: Advanced version of csishow.py

You maybe need reading the docs of PyQtGraph and PyQt5

> Matplotlib is a Python 2D plotting library which produces publication quality figures
> in a variety of hardcopy formats and interactive environments across platforms

> If you are doing anything requiring rapid plot updates, video, or realtime
> interactivity, matplotlib is not the best choice.
"""

import sys
import csiread
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QApplication


class CSIGUI():
    def __init__(self):
        super().__init__()
        self.csidata = self.load_data("../material/5300/dataset/sample_0x5_64_3000.dat")
        self.win = self.main_window()
        self.timer = None
        self.sender = None

    def load_data(self, file):
        print("data loading")
        csidata = csiread.CSI(file, if_report=False)
        csidata.read()
        csidata.csi = csidata.get_scaled_csi_sm()
        print("data load finished")
        return csidata

    def main_window(self):
        pg.setConfigOptions(antialias=True)                 # 抗锯齿
        pg.setConfigOptions(foreground=(25, 25, 25))        # 红色
        pg.setConfigOptions(background=(232, 232, 232))     # 灰白色

        win = pg.GraphicsWindow()
        win.setWindowTitle("CSI PLOT")                      # 窗口标题
        win.resize(1000, 600)                               # 窗口大小
        return win

    def run(self):
        context = QApplication(sys.argv)

        # self.plot_fig1()
        # self.plot_fig2()
        self.plot_fig3()
        # add your method here

        sys.exit(context.exec_())

    def plot_fig1(self):
        """Amplitude of csi"""
        win = self.win
        csidata = self.csidata

        # x, y轴的数据
        x = csidata.timestamp_low/1000000 - csidata.timestamp_low[0]/1000000
        y = np.abs(csidata.csi)[:, 5, 0, 0]

        # 添加子图:设置标题
        p = win.addPlot(title="Amplitude of csi(subcarray index=5)")
        p.plot(x, y, pen=(25, 25, 25))
        p.showGrid(x=False, y=True)                         # 显示网格
        p.setLabel('left', "振幅", units='A')
        p.setLabel('bottom', "时间", units='s')
    
    def plot_fig2(self):
        """Amplitude of csi"""
        win = self.win
        csidata = self.csidata

        # x, y轴的数据
        x = csidata.timestamp_low/1000000 - csidata.timestamp_low[0]/1000000
        y = np.abs(csidata.csi)[:, 25, 0, 0]

        # 添加子图:设置标题
        p = win.addPlot(title="Amplitude of csi(subcarray index=5)")
        p.plot(x, y, pen=(25, 25, 25))
        p.showGrid(x=False, y=True)                         # 显示网格
        p.setLabel('left', "振幅", units='A')
        p.setLabel('bottom', "时间", units='s')

    def plot_fig3(self):
        """Animation of csi"""
        win = self.win
        csidata = self.csidata

        # x, y轴的数据
        x = csidata.timestamp_low/1000000 - csidata.timestamp_low[0]/1000000
        y = np.abs(csidata.csi)[:, 5, 0, 0]
        time_diff = np.diff(csidata.timestamp_low) / 1000

        p = win.addPlot(title="Amplitude of csi(subcarray index=5)")
        curve = p.plot(pen=(25, 25, 25))                    # 不建议画数据点
        p.showGrid(x=False, y=True)                         # 显示网格
        p.setLabel('left', "振幅", units='A')
        p.setLabel('bottom', "时间", units='s')
        p.enableAutoRange('xy', False)
        p.setXRange(x[0], x[-1], padding=0)
        p.setYRange(y.min(), y.max(), padding=0)

        window_size = 2000                                  # 信号窗口大小(毫秒)
        fps = 60                                            # 窗口刷新频率(毫秒)

        self.index = 0
        self.data = np.zeros_like(x)
        self.data.fill(np.nan)
        self.y = y

        # 更新数据
        def update_data():
            self.data[self.index] = self.y[self.index]
            self.sender.setInterval(time_diff[self.index])
            self.index += 1
            if self.index >= self.csidata.count - 1:
                self.timer.stop()
                self.sender.stop()

        # 更新绘图
        def update_plot():
            curve.setData(x, self.data)

        self.sender = QTimer()
        self.sender.setTimerType(0)
        self.sender.timeout.connect(update_data)
        self.sender.start(1)

        self.timer = QTimer()
        self.timer.setTimerType(0)
        self.timer.timeout.connect(update_plot)
        self.timer.start(fps)


if __name__ == "__main__":
    CSIGUI().run()
