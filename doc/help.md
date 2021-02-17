# csiread's documentation(v1.3.5)

**This documentation is incomplete and needs to be improved**

## Introduction

**csiread** aims at parsing CSI data of Intel5300, Atheros and Nexmon_csi with Python **fast**. 

|        Function         | Matlab   | Python3+Numpy | Cython+Numpy(csiread)    | file size |
|-------------------------|----------|---------------|--------------------------|-----------|
| Nexmon.read:bcm4339     | 3.2309s  | 0.2739s       | 0.0898s                  | 44.0MB    |
| Nexmon.read:bcm4358     | 3.5987s  | 23.0025s      | 0.1558s                  | 44.0MB    |
| Atheros.read            | 3.3081s  | 14.6021s      | 0.1063s                  | 76.3MB    |
| Intel.read              | 1.6102s  | 7.6624s       | 0.0529s                  | 21.0MB    |
| Intel.get_total_rss     | 0.1786s  | 0.0030s       | 0.0030s                  |           |
| Intel.get_scaled_csi    | 0.5497s  | 0.1225s       | 0.0376s/0.0278s(inplace) |           |
| Intel.get_scaled_csi_sm | 5.0097s  | 0.3627s       | 0.0778s/0.0465s(inplace) |           |

Many CSI Tools only provide Matlab API parsing CSI data files. People who want to process CSI with Python have to install Matlab to convert `.dat` to `.mat`. This process is redundant and inefficient. Therefore, **Python API** is recommended. Unfortunately, the api implemented in pure Python is inefficient. With this in mind, I implemented csiread in Cython(Pybind11 may be another great choice). The table above shows the efficiency comparison of different implementations. They were all tested with **40k** packets on the same computer.

csiread is not only the translation of the Matlab API, but also a **CSI toolbox**. I added some utilities, real-time visualization and algorithms code in the `example` folder. These would be useful for Python-based CSI researchers.

## Installation

```bash
cd csiread
pip3 install -r requirements.txt
python3 setup.py sdist bdist_wheel
pip3 install -U dist/csiread*.whl
```

`*` is a wildcard character. After running `python3 setup.py sdist bdist_wheel`,there will be a wheel file like `csiread-1.3.4-cp36-cp36m-win_amd64.whl` in the `dist` folder. Replace `csiread*.whl` with it.

