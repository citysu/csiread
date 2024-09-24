from libc.stdio cimport FILE
cimport numpy as np


cdef class Intel:
    cdef readonly str file
    cdef readonly int count

    cdef public np.ndarray timestamp_low
    cdef public np.ndarray bfee_count
    cdef public np.ndarray Nrx
    cdef public np.ndarray Ntx
    cdef public np.ndarray rssi_a
    cdef public np.ndarray rssi_b
    cdef public np.ndarray rssi_c
    cdef public np.ndarray noise
    cdef public np.ndarray agc
    cdef public np.ndarray perm
    cdef public np.ndarray rate
    cdef public np.ndarray csi
    cdef public np.ndarray stp

    cdef public np.ndarray fc
    cdef public np.ndarray dur
    cdef public np.ndarray addr_des
    cdef public np.ndarray addr_src
    cdef public np.ndarray addr_bssid
    cdef public np.ndarray seq
    cdef public np.ndarray payload

    cdef np.ndarray buf_timestamp_low
    cdef np.ndarray buf_bfee_count
    cdef np.ndarray buf_Nrx
    cdef np.ndarray buf_Ntx
    cdef np.ndarray buf_rssi_a
    cdef np.ndarray buf_rssi_b
    cdef np.ndarray buf_rssi_c
    cdef np.ndarray buf_noise
    cdef np.ndarray buf_agc
    cdef np.ndarray buf_perm
    cdef np.ndarray buf_rate
    cdef np.ndarray buf_csi
    cdef np.ndarray buf_stp
    cdef np.ndarray buf_total_rss

    cdef np.ndarray buf_fc
    cdef np.ndarray buf_dur
    cdef np.ndarray buf_addr_des
    cdef np.ndarray buf_addr_src
    cdef np.ndarray buf_addr_bssid
    cdef np.ndarray buf_seq
    cdef np.ndarray buf_payload

    cdef np.uint32_t[:] buf_timestamp_low_mem
    cdef np.intp_t[:] buf_bfee_count_mem
    cdef np.intp_t[:] buf_Nrx_mem
    cdef np.intp_t[:] buf_Ntx_mem
    cdef np.intp_t[:] buf_rssi_a_mem
    cdef np.intp_t[:] buf_rssi_b_mem
    cdef np.intp_t[:] buf_rssi_c_mem
    cdef np.intp_t[:] buf_noise_mem
    cdef np.intp_t[:] buf_agc_mem
    cdef np.intp_t[:, :] buf_perm_mem
    cdef np.intp_t[:] buf_rate_mem
    cdef np.complex128_t[:, :, :, :] buf_csi_mem
    cdef np.float64_t[:] buf_total_rss_mem

    cdef np.intp_t[:] buf_fc_mem
    cdef np.intp_t[:] buf_dur_mem
    cdef np.intp_t[:, :] buf_addr_des_mem
    cdef np.intp_t[:, :] buf_addr_src_mem
    cdef np.intp_t[:, :] buf_addr_bssid_mem
    cdef np.intp_t[:] buf_seq_mem
    cdef np.uint8_t[:, :] buf_payload_mem

    cdef np.complex128_t[:, :] sm_2_20_mem
    cdef np.complex128_t[:, :] sm_2_40_mem
    cdef np.complex128_t[:, :] sm_3_20_mem
    cdef np.complex128_t[:, :] sm_3_40_mem

    cdef int nrxnum
    cdef int ntxnum
    cdef int pl_size
    cdef bint if_report

    cpdef read(self)
    cpdef seek(self, file, long pos, long num)
    cpdef pmsg(self, unsigned char *data)
    cpdef get_total_rss(self)
    cpdef get_scaled_csi(self, inplace=?)
    cdef __remove_sm(self, scaled_csi, inplace=?)


