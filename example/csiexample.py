#!/usr/bin python3
# -*- coding: utf-8 -*-

"""
csiread example
"""

import csiread
import time


def csitool_ap():
    """
    csitool - ap
    """
    print("="*40)
    print("csitool ap")

    csipath = "../material/5300/dataset/sample_0x1_ap.dat"
    csidata = csiread.CSI(csipath, Nrxnum=3, Ntxnum=3, pl_size=2)
    last = time.time()
    csidata.read()
    now = time.time()
    csidata.readstp()
    print('-'*40)

    lmember = [s for s in csidata.__dir__() if s[:2] != "__"]
    print("Methods: ", lmember[:3], lmember[5])
    print("Total time: ", now - last, "s")

    index = 10
    print("%dth packet: " % index)
    print(" filepath        ", csidata.filepath)
    print(" count           ", csidata.count)
    print(" timestamp_low   ", csidata.timestamp_low[index])
    print(" bfee_count      ", csidata.bfee_count[index])
    print(" Nrx             ", csidata.Nrx[index])
    print(" Ntx             ", csidata.Ntx[index])
    print(" rssiA           ", csidata.rssiA[index])
    print(" rssiB           ", csidata.rssiB[index])
    print(" rssiC           ", csidata.rssiC[index])
    print(" noise           ", csidata.noise[index])
    print(" agc             ", csidata.agc[index])
    print(" perm            ", csidata.perm[index])
    print(" rate            ", csidata.rate[index])
    print(" csi             ", csidata.csi[index].shape)
    print(" stp             ", csidata.stp[index])
    print('*'*40)
    print(" total_rss       ", csidata.get_total_rss()[index])
    print(" scaled_csi      ", csidata.get_scaled_csi()[index].shape)
    print('-'*40)
    # print("help: \n", csidata.__doc__)


def csitool_mon():
    """
    csitool - monitor
    """
    print("="*40)
    print("csitool monitor")

    csipath = "../material/5300/dataset/sample_0x5_64_3000.dat"
    csidata = csiread.CSI(csipath, Nrxnum=3, Ntxnum=1, pl_size=2)
    last = time.time()
    csidata.read()
    now = time.time()
    print('-'*40)

    lmember = [s for s in csidata.__dir__() if s[:2] != "__"]
    print("Methods: ", lmember[:3], lmember[5])
    print("Total time: ", now - last, "s")

    index = 10
    addr_src = ''
    for per_addr in csidata.addr_src[index]:
        addr_src += hex(per_addr)[2:] + ":"
    print("%dth packet: " % index)
    print(" filepath        ", csidata.filepath)
    print(" count           ", csidata.count)
    print(" timestamp_low   ", csidata.timestamp_low[index])
    print(" bfee_count      ", csidata.bfee_count[index])
    print(" Nrx             ", csidata.Nrx[index])
    print(" Ntx             ", csidata.Ntx[index])
    print(" rssiA           ", csidata.rssiA[index])
    print(" rssiB           ", csidata.rssiB[index])
    print(" rssiC           ", csidata.rssiC[index])
    print(" noise           ", csidata.noise[index])
    print(" agc             ", csidata.agc[index])
    print(" perm            ", csidata.perm[index])
    print(" rate            ", csidata.rate[index])
    print(" csi             ", csidata.csi[index].shape)
    print(" 0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0")
    print(" fc              ", csidata.fc[index])
    print(" dur             ", csidata.dur[index])
    print(" addr_src        ", ":".join([hex(per_addr)[2:] for per_addr in csidata.addr_src[index]]))
    print(" addr_des        ", ":".join([hex(per_addr)[2:] for per_addr in csidata.addr_des[index]]))
    print(" addr_bssid      ", ":".join([hex(per_addr)[2:] for per_addr in csidata.addr_bssid[index]]))
    print(" seq             ", csidata.seq[index])
    print(" payload         ", " ".join([hex(per_load)[2:] for per_load in csidata.payload[index]]))
    print('-'*40)
    # print("help: \n", csidata.__doc__)


def atheros():
    """
    atheros
    """
    print("="*40)
    print("atheros")

    csipath = "../material/atheros/dataset/ath_csi_1.dat"
    csidata = csiread.Atheros(csipath, Nrxnum=3, Ntxnum=3, pl_size=14, Tones=56)
    last = time.time()
    csidata.read()
    now = time.time()
    print('-'*40)

    lmember = [s for s in csidata.__dir__() if s[:2] != "__"]
    print("Methods: ", lmember[:1])
    print("Total time: ", now - last, "s")

    index = 10
    print("%dth packet: " % index)
    print(" filepath        ", csidata.filepath)
    print(" count           ", csidata.count)
    print(" timestamp       ", csidata.timestamp[index])
    print(" csi_len         ", csidata.csi_len[index])
    print(" tx_channel      ", csidata.tx_channel[index])
    print(" err_info        ", csidata.err_info[index])
    print(" noise_floor     ", csidata.noise_floor[index])
    print(" Rate            ", csidata.Rate[index])
    print(" bandWidth       ", csidata.bandWidth[index])
    print(" num_tones       ", csidata.num_tones[index])
    print(" nr              ", csidata.nr[index])
    print(" nc              ", csidata.nc[index])
    print(" rssi            ", csidata.rssi[index])
    print(" rssi_1          ", csidata.rssi_1[index])
    print(" rssi_2          ", csidata.rssi_2[index])
    print(" rssi_3          ", csidata.rssi_3[index])
    print(" payload_len     ", csidata.payload_len[index])
    print(" csi             ", csidata.csi[index].shape)
    print(" payload         ", csidata.payload[index])
    print('-'*40)
    # print("help: \n", csidata.__doc__)


if __name__ == "__main__":
    print("csiread.__version__: ", csiread.__version__)
    csitool_ap()
    csitool_mon()
    atheros()
