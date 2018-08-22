# csiread

Parse binary file obtained by csi-tool

get csi data by [Linux 802.11n CSI Tool](https://dhalperi.github.io/linux-80211n-csitool/), instead of reading it in matlab, you can use it in python directly. and 4 times faster than matlab when reading.

## Install 

### easy method

```
sudo pip3 install csiread
```

### from source

requries:  

```
sudo pip3 install numpy cython setuptools wheel
```

install:  

```
sudo python3 setup.py install
```

publish:  

```
python3 setup.py sdist bdist_wheel
```

## Usage

```
import csiread

csipath = "sample.dat"
csidata = csiread.CSI(csipath)
csidata.read()
csidata.readstp()

print(csidata.csi.shape)
print(csidata.timestamp)
...
print(csidata.Nrx)
```

you can find some useful data in `sample/` where you install `csiread`.  
all the csidata are in ndarray format.  

only Ubuntu16.04 was tested, I can't tell if it can work on Windows.