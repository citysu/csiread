from libc.stdio cimport (fopen, fread, fclose, fseek, ftell, printf, FILE,
                         SEEK_END, SEEK_SET, SEEK_CUR)
from libc.stdint cimport (uint8_t, uint16_t, uint32_t, uint64_t,
                          int8_t, int16_t, int32_t, int64_t)
from libc.stdlib cimport malloc, realloc, free
from libc.stddef cimport size_t
from libc.string cimport strncmp
import numpy as np
cimport numpy as np


# Section 1: C struct


cdef extern from "_picoscenes.hxx":
    cdef packed struct ModularPicoScenesRxFrameHeader:
        uint32_t frameLength
        uint32_t magicWord
        uint16_t frameVersion
        uint8_t numRxSegments
    
    cdef struct AbstractPicoScenesFrameSegment:
        uint32_t segmentLength
        uint8_t segNameLength
        uint8_t *segmentName
        uint16_t versionId
    
    cdef packed struct RxSBasicV1:
        uint16_t deviceType
        uint64_t tstamp
        int16_t centerFreq
        uint8_t packetFormat
        uint16_t cbw
        uint16_t guardInterval
        uint8_t mcs
        uint8_t numSTS
        uint8_t numESS
        uint8_t numRx
        int8_t noiseFloor
        int8_t rssi
        int8_t rssi_ctl0
        int8_t rssi_ctl1
        int8_t rssi_ctl2
    
    cdef packed struct RxSBasicV2:
        uint16_t deviceType
        uint64_t tstamp
        int16_t centerFreq
        uint8_t packetFormat
        uint16_t cbw
        uint16_t guardInterval
        uint8_t mcs
        uint8_t numSTS
        uint8_t numESS
        uint8_t numRx
        uint8_t numUser
        uint8_t userIndex
        int8_t noiseFloor
        int8_t rssi
        int8_t rssi_ctl0
        int8_t rssi_ctl1
        int8_t rssi_ctl2

    cdef packed struct RxSBasicV3:
        uint16_t deviceType
        uint64_t tstamp
        int16_t centerFreq
        int16_t controlFreq
        uint16_t cbw
        uint8_t packetFormat
        uint16_t pkt_cbw
        uint16_t guardInterval
        uint8_t mcs
        uint8_t numSTS
        uint8_t numESS
        uint8_t numRx
        uint8_t numUser
        uint8_t userIndex
        int8_t noiseFloor
        int8_t rssi
        int8_t rssi_ctl0
        int8_t rssi_ctl1
        int8_t rssi_ctl2

    cdef packed struct FeatureCode:
        uint32_t hasVersion
        uint32_t hasLength
        uint32_t hasMacAddr_cur
        uint32_t hasMacAddr_rom
        uint32_t hasChansel
        uint32_t hasBMode
        uint32_t hasEVM
        uint32_t hasTxChainMask
        uint32_t hasRxChainMask
        uint32_t hasTxpower
        uint32_t hasCF
        uint32_t hasTxTSF
        uint32_t hasLastHWTxTSF
        uint32_t hasChannelFlags
        uint32_t hasTxNess
        uint32_t hasTuningPolicy
        uint32_t hasPLLRate
        uint32_t hasPLLRefDiv
        uint32_t hasPLLClkSel
        uint32_t hasAGC
        uint32_t hasAntennaSelection
        uint32_t hasSamplingRate
        uint32_t hasCFO
        uint32_t hasSFO
        uint32_t hasPreciseTxTiming
    
    cdef packed struct IntelMVMParsedCSIHeader:
        uint32_t iqDataSize
        uint8_t reserved4[4]
        uint32_t ftmClock
        uint32_t samplingTick2
        uint8_t reserved16_52[36]
        uint32_t numTones
        uint8_t reserved60[4]
        uint32_t rssi1
        uint32_t rssi2
        uint8_t sourceAddress[6]
        uint8_t reserved74[2]
        uint8_t csiSequence
        uint8_t reserved77[11]
        uint32_t muClock # 88
        uint32_t rate_n_flags # 92

    cdef packed struct IntelMVMExtrta:
        uint16_t CSIHeaderLength
        IntelMVMParsedCSIHeader parsedHeader

    cdef packed struct ieee80211_mac_frame_header_frame_control_field:
        uint16_t version
        uint16_t type
        uint16_t subtype
        uint16_t toDS
        uint16_t fromDS
        uint16_t moreFrags
        uint16_t retry
        uint16_t power_mgmt
        uint16_t more
        uint16_t protect
        uint16_t order

    cdef packed struct ieee80211_mac_frame_header:
        ieee80211_mac_frame_header_frame_control_field fc
        uint16_t dur
        uint8_t addr1[6]
        uint8_t addr2[6]
        uint8_t addr3[6]
        uint16_t frag
        uint16_t seq

    cdef packed struct PicoScenesFrameHeader:
        uint32_t magicValue
        uint32_t version
        uint16_t deviceType
        uint8_t numSegments
        uint8_t frameType
        uint16_t taskId
        uint16_t txId

    cdef packed struct CSIV1:
        uint16_t deviceType		    # PicoScenesDeviceType
        int8_t packetFormat		    # PacketFormatEnum
        uint16_t cbw				# ChannelBandwidthEnum
        uint64_t carrierFreq
        uint64_t samplingRate
        uint32_t subcarrierBandwidth
        uint16_t numTones
        uint8_t numTx
        uint8_t numRx
        uint8_t numESS
        uint8_t antSel
        uint32_t csiBufferLength
        uint8_t payload[0]

    cdef packed struct CSIV2:
        uint16_t deviceType		    # PicoScenesDeviceType
        int8_t packetFormat		    # PacketFormatEnum
        uint16_t cbw			    # ChannelBandwidthEnum
        uint64_t carrierFreq
        uint64_t samplingRate
        uint32_t subcarrierBandwidth
        uint16_t numTones
        uint8_t numTx
        uint8_t numRx
        uint8_t numESS
        uint8_t antSel
        int16_t subcarrierOffset
        uint32_t csiBufferLength
        uint8_t payload[0]
    
    cdef packed struct CSIV3:
        uint16_t deviceType		    # PicoScenesDeviceType
        int8_t packetFormat		    # PacketFormatEnum
        uint16_t cbw			    # ChannelBandwidthEnum
        uint64_t carrierFreq
        uint64_t samplingRate
        uint32_t subcarrierBandwidth
        uint16_t numTones
        uint8_t numTx
        uint8_t numRx
        uint8_t numESS
        uint16_t numCSI
        uint8_t antSel
        int16_t subcarrierOffset
        uint32_t csiBufferLength
        uint8_t payload[0]


