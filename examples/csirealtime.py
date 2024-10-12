#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Plot CSI(Linux 802.11n CSI Tool, nexmon_csi) in real time

Usage:
    1. python3 csirealtime.py
    2. python3 csiserver.py ../material/5300/dataset/sample_0x5_64_3000.dat 3000 500
"""

import socket
import threading

import csiread
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

cache_len = 1000
cache_data1 = [np.nan] * cache_len
cache_data2 = [np.nan] * cache_len
cache_data3 = [np.nan] * cache_len

subcarrier_num = 256
cache_data4 = [np.nan] * subcarrier_num

nsc_pico = 56
cache_data5 = [np.nan] * nsc_pico

mutex = threading.Lock()


class GetDataThread(threading.Thread):
    def __init__(self, device):
        super(GetDataThread, self).__init__()
        self.running = True
        self.address_src = ('127.0.0.1', 10086)
        self.address_des = ('127.0.0.1', 10010)
        if device == 'intel':
            self.csidata = csiread.Intel(None, 3, 1)
        if device == 'nexmon':
            self.csidata = csiread.Nexmon(None, chip='4358', bw=80)
        if device == 'picoscenes':
            self.csidata = csiread.Picoscenes(None, {'CSI': [nsc_pico, 3, 1]})

    def __call__(self, event):
        self.running = False

    def run(self):
        self.update_background()

    def update_background(self):
        # config
        global cache_data1, cache_data2, cache_data3, \
            cache_data4, cache_data5, mutex
        count = 0

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(self.address_des)
            while self.running:
                data, address_src = s.recvfrom(4096)    # 65507
                msg_len = len(data)

                code = self.csidata.pmsg(data)
                if code == 0xbb:    # intel
                    scaled_csi_sm = self.csidata.get_scaled_csi()[0]
                    mutex.acquire()
                    cache_data1.pop(0)
                    cache_data1.append(scaled_csi_sm[15, 0, 0])
                    cache_data2.pop(0)
                    cache_data2.append(scaled_csi_sm[15, 1, 0])
                    cache_data3.pop(0)
                    cache_data3.append(scaled_csi_sm[15, 2, 0])
                    mutex.release()
                    count += 1
                if code == 0xf100:  # nexmon
                    mutex.acquire()
                    cache_data4 = np.fft.fftshift(self.csidata.csi[0])
                    mutex.release()
                    count += 1
                if code == 0xf300:  # picoscenes
                    mutex.acquire()
                    cache_data5 = self.csidata.raw[0]["CSI"]["CSI"][:, 0, 0]
                    mutex.release()
                    count += 1

                if count % 100 == 0:
                    print('receive %d bytes [msgcnt=%u]' % (msg_len, count))


def realtime_plot_intel(task):
    fig, ax = plt.subplots()
    fig.canvas.mpl_connect('close_event', task)
    plt.title('csi-amplitude')
    plt.xlabel('packets')
    plt.ylabel('amplitude')
    ax.set_ylim(0, 40)
    ax.set_xlim(0, cache_len)
    x = np.arange(0, cache_len, 1)

    line1,  = ax.plot(x, np.abs(cache_data1), linewidth=1.0, label='subcarrier_15_0_0')
    line2,  = ax.plot(x, np.abs(cache_data2), linewidth=1.0, label='subcarrier_15_1_0')
    line3,  = ax.plot(x, np.abs(cache_data3), linewidth=1.0, label='subcarrier_15_2_0')
    plt.legend()

    def init():
        line1.set_ydata([np.nan] * len(x))
        line2.set_ydata([np.nan] * len(x))
        line3.set_ydata([np.nan] * len(x))
        return line1, line2, line3,

    def animate(i):
        global cache_data1, cache_data2, cache_data3, mutex
        mutex.acquire()
        line1.set_ydata(np.abs(cache_data1))
        line2.set_ydata(np.abs(cache_data2))
        line3.set_ydata(np.abs(cache_data3))
        mutex.release()
        return line1, line2, line3,

    ani = animation.FuncAnimation(fig, animate, init_func=init, interval=1000/25,
                                  cache_frame_data=False, blit=True)
    plt.show()


def realtime_plot_nexmon(task):
    fig, ax = plt.subplots()
    fig.canvas.mpl_connect('close_event', task)
    plt.title('csi-amplitude')
    plt.xlabel('subcarrier')
    plt.ylabel('amplitude')
    ax.set_ylim(0, 4000)
    ax.set_xlim(0, subcarrier_num)
    x = np.arange(0, subcarrier_num)

    line4,  = ax.plot(x, np.abs(cache_data4), linewidth=1.0, label='subcarrier_256')
    plt.legend()

    def init():
        line4.set_ydata([np.nan] * subcarrier_num)
        return line4,

    def animate(i):
        global cache_data4, mutex
        mutex.acquire()
        line4.set_ydata(np.abs(cache_data4))
        mutex.release()
        return line4,

    ani = animation.FuncAnimation(fig, animate, init_func=init, interval=1000/25,
                                  cache_frame_data=False, blit=True)
    plt.show()


def realtime_plot_picoscenes(task):
    print("Warning: Picoscenes.pmsg method hasn't been READY!")
    fig, ax = plt.subplots()
    fig.canvas.mpl_connect('close_event', task)
    plt.title('csi-amplitude')
    plt.xlabel('subcarrier')
    plt.ylabel('amplitude')
    ax.set_ylim(0, 500)
    ax.set_xlim(0, nsc_pico)
    x = np.arange(0, nsc_pico)

    line5,  = ax.plot(x, np.abs(cache_data5), linewidth=1.0, label='subcarrier_56')
    plt.legend()

    def init():
        line5.set_ydata([np.nan] * nsc_pico)
        return line5,

    def animate(i):
        global cache_data5, mutex
        mutex.acquire()
        line5.set_ydata(np.abs(cache_data5))
        mutex.release()
        return line5,

    ani = animation.FuncAnimation(fig, animate, init_func=init, interval=1000/25,
                                  cache_frame_data=False, blit=True)
    plt.show()


def realtime_plot(device):
    task = GetDataThread(device)
    task.start()
    eval('realtime_plot_' + device)(task)
    task.join()


if __name__ == '__main__':
    realtime_plot('intel')
