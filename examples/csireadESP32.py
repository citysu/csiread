"""csiread.ESP32: implemented in pure Python

Ref: [ESP32-CSI-Tool](https://github.com/StevenMHernandez/ESP32-CSI-Tool).
    Get test data from here.

Tips:
    Candidate
"""

from timeit import default_timer
import numpy as np


class ESP32:
    def __init__(self, file, if_report=True):
        self.file = file
        self.if_report = if_report

    def read(self):
        with open(self.file) as f:
            count = 0
            csi_data, int_data, float_data, str_data = [], [], [], [[], [], []]
            while True:
                line = f.readline()
                if not line:
                    break
                line = line.split(',')
                str_data[0].append(line[0])
                str_data[1].append(line[1])
                str_data[2].append(line[2])
                float_data.append(' '.join(line[23:24]))
                int_data.append(' '.join(line[3:23] + line[24:25]))
                csi_data.append(line[-1][1:-2])
                count += 1

            self.type = str_data[0]
            self.role = str_data[1]
            self.mac = str_data[2]
            group = np.fromstring(' '.join(float_data), float, sep=' ').reshape(-1, 1)
            self.real_timestamp = group[:, 0]
            group = np.fromstring(' '.join(int_data), int, sep=' ').reshape(-1, 21)
            self.rssi = group[:, 0]
            self.rate = group[:, 1]
            self.sig_mode = group[:, 2]
            self.mcs = group[:, 3]
            self.bandwidth = group[:, 4]
            self.smoothing = group[:, 5]
            self.not_sounding = group[:, 6]
            self.aggregation = group[:, 7]
            self.stbc = group[:, 8]
            self.fec_coding = group[:, 9]
            self.sgi = group[:, 10]
            self.noise_floor = group[:, 11]
            self.apmdu_cnt = group[:, 12]
            self.channel = group[:, 13]
            self.secondary_channel = group[:, 14]
            self.local_timestamp = group[:, 15]
            self.ant = group[:, 16]
            self.sig_len = group[:, 17]
            self.rx_state = group[:, 18]
            self.real_time_set = group[: 19]
            self.len = group[:, 20]
            csi = np.fromstring(' '.join(csi_data), dtype=int, sep=' ').reshape(-1, 128)
            csi = csi[:, 1::2] + csi[:, ::2] * 1.j
            self.csi_data = csi

    def seek(self, file, pos, num):
        raise NotImplementedError

    def pmsg(self, data):
        if data.startswith('CSI_DATA'):
            csi_data = data.split(',[')[1][:-1]
            csi = np.fromstring(csi_data, dtype=int, sep=' ')
            csi = csi[1::2] + csi[::2] * 1.j
            self.csi_data = csi
            return 0xf200


if __name__ == '__main__':
    last = default_timer()
    csifile = '../material/esp32/dataset/example_csi.csv'
    csidata = ESP32(csifile, if_report=True)
    csidata.read()
    print(default_timer() - last, 's')
