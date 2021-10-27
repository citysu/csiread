import numpy as np


def init_dtype_intel(pl_size):
    dt = np.dtype([
        ('timestamp_low', np.uint32),
        ('bfee_count', np.int),
        ('Nrx', np.int),
        ('Ntx', np.int),
        ('rssi_a', np.int),
        ('rssi_b', np.int),
        ('rssi_c', np.int),
        ('noise', np.int),
        ('agc', np.int),
        ('perm', np.int),
        ('rate', np.int),
        ('csi', np.complex, (30, pl_size['nrxnum'], pl_size['ntxnum'])),
        ('stp', np.int),
        ('fc', np.int),
        ('dur', np.int),
        ('addr_des', np.int, (6, )),
        ('addr_src', np.int, (6, )),
        ('addr_bssid', np.int, (6, )),
        ('seq', np.int),
        ('payload', np.uint8, (pl_size['payload'])),
    ])
    return dt


def init_dtype_atheros(pl_size):
    dt = np.dtype([
        ('timestamp', np.uint64),
        ('csi_len', np.int),
        ('tx_channel', np.int),
        ('err_info', np.int),
        ('noise_floor', np.int),
        ('Rate', np.int),
        ('bandWidth', np.int),
        ('num_tones', np.int),
        ('nr', np.int),
        ('nc', np.int),
        ('rssi_1', np.int),
        ('rssi_2', np.int),
        ('rssi_3', np.int),
        ('payload_len', np.int),
        ('csi', np.complex, (pl_size['tones'], pl_size['nrxnum'], pl_size['ntxnum'])),
        ('payload', np.uint8, (pl_size['payload'])),
    ])
    return dt


def init_dtype_nexmon(pl_size):
    dt = np.dtype([
        ('sec', np.uint32),
        ('usec', np.uint32),
        ('caplen', np.int),
        ('wirelen', np.int),
        ('magic', np.int),
        ('src_addr', np.int, (6, )),
        ('seq', np.int),
        ('core', np.int),
        ('spatial', np.int),
        ('chan_spec', np.int),
        ('chip_version', np.int),
        ('csi', np.int),
        ('csi', np.complex, (int(pl_size['bw'] * 3.2), )),
    ])
    return dt


def init_dtype_nexmonpull46(pl_size):
    dt = np.dtype([
        ('sec', np.uint32),
        ('usec', np.uint32),
        ('caplen', np.int),
        ('wirelen', np.int),
        ('magic', np.int),
        ('rssi', np.int),
        ('src_addr', np.int, (6, )),
        ('seq', np.int),
        ('core', np.int),
        ('spatial', np.int),
        ('chan_spec', np.int),
        ('chip_version', np.int),
        ('csi', np.int),
        ('csi', np.complex, (int(pl_size['bw'] * 3.2), )),
    ])
    return dt


def init_dtype_esp32(pl_size):
    pass