cdef class Atheros:
    cdef readonly str file
    cdef readonly int count

    cdef public np.ndarray timestamp
    cdef public np.ndarray csi_len
    cdef public np.ndarray tx_channel
    cdef public np.ndarray err_info
    cdef public np.ndarray noise_floor
    cdef public np.ndarray Rate
    cdef public np.ndarray bandWidth
    cdef public np.ndarray num_tones
    cdef public np.ndarray nr
    cdef public np.ndarray nc
    cdef public np.ndarray rssi
    cdef public np.ndarray rssi_1
    cdef public np.ndarray rssi_2
    cdef public np.ndarray rssi_3
    cdef public np.ndarray payload_len
    cdef public np.ndarray csi
    cdef public np.ndarray payload

    cdef np.ndarray buf_timestamp
    cdef np.ndarray buf_csi_len
    cdef np.ndarray buf_tx_channel
    cdef np.ndarray buf_err_info
    cdef np.ndarray buf_noise_floor
    cdef np.ndarray buf_Rate
    cdef np.ndarray buf_bandWidth
    cdef np.ndarray buf_num_tones
    cdef np.ndarray buf_nr
    cdef np.ndarray buf_nc
    cdef np.ndarray buf_rssi
    cdef np.ndarray buf_rssi_1
    cdef np.ndarray buf_rssi_2
    cdef np.ndarray buf_rssi_3
    cdef np.ndarray buf_payload_len
    cdef np.ndarray buf_csi
    cdef np.ndarray buf_payload

    cdef np.uint64_t[:] buf_timestamp_mem
    cdef np.intp_t[:] buf_csi_len_mem
    cdef np.intp_t[:] buf_tx_channel_mem
    cdef np.intp_t[:] buf_err_info_mem
    cdef np.intp_t[:] buf_noise_floor_mem
    cdef np.intp_t[:] buf_Rate_mem
    cdef np.intp_t[:] buf_bandWidth_mem
    cdef np.intp_t[:] buf_num_tones_mem
    cdef np.intp_t[:] buf_nr_mem
    cdef np.intp_t[:] buf_nc_mem
    cdef np.intp_t[:] buf_rssi_mem
    cdef np.intp_t[:] buf_rssi_1_mem
    cdef np.intp_t[:] buf_rssi_2_mem
    cdef np.intp_t[:] buf_rssi_3_mem
    cdef np.intp_t[:] buf_payload_len_mem
    cdef np.complex128_t[:, :, :, :] buf_csi_mem
    cdef np.uint8_t[:, :] buf_payload_mem

    cdef int nrxnum
    cdef int ntxnum
    cdef int tones
    cdef int pl_size
    cdef bint if_report

    cpdef read(self, endian=?)
    cpdef seek(self, file, long pos, long num, endian=?)
    cpdef pmsg(self, unsigned char *data, endian=?)


cdef class Nexmon:
    cdef readonly str file
    cdef readonly int count
    cdef readonly str chip
    cdef readonly int bw
    cdef readonly bint nano

    cdef public np.ndarray sec
    cdef public np.ndarray usec
    cdef public np.ndarray caplen
    cdef public np.ndarray wirelen
    cdef public np.ndarray magic
    cdef public np.ndarray src_addr
    cdef public np.ndarray seq
    cdef public np.ndarray core
    cdef public np.ndarray spatial
    cdef public np.ndarray chan_spec
    cdef public np.ndarray chip_version
    cdef public np.ndarray csi

    cdef np.ndarray buf_sec
    cdef np.ndarray buf_usec
    cdef np.ndarray buf_caplen
    cdef np.ndarray buf_wirelen
    cdef np.ndarray buf_magic
    cdef np.ndarray buf_src_addr
    cdef np.ndarray buf_seq
    cdef np.ndarray buf_core
    cdef np.ndarray buf_spatial
    cdef np.ndarray buf_chan_spec
    cdef np.ndarray buf_chip_version
    cdef np.ndarray buf_csi

    cdef np.uint32_t[:] buf_sec_mem
    cdef np.uint32_t[:] buf_usec_mem
    cdef np.intp_t[:] buf_caplen_mem
    cdef np.intp_t[:] buf_wirelen_mem
    cdef np.intp_t[:] buf_magic_mem
    cdef np.intp_t[:, :] buf_src_addr_mem
    cdef np.intp_t[:] buf_seq_mem
    cdef np.intp_t[:] buf_core_mem
    cdef np.intp_t[:] buf_spatial_mem
    cdef np.intp_t[:] buf_chan_spec_mem
    cdef np.intp_t[:] buf_chip_version_mem
    cdef np.complex128_t[:, :] buf_csi_mem

    cdef bint if_report
    cdef public int _autoscale

    cpdef read(self)
    cpdef seek(self, file, long pos, long num)
    cpdef pmsg(self, unsigned char *data, endian=?)
    cdef get_count(self)
    cdef pcapheader(self, FILE *f)


cdef class NexmonPull46(Nexmon):
    cdef public np.ndarray rssi
    cdef public np.ndarray fc

    cdef np.ndarray buf_rssi
    cdef np.ndarray buf_fc

    cdef np.intp_t[:] buf_rssi_mem 
    cdef np.intp_t[:] buf_fc_mem

    cpdef seek(self, file, long pos, long num)
    cpdef pmsg(self, unsigned char *data, endian=?)
