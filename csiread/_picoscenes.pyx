# distutils: language = c++
from libc.stdio cimport (fopen, fread, fclose, fseek, ftell, printf, FILE,
                         SEEK_END, SEEK_SET, SEEK_CUR)
from libc.stdint cimport (uint8_t, uint16_t, uint32_t, uint64_t,
                          int8_t, int16_t, int32_t, int64_t)
from libc.stdlib cimport malloc, realloc, free
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.complex cimport complex as ccomplex

import numpy as np
cimport numpy as np


cdef extern from "<optional>" namespace "std" nogil:
    cdef cppclass optional[T]:
        ctypedef T value_type
        optional() except +
        optional(optional&) except +
        bint operator==(optional&, optional&)
        bint operator!=(optional&, optional&)
        bint operator<(optional&, optional&)
        bint operator>(optional&, optional&)
        bint operator<=(optional&, optional&)
        bint operator>=(optional&, optional&)
        bint has_value() const
        T& value()
        T& operator*()
        void swap(optional&)
        void reset()

cdef extern from "rxs_parsing_core/ModularPicoScenesFrame.hxx":
    # ModularPicoScenesFrame.hxx
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

    # ModularPicoScenesFrame.hxx
    cdef packed struct ieee80211_mac_frame_header:
        ieee80211_mac_frame_header_frame_control_field fc
        # uint16_t dur
        uint8_t addr1[6]
        uint8_t addr2[6]
        uint8_t addr3[6]
        uint16_t frag
        uint16_t seq


    # RxSBasicSegment.hxx
    cdef packed struct RxSBasic:
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
        # uint8_t numUser
        # uint8_t userIndex
        int8_t noiseFloor
        int8_t rssi
        int8_t rssi_ctl0
        int8_t rssi_ctl1
        int8_t rssi_ctl2

    # RxSBasicSegment.hxx
    cdef cppclass RxSBasicSegment:
        const RxSBasic &getBasic() const


    # RXSExtraInfo.hxx
    cdef enum AtherosCFTuningPolicy:    # uint8_t
        CFTuningByChansel
        CFTuningByFastCC
        CFTuningByHardwareReset
        CFTuningByDefault

    # RXSExtraInfo.hxx
    cdef struct ExtraInfo:
        # uint32_t featureCode
        bint hasLength
        bint hasVersion
        bint hasMacAddr_cur
        bint hasMacAddr_rom
        bint hasChansel
        bint hasBMode
        bint hasEVM
        bint hasTxChainMask
        bint hasRxChainMask
        bint hasTxpower
        bint hasCF
        bint hasTxTSF
        bint hasLastHWTxTSF
        bint hasChannelFlags
        bint hasTxNess
        bint hasTuningPolicy
        bint hasPLLRate
        bint hasPLLRefDiv
        bint hasPLLClkSel
        bint hasAGC
        bint hasAntennaSelection
        bint hasSamplingRate
        bint hasCFO
        bint hasSFO
        # bint hasPreciseTxTiming
        uint16_t length
        uint64_t version
        uint8_t macaddr_rom[6]
        uint8_t macaddr_cur[6]
        uint32_t chansel
        uint8_t bmode
        int8_t evm[20]
        uint8_t txChainMask
        uint8_t rxChainMask
        uint8_t txpower
        uint64_t cf
        uint32_t txTSF
        uint32_t lastHwTxTSF
        uint16_t channelFlags
        uint8_t tx_ness
        AtherosCFTuningPolicy tuningPolicy
        uint16_t pll_rate
        uint8_t pll_refdiv
        uint8_t pll_clock_select
        uint8_t agc
        uint8_t ant_sel[3]
        uint64_t samplingRate
        int32_t cfo
        int32_t sfo
        # double preciseTxTiming

    # ExtraInfoSegment.hxx
    cdef cppclass ExtraInfoSegment:
        const ExtraInfo &getExtraInfo() const


    # PicoScenesCommons.hxx
    cdef enum PicoScenesDeviceType:     # uint16_t
        QCA9300
        IWL5300
        IWLMVM
        MAC80211Compatible
        USRP
        VirtualSDR
        Unknown

    # PicoScenesCommons.hxx
    cdef enum PacketFormatEnum:         # int8_t
        PacketFormat_NonHT
        PacketFormat_HT
        PacketFormat_VHT
        PacketFormat_HESU
        PacketFormat_HEMU
        PacketFormat_Unknown

    # PicoScenesCommons.hxx
    cdef enum ChannelBandwidthEnum:     # uint16_t
        CBW_5
        CBW_10
        CBW_20
        CBW_40
        CBW_80
        CBW_160

    # CSISegment.hxx
    cdef cppclass CSIDimension:
        uint16_t numTones
        uint8_t numTx
        uint8_t numRx
        uint8_t numESS
        uint16_t numCSI

    # SignalMatrix.hxx
    cdef cppclass SignalMatrix[T]:
        vector[T] array
        vector[int64_t] dimensions

    # CSISegment.hxx
    cdef cppclass CSI:
        PicoScenesDeviceType deviceType
        PacketFormatEnum packetFormat
        ChannelBandwidthEnum cbw
        uint64_t carrierFreq
        uint64_t samplingRate
        uint32_t subcarrierBandwidth
        CSIDimension dimensions
        uint8_t antSel
        # int16_t subcarrierOffset
        vector[int16_t] subcarrierIndices
        SignalMatrix[ccomplex[double]] CSIArray
        SignalMatrix[double] magnitudeArray
        SignalMatrix[double] phaseArray

    # CSISegment.hxx
    cdef cppclass CSISegment:
        const CSI &getCSI() const


    # MVMExtraSegment.hxx
    cdef cppclass IntelMVMParsedCSIHeader:
        uint32_t ftmClock
        uint32_t muClock
        uint32_t rate_n_flags

    # MVMExtraSegment.hxx
    cdef cppclass IntelMVMExtrta:
        IntelMVMParsedCSIHeader parsedHeader

    # MVMExtraSegment.hxx
    cdef cppclass MVMExtraSegment:
        const IntelMVMExtrta &getMvmExtra() const


    # ModularPicoScenesFrame.hxx
    cdef packed struct PicoScenesFrameHeader:
        uint32_t magicValue
        uint32_t version
        PicoScenesDeviceType deviceType
        # uint8_t numSegments
        uint8_t frameType
        uint16_t taskId
        uint16_t txId


    # BasebandSignalSegment.hxx
    cdef cppclass BasebandSignalSegment:
        const SignalMatrix[ccomplex[double]] &getSignalMatrix() const


    # PreEQSymbolsSegment.hxx
    cdef cppclass PreEQSymbolsSegment:
        const SignalMatrix[ccomplex[double]] &getPreEqSymbols() const


    # ModularPicoScenesFrame.hxx
    cdef cppclass ModularPicoScenesRxFrame:
        ieee80211_mac_frame_header standardHeader
        RxSBasicSegment rxSBasicSegment
        ExtraInfoSegment rxExtraInfoSegment
        CSISegment csiSegment
        optional[MVMExtraSegment] mvmExtraSegment
        optional[PicoScenesFrameHeader] PicoScenesHeader
        optional[ExtraInfoSegment] txExtraInfoSegment
        optional[CSISegment] pilotCSISegment
        optional[CSISegment] legacyCSISegment
        optional[BasebandSignalSegment] basebandSignalSegment
        optional[PreEQSymbolsSegment] preEQSymbolsSegment
        vector[uint8_t] mpdu

        @staticmethod
        optional[ModularPicoScenesRxFrame] fromBuffer(const uint8_t *buffer, uint32_t bufferLength, bint interpolateCSI)
        string toString() const


