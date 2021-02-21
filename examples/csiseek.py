"""How to use seek() method

Usage:
    python3 csiseek.py

Note:
    1. This example should be tested with large files.
    2. ...
"""
import csiread
import os
import random
from timeit import default_timer
from utils import infer_device


def getPos(csifile):
    device = infer_device(csifile)
    if device == 'Intel':
        return getPosIntel(csifile)
    elif device == 'Atheros':
        return getPosAtheros(csifile)
    else:
        return getPosNexmon(csifile)


def getPosIntel(csifile):
    lens = os.path.getsize(csifile)
    cur, positions = 0, []
    last = [None, None]
    with open(csifile, 'rb') as f:
        while cur < (lens - 3):
            field_len = int.from_bytes(f.read(2), byteorder='big')
            code = int.from_bytes(f.read(1), byteorder='little')
            if code == 0xbb:
                if last[0] == 0xc1:
                    positions.append(cur - last[1] - 2)
                else:
                    positions.append(cur)
            last = [code, field_len]
            cur += (field_len + 2)
            f.seek(field_len - 1, os.SEEK_CUR)
    return positions


def getPosAtheros(csifile):
    lens = os.path.getsize(csifile)
    cur, positions = 0, []
    with open(csifile, 'rb') as f:
        while cur < (lens - 4):
            field_len = int.from_bytes(f.read(2), byteorder='little')
            f.seek(field_len, os.SEEK_CUR)
            positions.append(cur)
            cur += (field_len + 2)
    return positions


def getPosNexmon(csifile):
    lens = os.path.getsize(csifile)
    cur, positions = 24, []
    with open(csifile, 'rb') as f:
        magic = f.read(4)
        f.seek(20, os.SEEK_CUR)
        if magic in [b"\xa1\xb2\xc3\xd4", b"\xa1\xb2\x3c\x4d"]:
            endian = 'big'
        else:
            endian = 'little'
        while cur < (lens - 4):
            caplen = int.from_bytes(f.read(16)[8:12], byteorder=endian)
            if f.read(42)[6:12] == b'NEXMON':
                positions.append(cur)
            f.seek(caplen - 42, os.SEEK_CUR)
            cur += (caplen + 16)
    return positions


def seekIntel(csifile, num=36):
    positions_all = getPos(csifile)
    positions = positions_all[::num][:-1]
    random.shuffle(positions)
    print("-"*40, "[Intel]")

    last = default_timer()
    csidata = csiread.Intel(csifile, 3, 2, 0, False)
    csidata.read()
    cost_time = default_timer() - last
    print("%-18s: %18fs" % ("read()", cost_time))

    last = default_timer()
    csidata = csiread.Intel(None, 3, 2, 0, False, bufsize=num)
    for pos in positions:
        csidata.seek(csifile, pos, num)
    cost_time = (default_timer() - last) * len(positions_all) / (len(positions) * num)
    print("%-18s: %18fs" % ("seek(num=%d)" % (num), cost_time))


def seekAtheros(csifile, num=36):
    positions_all = getPos(csifile)
    positions = positions_all[::num][:-1]
    random.shuffle(positions)
    print("-"*40, "[Atheros]")

    last = default_timer()
    csidata = csiread.Atheros(csifile, 3, 2, 0, 56, False)
    csidata.read()
    cost_time = default_timer() - last
    print("%-18s: %18fs" % ("read()", cost_time))

    last = default_timer()
    csidata = csiread.Atheros(None, 3, 2, 0, 56, False, bufsize=num)
    for pos in positions:
        csidata.seek(csifile, pos, num)
    cost_time = (default_timer() - last) * len(positions_all) / (len(positions) * num)
    print("%-18s: %18fs" % ("seek(num=%d)" % (num), cost_time))


def seekNexmon(csifile, num=36):
    positions_all = getPos(csifile)
    positions = positions_all[::num][:-1]
    random.shuffle(positions)
    print("-"*40, "[Nexmon]")

    last = default_timer()
    csidata = csiread.Nexmon(csifile, '4358', 80, if_report=False)
    csidata.read()
    cost_time = default_timer() - last
    print("%-18s: %18fs" % ("read()", cost_time))

    last = default_timer()
    csidata = csiread.Nexmon(None, '4358', 80, if_report=False, bufsize=num)
    for pos in positions:
        csidata.seek(csifile, pos, num)
    cost_time = (default_timer() - last) * len(positions_all) / (len(positions) * num)
    print("%-18s: %18fs" % ("seek(num=%d)" % (num), cost_time))


if __name__ == "__main__":
    csifile_intel = "../material/5300/dataset/sample_0x5_64_3000.dat"
    csifile_atheros = "../material/atheros/dataset/ath_csi_1.dat"
    csifile_nexmon = "../material/nexmon/dataset/example.pcap"
    seekIntel(csifile_intel, 64)
    seekAtheros(csifile_atheros, 64)
    seekNexmon(csifile_nexmon, 2)