# Section 2: cython type for `raw`


cdef packed struct dtc_ieee80211_mac_frame_header_frame_control_field:
    uint8_t Version
    uint8_t Type
    uint8_t SubType
    uint8_t ToDS
    uint8_t FromDS
    uint8_t MoreFrags
    uint8_t Retry
    uint8_t PowerManagement
    uint8_t More
    uint8_t Protected
    uint8_t Order


cdef packed struct dtc_ieee80211_mac_frame_header:
    dtc_ieee80211_mac_frame_header_frame_control_field ControlField
    uint8_t Addr1[6]
    uint8_t Addr2[6]
    uint8_t Addr3[6]
    uint16_t Fragment
    uint16_t Sequence


cdef packed struct dtc_RXBasic:
    uint16_t deviceType
    uint64_t timestamp
    int16_t centerFreq
    int16_t controlFreq
    uint16_t CBW
    uint8_t packetFormat
    uint16_t packetCBW
    uint16_t GI
    uint8_t MCS
    uint8_t numSTS
    uint8_t numESS
    uint8_t numRx
    int8_t noiseFloor
    int8_t rssi
    int8_t rssi1
    int8_t rssi2
    int8_t rssi3


cdef packed struct dtc_ExtraInfo :
    uint8_t hasLength
    uint8_t hasVersion
    uint8_t hasMacAddr_cur
    uint8_t hasMacAddr_rom
    uint8_t hasChansel
    uint8_t hasBMode
    uint8_t hasEVM
    uint8_t hasTxChainMask
    uint8_t hasRxChainMask
    uint8_t hasTxpower
    uint8_t hasCF
    uint8_t hasTxTSF
    uint8_t hasLastHwTxTSF
    uint8_t hasChannelFlags
    uint8_t hasTxNess
    uint8_t hasTuningPolicy
    uint8_t hasPLLRate
    uint8_t hasPLLClkSel
    uint8_t hasPLLRefDiv
    uint8_t hasAGC
    uint8_t hasAntennaSelection
    uint8_t hasSamplingRate
    uint8_t hasCFO
    uint8_t hasSFO

    uint16_t length
    uint64_t version
    uint8_t macaddr_cur[6]
    uint8_t macaddr_rom[6]
    uint32_t chansel
    uint8_t bmode
    int8_t evm[20]
    uint8_t tx_chainmask
    uint8_t rx_chainmask
    uint8_t txpower
    uint64_t cf
    uint32_t txtsf
    uint32_t last_txtsf
    uint16_t channel_flags
    uint8_t tx_ness
    uint8_t tuning_policy
    uint16_t pll_rate
    uint8_t pll_clock_select
    uint8_t pll_refdiv
    uint8_t agc
    uint8_t ant_sel[3]
    uint64_t sf
    int32_t cfo
    int32_t sfo


cdef packed struct dtc_CSI_info:
    uint16_t DeviceType
    int8_t PacketFormat
    uint16_t CBW
    uint64_t CarrierFreq
    uint64_t SamplingRate
    uint32_t SubcarrierBandwidth
    uint16_t numTones
    uint8_t numTx
    uint8_t numRx
    uint8_t numESS
    uint16_t numCSI
    uint8_t ant_sel


cdef packed struct dtc_IntelMVMExtrta:
    uint32_t FMTClock
    uint32_t usClock
    uint32_t RateNFlags


cdef packed struct dtc_PicoScenesFrameHeader:
    uint32_t MagicValue
    uint32_t Version
    uint16_t DeviceType
    uint8_t FrameType
    uint16_t TaskId
    uint16_t TxId


cdef packed struct dtc_SignalMatrix_info:
    uint8_t ndim
    uint16_t shape[3]
    uint8_t itemsize
    char majority


cdef packed struct dtc_MPDU_info:
    uint16_t length


# Section 3: numpy type for `raw` (removed)


cdef init_array(pk_num, dtype):
    return np.zeros([pk_num], dtype)


# Section 4: functions for parsing


cdef SC_INDICES_9300 = {
    3: {
        20: np.r_[-122:-1, 2:123].astype(np.int32),       # HE20_242Subcarriers_Indices
        40: np.r_[-244:-2, 3:245].astype(np.int32),       # HE40_484Subcarriers_Indices
        80: np.r_[-500:-2, 3:501].astype(np.int32),       # HE80_996Subcarriers_Indices,
        160: np.r_[-1012:-514, -509:-11, 12:510, 515:1013].astype(np.int32),
                                                          # HE160_1992Subcarriers_Indices,
    },
    2: {
        20: np.r_[-28:0, 1:29].astype(np.int32),          # HTVHT20_56Subcarriers_Indices,
        40: np.r_[-58:-1, 2:59].astype(np.int32),         # HTVHT40_114Subcarriers_Indices,
        80: np.r_[-122:-1, 2:123].astype(np.int32),       # VHT80_242Subcarriers_Indices,
        160: np.r_[-250:-129, -126:-5, 6:127, 130:251].astype(np.int32),
                                                          # VHT160_484Subcarriers_Indices,
    },
    1: {
        20: np.r_[-28:0, 1:29].astype(np.int32),          # HTVHT20_56Subcarriers_Indices,
        40: np.r_[-58:-1, 2:59].astype(np.int32),         # HTVHT40_114Subcarriers_Indices,
    },
    0: {
        20: np.r_[-26:0, 1:27].astype(np.int32),          # NonHT20_52Subcarriers_Indices
    },
}


cdef SC_INDICES_5300 = {
    20: np.r_[-28:-1:2, -1, 1:28:2, 28].astype(np.int32),  # IWL5300SubcarrierIndices_CBW20
    40: np.r_[-58:-2:4, -2, 2:58:4, 58].astype(np.int32),  # IWL5300SubcarrierIndices_CBW40
}