cdef class Picoscenes:
    cdef readonly str file
    cdef readonly int count
    cdef public list raw
    cdef bint if_report

    def __cinit__(self, file, if_report=True, *argv, **kw):
        self.file = file
        self.if_report = if_report
        self.raw = list()

    def __init__(self, file, if_report=True):
        pass

    cpdef read(self):
        self.seek(self.file, 0, 0)

    cpdef seek(self, file, long pos, long num):
        cdef FILE *f

        tempfile = file.encode(encoding="utf-8")
        cdef char *datafile = tempfile

        f = fopen(datafile, "rb")
        if f is NULL:
            printf("Open failed!\n")
            exit(-1)
        
        fseek(f, 0, SEEK_END)
        cdef long lens = ftell(f)
        fseek(f, pos, SEEK_SET)

        cdef int count = 0
        cdef int l, i
        cdef uint32_t field_len
        cdef uint32_t buf_size = 1024
        cdef unsigned char *buf
        cdef optional[ModularPicoScenesRxFrame] frame

        if num == 0:
            num = lens
        if self.raw:
            self.raw.clear()

        buf = <unsigned char *>malloc(buf_size * sizeof(unsigned char)) # CHECK NULL
        while pos < (lens-4):
            l = <int>fread(buf, sizeof(unsigned char), 4, f)
            if l < 4:
                break
            field_len = cu32l(buf[0], buf[1], buf[2], buf[3]) + 4
            fseek(f, -4, SEEK_CUR)
            if buf_size < field_len:
                buf = <unsigned char *>realloc(buf, field_len)    # CHECK NULL
                buf_size = field_len
            l = <int>fread(buf, sizeof(unsigned char), field_len, f)

            # rxs_parsing_core
            frame = ModularPicoScenesRxFrame.fromBuffer(buf, field_len, True)
            self.raw.append(parse(&frame))

            pos += field_len
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
        frame = ModularPicoScenesRxFrame.fromBuffer(data, len(data), True)
        if self.raw:
            self.raw.pop(0)
        self.raw.append(parse(&frame))
        if self.if_report and self.raw[0]:
            print(frame.value().toString())
        self.count = 1
        return 0xf300       # status code


