# ChangeLog

## v1.3.7

_2021.08.08_

- fix bug(#4): typo in `Nexmon.pmsg`: chip 43455c0
- new feature: `scidx` supports 802.11ac, add `utils.phy_ifft` and `utils.phy_fft`
- new feature: add `Nexmon.group` to build spatial stream index
- new feature: add support for ESP32-CSI-Tool
- API changes: `Nexmon.pmsg(raw packet)` -> `Nexmon.pmsg(udp packet)`
- API changes: `calib(phase, bw, ng, axis)`-> `calib(phase, k, axis)`, where `k` is subcarrier index.
- update examples: improve csispotfi, csiviewer .etc

## v1.3.6

_2021.02.23_

- fix bug: Intel.timestamp_low, Athero.timestamp, Nexmon.sec and Nexmon.usec may overflow on Windows and 32-bit computers, they are stored as `np.uint64` and `np.uint32` now.
- fix bug: DeprecationWarning raised by Numpy(version >= 1.20.0)(I forgot it)

## v1.3.5

_2021.02.22_

- new features: add support for nexmon_csi
- new features: add `seek()` method and `csiread.utils` module.
- API changes: rename `csiread.CSI `to `csiread.Intel`
- API changes: rename `Intel.rssiA` to `Intel.rssi_a` .etc
- API changes: apply `lower_with_under` to method parameters
- API changes: new parameter: `bufsize`
- update examples: improve csiflask; ESP32(pure Python); `music.py` works.

## v1.3.4

_2020.11.18_

- new feature: process data faster
- new feature: add in-place operation in `csiread.CSI`
- new feature: add `CSI.pmsg()` and A`theros.pmsg()` to parse message in real time.
- new feature: both `CSI.payload` and `Atheros.payload` are MPDU and stored as `np.uint8` now.
- fix bug: `noise` will change after calling `get_scaled_csi()`
- fix bug: in matlab, `read_log_file` drops the last two packets(Atheros), but here we keep them.
- fix bug: `get_scaled_csi_sm()` value error.
- fix bug: `csiread.CSI` may not work well on big-endian computers.
- new examples: plot CSI in real time
- new example: implement `log_to_file` in pure Python
- new example: a better solution to the MemoryError

## v1.3.3

_2019.12.31_

- update examples
- new feature: add `__getitem__`
- new feature: add `get_scaled_csi_sm(), apply_sm()`

## v1.3.2

_2019.08.10_

- fix bug: choose big endian or little endian when using Atheros, e.g. csidata.read(endian='big')

## v1.3.1

_2019.07.13_

- fix bug: some value error on 32-bit computer
- fix bug: avoid built-in keyword, len -> lens
- new example: add `example/csishow.py` to plot data
- new example: add `example/csisplit.py` to split the data file of linux-80211n-tool into small pieces

## v1.3.0

_2019.06.04_

- fix bug: report format error
- fix bug: `count` value error
- new feature: add support for Atheros
- new feature: add processing functions of Intel5300: `get_scaled_csi(), get_total_rss()`
- new example