def init_dtype_picoscenes(pl_size):
    dt_ieee80211_mac_frame_header_frame_control_field = np.dtype([
        ('Version', np.uint8),
        ('Type', np.uint8),
        ('SubType', np.uint8),
        ('ToDS', np.uint8),
        ('FromDS', np.uint8),
        ('MoreFrags', np.uint8),
        ('Retry', np.uint8),
        ('PowerManagement', np.uint8),
        ('More', np.uint8),
        ('Protected', np.uint8),
        ('Order', np.uint8),
    ])

    dt_ieee80211_mac_frame_header = np.dtype([
        ('ControlField', dt_ieee80211_mac_frame_header_frame_control_field),
        ('Addr1', np.uint8, (6, )),
        ('Addr2', np.uint8, (6, )),
        ('Addr3', np.uint8, (6, )),
        ('Fragment', np.uint16),
        ('Sequence', np.uint16),
    ])

    dt_RxSBasic = np.dtype([
        ('deviceType', np.uint16),
        ('timestamp', np.uint64),
        ('centerFreq', np.int16),
        ('controlFreq', np.int16),
        ('CBW', np.uint16),
        ('packetFormat', np.uint8),
        ('packetCBW', np.uint16),
        ('GI', np.uint16),
        ('MCS', np.uint8),
        ('numSTS', np.uint8),
        ('numESS', np.uint8),
        ('numRx', np.uint8),
        ('noiseFloor', np.int8),
        ('rssi', np.int8),
        ('rssi1', np.int8),
        ('rssi2', np.int8),
        ('rssi3', np.int8),
    ])

    dt_ExtraInfo = np.dtype([
        ('hasLength', bool),
        ('hasVersion', bool),
        ('hasMacAddr_cur', bool),
        ('hasMacAddr_rom', bool),
        ('hasChansel', bool),
        ('hasBMode', bool),
        ('hasEVM', bool),
        ('hasTxChainMask', bool),
        ('hasRxChainMask', bool),
        ('hasTxpower', bool),
        ('hasCF', bool),
        ('hasTxTSF', bool),
        ('hasLastHwTxTSF', bool),
        ('hasChannelFlags', bool),
        ('hasTxNess', bool),
        ('hasTuningPolicy', bool),
        ('hasPLLRate', bool),
        ('hasPLLClkSel', bool),
        ('hasPLLRefDiv', bool),
        ('hasAGC', bool),
        ('hasAntennaSelection', bool),
        ('hasSamplingRate', bool),
        ('hasCFO', bool),
        ('hasSFO', bool),

        ('length', np.uint16),
        ('version', np.uint64),
        ('macaddr_cur', np.uint8, (6, )),
        ('macaddr_rom', np.uint8, (6, )),
        ('chansel', np.uint32),
        ('bmode', np.uint8),
        ('evm', np.int8, (20, )),
        ('tx_chainmask', np.uint8),
        ('rx_chainmask', np.uint8),
        ('txpower', np.uint8),
        ('cf', np.uint64),
        ('txtsf', np.uint32),
        ('last_txtsf', np.uint32),
        ('channel_flags', np.uint16),
        ('tx_ness', np.uint8),
        ('tuning_policy', np.uint8),
        ('pll_rate', np.uint16),
        ('pll_clock_select', np.uint8),
        ('pll_refdiv', np.uint8),
        ('agc', np.uint8),
        ('ant_sel', np.uint8, (3, )),
        ('sf', np.uint64),
        ('cfo', np.int32),
        ('sfo', np.int32)
    ])

    dt_CSI_info = np.dtype([
        ('DeviceType', np.uint16),
        ('PacketFormat', np.int8),
        ('CBW', np.uint16),
        ('CarrierFreq', np.uint64),
        ('SamplingRate', np.uint64),
        ('SubcarrierBandwidth', np.uint32),
        ('numTones', np.uint16),
        ('numTx', np.uint8),
        ('numRx', np.uint8),
        ('numESS', np.uint8),
        ('numCSI', np.uint16),
        ('ant_sel', np.uint8)
    ])

    dt_CSI = np.dtype([
        ('info', dt_CSI_info),
        ('CSI', complex, pl_size['CSI']),
        ('SubcarrierIndex', np.int32, (pl_size['CSI'][0], )),
    ])

    dt_PilotCSI = np.dtype([
        ('info', dt_CSI_info),
        ('CSI', complex, pl_size['PilotCSI']),
        ('SubcarrierIndex', np.int32, (pl_size['PilotCSI'][0], )),
    ])

    dt_LegacyCSI = np.dtype([
        ('info', dt_CSI_info),
        ('CSI', complex, pl_size['LegacyCSI']),
        ('SubcarrierIndex', np.int32, (pl_size['LegacyCSI'][0], )),
    ])

    dt_IntelMVMExtrta = np.dtype([
        ('FMTClock', np.uint32),
        ('usClock', np.uint32),
        ('RateNFlags', np.uint32),
    ])

    dt_PicoScenesFrameHeader = np.dtype([
        ('MagicValue', np.uint32),
        ('Version', np.uint32),
        ('DeviceType', np.uint16),
        ('FrameType', np.uint8),
        ('TaskId', np.uint16),
        ('TxId', np.uint16),
    ])

    dt_SignalMatrix_info = np.dtype([
        ('ndim', np.uint8),
        ('shape', np.uint16, (3, )),
        ('itemsize', np.uint8),
        ('majority', np.byte),       # rename? 
    ])

    dt_BasebandSignals = np.dtype([
        ('info', dt_SignalMatrix_info),
        ('data', np.complex128, pl_size['BasebandSignals'])
    ])

    dt_PreEQSymbols = np.dtype([
        ('info', dt_SignalMatrix_info),
        ('data', np.complex128, pl_size['PreEQSymbols'])
    ])

    dt_MPDU_info = np.dtype([
        ('length', np.uint16)
    ])

    dt_MPDU = np.dtype([
        ('info', dt_MPDU_info),
        ('data', np.uint8, (pl_size['MPDU'], ))
    ])

    dt = np.dtype([
        ('StandardHeader', dt_ieee80211_mac_frame_header),
        ('RxSBasic', dt_RxSBasic),
        ('RxExtraInfo', dt_ExtraInfo),
        ('CSI', dt_CSI),
        ('MVMExtra', dt_IntelMVMExtrta),
        ('PicoScenesHeader', dt_PicoScenesFrameHeader),
        ('TxExtraInfo', dt_ExtraInfo),
        ('PilotCSI', dt_PilotCSI),
        ('LegacyCSI', dt_LegacyCSI),
        ('BasebandSignals', dt_BasebandSignals),
        ('PreEQSymbols', dt_PreEQSymbols),
        ('MPDU', dt_MPDU),
    ])
    return dt
