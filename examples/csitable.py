#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""csitable: view the contents of packets using beautiful table

Note: run in jupyter notebook to get sample1.png.
"""

import csiread
import pandas as pd

csifile = "../material/5300/dataset/sample_0x5_64_3000.dat"
csidata = csiread.Intel(csifile, ntxnum=1, pl_size=6, if_report=False)
csidata.read()

# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)

stringify = lambda data, space: [space.join([hex(per)[2:].zfill(2).upper() 
                                             for per in data[index]])
                                 for index in range(len(data))]

data = csidata[:]
del data['csi']
del data['perm']
data['perm'] = csidata.perm.tolist()
data['csi.shape'] = [csidata.csi.shape[1:]]*csidata.count
data['fc'] = csidata.fc
data['dur'] = csidata.dur
data['seq'] = csidata.seq
data['addr_src'] = stringify(csidata.addr_src, ":")
data['addr_des'] = stringify(csidata.addr_des, ":")
data['addr_bssid'] = stringify(csidata.addr_bssid, ":")
data['payload[:6]'] = stringify(csidata.payload[:, :6], " ")

csitable = pd.DataFrame(data)
print(csitable[:10])
