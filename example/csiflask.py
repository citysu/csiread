#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""csi flask: A web application to plot CSI in realtime.

Usage:
    1. python3 csiflask.py
    2. open: http://127.0.0.1:5000, click 'start' button
    3. python3 csiserver.py ../material/5300/dataset/sample_0x5_64_3000.dat 3000 10000
    4. you'd better click 'stop' button before stopping csiserver.py

Tools:
    python: flask, flask-socketio
    javascript: socket.io, EChart, Three.js, UIkit, (Semantic-UI needs https://fonts.googleapis.com)

Note:
    1. Learn something about flask and flask-socketio before running csiflask.py
    2. This example is a toy, it just accepts the low packet rate.
"""

from flask import Flask, render_template_string
from flask_socketio import SocketIO, Namespace
import socket
import csiread


index_html = """
<!DOCTYPE html>
<html>
    <head>
        <title>CSI Flask</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.bootcdn.net/ajax/libs/echarts/4.7.0/echarts-en.common.js"></script>
        <script src="https://cdn.bootcdn.net/ajax/libs/socket.io/2.3.0/socket.io.js"></script>
        <script>
            var socket = io({autoConnect: false, transports: ['websocket']});
            var dataset =[0, 0, 0, 0, 0, 0, 0]
        </script>
    </head>
    {% raw %}
    <body>
        <h1>csi flask</h1>
        <button onclick="socket.open()">start</button>
        <button onclick="socket.close()">stop</button>
        <div id="csiviewer" style="width: 600px;height:400px;"></div>
        <script>
            var csiviewer = echarts.init(document.getElementById('csiviewer'));

            socket.on("message", function (data) {
                dataset.shift();
                dataset.push(data);
                option = {
                    xAxis: {
                        type: 'category',
                        data: ['1st', '2nd', '3th', '4th', '5th', '6th', '7th']
                    },
                    yAxis: {
                        type: 'value',
                        data: [0, 70]
                    },
                    series: [{
                        type: 'line',
                        data: dataset,
                    }]
                };
                csiviewer.setOption(option);
                console.log(dataset)
            });
        </script>
    </body>
    {% endraw %}
</html>
"""


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
socketio = SocketIO(app)


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
        csidata = csiread.CSI(None, 3, 2)
        address_des = ('127.0.0.1', 10010)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(address_des)
            s.settimeout(1)
            while self.task_status:
                try:
                    data, _ = s.recvfrom(4096)
                except socket.timeout:
                    continue
                code = csidata.pmsg(data)
                if code == 0xbb:
                    socketio.sleep(0.00001)
                    socketio.send(float(csidata.rssiA[0]))
        self.task_status = True

    def background_task_init(self):
        self.task_status = True
        self.task = None

    def background_task_stop(self):
        self.task_status = False
        self.task = None


socketio.on_namespace(CSIChat())


@app.route('/')
def index():
    return render_template_string(index_html)


if __name__ == '__main__':
    socketio.run(app, debug=True)
