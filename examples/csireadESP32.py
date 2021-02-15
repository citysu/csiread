"""csiread.ESP32: implemented in pure Python

Note: There is no plan to implement csiread.ESP32 with Cython.

Ref: [ESP32-CSI-Tool](https://github.com/StevenMHernandez/ESP32-CSI-Tool).
    Get test data from here.
"""

from timeit import default_timer

import numpy as np
import os


class ESP32:
    def __init__(self, file, if_report=True):
        self.file = file
        self.if_report = if_report

        pk_num = self.get_count()
        self.type = np.zeros([pk_num], 'U8')
        self.role = np.zeros([pk_num], 'U8')
        self.mac = np.zeros([pk_num], 'U17')
        self.rssi = np.zeros([pk_num], np.int_)
        self.rate = np.zeros([pk_num], np.int_)
        self.sig_mode = np.zeros([pk_num], np.int_)
        self.mcs = np.zeros([pk_num], np.int_)
        self.bandwidth = np.zeros([pk_num], np.int_)
        self.smoothing = np.zeros([pk_num], np.int_)
        self.not_sounding = np.zeros([pk_num], np.int_)
        self.aggregation = np.zeros([pk_num], np.int_)
        self.stbc = np.zeros([pk_num], np.int_)
        self.fec_coding = np.zeros([pk_num], np.int_)
        self.sgi = np.zeros([pk_num], np.int_)
        self.noise_floor = np.zeros([pk_num], np.int_)
        self.apmdu_cnt = np.zeros([pk_num], np.int_)
        self.channel = np.zeros([pk_num], np.int_)
        self.secondary_channel = np.zeros([pk_num], np.int_)
        self.local_timestamp = np.zeros([pk_num], np.int_)
        self.ant = np.zeros([pk_num], np.int_)
        self.sig_len = np.zeros([pk_num], np.int_)
        self.rx_state = np.zeros([pk_num], np.int_)
        self.real_time_set = np.zeros([pk_num], np.int_)
        self.real_timestamp = np.zeros([pk_num], np.float_)
        self.len = np.zeros([pk_num], np.int_)
        self.csi_data = np.zeros([pk_num, 64], dtype=np.complex_)

    def read(self):
        with open(self.file) as f:
            count = 0
            for line in f.readlines():
                line = line.split(',')
                self.type[count] = line[0]
                self.role[count] = line[1]
                self.mac[count] = line[2]
                self.rssi[count] = int(line[3])
                self.rate[count] = int(line[4])
                self.sig_mode[count] = int(line[5])
                self.mcs[count] = int(line[6])
                self.bandwidth[count] = int(line[7])
                self.smoothing[count] = int(line[8])
                self.not_sounding[count] = int(line[9])
                self.aggregation[count] = int(line[10])
                self.stbc[count] = int(line[11])
                self.fec_coding[count] = int(line[12])
                self.sgi[count] = int(line[13])
                self.noise_floor[count] = int(line[14])
                self.apmdu_cnt[count] = int(line[15])
                self.channel[count] = int(line[16])
                self.secondary_channel[count] = int(line[17])
                self.local_timestamp[count] = int(line[18])
                self.ant[count] = int(line[19])
                self.sig_len[count] = int(line[20])
                self.rx_state[count] = int(line[21])
                self.real_time_set[count] = int(line[22])
                self.real_timestamp[count] = float(line[23])
                self.len[count] = int(line[24])
                cline = line[-1].strip('[]').split(' ')[:-1]
                csi = [int(i) + int(j) * 1.j for i, j in zip(cline[::2], cline[1::2])]
                self.csi_data[count] = csi
                count += 1

    def get_count(self):
        lens = os.path.getsize(self.file)
        with open(self.file) as f:
            linesize = len(f.readline())
        return lens // linesize

    def create_large_file(self, count):
        with open(self.file) as f:
            data = f.readline()
        with open("esp32_lagre_file.csv", 'a+') as f:
            for i in range(count):
                f.write(data)


if __name__ == '__main__':
    last = default_timer()
    csifile = '../material/esp32/dataset/example_csi.csv'
    csidata = ESP32(csifile, if_report=True)
    csidata.read()
    print(default_timer() - last, 's')
