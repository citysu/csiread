#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""csiread example: view the contents of a packet

Note: If the csi file is stored in HDD instead of SSD, it will take
      a little longer to read it for the first time.
"""

from timeit import default_timer

import csiread


def intel(csifile, index, ntxnum=2):
    """csitool"""
    print("="*40+"[intel]")
    members = [s for s in dir(csiread.Intel)
               if not s.startswith("_")
               and callable(getattr(csiread.Intel, s))]
    print("Methods: \n ", members)

    print('Time:')
    last = default_timer()
    csidata = csiread.Intel(csifile, ntxnum=ntxnum, pl_size=10, if_report=False)
    csidata.read()
    print("  read                ", default_timer() - last, "s")

    last = default_timer()
    total_rss = csidata.get_total_rss()
    print("  get_total_rss       ", default_timer() - last, "s")

    last = default_timer()
    scaled_csi = csidata.get_scaled_csi()
    print("  get_scaled_csi      ", default_timer() - last, "s")

    last = default_timer()
    scaled_csi_sm = csidata.get_scaled_csi_sm()
    # scaled_csi_sm = csidata.apply_sm(scaled_csi)
    print("  get_scaled_csi_sm   ", default_timer() - last, "s")

    # Setting inplace to True may be dangerous but more efficient.
    temp = csiread.Intel(csifile, ntxnum=ntxnum, if_report=False)
    temp.read()
    last = default_timer()
    _ = temp.get_scaled_csi(inplace=True)       # _ is temp.csi == True
    print("  get_scaled_csi(T)   ", default_timer() - last, "s")

    temp = csiread.Intel(csifile, ntxnum=ntxnum, if_report=False)
    temp.read()
    last = default_timer()
    _ = temp.get_scaled_csi_sm(inplace=True)    # _ is temp.csi == True
    print("  get_scaled_csi_sm(T)", default_timer() - last, "s")

    print('-'*40)
    csidata.display(index)
    # print("a limitation: csidata.rate.size %d, csidata.rate.base.size %d" % (csidata.rate.size, csidata.rate.base.size))
    # print("help: \n", csidata.__doc__)


def atheros(csifile, index, ntxnum=2):
    """atheros"""
    print("="*40+"[atheros]")

    members = [s for s in dir(csiread.Atheros)
               if not s.startswith("_")
               and callable(getattr(csiread.Atheros, s))]
    print("Methods: \n ", members)

    print('Time:')
    last = default_timer()
    csidata = csiread.Atheros(csifile, ntxnum=ntxnum, pl_size=10, if_report=False)
    csidata.read()
    print("  read                ", default_timer() - last, "s")

    print('-'*40)
    csidata.display(index)
    # print("help: \n", csidata.__doc__)


def nexmon(csifile, index, chip, bw):
    """nexmon"""
    print("="*40+"[nexmon]")

    if csiread.__version__ < '1.3.5':
        print("csiread.Nexmon: version >= 1.3.5 is required");return

    members = [s for s in dir(csiread.Nexmon)
               if not s.startswith("_")
               and callable(getattr(csiread.Nexmon, s))]
    print("Methods: \n ", members)

    print('Time:')
    last = default_timer()
    csidata = csiread.Nexmon(csifile, chip, bw, if_report=False)
    csidata.read()
    print("  read                ", default_timer() - last, "s")

    print('-'*40)
    csidata.display(index)


def esp32(csifile, index):
    print("="*40+"[esp32]")

    if csiread.__version__ < '1.3.7':
        print("csiread.ESP32: version >= 1.3.7 is required");return

    members = [s for s in dir(csiread.ESP32)
               if not s.startswith("_")
               and callable(getattr(csiread.ESP32, s))]
    print("Methods: \n ", members)

    print('Time:')
    last = default_timer()
    csidata = csiread.ESP32(csifile, if_report=False)
    csidata.read()
    print("  read                ", default_timer() - last, "s")

    print('-'*40)
    csidata.display(index)


def picoscenes(csifile, index, pl_size):
    """picoscenes"""
    print("="*40+"[picoscenes]")

    if csiread.__version__ < '1.3.9':
        print("csiread.Picoscenes: version >= 1.3.9 is required");return

    members = [s for s in dir(csiread.Picoscenes)
               if not s.startswith("_")
               and callable(getattr(csiread.Picoscenes, s))]
    print("Methods: \n ", members)

    print('Time:')
    last = default_timer()
    csidata = csiread.Picoscenes(csifile, pl_size, False)
    csidata.read()
    print("  read                ", default_timer() - last, "s")

    last = default_timer()
    interp_csi, interp_scindex = csidata.interpolate_csi("CSI", "AP")
    print("  interpolate_csi     ", default_timer() - last, "s")

    print('-'*40)
    csidata.display(index)
    csidata.check()


if __name__ == "__main__":
    print("csiread.__version__: ", csiread.__version__)
    intel("../material/5300/dataset/sample_0x1_ap.dat", 10, ntxnum=2)
    intel("../material/5300/dataset/sample_0x5_64_3000.dat", 10, ntxnum=1)
    atheros("../material/atheros/dataset/ath_csi_1.dat", 10, ntxnum=2)
    nexmon("../material/nexmon/dataset/example.pcap", 0, '4358', 80)
    esp32("../material/esp32/dataset/example_csi.csv", 2)
    pl5300 = {
        'CSI': [30, 3, 2],
        'PilotCSI': [0, 0, 0],
        'LegacyCSI': [0, 0, 0],
        'BasebandSignals': [0, 0, 0],
        'PreEQSymbols': [0, 0, 0],
        'MPDU': 1522
    }
    pl9300 = {'CSI': [56, 3, 1], 'MPDU': 122}
    plN210 = [[56, 1, 1], [0, 0, 0], [52, 1, 1], [1040, 1, 1], [56, 6, 1], 1102]
    picoscenes("../material/picoscenes/dataset/rx_by_iwl5300.csi", 2, pl5300)
    picoscenes("../material/picoscenes/dataset/rx_by_qca9300.csi", 2, pl9300)
    picoscenes("../material/picoscenes/dataset/rx_by_usrpN210.csi", 50, plN210)
