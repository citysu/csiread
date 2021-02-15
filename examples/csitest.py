"""Check correctness(Linux 802.11n CSI Tool)

Usage:
	1. use the following matlab code to get 'log.all_csi.6.7.6.mat'.

	```matlab
	csidata = read_bf_file("sample_data/log.all_csi.6.7.6");
	for i = 1:length(csidata)
		csidata{i}.scaled_csi = get_scaled_csi(csidata{i});
		csidata{i}.scaled_csi_sm = get_scaled_csi_sm(csidata{i});
	end
	save("sample_data/log.all_csi.6.7.6.mat", 'csidata')
	```

	2. python3 csitest.py

Note:
	the sample data 'log.all_csi.6.7.6' of linux-80211n-csitool-supplementary
	contains Ntx=1, 2, 3.
"""

import numpy as np
from scipy.io import loadmat
import csiread


def python_read(csifile='log.all_csi.6.7.6'):
	csidata = csiread.Intel(csifile, ntxnum=3)
	csidata.read()
	pydata = csidata[:]
	pydata['scaled_csi'] = csidata.get_scaled_csi()
	pydata['scaled_csi_sm'] = csidata.get_scaled_csi_sm()
	return pydata


def matlab_read(matfile='log.all_csi.6.7.6.mat'):
	matdata = loadmat(matfile)
	mldata = {}
	pk_num = 29
	mldata['timestamp_low'] = np.zeros([pk_num], dtype=np.int_)
	mldata['bfee_count'] = np.zeros([pk_num], dtype=np.int_)
	mldata['Nrx'] = np.zeros([pk_num], dtype=np.int_)
	mldata['Ntx'] = np.zeros([pk_num], dtype=np.int_)
	mldata['rssi_a'] = np.zeros([pk_num], dtype=np.int_)
	mldata['rssi_b'] = np.zeros([pk_num], dtype=np.int_)
	mldata['rssi_c'] = np.zeros([pk_num], dtype=np.int_)
	mldata['noise'] = np.zeros([pk_num], dtype=np.int_)
	mldata['agc'] = np.zeros([pk_num], dtype=np.int_)
	mldata['perm'] = np.zeros([pk_num, 3], dtype=np.int_)
	mldata['rate'] = np.zeros([pk_num], dtype=np.int_)
	mldata['csi'] = np.zeros([pk_num, 30, 3, 3], dtype=np.complex_)
	mldata['scaled_csi'] = np.zeros([pk_num, 30, 3, 3], dtype=np.complex_)
	mldata['scaled_csi_sm'] = np.zeros([pk_num, 30, 3, 3], dtype=np.complex_)
	for i in range(pk_num):
		mldata['timestamp_low'][i] = matdata['csidata'][i, 0]['timestamp_low'][0, 0]
		mldata['bfee_count'][i] = matdata['csidata'][i, 0]['bfee_count'][0, 0]
		mldata['Nrx'][i] = matdata['csidata'][i, 0]['Nrx'][0, 0]
		mldata['Ntx'][i] = matdata['csidata'][i, 0]['Ntx'][0, 0]
		mldata['rssi_a'][i] = matdata['csidata'][i, 0]['rssi_a'][0, 0]
		mldata['rssi_b'][i] = matdata['csidata'][i, 0]['rssi_b'][0, 0]
		mldata['rssi_c'][i] = matdata['csidata'][i, 0]['rssi_c'][0, 0]
		mldata['noise'][i] = matdata['csidata'][i, 0]['noise'][0, 0]
		mldata['agc'][i] = matdata['csidata'][i, 0]['agc'][0, 0]
		mldata['perm'][i] = matdata['csidata'][i, 0]['perm'][0, 0].T[:, 0] - 1
		mldata['rate'][i] = matdata['csidata'][i, 0]['rate'][0, 0]
		mldata['csi'][i][:, :, :int(mldata['Ntx'][i])] = matdata['csidata'][i, 0]['csi'][0, 0].T
		mldata['scaled_csi'][i][:, :, :int(mldata['Ntx'][i])] = matdata['csidata'][i, 0]['scaled_csi'][0, 0].T
		mldata['scaled_csi_sm'][i][:, :, :int(mldata['Ntx'][i])] = matdata['csidata'][i, 0]['scaled_csi_sm'][0, 0].T
	return mldata


if __name__ == "__main__":
	pydata = python_read('log.all_csi.6.7.6')
	mldata = matlab_read('log.all_csi.6.7.6.mat')

	for i in mldata.keys():
		print('%-15s' % (i), np.sum(np.abs(pydata[i] - mldata[i])))
