import numpy as np


def init_dtype_picoscenes(pl_size):
    dt_ieee80211_mac_frame_header_frame_control_field = np.dtype([
        ('Version', np.uint16),
        ('Type', np.uint16),
        ('SubType', np.uint16),
        ('ToDS', np.uint16),
        ('FromDS', np.uint16),
        ('MoreFrags', np.uint16),
        ('Retry', np.uint16),
        ('PowerManagement', np.uint16),
        ('More', np.uint16),
        ('Protected', np.uint16),
        ('Order', np.uint16),
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
        ('DeviceType', np.uint16),
        ('Timestamp', np.uint64),
        ('CenterFreq', np.int16),
        ('ControlFreq', np.int16),
        ('CBW', np.uint16),
        ('PacketFormat', np.uint8),
        ('PacketCBW', np.uint16),
        ('GI', np.uint16),
        ('MCS', np.uint8),
        ('NumSTS', np.uint8),
        ('NumESS', np.uint8),
        ('NumRx', np.uint8),
        ('NoiseFloor', np.int8),
        ('RSSI', np.int8),
        ('RSSI1', np.int8),
        ('RSSI2', np.int8),
        ('RSSI3', np.int8),
    ])

    dt_ExtraInfo = np.dtype([
        ('HasLength', bool),
        ('HasVersion', bool),
        ('HasMacAddr_cur', bool),
        ('HasMacAddr_rom', bool),
        ('HasChansel', bool),
        ('HasBMode', bool),
        ('HasEVM', bool),
        ('HasTxChainMask', bool),
        ('HasRxChainMask', bool),
        ('HasTxpower', bool),
        ('HasCF', bool),
        ('HasTxTSF', bool),
        ('HasLastHwTxTSF', bool),
        ('HasChannelFlags', bool),
        ('HasTxNess', bool),
        ('HasTuningPolicy', bool),
        ('HasPLLRate', bool),
        ('HasPLLClkSel', bool),
        ('HasPLLRefDiv', bool),
        ('HasAGC', bool),
        ('HasAntennaSelection', bool),
        ('HasSamplingRate', bool),
        ('HasCFO', bool),
        ('HasSFO', bool),
        ('HasTemperature', bool),

        ('Length', np.uint16),
        ('Version', np.uint64),
        ('MACAddressCurrent', np.uint8, (6, )),
        ('MACAddressROM', np.uint8, (6, )),
        ('CHANSEL', np.uint32),
        ('BMode', np.uint8),
        ('EVM', np.int8, (20, )),
        ('TxChainMask', np.uint8),
        ('RxChainMask', np.uint8),
        ('TxPower', np.uint8),
        ('CF', np.uint64),
        ('TxTSF', np.uint32),
        ('LastTXTSF', np.uint32),
        ('ChannelFlags', np.uint16),
        ('TXNESS', np.uint8),
        ('TuningPolicy', np.uint8),
        ('PLLRate', np.uint16),
        ('PLLClockSelect', np.uint8),
        ('PLLRefDiv', np.uint8),
        ('AGC', np.uint8),
        ('ANTSEL', np.uint8, (3, )),
        ('SF', np.uint64),
        ('CFO', np.int32),
        ('SFO', np.int32),
        ('Temperature', np.int8),
    ])

    dt_CSI_info = np.dtype([
        ('DeviceType', np.uint16),
        ('FirmwareVersion', np.uint8),
        ('PacketFormat', np.int8),
        ('CBW', np.uint16),
        ('CarrierFreq', np.uint64),
        ('SamplingRate', np.uint64),
        ('SubcarrierBandwidth', np.uint32),
        ('NumTones', np.uint16),
        ('NumTx', np.uint8),
        ('NumRx', np.uint8),
        ('NumESS', np.uint8),
        ('NumCSI', np.uint16),
        ('ANTSEL', np.uint8)
    ])

    dt_CSI = np.dtype([
        ('Info', dt_CSI_info),
        ('CSI', complex, pl_size['CSI']),
        ('SubcarrierIndex', np.int32, (pl_size['CSI'][0], )),
    ])

    dt_PilotCSI = np.dtype([
        ('Info', dt_CSI_info),
        ('CSI', complex, pl_size['PilotCSI']),
        ('SubcarrierIndex', np.int32, (pl_size['PilotCSI'][0], )),
    ])

    dt_LegacyCSI = np.dtype([
        ('Info', dt_CSI_info),
        ('CSI', complex, pl_size['LegacyCSI']),
        ('SubcarrierIndex', np.int32, (pl_size['LegacyCSI'][0], )),
    ])

    dt_IntelMVMExtrta = np.dtype([
        ('FTMClock', np.uint32),
        ('MuClock', np.uint32),
        ('RateNFlags', np.uint32),
    ])

    dt_DPASRequest = np.dtype([
        ('RequestMode', np.uint8),
        ('BatchId', np.uint16),
        ('BatchLength', np.uint16),
        ('Sequence', np.uint16),
        ('Interval', np.uint16),
        ('Step', np.uint16),
        ('DeviceType', np.uint16),
        ('DeviceSubtype', np.uint16),
        ('CarrierFrequency', np.uint64),
        ('SamplingRate', np.uint32),
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
        ('Ndim', np.uint8),
        ('Shape', np.uint16, (3, )),
        ('Itemsize', np.uint8),
        ('Majority', np.byte),
    ])

    dt_BasebandSignals = np.dtype([
        ('Info', dt_SignalMatrix_info),
        ('Data', np.complex128, pl_size['BasebandSignals'])
    ])

    dt_PreEQSymbols = np.dtype([
        ('Info', dt_SignalMatrix_info),
        ('Data', np.complex128, pl_size['PreEQSymbols'])
    ])

    dt_MPDU_info = np.dtype([
        ('Length', np.uint32)
    ])

    dt_MPDU = np.dtype([
        ('Info', dt_MPDU_info),
        ('Data', np.uint8, (pl_size['MPDU'], ))
    ])

    dt = np.dtype([
        ('StandardHeader', dt_ieee80211_mac_frame_header),
        ('RxSBasic', dt_RxSBasic),
        ('RxExtraInfo', dt_ExtraInfo),
        ('CSI', dt_CSI),
        ('MVMExtra', dt_IntelMVMExtrta),
        ('DPASRequest', dt_DPASRequest),
        ('PicoScenesHeader', dt_PicoScenesFrameHeader),
        ('TxExtraInfo', dt_ExtraInfo),
        ('PilotCSI', dt_PilotCSI),
        ('LegacyCSI', dt_LegacyCSI),
        ('BasebandSignals', dt_BasebandSignals),
        ('PreEQSymbols', dt_PreEQSymbols),
        ('MPDU', dt_MPDU),
    ])
    return dt
