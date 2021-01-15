#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Plot CSI(nexmon_csi) in real time

Usage:
    1. sudo python3 csirealtime_nexmon.py
    2. sudo python3 csiserver.py ../material/5300/dataset/example.pcap 4 10000

Important:
    1. Nexmon.pmsg() is experimental, it may be modified in the future.
    The first arguement is raw packet, however, I'd like it to be udp packet. 
    2. csirealtime_nexmon.py and csiserver.py(Nexmon) need root or sudo 
    permissions. Only work on Linux.
"""

import socket
import threading

import csiread
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

subcarrier_num = 256
cache_data1 = [np.nan] * subcarrier_num
mutex = threading.Lock()


class GetDataThread(threading.Thread):
    def run(self):
        update_background()


def update_background():
    csidata = csiread.Nexmon(None, chip='4358', bw=80)

    # config
    global cache_data1, mutex
    count = 0

    with socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x3)) as s:
        while True:
            data, address_src = s.recvfrom(4096)
            msg_len = len(data)

            code = csidata.pmsg(data)
            if code == 0xf100:
                mutex.acquire()
                cache_data1 = np.fft.ifftshift(csidata.csi[0])
                mutex.release()
                count += 1
                if count % 100 == 0:
                    print('receive %d bytes [msgcnt=%u]' % (msg_len, count))


def realtime_plot():
    fig, ax = plt.subplots()
    plt.title('csi-amplitude')
    plt.xlabel('subcarrier')
    plt.ylabel('amplitude')
    ax.set_ylim(0, 4000)
    ax.set_xlim(0, subcarrier_num)
    x = np.arange(0, subcarrier_num)

    line1,  = ax.plot(x, np.abs(cache_data1), linewidth=1.0, label='subcarrier_256')
    plt.legend()

    def init():
        line1.set_ydata([np.nan] * subcarrier_num)
        return line1,

    def animate(i):
        global cache_data1, mutex
        mutex.acquire()
        line1.set_ydata(np.abs(cache_data1))
        mutex.release()
        return line1,

    ani = animation.FuncAnimation(fig, animate, init_func=init, interval=1000/25, blit=True)
    plt.show()


if __name__ == '__main__':
    task = GetDataThread()
    task.start()
    realtime_plot()
