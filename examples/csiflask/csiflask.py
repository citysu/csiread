#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""csi flask: A web application to plot CSI in realtime.

Usage:
    1. python3 csiflask.py
    2. open: http://127.0.0.1:5000, click 'start' button
    3. python3 csiserver.py ../material/5300/dataset/sample_0x5_64_3000.dat 3000 10000

Tools:
    python: flask, flask-socketio
    javascript: socket.io, EChart, UIkit

Note:
    1. Learn something about flask and flask-socketio before running csiflask.py
    2. Be careful of packet loss

    (Flask-SocketIO)[https://flask-socketio.readthedocs.io/en/latest/]
    ===========================================================================
    Version compatibility

    The Socket.IO protocol has been through a number of revisions, and some of
    these introduced backward incompatible changes, which means that the client
    and the server must use compatible versions for everything to work.

    The version compatibility chart below maps versions of this package to
    versions of the JavaScript reference implementation and the versions of
    the Socket.IO and Engine.IO protocols.
    ===========================================================================
"""

from flask import Flask, render_template
from flask_socketio import SocketIO, Namespace
import socket
import csiread
import numpy as np


class CSIChat(Namespace):
    def __init__(self):
        super(CSIChat, self).__init__()
        self.background_task_init()

    def on_connect(self):
        print("start")
        if self.task is None:
            self.task = socketio.start_background_task(target=self.background_task)

    def on_disconnect(self):
        print("close")
        self.background_task_stop()

    def background_task(self):
        csidata = csiread.Intel(None, 3, 2)
        # csidata = csiread.Nexmon(None, '4358', 80)
        address_des = ('127.0.0.1', 10010)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(address_des)
            s.settimeout(0.1)
            while self.task_status:
                socketio.sleep(0.0001)
                try:
                    data, _ = s.recvfrom(4096)
                except socket.timeout:
                    continue
                code = csidata.pmsg(data)
                if code == 0xbb:
                    csidata.get_scaled_csi_sm(True)
                    socketio.send({
                        'csi': np.abs(csidata.csi[0, :, 0, 0]).tolist()
                    })
                if code == 0xf100:        # Nexmon
                    csidata.csi = np.fft.fftshift(csidata.csi, axes=1)
                    socketio.send({
                        'csi': np.abs(csidata.csi[0, :]).tolist()
                    })

        self.task_status = True

    def background_task_init(self):
        self.task_status = True
        self.task = None

    def background_task_stop(self):
        self.task_status = False
        self.task = None


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
socketio = SocketIO(app)
socketio.on_namespace(CSIChat())


@app.route('/')
def index():
    return render_template('csiflask.html')


if __name__ == '__main__':
    socketio.run(app, debug=True)
