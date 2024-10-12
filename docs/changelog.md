# ChangeLog

## v1.4.1

- fix bug(#21): `nrxnum` and `ntxnum` should not be checked if `csi_len == 0`.
- fix bug(#31): it can be built with Cython>=3.0
- fix bug(#36): `NexmonPull46.rssi` should be parsed as `int8`.
- fix bug(#38): `buf_noise_mem` is not initialized in `get_scaled_csi()` method.
- fix bug: k_1 should be k[0] in `utils.calib`.
- compatibility: works with numpy2.0 (#37).
- update examples: upgrade dependencies of some examples
- fix some typos.

## v1.4.0

_2022.01.24_

- update: add `NexmonPull256`
- experimental feature: add support for PicoScenes
- improvement: improve `seek(..., num=1)`
- improvement: improve `get_total_rss`, `get_scaled_csi` and `get_scaled_csi_sm`. They were inefficient in a loop.
- fix bug: `import csiread` in an ipython shell raised `NameError: name 'exit' is not defined`
- fix bug(#18): `pyproject.toml` is required when executing `pip install <*.tar.gz from pypi>`

## v1.3.8

_2021.10.08_

- fix bug: typo(#11): `resahpe` -> `reshape`
- fix bug: exit abnormally if file does not exist.
- fix bug: two bytes contain core and spatial stream number(Nexmon), one is always zero. `or` them to avoid endian issue now.
- fix bug: `setup.py`: Get the compiler type correctly
- new feature: add `display` method to view a packet quickly.

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
- new feature: add `CSI.pmsg()` and `Atheros.pmsg()` to parse message in real time.
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