cdef FILE* crfopen(str file):
    tempfile = file.encode(encoding="utf-8")
    cdef char *datafile = tempfile
    cdef FILE *f = fopen(datafile, "rb")
    if f is NULL:
        printf("Open failed!\n")
        exit(-1)
    return f


cdef unsigned char *crfread(unsigned char *buf, uint32_t *buf_size,
                            FILE *f):
    cdef size_t l
    l = fread(buf, sizeof(unsigned char), 4, f)
    field_len = cu32(buf) + 4
    fseek(f, -4, SEEK_CUR)
    if buf_size[0] < field_len:
        buf = <unsigned char *>realloc(buf, field_len)
        buf_size[0] = field_len
    l = fread(buf, sizeof(unsigned char), field_len, f)
    return buf


cdef long getfilesize(FILE *f, pos):
    fseek(f, 0, SEEK_END)
    cdef long lens = ftell(f)
    fseek(f, pos, SEEK_SET)
    return lens


cdef inline uint8_t cu8(unsigned char *buf):
    return (<uint8_t*>buf)[0]


cdef inline uint16_t cu16(unsigned char *buf):
    return (<uint16_t*>buf)[0]


cdef inline uint32_t cu32(unsigned char *buf):
    return (<uint32_t*>buf)[0]


cdef inline uint64_t cu64(unsigned char *buf):
    return (<uint64_t*>buf)[0]


cdef inline int16_t c16(unsigned char *buf):
    return (<int16_t*>buf)[0]


cdef inline double cd64(unsigned char *buf):
    return (<double*>buf)[0]


cdef AbstractPicoScenesFrameSegment parse_AbstractPicoScenesFrameSegment(unsigned char *buf):
    cdef AbstractPicoScenesFrameSegment apsfs
    apsfs.segmentLength = cu32(buf)
    apsfs.segNameLength = cu8(buf + 4)
    apsfs.segmentName = buf + 5
    apsfs.versionId = cu16(buf + 5 + apsfs.segNameLength)
    return apsfs


cdef parseCSI9300scidx(np.int32_t[:] scidx, int8_t format,
                       uint16_t cbw, int offset):
    cdef int i
    cdef np.ndarray[np.int32_t] indices = SC_INDICES_9300[format][cbw]
    if scidx.shape[0] < len(indices):
        return False

    for i in range(len(indices)):
        scidx[i] = indices[i] + offset
    return True


cdef parseCSI5300scidx(np.int32_t[:] scidx, int8_t format,
                       uint16_t cbw, int offset):
    cdef int i
    cdef np.ndarray[np.int32_t] indices = SC_INDICES_5300[cbw]
    if scidx.shape[0] < len(indices):
        return False

    for i in range(len(indices)):
        scidx[i] = indices[i] + offset
    return True


cdef parseCSIUSRPscidx(np.int32_t[:] scidx, unsigned char *payload,
                       int16_t numTones):
    cdef int i
    if scidx.shape[0] < numTones:
        return False

    for i in range(numTones):
        scidx[i] = c16(payload + i * 2)
    return True


