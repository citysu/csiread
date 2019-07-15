# csiread

Parse channel state information from raw CSI data file obtained by
[Linux 802.11n CSI Tool](https://dhalperi.github.io/linux-80211n-csitool/) and
[Atheros CSI Tool](https://wands.sg/research/wifi/AtherosCSI/)

Parse `.dat` file in python directly, the code has been optimized with
`Cython`, and it just works on Linux and Windows,

If using Linux 802.11n CSI Tool, csiread can work when setting `connector_log=0x1, 0x4, 0x5`.

## Install

    cd csiread
    python3 setup.py sdist bdist_wheel
    sudo pip3 install -U dist/csiread*.whl

## Usage

    import csiread
    
    # Linux 802.11n CSI Tool
    csipath = "../material/5300/dataset/sample_0x1_ap.dat"
    csidata = csiread.CSI(csipath, Nrxnum=3, Ntxnum=1, pl_size=2)
    csidata.read()
    print(csidata.csi.shape)
    csi = csidata.get_scaled_csi()
    
    # Atheros CSI Tool
    csipath = "../material/atheros/dataset/ath_csi_1.dat"
    csidata = csiread.Atheros(csipath, Nrxnum=3, Ntxnum=3, pl_size=14, Tones=56)
    csidata.read(endian='little')
    print(csidata.csi.shape)

Read `example/*.py` and `csiread/csiread.pyx` for more detail.

1. `example/csiexample.py` is an example to view the contents of a packet
2. `example/csishow.py` is a script to help you observe csi quickly
3. `example/csisplit.py` is a script to split the data file of linux-80211n-tool into small pieces

## Material

### 5300

__netlink/log_to_file.c__: Record the timestamp when the csi packet was received in userspace.

__injection/random_packets.c__: Control the time interval more precisely when sending packets.

__injection/setup_injuect.sh__: The last two commands are exchanged to avoid some errors.

__dataset/sample_0x5_64_3000.dat__: connector_log=0x5, channel_number=64, packets_count=3000, 1000packets/s, monitor mode.

__dataset/sample_0x1_ap.dat__: ap mode

__csi-get__: a shell script to start and stop `log_to_file` in ap mode

First of all, you have to run the command `sudo stop network-manager` or `sudo service network-manager stop`.

### atheros

__recvCSI/main.c__: Record the timestamp when the csi packet was received in userspace.

__sendData/sendData.c__: Control the time interval more precisely when sending packets.

__dataset/ath_csi_1.dat__: Sample data of atheros.

## Log

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

