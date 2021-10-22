# csiread's documentation

## Introduction

**csiread** aims at parsing CSI data of Intel5300, Atheros, Nexmon_csi and ESP32-CSI-Tool with Python **fast**. 

Various CSI Tools only provide Matlab API parsing CSI data files. Those who want to process CSI with Python have to install Matlab to convert `.dat` to `.mat`. This process is redundant and inefficient. Therefore, **Python API** is recommended. Unfortunately, the API implemented in pure Python is inefficient. With this in mind, I implemented csiread in Cython(Pybind11 may be another great choice). The table below shows the efficiency comparison of different implementations. They were all tested with **40k** packets on the same computer.

|        Function         | Matlab   | Python3+Numpy | csiread    | file size |
|-------------------------|----------|---------------|------------|-----------|
| Nexmon.read:bcm4339     | 3.2309s  | 0.2739s       | 0.0703s    | 44.0MB    |
| Nexmon.read:bcm4358     | 3.5987s  | 23.0025s      | 0.1227s    | 44.0MB    |
| Atheros.read            | 3.3081s  | 14.6021s      | 0.0956s    | 76.3MB    |
| Intel.read              | 1.6102s  | 7.6624s       | 0.0479s    | 21.0MB    |
| Intel.get_total_rss     | 0.1786s  | 0.0030s       | 0.0030s    |           |
| Intel.get_scaled_csi    | 0.5497s  | 0.1225s       | 0.0376s/0.0278s |      |
| Intel.get_scaled_csi_sm | 5.0097s  | 0.3627s       | 0.0778s/0.0465s |      |

## Installation

It can be installed via `pip`:

```bash
pip3 install csiread
```

or build from source:

```bash
cd csiread
pip3 install -r requirements.txt
python3 setup.py sdist bdist_wheel
pip3 install -U dist/csiread*.whl
```

`*` is a wildcard character. After running `python3 setup.py sdist bdist_wheel`,there will be a wheel file like `csiread-1.3.4-cp36-cp36m-win_amd64.whl` in the `dist` folder. Replace `csiread*.whl` with it.

csiread is written in Cython, Cython requires a C compiler to be present on the system. You can refer to [Installing Cython](https://cython.readthedocs.io/en/latest/src/quickstart/install.html) for more details. If you don't want to install a C compiler, just fork the project and push a tag to the latest commit. Then wheel files can be found in `Github-Actions-Python package-Artifacts: csiread_dist`

## Usage

`examples` are the best usage instructions, and the API documentation can be found in `docstring`, so we won't repeat them here.

## Design

csiread provides 7 classes: `Intel, Atheros, Nexmon, AtherosPull10, NexmonPull46, ESP32 and Picoscenes`. Each class has 4 key methods: `read(), seek()`, `pmsg()` and `display()` which are used for reading a file, reading a file from a specific position, real-time parsing and viewing the contents of a packet respectively. `csiread.utils` provides some common functions.

csiread is not only the translation of the Matlab API, but also a **CSI toolbox**. I added some utilities, real-time visualization and algorithms code in the `examples` folder. These would be useful for Python-based CSI researchers.

### Nexmon CSI

The `Nexmon.group` is experimental, it may be incorrect due to `core` and `spatial`. `core` and `spatial` are ZERO or not recorded correctly in some files. I don't know how to solve it.

### ESP32-CSI-Tool

`pandas.read_csv` and `csiread.ESP32` have the similar performance, but `pandas.read_csv` is much more flexible.

### PicoScenes(unfinished)

The support for Picoscenes is an **experimental** feature. PicoScenes is still under active development, and csiread cannot be updated synchronously.

`csiread.Picoscenes` is based on the PicoScenes MATLAB Toolbox(PMT)(Last modified at 2021-10-06). It did parsing by calling `rxs_parsing_core` of Picoscenes directly before, and had similar performance to PMT. However, there are some bottlenecks.

- For parsing `.csi` file in Python， There are some useless memory copy in `rxs_parsing_core`.
- `rxs_parsing_core` copys the parsed result into `struct ModularPicoScenesRxFrame`. `csiread.Picoscenes` copys `struct ModularPicoScenesRxFrame` into `raw` list. `bundle` method copys `raw` into `ndarray`.
- I cannot build binary package conveniently

I plan to rewrite the `csiread.Picoscenes` with Cython completely. It will be about 10 times faster than before.

- `#pragma` is suppored by both `gcc` and `msvc`. Replace `__attribute__ ((__packed__))` with `#pragma pack(push, 1) ... #pragma pack(pop)`
- `raw` will be a `np.ndarray`, we don't need method `bundle` anymore. By default, `raw = np.zeros(...)`.
- `Mag` and `Phase` fileds are redundant, use `np.abs` and `np.angle` instead, Remove them.
- Add `interpolateCSI()` method
- The Attributes: `CSI, SubcarrierIndex, BasebandSignals, PreEQSymbols and MPDU` might cause failure of `bundle` method before. They can be variable length arrays. To store them in fixed leanth arrays, the parameter `pl_size` will be added. It can be `int, list, tuple and dict`, but it will be converted into `dict` finally. It controls how to parse these attributes. e.g. When `len(CSI_Aarray) > pl_size['CSI']`, the parsing of `CSI` attribute in this frame will be skipped.
- etc.

```python
# PicoScenes
csifile = "../material/picoscenes/dataset/rx_by_iwl5300.csi"
csidata = csiread.Picoscenes(file=csifile, pl_size=0, if_report=True, bufsize=0)
csidata.read()
print(csidata.raw["CSI"].shape)
```