cdef inline uint32_t cu32l(uint8_t a, uint8_t b, uint8_t c, uint8_t d):
    return a | (b << 8) | (c << 16) | (d << 24)


cdef parse_ieee80211_mac_frame_header(const ieee80211_mac_frame_header *m):
    cdef int i
    return {
        "ControlField": {
            'Version': m.fc.version,
            'Type': m.fc.type,
            'SubType': m.fc.subtype,
            'ToDS': m.fc.toDS,
            'FromDS': m.fc.fromDS,
            'MoreFrags': m.fc.moreFrags,
            'Retry': m.fc.retry,
            'PowerManagement': m.fc.power_mgmt,
            'More': m.fc.more,
            'Protected': m.fc.protect,
            'Order': m.fc.order,
        },
        "Addr1": [m.addr1[i] for i in range(6)],
        "Addr2": [m.addr2[i] for i in range(6)],
        "Addr3": [m.addr3[i] for i in range(6)],
        "Fragment": m.frag,
        "Sequence": m.seq,
    }


cdef parse_RxSBasic(const RxSBasic *m):
    return {
        "deviceType": m.deviceType,
        "timestamp": m.tstamp,
        "centerFreq": m.centerFreq,
        "controlFreq": m.controlFreq,
        "CBW": m.cbw,
        "packetFormat": m.packetFormat,
        "packetCBW": m.pkt_cbw,
        "GI": m.guardInterval,
        "MCS": m.mcs,
        "numSTS": m.numSTS,
        "numESS": m.numESS,
        "numRx": m.numRx,
        "noiseFloor": m.noiseFloor,
        "rssi": m.rssi,
        "rssi1": m.rssi_ctl0,
        "rssi2": m.rssi_ctl1,
        "rssi3": m.rssi_ctl2,
    }


cdef parse_ExtraInfo(const ExtraInfo *m):
    cdef int i
    result = {
        "hasLength": m.hasLength,
        "hasVersion": m.hasVersion,
        "hasMacAddr_cur": m.hasMacAddr_cur,
        "hasMacAddr_rom": m.hasMacAddr_rom,
        "hasChansel": m.hasChansel,
        "hasBMode": m.hasBMode,
        "hasEVM": m.hasEVM,
        "hasTxChainMask": m.hasTxChainMask,
        "hasRxChainMask": m.hasRxChainMask,
        "hasTxpower": m.hasTxpower,
        "hasCF": m.hasCF,
        "hasTxTSF": m.hasTxTSF,
        "hasLastHwTxTSF": m.hasLastHWTxTSF,
        "hasChannelFlags": m.hasChannelFlags,
        "hasTxNess": m.hasTxNess,
        "hasTuningPolicy": m.hasTuningPolicy,
        "hasPLLRate": m.hasPLLRate,
        "hasPLLClkSel": m.hasPLLClkSel,
        "hasPLLRefDiv": m.hasPLLRefDiv,
        "hasAGC": m.hasAGC,
        "hasAntennaSelection": m.hasAntennaSelection,
        "hasSamplingRate": m.hasSamplingRate,
        "hasCFO": m.hasCFO,
        "hasSFO": m.hasSFO,
    }
    if m.hasLength:
        result["length"] = m.length
    if m.hasVersion:
        result["version"] = m.version
    if m.hasMacAddr_cur:
        result["macaddr_cur"] = [m.macaddr_cur[i] for i in range(6)]
    if m.hasMacAddr_rom:
        result["macaddr_rom"] = [m.macaddr_rom[i] for i in range(6)]
    if m.hasChansel:
        result["chansel"] = m.chansel
    if m.hasBMode:
        result["bmode"] = m.bmode
    if m.hasEVM:
        result["evm"] = [m.evm[i] for i in range(18)]
    if m.hasTxChainMask:
        result["tx_chainmask"] = m.txChainMask
    if m.hasRxChainMask:
        result["rx_chainmask"] = m.rxChainMask
    if m.hasTxpower:
        result["txpower"] = m.txpower
    if m.hasCF:
        result["cf"] = m.cf
    if m.hasTxTSF:
        result["txtsf"] = m.txTSF
    if m.hasLastHWTxTSF:
        result["last_txtsf"] = m.lastHwTxTSF
    if m.hasChannelFlags:
        result["channel_flags"] = m.channelFlags
    if m.hasTxNess:
        result["tx_ness"] = m.tx_ness
    if m.hasTuningPolicy:
        result["tuning_policy"] = m.tuningPolicy
    if m.hasPLLRate:
        result["pll_rate"] = m.pll_rate
    if m.hasPLLClkSel:
        result["pll_clock_select"] = m.pll_clock_select
    if m.hasPLLRefDiv:
        result["pll_refdiv"] = m.pll_refdiv
    if m.hasAGC:
        result["agc"] = m.agc
    if m.hasAntennaSelection:
        result["ant_sel"] = [m.ant_sel[i] for i in range(3)]
    if m.hasSamplingRate:
        result["sf"] = m.samplingRate
    if m.hasCFO:
        result["cfo"] = m.cfo
    if m.hasSFO:
        result["sfo"] = m.sfo
    return result