csiread is written in Cython, Cython requires a C compiler to be present on the system. You can refer to [Installing Cython](https://cython.readthedocs.io/en/latest/src/quickstart/install.html) for more details. If you don't want to install a C compiler, just fork the project and push a tag to the latest commit. Then wheel files can be found in `Github-Actions-Python package-Artifacts: csiread_dist`

## Usage(API)

### csiread.csiread

------

**>< class Intel**(file, nrxnum=3, ntxnum=2, pl_size=0, if_report=True, bufsize=0)

Parse CSI obtained using 'Linux 802.11n CSI Tool'.

Args:

- **file** (*str or None*): CSI data file. If `str`, `read` and `readstp` methods are allowed. If `None`, `seek` and `pmsg` methods are allowed.
- **nrxnum** (*int, optional*): The number of receive antennas. Default: 3
- **ntxnum** (*int, optional*): The number of transmit antennas. Default: 2
- **pl_size** (*int, optional*): The size of payload to be used. Default: 0
- **if_report** (*bool, optional*): Report the parsed result. Default: `True`
- **bufsize** (*int, optional*): The maximum amount of packets to be parsed. If `0` and file is `str`, all packets will be parsed. If `0` and file is `None`, this parameter is ignored by `pmsg` method. Default: 0

Attributes:

- **file** (*str, readonly*): CSI data file.
- **count** (*int, readonly*): Count of 0xbb packets parsed
- **timestamp_low** (*ndarray*): The low 32 bits of the NIC's 1 MHz clock. It wraps about every 4300 seconds, or 72 minutes.
- **bfee_count** (*ndarray*): The count of the total number of beamforming measurements that have been recorded by the driver and sent to userspace. The netlink channel between the kernel and userspace is lossy, so these can be used to detect measurements that were dropped in this pipe.
- **Nrx** (*ndarray*): The number of antennas used to receive the packet.
- **Ntx** (*ndarray*): The number of space/time streams transmitted.
- **rssi_a** (*ndarray*): RSSI measured by the receiving NIC at the input to antenna port A. This measurement is made during the packet preamble. This value is in dB relative to an internal reference.
- **rssi_b** (*ndarray*): See `rssi_a`
- **rssi_c** (*ndarray*): See `rssi_a`
- **noise** (*ndarray*): noise
- **agc** (*ndarray*): Automatic Gain Control (AGC) setting in dB
- **perm** (*ndarray*): Tell us how the NIC permuted the signals from the 3 receive antennas into the 3 RF chains that process the measurements.
- **rate** (*ndarray*): The rate at which the packet was sent, in the same format as the rate_n_flags
- **csi** (*ndarray*): The CSI itself, normalized to an internal reference. It is a Count×30×Nrx×Ntx 4-D tensor where the second dimension is across 30 subcarriers in the OFDM channel. For a 20 MHz-wide channel, these correspond to about half the OFDM subcarriers, and for a 40 MHz-wide channel, this is about one in every 4 subcarriers.
- **stp** (*ndarray*): World timestamp recorded by the modified `log_to_file`.
- **fc** (*ndarray*): Frame control
- **dur** (*ndarray*): Duration
- **addr_des** (*ndarray*): Destination MAC address
- **addr_src** (*ndarray*): Source MAC address
- **addr_bssid** (*ndarray*): BSSID MAC address
- **seq** (*ndarray*): Sequence number of packet
- **payload** (*ndarray*): MAC frame to be used

Examples:

```python
csifile = "../material/5300/dataset/sample_0x1_ap.dat"
csidata = csiread.Intel(csifile, nrxnum=3, ntxnum=2, pl_size=10)
csidata.read()
csi = csidata.get_scaled_csi()
print(csidata.csi.shape)
```

References:

1. [Linux 802.11n CSI Tool](https://dhalperi.github.io/linux-80211n-csitool/)
2. [linux-80211n-csitool-supplementary](https://github.com/dhalperi/linux-80211n-csitool-supplementary)
3. [Linux 802.11n CSI Tool-FAQ](https://dhalperi.github.io/linux-80211n-csitool/faq.html)

------

**>< Intel.read**()

Parse data if 0xbb and 0xc1 packets

Examples:

```python
csifile = "../material/5300/dataset/sample_0x1_ap.dat"
csidata = csiread.Intel(csifile)
csidata.read()
```

------

**>< Intel.seek**(file, pos, num)

Read packets from a specific position

This method allows us to read different parts of different files randomly. It could be useful in Machine Learning. However, it could be very slow when reading files in HDD for the first time. For this case, it is better to do a pre-read with `read()` first.

Args:

- **file** (*str*): CSI data file.
- **pos** (*int*): Position of file descriptor corresponding to the packet. Currenctly, it must be returned by the function in `example/csiseek.py`.
- **num** (*int*): Number of packets to be read. `num <= bufsize` must be true. If `0`, all packets after `pos` will be read.

Examples:

```python
csifile = "../material/5300/dataset/sample_0x1_ap.dat"
csidata = csiread.Intel(None, bufsize=16)
for i in range(10):
	csidata.seek(csifile, 0, i+1)
	print(csidata.csi.shape)
```

------

**>< Intel.pmsg**(data)

Parse message in real time

Args:

- **data** (*bytes*): A bytes object representing the data received by udp socket

Returns:

- **int**: The status code. If `0xbb` and `0xc1`, parse message successfully. Otherwise, the `data` is not a CSI packet.

Examples:

```python
import socket
import csiread

csidata = csiread.Intel(None)
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
	s.bind(('127.0.0.1', 10011))
	while True:
		data, address_src = s.recvfrom(4096)
		code = csidata.pmsg(data)
		if code == 0xbb:
			print(csidata.csi.shape)
```

------

**>< Intel.get_total_rss**()

Calculates the Received Signal Strength[RSS] in dBm from CSI

Examples:

```python
csifile = "../material/5300/dataset/sample_0x1_ap.dat"
csidata = csiread.Intel(csifile)
csidata.read()
rssi = csidata.get_total_rss()
print(rssi.shape)
```

------

**>< Intel.get_scaled_csi**(inplace=False)

Converts CSI to channel matrix H

Args:

- **inplace** (*bool*): Optionally do the operation in-place. Default: False

Returns:

- **ndarray**: Channel matrix H

Examples:

```python
csifile = "../material/5300/dataset/sample_0x1_ap.dat"
csidata = csiread.Intel(csifile)
csidata.read()
scaled_csi = csidata.get_scaled_csi(False)
print(scaled_csi.shape)
print("scaled_csi is csidata.csi: ", scaled_csi is csidata.csi)
```

------

**>< Intel.get_scaled_csi_sm**(inplace=False)

Converts CSI to pure channel matrix H

This version undoes Intel's spatial mapping to return the pure MIMO channel matrix H.

Args:

- **inplace** (*bool*): Optionally do the operation in-place. Default: False

Returns:

- **ndarray**: The pure MIMO channel matrix H.

Examples:

```python
csifile = "../material/5300/dataset/sample_0x1_ap.dat"
csidata = csiread.Intel(csifile)
csidata.read()
scaled_csi_sm = csidata.get_scaled_csi_sm(False)
print(scaled_csi.shape)
print("scaled_csi_sm is csidata.csi: ", scaled_csi_sm is csidata.csi)
```

------

**>< Intel.apply_sm**(scaled_csi)

Undo the input spatial mapping

Args:

- **scaled_csi** (*ndarray*): Channel matrix H.

Returns:

- **ndarray**: The pure MIMO channel matrix H.

Examples:

```python
csifile = "../material/5300/dataset/sample_0x1_ap.dat"
csidata = csiread.Intel(csifile)
csidata.read()
scaled_csi = csidata.get_scaled_csi()
scaled_csi_sm = csidata.apply_sm(scaled_csi)
print(scaled_csi_sm.shape)
```

------

**>< Intel.readstp**(endian='little')

Parse timestamp recorded by the modified `log_to_file`

`file.dat` and `file.datstp` must be in the same directory.

Args:

- **endian** (*str*): The byte order of `file.datstp`, it can be `little` and `big`. Default: `little`

Returns:

- **int**: timestamp of the first packet.

Examples:

```python
csifile = "../material/5300/dataset/sample_0x1_ap.dat"
csidata = csiread.Intel(csifile)
first_stp = csidata.readstp()
print(first_stp)
```

------

**>< class Atheros**(file, nrxnum=3, ntxnum=2, tones=56, pl_size=0, if_report=True, bufsize=0)

Parse CSI obtained using 'Atheros CSI Tool'.

Args:

- **file** (*str or None*): CSI data file. If `str`, `read` and `readstp` methods are allowed. If `None`, `seek` and `pmsg` methods are allowed.
- **nrxnum** (*int, optional*): Number of receive antennas. Default: 3
- **ntxnum** (*int, optional*): Number of transmit antennas. Default: 2
- **tones** (*int, optional*): The number of subcarrier. It can be 56 and 114. Default: 56
- **pl_size** (*int, optional*): The size of payload to be used. Default: 0
- **if_report** (*bool, optional*): Report the parsed result. Default: `True`
- **bufsize** (*int, optional*): The maximum amount of packets to be parsed. If `0` and file is `str`, all packets will be parsed. If `0` and file is `None`, this parameter is ignored by `pmsg` method. Default: 0

Attributes:

- **file** (*str, readonly*): CSI data file
- **count** (*int, readonly*): Count of csi packets parsed
- **timestamp** (*ndarray*): The time when packet is received, expressed in μs
- **csi_len** (*ndarray*): The csi data length in the received data buffer, expressed in bytes
- **tx_channel** (*ndarray*): The center frequency of the wireless channel, expressed in MHz
- **err_info** (*ndarray*): The phy error code, set to 0 if correctly received
- **noise_floor** (*ndarray*): The noise floor, expressed in dB. But it needs to be update and is set to 0 in current version.
- **Rate** (*ndarray*): The data rate of the received packet. Its value is a unsigned 8 bit integer number and the mapping between this value and the rate choice of 802.11 protocol
- **bandWidth** (*ndarray*): The channel bandwidth. It is 20MHz if set to 0 and 40MHz if set to 1
- **num_tones** (*ndarray*): The number of subcarrier that used for data transmission.
- **nr** (*ndarray*): Number of receiving antenna
- **nc** (*ndarray*): Number of transmitting antenna
- **rsssi** (*ndarray*): The rssi of combination of all active chains
- **rssi_1** (*ndarray*): The rssi of active chain 0
- **rssi_2** (*ndarray*): The rssi of active chain 1
- **rssi_3** (*ndarray*): The rssi of active chain 2
- **payload_len** (*ndarray*): The payload length of received packet, expressed in bytes.
- **csi** (*ndarray*): CSI
- **payload** (*ndarray*): MAC frame to be used

Examples:

```python
csifile = "../material/atheros/dataset/ath_csi_1.dat"
csidata = csiread.Atheros(csifile, nrxnum=3, ntxnum=2, pl_size=10, tones=56)
csidata.read(endian='little')
print(csidata.csi.shape)
```

References:

1. [Atheros CSI Tool](https://wands.sg/research/wifi/AtherosCSI/)
2. [Atheros-CSI-Tool-UserSpace-APP](https://github.com/xieyaxiongfly/Atheros-CSI-Tool-UserSpace-APP)
3. [Atheros CSI Tool User Guide](https://wands.sg/research/wifi/AtherosCSI/document/Atheros-CSI-Tool-User-Guide.pdf)

------

**>< Atheros.read**(endian='little')

Parse data

Args：

- **endian** (*str*): The byte order of `file.dat`， it can be `little` and `big`. Default: `little`

Examples:

```python
csifile = "../material/atheros/dataset/ath_csi_1.dat"
csidata = csiread.Atheros(csifile)
csidata.read()
```

------

**>< Atheros.seek**(file, pos, num, endian='little')

Read packets from a specific position

This method allows us to read different parts of different files randomly. It could be useful in Machine Learning. However, it could be very slow when reading files in HDD for the first time. For this case, it is better to use `read()` for a pre-read first.

Args:

- **file** (*str*): CSI data file.
- **pos** (*int*): Position of file descriptor corresponding to the packet. Currenctly, it must be returned by the function in `example/csiseek.py`.
- **num** (*int*): Number of packets to be read. `num <= bufsize` must be true. If `0`, all packets after `pos` will be read.
- **endian** (*str*): The byte order of `file.dat`， it can be `little` and `big`. Default: `little`

Examples:

```python
csifile = "../material/atheros/dataset/ath_csi_1.dat"
csidata = csiread.Atheros(None, bufsize=16)
for i in range(10):
	csidata.seek(csifile, 0, i+1)
	print(csidata.csi.shape)
```

------

**>< Atheros.pmsg**(data)

Parse message in real time

Args:

- **data** (*bytes*): A bytes object representing the data received by udp socket
- **endian** (*str*): The byte order of `file.dat`， it can be `little` and `big`. Default: `little`

Returns:

- **int**: The status code. If `0xff00`, parse message successfully. Otherwise, the `data` is not a CSI packet.

Examples:

```python
import socket
import csiread

csidata = csiread.Atheros(None)
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
	s.bind(('127.0.0.1', 10011))
	while True:
		data, address_src = s.recvfrom(4096)
		code = csidata.pmsg(data)
		if code == 0xff00:
			print(csidata.csi.shape)
```

------

**>< Atheros.readstp**(endian='little')

Parse timestamp recorded by the modified `recv_csi`

`file.dat` and `file.datstp` must be in the same directory.

Args:

- **endian** (*str*): The byte order of `file.datstp`， it can be `little` and `big`. Default: `little`

Returns:

- **int**: Timestamp of the first packet.

Examples:

```python
csifile = "../material/atheros/dataset/ath_csi_1.dat"
csidata = csiread.Atheros(csifile)
first_stp = csidata.readstp()
print(first_stp)
```

------

**>< class Nexmon**(file, chip, bw, if_report=True, bufsize=0)

Parse CSI obtained using 'nexmon_csi'.

Args:

- **file** (*str or None*): CSI data file `.pcap`. If `str`, `read` methods is allowed. If `None`, `seek` and `pmsg` methods are allowed.
- **chip** (*str*): WiFi Chip, it can be '4339', '43455c0', '4358' and '4366c0'.
- **bw** (*int*): bandwidth, it can be 20, 40 and 80.
- **if_report** (*bool, optional*): Report the parsed result. Default: `True`
- **bufsize** (*int, optional*): The maximum amount of packets to be parsed. If `0` and file is `str`, all packets will be parsed. If `0` and file is `None`, this parameter is ignored by `pmsg` method. Default: 0

Attributes:

- **file** (*str, readonly*): CSI data file
- **count** (*int, readonly*): Count of csi packets parsed
- **chip** (*str, readonly*): Chip type we set
- **bw** (*int, readonly*): Bandwidth we set
- **nano** (*bool, readonly*): nanosecond-resolution or not
- **sec** (*ndarray*): Time the packet was captured
- **usec** (*ndarray*): The microseconds when this packet was captured, as an offset to `sec` if `nano` is True. The nanoseconds when the packet was captured, as an offset to `sec` if `nano` is False.
- **caplen** (*ndarray*): The number of bytes of packet data actually captured and saved in the file
- **wirelen** (*ndarray*): The length of the packet as it appeared on the network when it was captured
- **magic** (*ndarray*): Four magic bytes 0x11111111
- **src_addr** (*ndarray*): Source MAC address 
- **seq** (*ndarray*): Sequence number of the Wi-Fi frame that triggered the collection of the CSI contained in packets
- **core** (*ndarray*): Core
- **spatial** (*ndarray*): Spatial stream 
- **chan_spec** (*ndarray*): (unknown)
- **chip_version** (*ndarray*): The chip version
- **csi** (*ndarray*): CSI

Examples:

```python
csifile = "../material/nexmon/dataset/example.pcap"
csidata = csiread.Nexmon(csifile, chip='4358', bw=80)
csidata.read()
print(csidata.csi.shape)
```

References:

1. [nexmon_csi](https://github.com/seemoo-lab/nexmon_csi)
2. [rdpcap](https://github.com/secdev/scapy/blob/master/scapy/utils.py)
3. [Libpcap File Format](https://wiki.wireshark.org/Development/LibpcapFileFormat)

------

**>< Nexmon.read**()

Parse data

Examples:

```python
csifile = "../material/nexmon/dataset/example.pcap"
csidata = csiread.Nexmon(csifile, chip='4358', bw=80)
csidata.read()
print(csidata.csi.shape)
```

**>< Nexmon.seek**(file, pos, num)

Read packets from a specific position

This method allows us to read different parts of different files randomly. It could be useful in Machine Learning. However, it could be very slow when reading files in HDD for the first time. For this case, it is better to use `read()` for a pre-read first.

Args:

- **file** (*str*): CSI data file `.pcap`.
- **pos** (*int*): Position of file descriptor corresponding to the packet. Currenctly, it must be returned by the function in `example/csiseek.py`.
- **num** (*int*): Number of packets to be read. `num <= bufsize` must be true. If `0`, all packets after `pos` will be read.

Examples:

```python
csifile = "../material/nexmon/dataset/example.pcap"
csidata = csiread.Nexmon(None, chip='4358', bw=80, bufsize=4)
for i in range(4):
	csidata.seek(csifile, 0, i+1)
	print(csidata.csi.shape)
```

**>< Nexmon.pmsg**(data, endian='little')

Parse message in real time

Args:

- **data** (*bytes*): A bytes object representing the data received by raw socket
- **endian** (*str*): The byte order of `file.dat`， it can be `little` and `big`. Default: `little`

Returns:

- **int**: The status code. If `0xf100`, parse message successfully. Otherwise, the `data` is not a CSI packet.

Examples:

```python
import socket
import csiread

csidata = csiread.Nexmon(None, chip='4358', bw=80)
with socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x3)) as s:
	while True:
		data, address_src = s.recvfrom(4096)
		code = csidata.pmsg(data)
		if code == 0xf100:
			print(csidata.csi.shape)
```

### csiread.utils

------

**>< scidx**(bw, ng)

SubCarrier InDeX

Table 9-54-Number of matrices and carrier grouping

Args:

- **bw** (*int*): Bandwidth, it can be 20 and 40.
- **ng** (*int*): Grouping, it can be 1, 2 and 4.

Returns:

- **ndarray**: subcarrier index

Examples:

```python
s_index = scidx(20, 2)
```

References:
    
1. IEEE Standard for Information technology—Telecommunications and information exchange between systems Local and metropolitan area networks—Specific requirements - Part 11: Wireless LAN Medium Access Control (MAC) and Physical Layer (PHY) Specifications, in IEEE Std 802.11-2016 (Revision of IEEE Std 802.11-2012), vol., no., pp.1-3534, 14 Dec. 2016, doi: 10.1109/IEEESTD.2016.7786995.

------

**>< calib**(phase, bw=20, ng=2, axis=1)

Phase calibration

Args:

- **phase** (*ndarray*): Unwrapped phase of CSI.
- **bw** (*int*): Bandwidth, it can be 20 and 40. Default: 20
- **ng** (*int*): Grouping, it can be 1, 2 and 4. Default: 2
- **axis** (*int*): Axis along which is subcarrier. Default: 1

Returns:

- **ndarray**: Phase calibrated

Examples:

```python
csi = csidata.csi[:10]
phase = np.unwrap(np.angle(csi), axis=1)
phase = calib(phase, bw=20, ng=2, axis=1)
```

References:

1. Enabling Contactless Detection of Moving Humans with Dynamic Speeds Using CSI

## Log

### v1.3.5

1. new feature: add support for nexmon_csi
2. new feature(**todo**): add `seek()` method.
3. new feature: add some common functions in csiread/utils.py
4. new feature(**todo**): build documentation(update codestyle and docstring)
5. API changes(**todo**): rename csiread.CSI to csiread.Intel; rename Intel.rssiA to Intel.rssi_a
6. API changes(**todo**): apply lower_with_under to method parameters; add a new parameter: bufsize 
7. fix bug(**todo**): remove DeprecationWarning caused by Numpy(version >= 1.2.0)
8. update examples: improve csiflask; ESP32(pure Python); `music.py` works.

### v1.3.4

1. new feature: process data faster
2. new feature: add in-place operation in csiread.CSI
3. new feature: add CSI.pmsg() and Atheros.pmsg() to parse message in real time.
4. new feature: both CSI.payload and Atheros.payload are MPDU and stored in np.uint8 now.
5. fix bug: noise will change after calling get_scaled_csi()
6. fix bug: in matlab, read_log_file drops the last two packets(Atheros), but here we keep them.
7. fix bug: get_scaled_csi_sm() value error.
8. fix bug: csiread.CSI may not work well on big-endian computers.
9. new examples: plot CSI in real time
10. new example: implement log_to_file in pure Python
11. new example: a better solution to the MemoryError

### v1.3.3

1. update examples
2. new feature: add `__getitem__`
3. new feature: add get_scaled_csi_sm(), apply_sm()

### v1.3.2

1. fix bug: choose big endian or little endian when using Atheros, e.g. csidata.read(endian='big')

### v1.3.1

1. fix bug: some value error on 32-bit computer
2. fix bug: avoid built-in keyword, len -> lens
3. new example: add `example/csishow.py` to plot data
4. new example: add `example/csisplit.py` to split the data file of linux-80211n-tool into small pieces

### v1.3.0

1. fix bug: report format error
2. fix bug: `count` value error
3. new feature: add support for atheros
4. new feature: add processing functions of intel 5300: get_scaled_csi(), get_total_rss()
5. new example