cdef parseCSI9300(np.complex128_t[:, :, :] csi, unsigned char *payload,
                  uint16_t numTones, uint8_t numTx, uint8_t numRx):
    cdef int i, j
    cdef int tempArray[4]
    cdef int valuePos, pos, rxIndex, txIndex, toneIndex
    cdef uint16_t negativeSignBit = (1 << (10 - 1))
    cdef uint16_t minNegativeValue = (1 << 10)

    if numTones > csi.shape[0] or numRx > csi.shape[1] or numTx > csi.shape[2]:
        return False

    for i in range((numTones * numTx * numRx) >> 1):
        j = i * 5
        tempArray[0] = ((payload[j + 0] & 0xffU) >> 0U) + \
                       ((payload[j + 1] & 0x03u) << 8u)
        tempArray[1] = ((payload[j + 1] & 0xfcU) >> 2U) + \
                       ((payload[j + 2] & 0x0fU) << 6U)
        tempArray[2] = ((payload[j + 2] & 0xf0U) >> 4U) + \
                       ((payload[j + 3] & 0x3fU) << 4U)
        tempArray[3] = ((payload[j + 3] & 0xc0U) >> 6U) + \
                       ((payload[j + 4] & 0xffU) << 2U)
        for j in range(4):
            if (tempArray[j] & negativeSignBit):
                tempArray[j] -= minNegativeValue

        valuePos = i * 2
        rxIndex = valuePos % numRx
        txIndex = (valuePos // numRx) % numTx
        toneIndex = valuePos // (numRx * numTx);
        csi[toneIndex, rxIndex, txIndex].real = tempArray[1]
        csi[toneIndex, rxIndex, txIndex].imag = tempArray[0]

        valuePos += 1
        rxIndex = valuePos % numRx
        txIndex = (valuePos // numRx) % numTx
        toneIndex = valuePos // (numRx * numTx);
        csi[toneIndex, rxIndex, txIndex].real = tempArray[3]
        csi[toneIndex, rxIndex, txIndex].imag = tempArray[2]
    return True


cdef parseCSI5300(np.complex128_t[:, :, :] csi, unsigned char *payload,
                  uint16_t numTones, uint8_t numTx, uint8_t numRx,
                  uint8_t antSel):
    """Parse CSI of Intel 5300 NIC

    Important:
        1. rxs_parsing_core does a permutation(dobule sort) with `antSel` in
        CSISegment.hxx(parseIWL5300CSIData). However, It seems that I can get
        the same result without permutation
    """
    cdef int i, j, k, pos
    cdef int index_step, perm_j
    cdef int index = 0
    cdef uint8_t remainder
    cdef double a, b

    if numTones > csi.shape[0] or numRx > csi.shape[1] or numTx > csi.shape[2]:
        return False

    for i in range(numTones):
        index += 3
        remainder = index % 8
        for j in range(numRx):
            for k in range(numTx):
                index_step =  index >> 3
                a = <double><int8_t>(((payload[index_step + 0] >> remainder) | (payload[index_step + 1] << (8 - remainder))) & 0xff)
                b = <double><int8_t>(((payload[index_step + 1] >> remainder) | (payload[index_step + 2] << (8 - remainder))) & 0xff)
                csi[i, j, k].real = a
                csi[i, j, k].imag = b
                index += 16
    return True


cdef parseCSIUSRP(np.complex128_t[:, :, :] csi, unsigned char *payload,
                  uint32_t csiBufferLength):
    """parseSignalMatrix = parseCSIUSRP"""
    cdef uint32_t i, j, k, g
    cdef uint32_t offset = 0
    cdef uint8_t matrixVersion = cu8(payload+3) - 48
    cdef uint8_t ndim = cu8(payload+4)
    offset += 5
    cdef uint16_t shape[3]

    for i in range(3):
        shape[i] = 1
    for i in range(ndim):
        if matrixVersion == 1:
            shape[i] = cu32(payload+offset)
            offset += 4
        if matrixVersion == 2:
            shape[i] = cu64(payload+offset)
            offset += 8

    if shape[0] > csi.shape[0] or shape[1] > csi.shape[1] or shape[2] > csi.shape[2]:
        return False

    offset += 4
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                g = (i * (shape[1] * shape[2]) + j * shape[2] + k) * 16
                csi[i, j, k].real = cd64(payload + offset + g + 0)
                csi[i, j, k].imag = cd64(payload + offset + g + 8)
    return True


cdef parse_SignalMatrixV1(unsigned char *buf, dtc_SignalMatrix_info *m,
                          np.complex128_t[:, :, :] data):
    """parseSignalMatrix = parseCSIUSRP"""
    cdef uint32_t i, j, k, g
    cdef uint32_t offset = 0
    cdef uint8_t matrixVersion = cu8(buf+3) - 48
    m.ndim = cu8(buf+4)
    offset += 5

    for i in range(3):
        m.shape[i] = 1
    for i in range(m.ndim):
        if matrixVersion == 1:
            m.shape[i] = cu32(buf+offset)
            offset += 4
        if matrixVersion == 2:
            m.shape[i] = cu64(buf+offset)
            offset += 8

    cdef bytes complexChar = <char>cu8(buf+offset+0)
    cdef bytes typeChar = <char>cu8(buf+offset+1)
    m.itemsize = cu8(buf+offset+2)
    m.majority = <char>cu8(buf+offset+3)
    offset += 4

    if m.shape[0] > data.shape[0] or m.shape[1] > data.shape[1] or m.shape[2] > data.shape[2]:
        return False

    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            for k in range(m.shape[2]):
                g = (i * (m.shape[1] * m.shape[2]) + j * m.shape[2] + k) * 16
                data[i, j, k].real = cd64(buf + offset + g + 0)
                data[i, j, k].imag = cd64(buf + offset + g + 8)
    return True


cdef parse_RxSBasicV1(unsigned char *buf, dtc_RXBasic *m):
    cdef RxSBasicV1 *rsbv1 = <RxSBasicV1*>buf
    m.deviceType = rsbv1.deviceType
    m.timestamp = rsbv1.tstamp
    m.centerFreq = rsbv1.centerFreq
    m.controlFreq = rsbv1.centerFreq
    m.packetFormat = rsbv1.packetFormat
    m.CBW = rsbv1.cbw
    m.packetCBW = rsbv1.cbw
    m.GI = rsbv1.guardInterval
    m.MCS = rsbv1.mcs
    m.numSTS = rsbv1.numSTS
    m.numESS = rsbv1.numESS
    m.numRx = rsbv1.numRx
    m.noiseFloor = rsbv1.noiseFloor
    m.rssi = rsbv1.noiseFloor + rsbv1.rssi
    m.rssi1 = rsbv1.noiseFloor + rsbv1.rssi_ctl0
    m.rssi2 = rsbv1.noiseFloor + rsbv1.rssi_ctl1
    m.rssi3 = rsbv1.noiseFloor + rsbv1.rssi_ctl2


cdef parse_RxSBasicV2(unsigned char *buf, dtc_RXBasic *m):
    cdef RxSBasicV2 *rsbv2 = <RxSBasicV2*>buf
    m.deviceType = rsbv2.deviceType
    m.timestamp = rsbv2.tstamp
    m.centerFreq = rsbv2.centerFreq
    m.controlFreq = rsbv2.centerFreq
    m.packetFormat = rsbv2.packetFormat
    m.CBW = rsbv2.cbw
    m.packetCBW = rsbv2.cbw
    m.GI = rsbv2.guardInterval
    m.MCS = rsbv2.mcs
    m.numSTS = rsbv2.numSTS
    m.numESS = rsbv2.numESS
    m.numRx = rsbv2.numRx
    m.noiseFloor = rsbv2.noiseFloor
    m.rssi = rsbv2.noiseFloor + rsbv2.rssi
    m.rssi1 = rsbv2.noiseFloor + rsbv2.rssi_ctl0
    m.rssi2 = rsbv2.noiseFloor + rsbv2.rssi_ctl1
    m.rssi3 = rsbv2.noiseFloor + rsbv2.rssi_ctl2


cdef parse_RxSBasicV3(unsigned char *buf, dtc_RXBasic *m):
    cdef RxSBasicV3 *rsbv3 = <RxSBasicV3*>buf
    m.deviceType = rsbv3.deviceType
    m.timestamp = rsbv3.tstamp
    m.centerFreq = rsbv3.centerFreq
    m.controlFreq = rsbv3.controlFreq
    m.packetFormat = rsbv3.packetFormat
    m.CBW = rsbv3.cbw
    m.packetCBW = rsbv3.pkt_cbw
    m.GI = rsbv3.guardInterval
    m.MCS = rsbv3.mcs
    m.numSTS = rsbv3.numSTS
    m.numESS = rsbv3.numESS
    m.numRx = rsbv3.numRx
    m.noiseFloor = rsbv3.noiseFloor
    m.rssi = rsbv3.rssi
    m.rssi1 = rsbv3.rssi_ctl0
    m.rssi2 = rsbv3.rssi_ctl1
    m.rssi3 = rsbv3.rssi_ctl2





cdef parse_ExtraInfoV1(unsigned char *buf, dtc_ExtraInfo *m):
    cdef FeatureCode *featurecode = <FeatureCode*>buf
    cdef int offset = 4
    cdef int i

    m.hasLength = featurecode.hasLength
    m.hasVersion = featurecode.hasVersion
    m.hasMacAddr_cur = featurecode.hasMacAddr_cur
    m.hasMacAddr_rom = featurecode.hasMacAddr_rom
    m.hasChansel = featurecode.hasChansel
    m.hasBMode = featurecode.hasBMode
    m.hasEVM = featurecode.hasEVM
    m.hasTxChainMask = featurecode.hasTxChainMask
    m.hasRxChainMask = featurecode.hasRxChainMask
    m.hasTxpower = featurecode.hasTxpower
    m.hasCF = featurecode.hasCF
    m.hasTxTSF = featurecode.hasTxTSF
    m.hasLastHwTxTSF = featurecode.hasLastHWTxTSF
    m.hasChannelFlags = featurecode.hasChannelFlags
    m.hasTxNess = featurecode.hasTxNess
    m.hasTuningPolicy = featurecode.hasTuningPolicy
    m.hasPLLRate = featurecode.hasPLLRate
    m.hasPLLClkSel = featurecode.hasPLLRefDiv
    m.hasPLLRefDiv = featurecode.hasPLLClkSel
    m.hasAGC = featurecode.hasAGC
    m.hasAntennaSelection = featurecode.hasAntennaSelection
    m.hasSamplingRate = featurecode.hasSamplingRate
    m.hasCFO = featurecode.hasCFO
    m.hasSFO = featurecode.hasSFO

    if featurecode.hasLength:
        m.length = cu16(buf + offset)
        offset += 2
    if featurecode.hasVersion:
        m.version = cu64(buf + offset)
        offset += 8
    if featurecode.hasMacAddr_cur:
        for i in range(6):
            m.macaddr_cur[i] = cu8(buf + offset + i)
        offset += 6
    if featurecode.hasMacAddr_rom:
        for i in range(6):
            m.macaddr_rom[i] = cu8(buf + offset + i)
        offset += 6
    if featurecode.hasChansel:
        m.chansel = cu32(buf + offset)
        offset += 4
    if featurecode.hasBMode:
        m.bmode =cu8(buf + offset)
        offset += 1
    if featurecode.hasEVM:
        for i in range(20):
            m.evm[i] = cu8(buf + offset + i)
        offset += 20
    if featurecode.hasTxChainMask:
        m.tx_chainmask = cu8(buf + offset)
        offset += 1
    if featurecode.hasRxChainMask:
        m.rx_chainmask = cu8(buf + offset)
        offset += 1
    if featurecode.hasTxpower:
        m.txpower = cu8(buf + offset)
        offset += 1
    if featurecode.hasCF:
        m.cf = cu64(buf + offset)
        offset += 8
    if featurecode.hasTxTSF:
        m.txtsf = cu32(buf + offset)
        offset += 4
    if featurecode.hasLastHWTxTSF:
        m.last_txtsf = cu32(buf + offset)
        offset += 4
    if featurecode.hasChannelFlags:
        m.channel_flags = cu16(buf + offset)
        offset += 2
    if featurecode.hasTxNess:
        m.tx_ness = cu8(buf + offset)
        offset += 1
    if featurecode.hasTuningPolicy:
        m.tuning_policy = cu8(buf + offset)
        offset += 1
    if featurecode.hasPLLRate:
        m.pll_rate = cu16(buf + offset)
        offset += 2
    if featurecode.hasPLLClkSel:
        m.pll_clock_select = cu8(buf + offset)
        offset += 1
    if featurecode.hasPLLRefDiv:
        m.pll_refdiv = cu8(buf + offset)
        offset += 1
    if featurecode.hasAGC:
        m.agc = cu8(buf + offset)
        offset += 1
    if featurecode.hasAntennaSelection:
        m.ant_sel[0] = (cu8(buf + offset)) & 0x1U
        m.ant_sel[1] = (cu8(buf + offset) >> 0x2U) & 0x1U
        m.ant_sel[2] = (cu8(buf + offset) >> 0x4U) & 0x1U
        offset += 1
    if featurecode.hasSamplingRate:
        m.sf = cu64(buf + offset)
        offset += 8
    if featurecode.hasCFO:
        m.cfo = cu32(buf + offset)
        offset += 4
    if featurecode.hasSFO:
        m.sfo = cu32(buf + offset)
        offset += 4


cdef parse_MVMExtraV1(unsigned char *buf, dtc_IntelMVMExtrta *m):
    cdef IntelMVMExtrta *imvme = <IntelMVMExtrta*>buf
    m.FMTClock = imvme.parsedHeader.ftmClock
    m.usClock = imvme.parsedHeader.muClock
    m.RateNFlags = imvme.parsedHeader.rate_n_flags


cdef parse_CSIV1(unsigned char *buf, dtc_CSI_info *m,
                 np.ndarray[np.complex128_t, ndim=3] csi,
                 np.ndarray[np.int32_t] scidx):
    cdef CSIV1 *csiv1 = <CSIV1*>buf
    cdef int actualNumSTSPerChain

    m.DeviceType = csiv1.deviceType
    m.PacketFormat = csiv1.packetFormat
    m.CBW = csiv1.cbw
    m.CarrierFreq = csiv1.carrierFreq
    m.SamplingRate = csiv1.samplingRate
    m.SubcarrierBandwidth = csiv1.subcarrierBandwidth
    m.numTones = csiv1.numTones
    m.numTx = csiv1.numTx
    m.numRx = csiv1.numRx
    if csiv1.deviceType == 0x9300:
        actualNumSTSPerChain = csiv1.csiBufferLength // (140 if csiv1.cbw == 20 else 285) // csiv1.numRx
        m.numESS = actualNumSTSPerChain - csiv1.numTx
        m.numCSI = 1
        m.ant_sel = csiv1.antSel
        parseCSI9300scidx(scidx, csiv1.packetFormat, csiv1.cbw, 0)
        parseCSI9300(csi, csiv1.payload, csiv1.numTones, actualNumSTSPerChain, csiv1.numRx)
    elif csiv1.deviceType == 0x5300:
        actualNumSTSPerChain = (csiv1.csiBufferLength - 12) // 60 // csiv1.numRx
        m.numESS = actualNumSTSPerChain - csiv1.numTx
        m.numCSI = 1
        m.ant_sel = csiv1.antSel
        parseCSI5300scidx(scidx, csiv1.packetFormat, csiv1.cbw, 0)
        parseCSI5300(csi, csiv1.payload, csiv1.numTones, actualNumSTSPerChain, csiv1.numRx, csiv1.antSel)
    elif csiv1.deviceType == 0x1234:
        m.numESS = csiv1.numESS
        m.numCSI = 1
        m.ant_sel = csiv1.antSel
        parseCSIUSRPscidx(scidx, csiv1.payload, csiv1.numTones)
        parseCSIUSRP(csi, csiv1.payload + csiv1.numTones * 2, csiv1.csiBufferLength - csiv1.numTones * 2)


cdef parse_CSIV2(unsigned char *buf, dtc_CSI_info *m,
                 np.ndarray[np.complex128_t, ndim=3] csi,
                 np.ndarray[np.int32_t] scidx):    
    cdef CSIV2 *csiv2 = <CSIV2*>buf
    cdef int actualNumSTSPerChain

    m.DeviceType = csiv2.deviceType
    m.PacketFormat = csiv2.packetFormat
    m.CBW = csiv2.cbw
    m.CarrierFreq = csiv2.carrierFreq
    m.SamplingRate = csiv2.samplingRate
    m.SubcarrierBandwidth = csiv2.subcarrierBandwidth
    m.numTones = csiv2.numTones
    m.numTx = csiv2.numTx
    m.numRx = csiv2.numRx
    if csiv2.deviceType == 0x9300:
        actualNumSTSPerChain = csiv2.csiBufferLength // (140 if csiv2.cbw == 20 else 285) // csiv2.numRx
        m.numESS = actualNumSTSPerChain - csiv2.numTx
        m.numCSI = 1
        m.ant_sel = csiv2.antSel
        parseCSI9300scidx(scidx, csiv2.packetFormat, csiv2.cbw, csiv2.subcarrierOffset)
        parseCSI9300(csi, csiv2.payload, csiv2.numTones, actualNumSTSPerChain, csiv2.numRx)
    elif csiv2.deviceType == 0x5300:
        actualNumSTSPerChain = (csiv2.csiBufferLength - 12) // 60 // csiv2.numRx
        m.numESS = actualNumSTSPerChain - csiv2.numTx
        m.numCSI = 1
        m.ant_sel = csiv2.antSel
        parseCSI5300scidx(scidx, csiv2.packetFormat, csiv2.cbw, csiv2.subcarrierOffset)
        parseCSI5300(csi, csiv2.payload, csiv2.numTones, actualNumSTSPerChain, csiv2.numRx, csiv2.antSel)
    elif csiv2.deviceType == 0x1234:
        m.numESS = csiv2.numESS
        m.numCSI = 1
        m.ant_sel = csiv2.antSel
        parseCSIUSRPscidx(scidx, csiv2.payload, csiv2.numTones)
        parseCSIUSRP(csi, csiv2.payload + csiv2.numTones * 2, csiv2.csiBufferLength - csiv2.numTones * 2)


cdef parse_CSIV3(unsigned char *buf, dtc_CSI_info *m,
                 np.ndarray[np.complex128_t, ndim=3] csi,
                 np.ndarray[np.int32_t] scidx):
    cdef CSIV3 *csiv3 = <CSIV3*>buf
    cdef int actualNumSTSPerChain

    m.DeviceType = csiv3.deviceType
    m.PacketFormat = csiv3.packetFormat
    m.CBW = csiv3.cbw
    m.CarrierFreq = csiv3.carrierFreq
    m.SamplingRate = csiv3.samplingRate
    m.SubcarrierBandwidth = csiv3.subcarrierBandwidth
    m.numTones = csiv3.numTones
    m.numTx = csiv3.numTx
    m.numRx = csiv3.numRx
    if csiv3.deviceType == 0x9300:
        actualNumSTSPerChain = csiv3.csiBufferLength // (140 if csiv3.cbw == 20 else 285) // csiv3.numRx
        m.numESS = actualNumSTSPerChain - csiv3.numTx
        m.numCSI = 1
        m.ant_sel = csiv3.antSel
        parseCSI9300scidx(scidx, csiv3.packetFormat, csiv3.cbw, csiv3.subcarrierOffset)
        parseCSI9300(csi, csiv3.payload, csiv3.numTones, actualNumSTSPerChain, csiv3.numRx)
    elif csiv3.deviceType == 0x5300:
        actualNumSTSPerChain = (csiv3.csiBufferLength - 12) // 60 // csiv3.numRx
        m.numESS = actualNumSTSPerChain - csiv3.numTx
        m.numCSI = 1
        m.ant_sel = csiv3.antSel
        parseCSI5300scidx(scidx, csiv3.packetFormat, csiv3.cbw, csiv3.subcarrierOffset)
        parseCSI5300(csi, csiv3.payload, csiv3.numTones, actualNumSTSPerChain, csiv3.numRx, csiv3.antSel)
    elif csiv3.deviceType == 0x1234:
        m.numESS = csiv3.numESS
        m.numCSI = csiv3.numCSI
        m.ant_sel = csiv3.antSel
        parseCSIUSRPscidx(scidx, csiv3.payload, csiv3.numTones)
        parseCSIUSRP(csi, csiv3.payload + csiv3.numTones * 2, csiv3.csiBufferLength - csiv3.numTones * 2)


cdef parse_MPDU(unsigned char *buf, dtc_MPDU_info *m, np.uint8_t[:] mpdu, uint32_t length):
    cdef uint32_t i
    m.length = length
    if mpdu.shape[0] < length:
        return False

    for i in range(length):
        mpdu[i] = cu8(buf + i)
    return True


cdef parse_StandardHeader(unsigned char *buf, dtc_ieee80211_mac_frame_header *m):
    cdef ieee80211_mac_frame_header *imfh = <ieee80211_mac_frame_header*>buf
    cdef int i

    m.ControlField.Version = imfh.fc.version
    m.ControlField.Type = imfh.fc.type
    m.ControlField.SubType = imfh.fc.subtype
    m.ControlField.ToDS = imfh.fc.toDS
    m.ControlField.FromDS = imfh.fc.fromDS
    m.ControlField.MoreFrags = imfh.fc.moreFrags
    m.ControlField.Retry = imfh.fc.retry
    m.ControlField.PowerManagement = imfh.fc.power_mgmt
    m.ControlField.More = imfh.fc.more
    m.ControlField.Protected = imfh.fc.protect
    m.ControlField.Order = imfh.fc.order
    for i in range(6):
        m.Addr1[i] = imfh.addr1[i]
        m.Addr2[i] = imfh.addr2[i]
        m.Addr3[i] = imfh.addr3[i]
    m.Fragment = imfh.frag
    m.Sequence = imfh.seq


cdef parse_PicoScenesHeader(unsigned char *buf, dtc_PicoScenesFrameHeader *m):
    cdef PicoScenesFrameHeader *psfh = <PicoScenesFrameHeader*>buf
    m.MagicValue = psfh.magicValue
    m.Version = psfh.version
    m.DeviceType = psfh.deviceType
    m.FrameType = psfh.frameType
    m.TaskId = psfh.taskId
    m.TxId = psfh.txId


cdef parse_RxSBasic(uint16_t versionId, unsigned char *buf, dtc_RXBasic *m):
    if versionId == 0x1:
        parse_RxSBasicV1(buf, m)
    elif versionId == 0x2:
        parse_RxSBasicV2(buf, m)
    elif versionId == 0x3:
        parse_RxSBasicV3(buf, m)
    else:
        pass


cdef parse_ExtraInfo(uint16_t versionId, unsigned char *buf, dtc_ExtraInfo *m):
    if versionId == 0x1:
        parse_ExtraInfoV1(buf, m)
    else:
        pass


cdef parse_MVMExtra(uint16_t versionId, unsigned char *buf, dtc_IntelMVMExtrta *m):
    if versionId == 0x1:
        parse_MVMExtraV1(buf, m)
    else:
        pass


cdef parse_CSI(uint16_t versionId, unsigned char *buf, dtc_CSI_info *m,
               np.ndarray[np.complex128_t, ndim=3] csi,
               np.ndarray[np.int32_t] scidx):
    if versionId == 0x1:
        parse_CSIV1(buf, m, csi, scidx)
    elif versionId == 0x2:
        parse_CSIV2(buf, m, csi, scidx)
    elif versionId == 0x3:
        parse_CSIV3(buf, m, csi, scidx)
    else:
        pass


cdef parse_SignalMatrix(uint16_t versionId, unsigned char *buf, dtc_SignalMatrix_info *m,
                       np.complex128_t[:, :, :] data):
    if versionId == 0x1:
        parse_SignalMatrixV1(buf, m, data)
    else:
        pass

# Section 5: Picoscenes


cdef class Picoscenes:
    cdef readonly str file
    cdef readonly int count

    cdef public np.ndarray raw

    cdef bint if_report

    def __cinit__(self, file, dtype, if_report=True, bufsize=0,
                  *argv, **kw):
        self.file = file
        self.if_report = if_report

    def __init__(self, file, dtype, if_report=True, bufsize=0):
        pk_num = self.__get_pknum(bufsize)
        self.raw = init_array(pk_num, dtype)

    cdef __get_pknum(self, bufsize):
        if bufsize == 0:
            if self.file is None:
                self.count = 1
                pk_num = 1
                self.count = 1
            else:
                pk_num = self.__get_count()
        else:
            pk_num = bufsize
        return pk_num

    cdef __get_count(self):
        cdef int count = 0
        cdef long pos = 0
        cdef uint32_t field_len
        cdef size_t l
        cdef FILE *f = crfopen(self.file)
        cdef lens = getfilesize(f, 0)
        cdef unsigned char buf[4]

        while pos < (lens - 4):
            l = fread(buf, sizeof(unsigned char), 4, f)
            field_len = cu32(buf) + 4
            fseek(f, field_len - 4, SEEK_CUR)

            pos += field_len
            count += 1
        fclose(f)
        return count

    cpdef read(self):
        self.seek(self.file, 0, 0) 

    cpdef seek(self, file, long pos, long num):
        cdef FILE *f = crfopen(self.file)
        cdef lens = getfilesize(f, 0)
        cdef uint32_t buf_size = 4              # Require: buf_size >= 4
        cdef unsigned char *buf = <unsigned char *>malloc(
            buf_size * sizeof(unsigned char))
        if num == 0:
            num = lens

        # Todo:
        # 1. dtypedef np.ndarray[...]
        # 2. rename mem_xxxxxx
        cdef np.ndarray[dtc_ieee80211_mac_frame_header] mem_StandardHeader = self.raw["StandardHeader"]
        cdef np.ndarray[dtc_RXBasic] mem_RxSBasic = self.raw["RxSBasic"]
        cdef np.ndarray[dtc_ExtraInfo] mem_RxExtraInfo = self.raw["RxExtraInfo"]
        cdef np.ndarray[dtc_CSI_info] mem_CSI_info = self.raw["CSI"]["info"]
        cdef np.ndarray[dtc_IntelMVMExtrta] mem_MVMExtra = self.raw["MVMExtra"]
        cdef np.ndarray[dtc_PicoScenesFrameHeader] mem_PicoScenesHeader = self.raw["PicoScenesHeader"]
        cdef np.ndarray[dtc_ExtraInfo] mem_TxExtraInfo = self.raw["TxExtraInfo"]
        cdef np.ndarray[dtc_CSI_info] mem_PilotCSI_info = self.raw["PilotCSI"]["info"]
        cdef np.ndarray[dtc_CSI_info] mem_LegacyCSI_info = self.raw["LegacyCSI"]["info"]
        cdef np.ndarray[dtc_SignalMatrix_info] mem_BasebandSignals_info = self.raw["BasebandSignals"]["info"]
        cdef np.ndarray[dtc_SignalMatrix_info] mem_PreEQSymbols_info = self.raw["PreEQSymbols"]["info"]
        cdef np.ndarray[dtc_MPDU_info] mem_MPDU_info = self.raw["MPDU"]["info"]

        cdef np.ndarray[np.complex128_t, ndim=4] mem_CSI_CSI = self.raw["CSI"]["CSI"]
        cdef np.ndarray[np.complex128_t, ndim=4] mem_PilotCSI_CSI = self.raw["PilotCSI"]["CSI"]
        cdef np.ndarray[np.complex128_t, ndim=4] mem_LegacyCSI_CSI = self.raw["LegacyCSI"]["CSI"]
        cdef np.ndarray[np.complex128_t, ndim=4] mem_BasebandSignals_data = self.raw["BasebandSignals"]["data"]
        cdef np.ndarray[np.complex128_t, ndim=4] mem_PreEQSymbols_data = self.raw["PreEQSymbols"]["data"]
        cdef np.ndarray[np.uint8_t, ndim=2] mem_MPDU_data = self.raw["MPDU"]["data"]

        cdef np.ndarray[np.int32_t, ndim=2] mem_CSI_SubcarrierIndex = self.raw["CSI"]["SubcarrierIndex"]
        cdef np.ndarray[np.int32_t, ndim=2] mem_PilotCSI_SubcarrierIndex = self.raw["PilotCSI"]["SubcarrierIndex"]
        cdef np.ndarray[np.int32_t, ndim=2] mem_LegacyCSI_SubcarrierIndex = self.raw["LegacyCSI"]["SubcarrierIndex"]

        cdef int count = 0
        cdef int cur = 0
        cdef int i, offset
        cdef ModularPicoScenesRxFrameHeader *mpsrfh
        cdef AbstractPicoScenesFrameSegment apsfs
        cdef PicoScenesFrameHeader *psfh

        while pos < (lens-4):
            buf = crfread(buf, &buf_size, f)
            cur = 0

            # ModularPicoScenesRxFrameHeader
            mpsrfh = <ModularPicoScenesRxFrameHeader*>buf
            if mpsrfh.magicWord != 0x20150315  or mpsrfh.frameVersion != 0x1:
                pos += (mpsrfh.frameLength + 4)
                continue
            cur += sizeof(ModularPicoScenesRxFrameHeader)

            # MUST
            for i in range(mpsrfh.numRxSegments):
                apsfs = parse_AbstractPicoScenesFrameSegment(buf + cur)
                offset = apsfs.segNameLength + 7

                if not strncmp(<const char *>apsfs.segmentName, b"RxSBasic", apsfs.segNameLength):
                    parse_RxSBasic(apsfs.versionId, buf + cur + offset, &mem_RxSBasic[count])
                elif not strncmp(<const char *>apsfs.segmentName, b"ExtraInfo", apsfs.segNameLength):
                    parse_ExtraInfo(apsfs.versionId, buf + cur + offset, &mem_RxExtraInfo[count])
                elif not strncmp(<const char *>apsfs.segmentName, b"MVMExtra", apsfs.segNameLength):
                    parse_MVMExtra(apsfs.versionId, buf + cur + offset, &mem_MVMExtra[count])
                elif not strncmp(<const char *>apsfs.segmentName, b"CSI", apsfs.segNameLength):
                    parse_CSI(apsfs.versionId, buf + cur + offset, &mem_CSI_info[count], mem_CSI_CSI[count], mem_CSI_SubcarrierIndex[count])
                elif not strncmp(<const char *>apsfs.segmentName, b"PilotCSI", apsfs.segNameLength):
                    parse_CSI(apsfs.versionId, buf + cur + offset, &mem_PilotCSI_info[count], mem_PilotCSI_CSI[count], mem_PilotCSI_SubcarrierIndex[count])
                elif not strncmp(<const char *>apsfs.segmentName, b"LegacyCSI", apsfs.segNameLength):
                    parse_CSI(apsfs.versionId, buf + cur + offset, &mem_LegacyCSI_info[count], mem_LegacyCSI_CSI[count], mem_LegacyCSI_SubcarrierIndex[count])
                elif not strncmp(<const char *>apsfs.segmentName, b"BasebandSignal", apsfs.segNameLength):
                    parse_SignalMatrix(apsfs.versionId, buf + cur + offset, &mem_BasebandSignals_info[count], mem_BasebandSignals_data[count])
                elif not strncmp(<const char *>apsfs.segmentName, b"PreEQSymbols", apsfs.segNameLength):
                    parse_SignalMatrix(apsfs.versionId, buf + cur + offset, &mem_PreEQSymbols_info[count], mem_PreEQSymbols_data[count])
                else:
                    pass
                cur += (4 + apsfs.segmentLength)

            # MPDU
            parse_MPDU(buf + cur, &mem_MPDU_info[count], mem_MPDU_data[count],  mpsrfh.frameLength + 4 - cur)

            # StandardHeader
            parse_StandardHeader(buf + cur, &mem_StandardHeader[count])
            cur += sizeof(ieee80211_mac_frame_header)

            # PicoScenesFrameHeader
            psfh = <PicoScenesFrameHeader*>(buf + cur)
            if psfh.magicValue == 0x20150315:
                parse_PicoScenesHeader(buf + cur, &mem_PicoScenesHeader[count])
                cur += sizeof(PicoScenesFrameHeader)

                # Optional
                for i in range(psfh.numSegments):
                    apsfs = parse_AbstractPicoScenesFrameSegment(buf + cur)
                    offset = apsfs.segNameLength + 7

                    if not strncmp(<const char *>apsfs.segmentName, b"ExtraInfo", apsfs.segNameLength):
                        parse_ExtraInfo(apsfs.versionId, buf + cur + offset, &mem_TxExtraInfo[count])
                    cur += (4 + apsfs.segmentLength)

            pos += (mpsrfh.frameLength + 4)
            count += 1
            if count >= num:
                break
        free(buf)
        fclose(f)
        self.count = count
        if self.if_report:
            printf("%d packets parsed\n", count)

    cpdef pmsg(self, unsigned char *data):
        # This method hasn't been ready
        return 0xf300       # status code