cdef parse_CSI(const CSI *m):
    return {
        "DeviceType": <uint16_t>m.deviceType,
        "PacketFormat": <int8_t>m.packetFormat,
        "CBW": <uint16_t>m.cbw,
        "CarrierFreq": m.carrierFreq,
        "SamplingRate": m.samplingRate,
        "SubcarrierBandwidth": m.subcarrierBandwidth,
        "numTones": m.dimensions.numTones,
        "numTx": m.dimensions.numTx,
        "numRx": m.dimensions.numRx,
        "numESS": m.dimensions.numESS,
        "numCSI": m.dimensions.numCSI,
        "ant_sel": m.dimensions.numESS,
        "CSI": m.CSIArray.array,
        "Mag": m.magnitudeArray.array,
        "Phase":m.phaseArray.array,
        "SubcarrierIndex": m.subcarrierIndices,
    }


cdef parse_IntelMVMParsedCSIHeader(const IntelMVMParsedCSIHeader *m):
    return {
        "FMTClock": m.ftmClock,
        "usClock": m.muClock,
        "RateNFlags": m.rate_n_flags,
    }


cdef parse_PicoScenesFrameHeader(const PicoScenesFrameHeader *m):
    return {
        "MagicValue": m.magicValue,
        "Version": m.version,
        "DeviceType": <uint16_t>m.deviceType,
        "FrameType": m.frameType,
        "TaskId": m.taskId,
        "TxId": m.txId,
    }


cdef parse_SignalMatrix(const SignalMatrix[ccomplex[double]] *m):
    return np.asarray(m.array).reshape(m.dimensions)


cdef parse(optional[ModularPicoScenesRxFrame] *frame):
    data = {}
    cdef ModularPicoScenesRxFrame frame_value
    if frame.has_value():
        frame_value = frame.value()
        data = {
            "StandardHeader": parse_ieee80211_mac_frame_header(&frame_value.standardHeader),
            "RxSBasic": parse_RxSBasic(&frame_value.rxSBasicSegment.getBasic()),
            "RxExtraInfo": parse_ExtraInfo(&frame_value.rxExtraInfoSegment.getExtraInfo()),
            "CSI": parse_CSI(&frame_value.csiSegment.getCSI()),
        }
        if frame_value.mvmExtraSegment.has_value():
            data["MVMExtra"] = parse_IntelMVMParsedCSIHeader(&frame_value.mvmExtraSegment.value().getMvmExtra().parsedHeader)
        if frame_value.PicoScenesHeader.has_value():
            data["PicoScenesHeader"] = parse_PicoScenesFrameHeader(&frame_value.PicoScenesHeader.value())
        if frame_value.txExtraInfoSegment.has_value():
            data["TxExtraInfo"] = parse_ExtraInfo(&frame_value.txExtraInfoSegment.value().getExtraInfo())
        if frame_value.pilotCSISegment.has_value():
            data["PilotCSI"] = parse_CSI(&frame_value.pilotCSISegment.value().getCSI())
        if frame_value.legacyCSISegment.has_value():
            data["LegacyCSI"]  = parse_CSI(&frame_value.legacyCSISegment.value().getCSI())
        if frame_value.basebandSignalSegment.has_value():
            data["BasebandSignals"] = parse_SignalMatrix(&frame_value.basebandSignalSegment.value().getSignalMatrix())
        if frame_value.preEQSymbolsSegment.has_value():
            data["PreEQSymbols"] = parse_SignalMatrix(&frame_value.preEQSymbolsSegment.value().getPreEqSymbols())
        data["MPDU"] = frame_value.mpdu
    return data
