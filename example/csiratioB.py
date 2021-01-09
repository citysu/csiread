#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CSI ratioB: Plot CSI ratio of two antennas in real time(Linux 802.11n CSI Tool)

Usage:
    1. python3 csiratioB.py
    2. python3 csiserver.py ../material/5300/dataset/sample_0x5_64_3000.dat 3000 10000

Note:
    1. this is just a demo, because it's too slow :(
    2. You need right data to get beautiful result
    3. csiserver.py: Use a large delay value to avoid too much packets loss

Ref:
    realtime_plot: [MATPLOTLIB UNCHAINED](https://matplotlib.org/3.1.3/gallery/animation/unchained.html#matplotlib-unchained)
    csi ratio: [FarSense: Pushing the Range Limit of WiFi-based Respiration Sensing with CSI Ratio of Two Antennas](https://arxiv.org/pdf/1907.03994v1.pdf)
"""

import socket
import threading

import csiread
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['toolbar'] = "None"

cache = np.zeros([30, 800])
mutex = threading.Lock()


class GetDataThread(threading.Thread):
    def __init__(self):
        super(GetDataThread, self).__init__()
        self.__state = True

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
            s.settimeout(0.1)
            while self.__state:
                try:
                    data, address_src = s.recvfrom(4096)
                except socket.timeout:
                    continue
                msg_len = len(data)

                code = csidata.pmsg(data)
                if code == 0xbb:
                    csi = csidata.get_scaled_csi_sm()
                    scaled_csi_sm = np.abs(csi[0, :, 0, 0] / csi[0:, :, 1, 0])
                    mutex.acquire()
                    cache[:, :-1] = cache[:, 1:]
                    cache[:, -1] = scaled_csi_sm
                    mutex.release()
                    count += 1
                    if count % 100 == 0:
                        print('receive %d bytes [msgcnt=%u], seq=%d' % (msg_len, count, csidata.seq))

    def stop(self):
        self.__state = False


def realtime_plot():
    fig = plt.figure(figsize=(16/2, 9/2), facecolor='black')
    ax = plt.subplot(111, frameon=False)
    ax.set_ylim(-10, 70)
    # ax.set_xticks([])
    ax.set_yticks([])
    ax.tick_params(axis='x', colors='white')
    ax.xaxis.label.set_color('white')
    ax.set_xlabel('Packets')
    ax.text(0.5, 1.0, "Ratio of CSI(30x)", transform=ax.transAxes,
            ha="center", va="bottom", color="w",
            family="sans-serif", fontweight="light", fontsize=16)

    lens = cache.shape[-1]
    X = np.linspace(-int(lens/2), int(lens/2), lens)
    lines = []
    for i in range(len(cache)):
        xscale = 1 - i / 200.
        lw = 1.0 - i / 75.0
        line, = ax.plot(xscale * X, i/2 + cache[i], lw=lw, alpha=0.5)
        lines.append(line)

    def animate(i):
        global cache, mutex
        mutex.acquire()
        for i in range(len(cache)):
            lines[i].set_ydata(i/2 + cache[i])
        mutex.release()
        return lines

    ani = animation.FuncAnimation(fig, animate, interval=1000/30, blit=False)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    task = GetDataThread()
    task.start()
    realtime_plot()
    task.stop()
