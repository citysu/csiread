#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""csiread example: view the contents of a packet

Note: If the csi file is stored in HDD instead of SSD, it will take
      a little longer to read it for the first time.
"""

import csiread
import time


def csitool_ap():
    """
    csitool - ap
    """
    print("="*40)
    print("csitool ap")

    last = time.time()
    csifile = "../material/5300/dataset/sample_0x1_ap.dat"
    csidata = csiread.CSI(csifile, Nrxnum=3, Ntxnum=2, pl_size=10)
    csidata.read()
    now = time.time()
    csidata.readstp()

    print('-'*40)
    lmember = [s for s in csidata.__dir__() if s[:2] != "__" and callable(getattr(csidata, s))]
    print("Methods: \n", lmember)
    print('Time:')
    print(" read                ", now - last, "s")
    last = time.time()
    total_rss = csidata.get_total_rss()
    now = time.time()
    print(" get_total_rss       ", now - last, "s")
    last = time.time()
    scaled_csi = csidata.get_scaled_csi()
    now = time.time()
    print(" get_scaled_csi      ", now - last, "s")
    last = time.time()
    scaled_csi_sm = csidata.get_scaled_csi_sm()
    # scaled_csi_sm = csidata.apply_sm(scaled_csi)
    now = time.time()
    print(" get_scaled_csi_sm   ", now - last, "s")
    print('-'*40)

    index = 10
    print("%dth packet: " % index)
    print(" file                ", csidata.file)
    print(" count               ", csidata.count)
    print(" timestamp_low       ", csidata.timestamp_low[index])
    print(" bfee_count          ", csidata.bfee_count[index])
    print(" Nrx                 ", csidata.Nrx[index])
    print(" Ntx                 ", csidata.Ntx[index])
    print(" rssiA               ", csidata.rssiA[index])
    print(" rssiB               ", csidata.rssiB[index])
    print(" rssiC               ", csidata.rssiC[index])
    print(" noise               ", csidata.noise[index])
    print(" agc                 ", csidata.agc[index])
    print(" perm                ", csidata.perm[index])
    print(" rate                ", csidata.rate[index])
    print(" csi                 ", csidata.csi[index].shape)
    print(" stp                 ", csidata.stp[index])
    print(" total_rss           ", total_rss[index])
    print(" scaled_csi.shape    ", scaled_csi[index].shape)
    print(" scaled_csi_sm.shape ", scaled_csi_sm[index].shape)
    print('-'*40)
    # print("help: \n", csidata.__doc__)


def csitool_mon():
    """
    csitool - monitor
    """
    print("="*40)
    print("csitool monitor")

    last = time.time()
    csifile = "../material/5300/dataset/sample_0x5_64_3000.dat"
    csidata = csiread.CSI(csifile, Nrxnum=3, Ntxnum=1, pl_size=10)
    csidata.read()
    now = time.time()

    print('-'*40)
    lmember = [s for s in csidata.__dir__() if s[:2] != "__" and callable(getattr(csidata, s))]
    print("Methods: \n", lmember)
    print('Time:')
    print(" read                ", now - last, "s")
    last = time.time()
    total_rss = csidata.get_total_rss()
    now = time.time()
    print(" get_total_rss       ", now - last, "s")
    last = time.time()
    scaled_csi = csidata.get_scaled_csi()
    now = time.time()
    print(" get_scaled_csi      ", now - last, "s")
    last = time.time()
    scaled_csi_sm = csidata.get_scaled_csi_sm()
    # scaled_csi_sm = csidata.apply_sm(scaled_csi)
    now = time.time()
    print(" get_scaled_csi_sm   ", now - last, "s")
    # Setting inplace to True may be dangerous but more efficient.
    csidata_temp = csiread.CSI(csifile, Nrxnum=3, Ntxnum=1, pl_size=10, if_report=False)
    csidata_temp.read()
    last = time.time()
    _ = csidata_temp.get_scaled_csi(inplace=True)       # _ is csidata_temp.csi = True
    now = time.time()
    print(" get_scaled_csi(T)   ", now - last, "s")
    csidata_temp = csiread.CSI(csifile, Nrxnum=3, Ntxnum=1, pl_size=10, if_report=False)
    csidata_temp.read()
    last = time.time()
    _ = csidata_temp.get_scaled_csi_sm(inplace=True)    # _ is csidata_temp.csi = True
    now = time.time()
    print(" get_scaled_csi_sm(T)", now - last, "s")
    print('-'*40)

    index = 10
    print("%dth packet: " % index)
    print(" file                ", csidata.file)
    print(" count               ", csidata.count)
    print(" timestamp_low       ", csidata.timestamp_low[index])
    print(" bfee_count          ", csidata.bfee_count[index])
    print(" Nrx                 ", csidata.Nrx[index])
    print(" Ntx                 ", csidata.Ntx[index])
    print(" rssiA               ", csidata.rssiA[index])
    print(" rssiB               ", csidata.rssiB[index])
    print(" rssiC               ", csidata.rssiC[index])
    print(" noise               ", csidata.noise[index])
    print(" agc                 ", csidata.agc[index])
    print(" perm                ", csidata.perm[index])
    print(" rate                ", csidata.rate[index])
    print(" csi                 ", csidata.csi[index].shape)
    print(" total_rss           ", total_rss[index])
    print(" scaled_csi.shape    ", scaled_csi[index].shape)
    print(" scaled_csi_sm.shape ", scaled_csi_sm[index].shape)

    print(" fc                  ", csidata.fc[index])
    print(" dur                 ", csidata.dur[index])
    print(" addr_src            ", ":".join([hex(per)[2:].zfill(2) for per in csidata.addr_src[index]]))
    print(" addr_des            ", ":".join([hex(per)[2:].zfill(2) for per in csidata.addr_des[index]]))
    print(" addr_bssid          ", ":".join([hex(per)[2:].zfill(2) for per in csidata.addr_bssid[index]]))
    print(" seq                 ", csidata.seq[index])
    print(" payload             ", " ".join([hex(per)[2:].zfill(2) for per in csidata.payload[index]]))
    print('-'*40)
    # print("a limitation: csidata.rate.size %d, csidata.rate.base.size %d" % (csidata.rate.size, csidata.rate.base.size))
    # print("help: \n", csidata.__doc__)


def atheros():
    """
    atheros
    """
    print("="*40)
    print("atheros")

    last = time.time()
    csifile = "../material/atheros/dataset/ath_csi_1.dat"
    csidata = csiread.Atheros(csifile, Nrxnum=3, Ntxnum=2, pl_size=10, Tones=56)
    csidata.read()
    now = time.time()
    print('-'*40)

    lmember = [s for s in csidata.__dir__() if s[:2] != "__"]
    print("Methods: \n", lmember[:1])
    print('Time:')
    print(" read                ", now - last, "s")
    print('-'*40)

    index = 10
    print("%dth packet: " % index)
    print(" file                ", csidata.file)
    print(" count               ", csidata.count)
    print(" timestamp           ", csidata.timestamp[index])
    print(" csi_len             ", csidata.csi_len[index])
    print(" tx_channel          ", csidata.tx_channel[index])
    print(" err_info            ", csidata.err_info[index])
    print(" noise_floor         ", csidata.noise_floor[index])
    print(" Rate                ", csidata.Rate[index])
    print(" bandWidth           ", csidata.bandWidth[index])
    print(" num_tones           ", csidata.num_tones[index])
    print(" nr                  ", csidata.nr[index])
    print(" nc                  ", csidata.nc[index])
    print(" rssi                ", csidata.rssi[index])
    print(" rssi_1              ", csidata.rssi_1[index])
    print(" rssi_2              ", csidata.rssi_2[index])
    print(" rssi_3              ", csidata.rssi_3[index])
    print(" payload_len         ", csidata.payload_len[index])
    print(" csi                 ", csidata.csi[index].shape)
    print(" payload             ", " ".join([hex(per)[2:].zfill(2) for per in csidata.payload[index]]))
    print('-'*40)
    # print("help: \n", csidata.__doc__)


if __name__ == "__main__":
    print("csiread.__version__: ", csiread.__version__)
    csitool_ap()
    csitool_mon()
    atheros()
