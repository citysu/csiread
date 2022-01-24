# csiread [![PyPI](https://img.shields.io/pypi/v/csiread?)](https://pypi.org/project/csiread/)

A **fast** channel state information parser for Intel, Atheros, Nexmon, ESP32 and PicoScenes in Python.

- Full support for [Linux 802.11n CSI Tool](https://dhalperi.github.io/linux-80211n-csitool/), [Atheros CSI Tool](https://wands.sg/research/wifi/AtherosCSI/), [nexmon_csi](https://github.com/seemoo-lab/nexmon_csi) and [ESP32-CSI-Tool](https://github.com/StevenMHernandez/ESP32-CSI-Tool)
- Support for [PicoScenes](https://ps.zpj.io) is **experimental**.
- At least 15 times faster than the implementation in Matlab
- Real-time parsing and visualization.

<center><b>real-time plotting</b></center>

![real-time plotting](https://github.com/citysu/csiread/blob/master/docs/sample2.png)

## Introduction

Various CSI Tools only provide Matlab API parsing CSI data files. Those who want to process CSI with Python have to install Matlab to convert `.dat` to `.mat`. This process is redundant and inefficient. Therefore, **Python API** is recommended. Unfortunately, the API implemented in pure Python is inefficient. With this in mind, I implemented csiread in Cython(Pybind11 may be another great choice). The table below shows the performance of different implementations. They were all tested with **40k** packets on the same computer.

|        Function         | Matlab   | Python3+Numpy | csiread    | file size |
|-------------------------|----------|---------------|------------|-----------|
| Nexmon.read:bcm4339     | 3.2309s  | 0.2739s       | 0.0703s    | 44.0MB    |
| Nexmon.read:bcm4358     | 3.5987s  | 23.0025s      | 0.1227s    | 44.0MB    |
| Atheros.read            | 3.3081s  | 14.6021s      | 0.0956s    | 76.3MB    |
| Intel.read              | 1.6102s  | 7.6624s       | 0.0479s    | 21.0MB    |
| Intel.get_total_rss     | 0.1786s  | 0.0030s       | 0.0030s    |           |
| Intel.get_scaled_csi    | 0.5497s  | 0.1225s       | 0.0376s/0.0278s |      |
| Intel.get_scaled_csi_sm | 5.0097s  | 0.3627s       | 0.0778s/0.0465s |      |

This tool is not only the translation of the Matlab API, but also a **CSI toolbox**. I added some utilities, real-time visualization and algorithms code in the `examples` folder. These would be useful for Python-based CSI researchers.

## Install

```bash
pip3 install csiread
```

## Quickstart

```python
import csiread

# Linux 802.11n CSI Tool
csifile = "../material/5300/dataset/sample_0x1_ap.dat"
csidata = csiread.Intel(csifile, nrxnum=3, ntxnum=2, pl_size=10)
csidata.read()
csi = csidata.get_scaled_csi()
print(csidata.csi.shape)

# Atheros CSI Tool
csifile = "../material/atheros/dataset/ath_csi_1.dat"
csidata = csiread.Atheros(csifile, nrxnum=3, ntxnum=2, pl_size=10, tones=56)
csidata.read(endian='little')
print(csidata.csi.shape)

# nexmon_csi
csifile = "../material/nexmon/dataset/example.pcap"
csidata = csiread.Nexmon(csifile, chip='4358', bw=80)
csidata.read()
print(csidata.csi.shape)

# ESP32-CSI-Tool
csifile = "../material/esp32/dataset/example_csi.csv"
csidata = csiread.ESP32(csifile, csi_only=True)
csidata.read()
print(csidata.csi.shape)

# PicoScenes
csifile = "../material/picoscenes/dataset/rx_by_iwl5300.csi"
csidata = csiread.Picoscenes(csifile, {'CSI': [30, 3, 2], 'MPDU': 1522})
csidata.read()
csidata.check()
print(csidata.raw['CSI']['CSI'].shape)
```

`examples` are the best usage instructions. The API documentation can be found in `docstring` of file `core.py`, so we won't repeat them here.

## Build from source

```bash
cd csiread
pip3 install -r requirements.txt
python3 setup.py sdist bdist_wheel
pip3 install -U dist/csiread*.whl
```

`*` is a shell wildcard. After running `python3 setup.py sdist bdist_wheel`,there will be a wheel file like `csiread-1.3.4-cp36-cp36m-win_amd64.whl` in the `dist` folder. Replace `csiread*.whl` with it.

csiread is written in Cython, Cython requires a C compiler to be present on the system. You can refer to [Installing Cython](https://cython.readthedocs.io/en/latest/src/quickstart/install.html) for more details. If you don't want to install a C compiler, just fork the project and push a tag to the latest commit. Then wheel files can be found in `Github-Actions-Python package-Artifacts: csiread_dist`

## Design

csiread provides 7 classes: `Intel, Atheros, Nexmon, AtherosPull10, NexmonPull46, ESP32 and Picoscenes`. Each class has 4 key methods: `read(), seek()`, `pmsg()` and `display()` which are used for reading a file, reading a file from a specific position, real-time parsing and viewing the contents of a packet respectively. `csiread.utils` provides some common functions.

### Nexmon CSI

- `csiread.Nexmon` is based on the commit of nexmon_csi(Aug 29, 2020): `ba99ce12a6a42d7e4ec75e6f8ace8f610ed2eb60`
- `csiread.NexmonPull256` is the same as `csiread.NexmonPull46`. It works with the latest master branch (Dec 11, 2021): `c037576b7035619e2716229c7622f4e8c511635f`
- The `Nexmon.group` is experimental, it may be incorrect due to `core` and `spatial`. `core` and `spatial` are ZERO or not recorded correctly in some files. I don't know how to solve it.

### ESP32-CSI-Tool

- `pandas.read_csv` and `csiread.ESP32` have the similar performance, but `pandas.read_csv` is much more flexible.

### PicoScenes

The support for Picoscenes is an **experimental** feature. PicoScenes is still under active development, csiread cannot be updated synchronously.

- `csidata.raw` is a [structured array](https://numpy.org/doc/stable/user/basics.rec.html#structured-arrays) in numpy and stores the parsed result. 
- `Mag` and `Phase` fileds have been removed, use `np.abs` and `np.angle` instead.
- Call `check()` method after `read()`, Then set `pl_size` according to the report.
- Edge padding are applied to `raw["xxx"]["SubcarrierIndex"]` for plotting.
- The method `pmsg` has been implemented, but not yet ready.
- Accessing CSI like `csidata.CSI.CSI` is only available after calling `read` method.
- 5-10 times faster than before
- `parseCSIMVM(...)` in `_picoscenes.pyx` may be incorrect.

`csiread.Picoscenes` is based on the PicoScenes MATLAB Toolbox(PMT)(Last modified at 2022-01-21).
