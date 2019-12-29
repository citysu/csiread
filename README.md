# csiread

Parse channel state information from raw CSI data file in Python.

CSI can be received by [Linux 802.11n CSI Tool](https://dhalperi.github.io/linux-80211n-csitool/) and [Atheros CSI Tool](https://wands.sg/research/wifi/AtherosCSI/). It just works on Linux and Windows. If using Linux 802.11n CSI Tool, csiread can work when setting `connector_log=0x1, 0x4, 0x5`.

## Install

    cd csiread
    pip3 install -r requirements.txt
    python3 setup.py sdist bdist_wheel
    pip3 install -U dist/csiread*.whl

## Usage

    import csiread
    
    # Linux 802.11n CSI Tool
    csifile = "../material/5300/dataset/sample_0x1_ap.dat"
    csidata = csiread.CSI(csifile, Nrxnum=3, Ntxnum=1, pl_size=2)
    csidata.read()
    csi = csidata.get_scaled_csi()
    print(csidata.csi.shape)

    # Atheros CSI Tool
    csifile = "../material/atheros/dataset/ath_csi_1.dat"
    csidata = csiread.Atheros(csifile, Nrxnum=3, Ntxnum=3, pl_size=14, Tones=56)
    csidata.read(endian='little')
    print(csidata.csi.shape)

Read `example/*.py` and `csiread/csiread.pyx` for more detail.

## Material

### Intel 5300

__netlink/log_to_file.c__: record timestamp when the csi packet was received in userspace.

__injection/random_packets.c__: control the time interval more precisely when sending packets.

__injection/setup_injuect.sh__: the last two commands are exchanged to avoid some error.

__dataset/sample_0x5_64_3000.dat__: connector_log=0x5, channel_number=64, packets_count=3000,
1000packets/s, monitor mode.

__dataset/sample_0x1_ap.dat__: ap mode

__csi-get__: a shell script to start and stop `log_to_file` in ap mode

### Atheros

__recvCSI/main.c__: record timestamp when the csi packet was received in userspace.

__sendData/sendData.c__: control the time interval more precisely when sending packets.

__dataset/ath_csi_1.dat__: sample data of atheros.

## Log

### v1.3.3

1. fix bug: set max(CSI.payload size) = 500
2. new feature: add `__getitem__`

### v1.3.2

1. fix bug: choose big endian or little endian when using Atheros, e.g. csidata.read(endian='big')

### v1.3.1

1. fix bug: some value error on 32-bit computer
2. add feature: add `example/csishow.py` to plot data
3. add feature: add `example/csisplit.py` to split the data file of linux-80211n-tool into small pieces
4. fix bug: avoid built-in keyword， len -> lens

### v1.3.0

1. fix bug: report format error
2. fix bug: `count` value error
3. new feature: add suppport for atheros
4. new feature: add processing function of intel 5300: get_scaled_csi(), get_total_rss()
5. new example
