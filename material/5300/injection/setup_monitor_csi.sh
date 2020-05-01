#!/usr/bin/sudo /bin/bash
modprobe -r iwlwifi mac80211 cfg80211
modprobe iwlwifi connector_log=0x5
# Setup monitor mode, loop until it works
iwconfig wlan0 mode monitor 2>/dev/null 1>/dev/null
while [ $? -ne 0 ]
do
	iwconfig wlan0 mode monitor 2>/dev/null 1>/dev/null
done
iw wlan0 set channel $1 $2
ifconfig wlan0 up

# Increase the UDP socket buffer size to aviod 'No buffer space' at the receiver.
# sysctl net.core.rmem_default
# sysctl net.core.rmem_max
sysctl -w net.core.rmem_default 1638400
sysctl -w net.core.rmem_max 1638400