# Material

All the files are from [linux-80211n-csitool-supplementary](https://github.com/dhalperi/linux-80211n-csitool-supplementary), [Atheros-CSI-Tool-UserSpace-APP](https://github.com/xieyaxiongfly/Atheros-CSI-Tool-UserSpace-APP), [nexmon_csi](https://github.com/seemoo-lab/nexmon_csi) and [ESP32-CSI-Tool](https://github.com/StevenMHernandez/ESP32-CSI-Tool) expect `5300/dataset` and `atheros/dataset`. Some of them were modified.

## Intel 5300

__netlink/log_to_file.c__: record timestamp when the csi packet was received in userspace.

__injection/random_packets.c__: control the time interval more precisely when sending packets.

__injection/setup_monitor_csi.sh__: increase the UDP socket buffer size to aviod 'No buffer space' at the receiver.

__injection/setup_inject.sh__: the last two commands are exchanged to avoid some error.

__dataset/sample_0x5_64_3000.dat__: connector_log=0x5, channel_number=64, packets_count=3000,
1000packets/s, monitor mode.

__dataset/sample_0x1_ap.dat__: ap mode

## Atheros

__recvCSI/main.c__: record timestamp when the csi packet was received in userspace.

__sendData/sendData.c__: control the time interval more precisely when sending packets.

__dataset/ath_csi_1.dat__: sample data of atheros.