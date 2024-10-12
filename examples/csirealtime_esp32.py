#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ESP32-CSI-Tool realtime plotting

Usage(linux):
    python3 csiserver.py ../material/esp32/dataset/example_csi.csv 0 1000 | python3 csirealtime_esp32.py

Note:
    Haven't been tested with ESP32-CSI-Tool.
"""

import threading
import sys

import csiread
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np


packet_num, subcarrier_num = 10, 64
cache_data = np.zeros([packet_num, subcarrier_num], dtype=complex)
mutex = threading.Lock()


class GetDataThread(threading.Thread):
    def __init__(self):
        super(GetDataThread, self).__init__()
        self.running = True

    def __call__(self, event):
        self.running = False

    def run(self):
        self.update_background()

    def update_background(self):
        csidata = csiread.ESP32(None, False)
        global cache_data, mutex
        while self.running:
            data = sys.stdin.readline().strip('\n')
            code = csidata.pmsg(data)
            if code == 0xf200:
                mutex.acquire()
                cache_data[:-1] = cache_data[1:]
                cache_data[1:] = csidata.csi[0]
                mutex.release()


def realtime_plot_esp32(task):
    fig, ax = plt.subplots()
    fig.canvas.mpl_connect('close_event', task)
    plt.title('csi-amplitude')
    plt.xlabel('subcarrier')
    plt.ylabel('amplitude')
    ax.set_ylim(0, 100)
    ax.set_xlim(0, subcarrier_num)
    x = np.arange(0, subcarrier_num)

    lines = ax.plot(x, np.abs(cache_data).T, linewidth=1.0, label='subcarrier_64')

    def init():
        return lines

    def animate(i):
        global cache_data, mutex
        mutex.acquire()
        for i in range(packet_num):
            lines[i].set_ydata(np.abs(cache_data[i]))
        mutex.release()
        return lines

    ani = animation.FuncAnimation(fig, animate, init_func=init, interval=1000/60,
                                  cache_frame_data=False, blit=True)
    plt.show()


if __name__ == '__main__':
    task = GetDataThread()
    task.start()
    realtime_plot_esp32(task)
    task.join()
