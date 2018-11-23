# csiread

Parse binary file obtained by 
[Linux 802.11n CSI Tool](https://dhalperi.github.io/linux-80211n-csitool/)

Parsing `.dat` file in python directly. and 4 times faster than matlab when 
parsing. the csiread tool only works when setting `connector_log=0x1, 0x4, 0x5`,
and just works on Linux

## Install 

    sudo pip3 install csiread

or  

    sudo python3 setup.py install

publish:  

    python3 setup.py sdist bdist_wheel

## Usage

    import csiread

    csipath = "sample_0x1_ap.dat"
    csidata = csiread.CSI(csipath)
    csidata.read()
    csidata.readstp()

    print(csidata.csi.shape)
    print(csidata.timestamp)
    ...
    print(csidata.Nrx)

## Material 

`log_to_file.c`: log the world timestamp of when it has receviced csi packets in userspace

`random_packets.c`: control the sequence of the packet.

`sample_0x5_64_3000.dat`: connector_log=0x5, channel_number=64, packets_count=3000

## Tip:
ap mode:

    sudo stop network-manager
    sudo modprobe -r iwlwifi mac80211
    sudo modprobe iwlwifi connector_log=0x1

    sudo ifconfig wlan0 up
    sudo iw dev wlan0 connect <BSSID>
    sudo dhcpcd wlan0

monitor mode: 

    sudo stop network-manager

    ./setup_inject.sh 64 HT20
    sudo echo 0x4101 | sudo tee `sudo find /sys -name monitor_tx_rate`
    sudo ./seq_packets 10000 100 1 1000

setup_inject.sh:

    ...
    ifconfig mon0 up
    iw mon0 set channel $1 $2
