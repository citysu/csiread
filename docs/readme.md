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

### PicoScenes

The support for Picoscenes is an **experimental** feature. It is disabled by default and hasn't been available in the published package. You have to enable it from source by yourself. More importantly, PicoScenes is still under active development, and csiread cannot be updated synchronously.

`csiread.Picoscenes` is based on the PicoScenes MATLAB Toolbox(PMT)(Last modified at 2021-10-06). It does parsing by calling `rxs_parsing_core` of Picoscenes directly. They have the similar performance. The latest PMT is recommended, but you may fail to enable it with newer PMT(>2021-10-06). You have to solve it by yourself. Next, I will show you how to enable support for picoscenes on Linux and Windows.

Tips: folder `csiread/csiread/rxs_parsing_core` is the copy of official PMT:`rxs_parsing_core` (without modification)

```python
# PicoScenes
csifile = "../material/picoscenes/dataset/rx_by_iwl5300.csi"
csidata = csiread.Picoscenes(csifile)
csidata.read()
print(csidata.raw[0]["CSI"].keys())
```

#### Linux/GCC

1. Open `setup.py` and set `ENABLE_PICO = True`
2. Build from source:

	```bash
	cd csiread
	pip3 install -r requirements.txt
	python3 setup.py sdist bdist_wheel
	pip3 install -U dist/csiread*.whl
	```

#### Windows/TDM-GCC 64

1. Open `setup.py` and set `ENABLE_PICO = True`
2. Install TDM-GCC 64. If you have installed MSVC on your computer, create a file named `setup.cfg` under `csiread/`. add

	```txt
	[build]
	compiler=mingw32
	```

3. Install dependencies

	```bash
	cd csiread
	pip3 install -r requirements.txt
	```

4. I used Window 10 and Python 3.9.7(64 bit) for test. The file `<PYTHON_ROOT>/Lib/distutils/cygwinccompiler.py` is too old to work with Python(version >= 3.5.0). Open it and find function `get_msvcr`. Add the following code before `else:`:

	```python
	elif msc_ver >= '1900':
		return ['vcruntime140']
	```

5. Build from source:

	```bash
	python3 setup.py sdist bdist_wheel
	pip3 install -U dist/csiread*.whl
	```

6. There will be some warnings, but there seems to be no value errors. You can open `setup.py` and disable them by replacing

	```python
	e.extra_compile_args += ['-DMS_WIN64']
	```

	with

	```python
	e.extra_compile_args += ['-DMS_WIN64', '-Wno-attributes', '-Wno-format', '-Wno-format-extra-args', '-Wno-sign-compare']
	```

#### Windows/Visual Studio

`rxs_parsing_core` is designed for `gcc` and hasn't supported `msvc` yet. We have to do some modifications to avoid compilation errors.

1. Open `setup.py` and set `ENABLE_PICO = True`
2. Install Visual Studio or Bulild Tools
3. Add `#include <functional>` into `MVMExtraSegment.hxx` and `#include <optional>` into `AbstractPicoScenesFrameSegment.hxx`
4. `msvc` doesn't support `__attribute__ ((__packed__))` syntax. Replace

	```cpp
	struct PicoScenesFrameHeader {
		...
	} __attribute__ ((__packed__));
	```

	with

	```cpp
	#pragma pack(push, 1)
	struct PicoScenesFrameHeader {
		...
	};
	#pragma pack(pop)
	```

	Find all `struct` and `class` with `__attribute__ ((__packed__))` in `rxs_parsing_core`. Make the same changes. 
	Ref: [Pragma directives and the __pragma and _Pragma keywords](https://docs.microsoft.com/en-us/cpp/preprocessor/pragma-directives-and-the-pragma-keyword?view=msvc-160)

5. Build from source:

	```bash
	cd csiread
	pip3 install -r requirements.txt
	python3 setup.py sdist bdist_wheel
	pip3 install -U dist/csiread*.whl
	```

6. There will be a lot of warnings caused by `rxs_parsing_core`, but there seems to be no value errors.
