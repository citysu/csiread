#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""csiread example: view the contents of a packet

Note: If the csi file is stored in HDD instead of SSD, it will take
      a little longer to read it for the first time.
"""

from timeit import default_timer

import csiread


def stringify(array, space=':'):
    return space.join([hex(element)[2:].zfill(2) for element in array])


def intel(csifile, index, ntxnum=2):
    """csitool"""
    print("="*40+"[intel]")
    members = [s for s in dir(csiread.Intel) if not s.startswith("__") and callable(getattr(csiread.Intel, s))]
    print("Methods: \n", members)

    print('Time:')
    last = default_timer()
    csidata = csiread.Intel(csifile, ntxnum=ntxnum, pl_size=10, if_report=False)
    csidata.read()
    print(" read                ", default_timer() - last, "s")

    last = default_timer()
    total_rss = csidata.get_total_rss()
    print(" get_total_rss       ", default_timer() - last, "s")

    last = default_timer()
    scaled_csi = csidata.get_scaled_csi()
    print(" get_scaled_csi      ", default_timer() - last, "s")

    last = default_timer()
    scaled_csi_sm = csidata.get_scaled_csi_sm()
    # scaled_csi_sm = csidata.apply_sm(scaled_csi)
    print(" get_scaled_csi_sm   ", default_timer() - last, "s")

    # Setting inplace to True may be dangerous but more efficient.
    temp = csiread.Intel(csifile, ntxnum=ntxnum, if_report=False)
    temp.read()
    last = default_timer()
    _ = temp.get_scaled_csi(inplace=True)       # _ is temp.csi == True
    print(" get_scaled_csi(T)   ", default_timer() - last, "s")

    temp = csiread.Intel(csifile, ntxnum=ntxnum, if_report=False)
    temp.read()
    last = default_timer()
    _ = temp.get_scaled_csi_sm(inplace=True)    # _ is temp.csi == True
    print(" get_scaled_csi_sm(T)", default_timer() - last, "s")

    print('-'*40)
    print("%dth packet: " % index)
    print(" file                ", csidata.file)
    print(" count               ", csidata.count)
    print(" timestamp_low       ", csidata.timestamp_low[index])
    print(" bfee_count          ", csidata.bfee_count[index])
    print(" Nrx                 ", csidata.Nrx[index])
    print(" Ntx                 ", csidata.Ntx[index])
    print(" rssi_a              ", csidata.rssi_a[index])
    print(" rssi_b              ", csidata.rssi_b[index])
    print(" rssi_c              ", csidata.rssi_c[index])
    print(" noise               ", csidata.noise[index])
    print(" agc                 ", csidata.agc[index])
    print(" perm                ", csidata.perm[index])
    print(" rate                ", csidata.rate[index])
    print(" csi                 ", csidata.csi[index].shape)
    print(" total_rss           ", total_rss[index])
    print(" scaled_csi.shape    ", scaled_csi[index].shape)
    print(" scaled_csi_sm.shape ", scaled_csi_sm[index].shape)
    if csidata.fc.size > index:
        print(" fc                  ", csidata.fc[index])
        print(" dur                 ", csidata.dur[index])
        print(" addr_src            ", stringify(csidata.addr_src[index], ":"))
        print(" addr_des            ", stringify(csidata.addr_des[index], ":"))
        print(" addr_bssid          ", stringify(csidata.addr_bssid[index], ":"))
        print(" seq                 ", csidata.seq[index])
        print(" payload             ", stringify(csidata.payload[index], " "))
    # print("a limitation: csidata.rate.size %d, csidata.rate.base.size %d" % (csidata.rate.size, csidata.rate.base.size))
    # print("help: \n", csidata.__doc__)


def atheros(csifile, index, ntxnum=2):
    """atheros"""
    print("="*40+"[atheros]")

    members = [s for s in dir(csiread.Atheros) if not s.startswith("__") and callable(getattr(csiread.Atheros, s))]
    print("Methods: \n", members)

    print('Time:')
    last = default_timer()
    csidata = csiread.Atheros(csifile, ntxnum=ntxnum, pl_size=10, if_report=False)
    csidata.read()
    print(" read                ", default_timer() - last, "s")

    print('-'*40)
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
    # print("help: \n", csidata.__doc__)


def nexmon(csifile, index, chip, bw):
    """nexmon"""
    print("="*40+"[nexmon]")

    if csiread.__version__ < '1.3.5':
        print("csiread.Nexmon: version >= 1.3.5 is required");return

    members = [s for s in dir(csiread.Nexmon) if not s.startswith("__") and callable(getattr(csiread.Nexmon, s))]
    print("Methods: \n", members)

    print('Time:')
    last = default_timer()
    csidata = csiread.Nexmon(csifile, chip, bw, if_report=False)
    csidata.read()
    print(" read                ", default_timer() - last, "s")

    print('-'*40)
    print("%dth packet: " % index)
    print(" file                ", csidata.file)
    print(" count               ", csidata.count)
    print(" chip                ", csidata.chip)
    print(" bw                  ", csidata.bw)
    print(" nano                ", csidata.nano)
    print(" sec                 ", csidata.sec[index])
    print(" usec                ", csidata.usec[index])
    print(" caplen              ", csidata.caplen[index])
    print(" wirelen             ", csidata.wirelen[index])
    print(" magic               ", hex(csidata.magic[index]))
    print(" src_addr            ", stringify(csidata.src_addr[index], ":"))
    print(" seq                 ", csidata.seq[index])
    print(" core                ", csidata.core[index])
    print(" spatial             ", csidata.spatial[index])
    print(" chan_spec           ", csidata.chan_spec[index])
    print(" chip_version        ", csidata.chip_version[index])
    print(" csi                 ", csidata.csi[index].shape)


def esp32(csifile, index):
    print("="*40+"[esp32]")

    if csiread.__version__ < '1.3.7':
        print("csiread.ESP32: version >= 1.3.7 is required");return

    members = [s for s in dir(csiread.ESP32) if not s.startswith("__") and callable(getattr(csiread.ESP32, s))]
    print("Methods: \n", members)

    print('Time:')
    last = default_timer()
    csidata = csiread.ESP32(csifile, if_report=False)
    csidata.read()
    print(" read                ", default_timer() - last, "s")

    print('-'*40)
    print("%dth packet: " % index)
    print(" file                ", csidata.file)
    print(" count               ", csidata.count)
    print(" type                ", csidata.type[index])
    print(" role                ", csidata.role[index])
    print(" mac                 ", csidata.mac[index])
    print(" rssi                ", csidata.rssi[index])
    print(" rate                ", csidata.rate[index])
    print(" sig_mode            ", csidata.sig_mode[index])
    print(" mcs                 ", csidata.mcs[index])
    print(" bandwidth           ", csidata.bandwidth[index])
    print(" smoothing           ", csidata.smoothing[index])
    print(" not_sounding        ", csidata.not_sounding[index])
    print(" aggregation         ", csidata.aggregation[index])
    print(" stbc                ", csidata.stbc[index])
    print(" fec_coding          ", csidata.fec_coding[index])
    print(" sgi                 ", csidata.sgi[index])
    print(" noise_floor         ", csidata.noise_floor[index])
    print(" ampdu_cnt           ", csidata.ampdu_cnt[index])
    print(" channel             ", csidata.channel[index])
    print(" secondary_channel   ", csidata.secondary_channel[index])
    print(" local_timestamp     ", csidata.local_timestamp[index])
    print(" ant                 ", csidata.ant[index])
    print(" sig_len             ", csidata.sig_len[index])
    print(" rx_state            ", csidata.rx_state[index])
    print(" real_time_set       ", csidata.real_time_set[index])
    print(" real_timestamp      ", csidata.real_timestamp[index])
    print(" len                 ", csidata.len[index])
    print(" csi                 ", csidata.csi[index].shape)


if __name__ == "__main__":
    print("csiread.__version__: ", csiread.__version__)
    intel("../material/5300/dataset/sample_0x1_ap.dat", 10, ntxnum=2)
    intel("../material/5300/dataset/sample_0x5_64_3000.dat", 10, ntxnum=1)
    atheros("../material/atheros/dataset/ath_csi_1.dat", 10, ntxnum=2)
    nexmon("../material/nexmon/dataset/example.pcap", 0, '4358', 80)
    esp32("../material/esp32/dataset/example_csi.csv", 2)
