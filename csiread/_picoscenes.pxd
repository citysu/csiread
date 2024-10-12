from libc.stdio cimport FILE
from libc.stdint cimport (uint8_t, uint16_t, uint32_t, uint64_t,
                          int8_t, int16_t, int32_t, int64_t)
cimport numpy as np


# Section 1: C struct for parsing


cdef extern from "_picoscenes.h":
    cdef enum PicoScenesDeviceType:
        QCA9300
        IWL5300
        IWLMVM_AX200
        IWLMVM_AX210
        MAC80211Compatible
        USRP
        VirtualSDR
        Unknown
    
    cdef enum PacketFormatEnum:
        PacketFormat_NonHT
        PacketFormat_HT
        PacketFormat_VHT
        PacketFormat_HESU
        PacketFormat_HEMU
        PacketFormat_Unknown

    cdef enum ChannelBandwidthEnum:
        CBW_5
        CBW_10
        CBW_20
        CBW_40
        CBW_80
        CBW_160

    cdef enum ChannelModeEnum:
        HT20
        HT40_MINUS
        HT40_PLUS

    cdef enum GuardIntervalEnum:
        GI_400
        GI_800
        GI_1600
        GI_3200

    cdef enum ChannelCodingEnum:
        BCC
        LDPC

    cdef enum AtherosCFTuningPolicy:
        CFTuningByChansel
        CFTuningByFastCC
        CFTuningByHardwareReset
        CFTuningByDefault

    cdef struct PilotScidx:
        int16_t NonHT20_52[4]
        int16_t HTVHT20_56[4]
        int16_t HTVHT40_114[6]
        int16_t VHT80_242[8]
        int16_t VHT160_484[16]
        int16_t HE20_242[8]
        int16_t HE40_484[16]
        int16_t HE80_996[16]
        int16_t HE160_1992[32]

    cdef PilotScidx pilot_scidx

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
        uint32_t hasTemperature
    
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

    cdef packed struct DPASRequestV1:
        uint16_t batchId
        uint16_t batchLength
        uint16_t sequenceId
        uint16_t intervalTime
    
    cdef packed struct DPASRequestV2:
        uint16_t batchId
        uint16_t batchLength
        uint16_t sequenceId
        uint16_t intervalTime
        uint16_t intervalStep
    
    cdef packed struct DPASRequestV3:
        uint16_t batchId
        uint16_t batchLength
        uint16_t sequenceId
        uint16_t intervalTime
        uint16_t intervalStep
        uint16_t deviceType             # PicoScenesDeviceType
        uint64_t carrierFrequency
        uint32_t samplingFrequency

    cdef packed struct DPASRequestV4:
        uint8_t  requestMode
        uint16_t batchId
        uint16_t batchLength
        uint16_t sequenceId
        uint16_t intervalTime
        uint16_t intervalStep
        uint16_t deviceType             # PicoScenesDeviceType
        uint16_t deviceSubtype
        uint64_t carrierFrequency
        uint32_t samplingFrequency

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

    cdef packed struct CSIV4:
        uint16_t deviceType		    # PicoScenesDeviceType
        uint8_t firmwareVersion
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

# Section 2: cython type for `raw` array.


cdef packed struct dtc_ieee80211_mac_frame_header_frame_control_field:
    uint16_t Version
    uint16_t Type
    uint16_t SubType
    uint16_t ToDS
    uint16_t FromDS
    uint16_t MoreFrags
    uint16_t Retry
    uint16_t PowerManagement
    uint16_t More
    uint16_t Protected
    uint16_t Order


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
    uint8_t hasTemperature

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
    int8_t temperature


cdef packed struct dtc_CSI_Info:
    uint16_t DeviceType
    uint8_t firmwareVersion
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

cdef packed struct dtc_DPASRequest:
    uint8_t  requestMode
    uint16_t batchId
    uint16_t batchLength
    uint16_t sequenceId
    uint16_t intervalTime
    uint16_t intervalStep
    uint16_t deviceType             # PicoScenesDeviceType
    uint16_t deviceSubtype
    uint64_t carrierFrequency
    uint32_t samplingFrequency


cdef packed struct dtc_PicoScenesFrameHeader:
    uint32_t MagicValue
    uint32_t Version
    uint16_t DeviceType
    uint8_t FrameType
    uint16_t TaskId
    uint16_t TxId


cdef packed struct dtc_SignalMatrix_Info:
    uint8_t ndim
    uint16_t shape[3]
    uint8_t itemsize
    char majority


cdef packed struct dtc_MPDU_Info:
    uint32_t length


# Section 3: Picoscenes


cdef class Picoscenes:
    cdef readonly str file
    cdef readonly int count

    cdef public np.ndarray raw
    cdef np.ndarray cache

    cdef dtc_ieee80211_mac_frame_header[:] mem_StandardHeader
    cdef dtc_RXBasic[:] mem_RxSBasic
    cdef dtc_ExtraInfo[:] mem_RxExtraInfo
    cdef dtc_DPASRequest[:] mem_DPASRequest
    cdef dtc_CSI_Info[:] mem_CSI_Info
    cdef dtc_IntelMVMExtrta[:] mem_MVMExtra
    cdef dtc_PicoScenesFrameHeader[:] mem_PicoScenesHeader
    cdef dtc_ExtraInfo[:] mem_TxExtraInfo
    cdef dtc_CSI_Info[:] mem_PilotCSI_Info
    cdef dtc_CSI_Info[:] mem_LegacyCSI_Info
    cdef dtc_SignalMatrix_Info[:] mem_BasebandSignals_Info
    cdef dtc_SignalMatrix_Info[:] mem_PreEQSymbols_Info
    cdef dtc_MPDU_Info[:] mem_MPDU_Info
    cdef np.complex128_t[:, :, :, :] mem_CSI_CSI
    cdef np.complex128_t[:, :, :, :] mem_PilotCSI_CSI
    cdef np.complex128_t[:, :, :, :] mem_LegacyCSI_CSI
    cdef np.complex128_t[:, :, :, :] mem_BasebandSignals_Data
    cdef np.complex128_t[:, :, :, :] mem_PreEQSymbols_Data
    cdef np.uint8_t[:, :] mem_MPDU_Data
    cdef np.int32_t[:, :] mem_CSI_SubcarrierIndex
    cdef np.int32_t[:, :] mem_PilotCSI_SubcarrierIndex
    cdef np.int32_t[:, :] mem_LegacyCSI_SubcarrierIndex

    cdef bint if_report

    cpdef read(self)
    cpdef seek(self, file, long pos, long num)
    cpdef pmsg(self, data)
    cpdef interpolate_csi(self, name, bint IQ=?)
    cdef void init_memview(self)
    cdef int get_pknum(self, int bufsize)
    cdef int get_count(self)
    cdef bint parse(self, unsigned char *buf, uint32_t buf_length, int count)
