from libc.stdio cimport (fopen, fread, fclose, fseek, ftell, printf, FILE,
                         SEEK_END, SEEK_SET, SEEK_CUR)
from libc.stdint cimport (uint8_t, uint16_t, uint32_t, uint64_t,
                          int8_t, int16_t, int32_t, int64_t)
from libc.stdlib cimport malloc, realloc, free
from libc.stddef cimport size_t
from libc.string cimport strncmp
import numpy as np
cimport numpy as np
cimport cython


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

