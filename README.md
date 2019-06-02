# csiread

Parse channel state information obtained by
[Linux 802.11n CSI Tool](https://dhalperi.github.io/linux-80211n-csitool/) and
[Atheros CSI Tool](https://wands.sg/research/wifi/AtherosCSI/)

Parse `.dat` file in python directly, the code has been speed up with
`Cython`, and it just works on Linux and Windows,

If using CSITool, csiread can work when setting `connector_log=0x1, 0x4, 0x5`.

## Install

    cd csiread
    python3 setup.py sdist bdist_wheel
    sudo pip3 install dist/csiread*.whl

## Usage

    import csiread

    # Linux 802.11n CSI Tool
    csipath = "../material/5300/dataset/sample_0x1_ap.dat"
    csidata = csiread.CSI(csipath, Nrxnum=3, Ntxnum=1, pl_size=2)
    csidata.read()
    print(csidata.csi.shape)

    # Atheros CSI Tool
    csipath = "../material/atheros/dataset/ath_csi_1.dat"
    csidata = csiread.Atheros(csipath, Nrxnum=3, Ntxnum=3, pl_size=14, Tones=56)
    csidata.read()
    print(csidata.csi.shape)

read `example/csiexample.py` and `csiread/csiread.pyx` for more detail.

## Material

### 5300

__netlink/log_to_file.c__: log the world timestamp of when it has receviced csi packets in userspace.

__injection/random_packets.c__: Use timing threads to control time intervals, and set the serial number of the packet, but be careful, it's not the serial number of csi.

__injection/setup_injuect.sh__: The last two commands are exchanged to aviod some error.

__dataset/sample_0x5_64_3000.dat__: connector_log=0x5, channel_number=64, packets_count=3000, monitor mode

__dataset/sample_0x1_ap.dat__: ap mode

__csi-get__: a shell script to log csi and stop in ap mode

first o all, you have to run the command `sudo stop network-manager` or `sudo service network-manager stop`.

### atheros

__recvCSI/main.c__:log the world timestamp of when it has receviced csi packets in userspace.

__sendData/sendData.c__: Use timing threads to control time intervals, and contorl delay time in Termianl

__dataset/ath_csi_1.dat__: sample data of atheros.

## Log

### v1.3.0

1. fix bug: report 的格式错误
2. fix bug: count 以后将仅仅是0xbb数据包的个数
3. fix bug: count 大于正确数值的错误
4. new feature: 添加 atheros数据解析支持
5. new feature: 添加 csitool处理函数 get_scaled_csi(), get_total_rss()
6. new example