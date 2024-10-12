from libc.stdio cimport (fopen, fread, fclose, fseek, ftell, printf, FILE,
                         SEEK_END, SEEK_SET, SEEK_CUR)
from libc.stdint cimport (uint8_t, uint16_t, uint32_t, uint64_t,
                          int8_t, int16_t, int32_t, int64_t)
from libc.stdlib cimport malloc, realloc, free, exit
from libc.stddef cimport size_t
from libc.string cimport strncmp
from libc.math cimport abs, atan2, pi, cos, sin
import numpy as np
cimport numpy as np
cimport cython


# Functions for parsing


cdef FILE* crfopen(str file):
    tempfile = file.encode(encoding="utf-8")
    cdef char *datafile = tempfile
    cdef FILE *f = fopen(datafile, "rb")
    if f is NULL:
        printf("Open failed!\n")
        exit(-1)
    return f


cdef unsigned char *crfread(unsigned char *buf, uint32_t *buf_size,
                            FILE *f, uint32_t *field_len):
    cdef size_t l
    l = fread(buf, sizeof(unsigned char), 4, f)
    field_len[0] = cu32(buf) + 4
    fseek(f, -4, SEEK_CUR)
    if buf_size[0] < field_len[0]:
        buf = <unsigned char *>realloc(buf, field_len[0])
        buf_size[0] = field_len[0]
        if buf is NULL:
            printf("realloc failed\n")
            fclose(f)
            exit(-1)
    return buf


cdef long getfilesize(FILE *f, long pos):
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


cdef void parse_AbstractPicoScenesFrameSegment(unsigned char *buf, 
    AbstractPicoScenesFrameSegment *m):
    m.segmentLength = cu32(buf)
    m.segNameLength = cu8(buf + 4)
    m.segmentName = buf + 5
    m.versionId = cu16(buf + 5 + m.segNameLength)


cdef int16_t* get_scidx_pilot(int8_t format, uint16_t cbw):
    global pilot_scidx
    if format == PacketFormatEnum.PacketFormat_HESU:
        if cbw == ChannelBandwidthEnum.CBW_20:
            return pilot_scidx.HE20_242
        elif cbw == ChannelBandwidthEnum.CBW_40:
            return pilot_scidx.HE40_484
        elif cbw == ChannelBandwidthEnum.CBW_80:
            return pilot_scidx.HE80_996
        elif cbw == ChannelBandwidthEnum.CBW_160:
            return pilot_scidx.HE160_1992
        else:
            pass
    elif format == PacketFormatEnum.PacketFormat_VHT:
        if cbw == ChannelBandwidthEnum.CBW_20:
            return pilot_scidx.HTVHT20_56
        elif cbw == ChannelBandwidthEnum.CBW_40:
            return pilot_scidx.HTVHT40_114
        elif cbw == ChannelBandwidthEnum.CBW_80:
            return pilot_scidx.VHT80_242
        elif cbw == ChannelBandwidthEnum.CBW_160:
            return pilot_scidx.VHT160_484
        else:
            pass
    elif format == PacketFormatEnum.PacketFormat_HT:
        if cbw == ChannelBandwidthEnum.CBW_20:
            return pilot_scidx.HTVHT20_56
        elif cbw == ChannelBandwidthEnum.CBW_40:
            return pilot_scidx.HTVHT40_114
        else:
            pass
    elif format == PacketFormatEnum.PacketFormat_NonHT:
        if cbw == ChannelBandwidthEnum.CBW_20:
            return pilot_scidx.NonHT20_52
    else:
        pass
    return NULL


cdef bint set_scidx_all(np.int32_t[:] scidx, int count, int offset,
                  int a, int b, int c, int d, int16_t *pilot_scidx,
                  bint skip_pilot):
    cdef int i
    cdef int j = 0
    cdef int k = 0
    if scidx.shape[0] < count:
        return False

    for i in range(-a, -b):
        if skip_pilot and j == pilot_scidx[k]:
            k += 1
            continue
        scidx[j] = i + offset
        j += 1
    for i in range(-c, -d):
        if skip_pilot and j == pilot_scidx[k]:
            k += 1
            continue
        scidx[j] = i + offset
        j += 1
    for i in range(c + 1, d + 1):
        if skip_pilot and j == pilot_scidx[k]:
            k += 1
            continue
        scidx[j] = i + offset
        j += 1
    for i in range(b + 1, a + 1):
        if skip_pilot and j == pilot_scidx[k]:
            k += 1
            continue
        scidx[j] = i + offset
        j += 1
    for i in range(count, scidx.shape[0]):
        scidx[j] = a + offset
        j += 1
    return True


cdef bint get_scidx_all(np.int32_t[:] scidx, int8_t format,
                        uint16_t cbw, int offset, bint skip_pilot=False):
    global pilot_scidx
    if format == PacketFormatEnum.PacketFormat_HESU:
        if cbw == ChannelBandwidthEnum.CBW_20:
            return set_scidx_all(scidx, 242, offset, 122, 1, 0, 0,
                                 pilot_scidx.HE20_242, skip_pilot)
        elif cbw == ChannelBandwidthEnum.CBW_40:
            return set_scidx_all(scidx, 484, offset, 244, 2, 0, 0,
                                 pilot_scidx.HE40_484, skip_pilot)
        elif cbw == ChannelBandwidthEnum.CBW_80:
            return set_scidx_all(scidx, 996, offset, 500, 2, 0, 0,
                                 pilot_scidx.HE80_996, skip_pilot)
        elif cbw == ChannelBandwidthEnum.CBW_160:
            return set_scidx_all(scidx, 1992, offset, 1012, 514, 509, 11,
                                 pilot_scidx.HE160_1992, skip_pilot)
        else:
            pass
    elif format == PacketFormatEnum.PacketFormat_VHT:
        if cbw == ChannelBandwidthEnum.CBW_20:
            return set_scidx_all(scidx, 56, offset, 28, 0, 0, 0,
                                 pilot_scidx.HTVHT20_56, skip_pilot)
        elif cbw == ChannelBandwidthEnum.CBW_40:
            return set_scidx_all(scidx, 114, offset, 58, 1, 0, 0,
                                 pilot_scidx.HTVHT40_114, skip_pilot)
        elif cbw == ChannelBandwidthEnum.CBW_80:
            return set_scidx_all(scidx, 242, offset, 122, 1, 0, 0,
                                 pilot_scidx.VHT80_242, skip_pilot)
        elif cbw == ChannelBandwidthEnum.CBW_160:
            return set_scidx_all(scidx, 484, offset, 250, 129, 126, 5,
                                 pilot_scidx.VHT160_484, skip_pilot)
        else:
            pass
    elif format == PacketFormatEnum.PacketFormat_HT:
        if cbw == ChannelBandwidthEnum.CBW_20:
            return set_scidx_all(scidx, 56, offset, 28, 0, 0, 0,
                                 pilot_scidx.HTVHT20_56, skip_pilot)
        elif cbw == ChannelBandwidthEnum.CBW_40:
            return set_scidx_all(scidx, 114, offset, 58, 1, 0, 0,
                                 pilot_scidx.HTVHT40_114, skip_pilot)
        else:
            pass
    elif format == PacketFormatEnum.PacketFormat_NonHT:
        if cbw == ChannelBandwidthEnum.CBW_20:
            return set_scidx_all(scidx, 52, offset, 26, 0, 0, 0,
                                 pilot_scidx.NonHT20_52, skip_pilot)
    else:
        pass
    return True


cdef bint get_scidx_5300(np.int32_t[:] scidx, int count, int offset,
                         int a, int b, int step):
    cdef int i, j
    if scidx.shape[0] < count:
        return False

    j = -a + offset
    for i in range(14):
        scidx[i] = j
        j += step
    scidx[14] = -b

    j = b + offset
    for i in range(15, 29):
        scidx[i] = j
        j += step
    scidx[29] = a
    for i in range(count, scidx.shape[0]):
        scidx[i] = a + offset
    return True


cdef bint parseCSI9300scidx(np.int32_t[:] scidx, int8_t format,
                            uint16_t cbw, int offset):
    return get_scidx_all(scidx, format, cbw, offset, False)


cdef bint parseCSI5300scidx(np.int32_t[:] scidx, int8_t format,
                            uint16_t cbw, int offset):
    if cbw == ChannelBandwidthEnum.CBW_20:
        return get_scidx_5300(scidx, 30, offset, 28, 1, 2)
    elif cbw == ChannelBandwidthEnum.CBW_40:
        return get_scidx_5300(scidx, 30, offset, 58, 2, 4)
    else:
        pass
    return True


cdef bint parseCSIMVMscidx(np.int32_t[:] scidx, int8_t format,
                          uint16_t cbw, int offset, bint skipPilotSubcarriers):
    return get_scidx_all(scidx, format, cbw, offset, skipPilotSubcarriers)


cdef bint parseCSIUSRPscidx(np.int32_t[:] scidx, unsigned char *payload,
                            int16_t numTones):
    cdef int i
    if scidx.shape[0] < numTones:
        return False

    for i in range(numTones):
        scidx[i] = c16(payload + i * 2)
    for i in range(numTones, scidx.shape[0]):
        scidx[i] = c16(payload + (numTones - 1) * 2)
    return True


cdef bint parseCSI9300(np.complex128_t[:, :, :] csi, unsigned char *payload,
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
        txIndex = <int>(valuePos / numRx) % numTx
        toneIndex = <int>(valuePos / (numRx * numTx))
        csi[toneIndex, rxIndex, txIndex].real = tempArray[1]
        csi[toneIndex, rxIndex, txIndex].imag = tempArray[0]

        valuePos += 1
        rxIndex = valuePos % numRx
        txIndex = <int>(valuePos / numRx) % numTx
        toneIndex = <int>(valuePos / (numRx * numTx))
        csi[toneIndex, rxIndex, txIndex].real = tempArray[3]
        csi[toneIndex, rxIndex, txIndex].imag = tempArray[2]
    return True


cdef bint parseCSI5300(np.complex128_t[:, :, :] csi, unsigned char *payload,
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
    cdef uint8_t a, b

    if numTones > csi.shape[0] or numRx > csi.shape[1] or numTx > csi.shape[2]:
        return False

    for i in range(numTones):
        index += 3
        remainder = <uint8_t>(index % 8)
        for j in range(numRx):
            for k in range(numTx):
                index_step =  index >> 3
                a = payload[index_step + 0] >> remainder
                b = payload[index_step + 1] >> remainder
                a |= payload[index_step + 1] << (8 - remainder)
                b |= payload[index_step + 2] << (8 - remainder)
                csi[i, j, k].real = <double><int8_t>(a & 0xff)
                csi[i, j, k].imag = <double><int8_t>(b & 0xff)
                index += 16
    return True

cdef bint parseCSIMVM(np.complex128_t[:, :, :] csi, unsigned char *payload,
                      uint16_t numTones, uint8_t numTx, uint8_t numRx,
                      int8_t format, uint16_t cbw, uint8_t fwversion,
                      bint skip_pilot):
    """Important: this function may be incorrect"""
    cdef int16_t *p = get_scidx_pilot(format, cbw)
    cdef int i, j, k, g
    cdef int offset = 0
    cdef int p_idx = 0
    for k in range(numTx):
        for j in range(numRx):
            g = 0
            for i in range(numTones):
                if fwversion == 67 or fwversion == 68:
                    if format == PacketFormatEnum.PacketFormat_HESU and \
                        cbw == ChannelBandwidthEnum.CBW_160:
                        if i > 995 and i < 1024:
                            offset += 4
                            continue
                    if format == PacketFormatEnum.PacketFormat_VHT and \
                        cbw == ChannelBandwidthEnum.CBW_160:
                        if i > 241 and i < 256:
                            offset += 4
                            continue
                if skip_pilot and g == p[p_idx]:
                    p_idx += 1
                    offset += 4
                    continue
                csi[g, j, k].real = c16(payload + offset + 0)
                csi[g, j, k].imag = c16(payload + offset + 2)
                offset += 4
                g += 1
    return True


cdef bint parseCSIUSRP(np.complex128_t[:, :, :] csi, unsigned char *payload,
                       uint32_t csiBufferLength):
    """parseSignalMatrix = parseCSIUSRP"""
    cdef uint32_t i, j, k
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
            shape[i] = <uint16_t>cu64(payload+offset)
            offset += 8

    if shape[0] > csi.shape[0] or shape[1] > csi.shape[1] \
        or shape[2] > csi.shape[2]:
        return False

    offset += 4
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                csi[i, j, k].real = cd64(payload + offset + 0)
                csi[i, j, k].imag = cd64(payload + offset + 8)
                offset += 16
    return True


cdef bint parse_SignalMatrixV1(unsigned char *buf, dtc_SignalMatrix_Info *m,
                               np.complex128_t[:, :, :] data):
    """parseSignalMatrix = parseCSIUSRP"""
    cdef uint32_t i, j, k
    cdef uint32_t offset = 0
    cdef uint8_t matrixVersion = cu8(buf+3) - 48
    m.ndim = cu8(buf+4)
    offset += 5

    for i in range(3):
        m.shape[i] = 1
    for i in range(m.ndim):
        if matrixVersion == 1:
            m.shape[i] = <uint16_t>cu32(buf+offset)
            offset += 4
        if matrixVersion == 2:
            m.shape[i] = <uint16_t>cu64(buf+offset)
            offset += 8

    cdef char complexChar = <char>cu8(buf+offset+0)
    cdef char typeChar = <char>cu8(buf+offset+1)
    m.itemsize = cu8(buf+offset+2)
    m.majority = <char>cu8(buf+offset+3)
    offset += 4

    if m.shape[0] > data.shape[0] or m.shape[1] > data.shape[1] \
        or m.shape[2] > data.shape[2]:
        return False

    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            for k in range(m.shape[2]):
                data[i, j, k].real = cd64(buf + offset + 0)
                data[i, j, k].imag = cd64(buf + offset + 8)
                offset += 16
    return True


cdef void parse_RxSBasicV1(unsigned char *buf, dtc_RXBasic *m):
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


cdef void parse_RxSBasicV2(unsigned char *buf, dtc_RXBasic *m):
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


cdef void parse_RxSBasicV3(unsigned char *buf, dtc_RXBasic *m):
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


cdef void parse_ExtraInfoV1(unsigned char *buf, dtc_ExtraInfo *m):
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
    m.hasTemperature = featurecode.hasTemperature 

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
    if featurecode.hasTemperature:
        m.temperature = (buf + offset)[0]
        offset += 1


cdef void parse_MVMExtraV1(unsigned char *buf, dtc_IntelMVMExtrta *m):
    cdef IntelMVMExtrta *imvme = <IntelMVMExtrta*>buf
    m.FMTClock = imvme.parsedHeader.ftmClock
    m.usClock = imvme.parsedHeader.muClock
    m.RateNFlags = imvme.parsedHeader.rate_n_flags


cdef void parse_DPASRequestV1(unsigned char *buf, dtc_DPASRequest *m):
    cdef DPASRequestV1 *dpasr = <DPASRequestV1*>buf
    m.batchId = dpasr.batchId
    m.batchLength = dpasr.batchLength
    m.sequenceId = dpasr.sequenceId
    m.intervalTime = dpasr.intervalTime


cdef void parse_DPASRequestV2(unsigned char *buf, dtc_DPASRequest *m):
    cdef DPASRequestV2 *dpasr = <DPASRequestV2*>buf
    m.batchId = dpasr.batchId
    m.batchLength = dpasr.batchLength
    m.sequenceId = dpasr.sequenceId
    m.intervalTime = dpasr.intervalTime
    m.intervalStep = dpasr.intervalStep


cdef void parse_DPASRequestV3(unsigned char *buf, dtc_DPASRequest *m):
    cdef DPASRequestV3 *dpasr = <DPASRequestV3*>buf
    m.batchId = dpasr.batchId
    m.batchLength = dpasr.batchLength
    m.sequenceId = dpasr.sequenceId
    m.intervalTime = dpasr.intervalTime
    m.intervalStep = dpasr.intervalStep
    m.deviceType = dpasr.deviceType
    m.carrierFrequency = dpasr.carrierFrequency
    m.samplingFrequency = dpasr.samplingFrequency

cdef void parse_DPASRequestV4(unsigned char *buf, dtc_DPASRequest *m):
    cdef DPASRequestV4 *dpasr = <DPASRequestV4*>buf
    m.requestMode = dpasr.requestMode
    m.batchId = dpasr.batchId
    m.batchLength = dpasr.batchLength
    m.sequenceId = dpasr.sequenceId
    m.intervalTime = dpasr.intervalTime
    m.intervalStep = dpasr.intervalStep
    m.deviceType = dpasr.deviceType
    m.deviceSubtype = dpasr.deviceSubtype
    m.carrierFrequency = dpasr.carrierFrequency
    m.samplingFrequency = dpasr.samplingFrequency


cdef void parse_CSIV1(unsigned char *buf, dtc_CSI_Info *m,
                      np.complex128_t[:, :, :] csi,
                      np.int32_t[:] scidx):
    cdef CSIV1 *csiv1 = <CSIV1*>buf
    cdef int actualNumSTSPerChain
    cdef int temp

    m.DeviceType = csiv1.deviceType
    m.PacketFormat = csiv1.packetFormat
    m.CBW = csiv1.cbw
    m.CarrierFreq = csiv1.carrierFreq
    m.SamplingRate = csiv1.samplingRate
    m.SubcarrierBandwidth = csiv1.subcarrierBandwidth
    m.numTones = csiv1.numTones
    m.numTx = csiv1.numTx
    m.numRx = csiv1.numRx
    if csiv1.deviceType == PicoScenesDeviceType.QCA9300:
        m.firmwareVersion = 0
        temp = 140 if csiv1.cbw == ChannelBandwidthEnum.CBW_20 else 285
        actualNumSTSPerChain = <int>(csiv1.csiBufferLength / temp)
        actualNumSTSPerChain = <int>(actualNumSTSPerChain / csiv1.numRx)
        m.numESS = actualNumSTSPerChain - csiv1.numTx
        m.numCSI = 1
        m.ant_sel = csiv1.antSel
        parseCSI9300scidx(scidx, csiv1.packetFormat, csiv1.cbw, 0)
        parseCSI9300(csi, csiv1.payload, csiv1.numTones,
                     actualNumSTSPerChain, csiv1.numRx)
    elif csiv1.deviceType == PicoScenesDeviceType.IWL5300:
        m.firmwareVersion = 52
        actualNumSTSPerChain = <int>((csiv1.csiBufferLength - 12) / 60)
        actualNumSTSPerChain = <int>(actualNumSTSPerChain / csiv1.numRx)
        m.numESS = actualNumSTSPerChain - csiv1.numTx
        m.numCSI = 1
        m.ant_sel = csiv1.antSel
        parseCSI5300scidx(scidx, csiv1.packetFormat, csiv1.cbw, 0)
        parseCSI5300(csi, csiv1.payload, csiv1.numTones,
                     actualNumSTSPerChain, csiv1.numRx, csiv1.antSel)
    elif csiv1.deviceType == PicoScenesDeviceType.USRP:
        m.firmwareVersion = 0
        m.numESS = csiv1.numESS
        m.numCSI = 1
        m.ant_sel = csiv1.antSel
        parseCSIUSRPscidx(scidx, csiv1.payload, csiv1.numTones)
        parseCSIUSRP(csi, csiv1.payload + csiv1.numTones * 2,
                     csiv1.csiBufferLength - csiv1.numTones * 2)


cdef void parse_CSIV2(unsigned char *buf, dtc_CSI_Info *m,
                      np.complex128_t[:, :, :] csi,
                      np.int32_t[:] scidx):    
    cdef CSIV2 *csiv2 = <CSIV2*>buf
    cdef int actualNumSTSPerChain
    cdef int temp

    m.DeviceType = csiv2.deviceType
    m.PacketFormat = csiv2.packetFormat
    m.CBW = csiv2.cbw
    m.CarrierFreq = csiv2.carrierFreq
    m.SamplingRate = csiv2.samplingRate
    m.SubcarrierBandwidth = csiv2.subcarrierBandwidth
    m.numTones = csiv2.numTones
    m.numTx = csiv2.numTx
    m.numRx = csiv2.numRx
    if csiv2.deviceType == PicoScenesDeviceType.QCA9300:
        m.firmwareVersion = 0
        temp = 140 if csiv2.cbw == ChannelBandwidthEnum.CBW_20 else 285
        actualNumSTSPerChain = <int>(csiv2.csiBufferLength / temp)
        actualNumSTSPerChain = <int>(actualNumSTSPerChain / csiv2.numRx)
        m.numESS = actualNumSTSPerChain - csiv2.numTx
        m.numCSI = 1
        m.ant_sel = csiv2.antSel
        parseCSI9300scidx(scidx, csiv2.packetFormat,
                          csiv2.cbw, csiv2.subcarrierOffset)
        parseCSI9300(csi, csiv2.payload, csiv2.numTones,
                     actualNumSTSPerChain, csiv2.numRx)
    elif csiv2.deviceType == PicoScenesDeviceType.IWL5300:
        m.firmwareVersion = 52
        actualNumSTSPerChain = <int>((csiv2.csiBufferLength - 12) / 60)
        actualNumSTSPerChain = <int>(actualNumSTSPerChain / csiv2.numRx)
        m.numESS = actualNumSTSPerChain - csiv2.numTx
        m.numCSI = 1
        m.ant_sel = csiv2.antSel
        parseCSI5300scidx(scidx, csiv2.packetFormat,
                          csiv2.cbw, csiv2.subcarrierOffset)
        parseCSI5300(csi, csiv2.payload, csiv2.numTones,
                     actualNumSTSPerChain, csiv2.numRx, csiv2.antSel)
    elif csiv2.deviceType == PicoScenesDeviceType.USRP:
        m.firmwareVersion = 0
        m.numESS = csiv2.numESS
        m.numCSI = 1
        m.ant_sel = csiv2.antSel
        parseCSIUSRPscidx(scidx, csiv2.payload, csiv2.numTones)
        parseCSIUSRP(csi, csiv2.payload + csiv2.numTones * 2,
                     csiv2.csiBufferLength - csiv2.numTones * 2)


cdef void parse_CSIV3(unsigned char *buf, dtc_CSI_Info *m,
                      np.complex128_t[:, :, :] csi,
                      np.int32_t[:] scidx):
    cdef CSIV3 *csiv3 = <CSIV3*>buf
    cdef int actualNumSTSPerChain
    cdef int temp

    m.DeviceType = csiv3.deviceType
    m.PacketFormat = csiv3.packetFormat
    m.CBW = csiv3.cbw
    m.CarrierFreq = csiv3.carrierFreq
    m.SamplingRate = csiv3.samplingRate
    m.SubcarrierBandwidth = csiv3.subcarrierBandwidth
    m.numTones = csiv3.numTones
    m.numTx = csiv3.numTx
    m.numRx = csiv3.numRx
    if csiv3.deviceType == PicoScenesDeviceType.QCA9300:
        m.firmwareVersion = 0
        temp = 140 if csiv3.cbw == ChannelBandwidthEnum.CBW_20 else 285
        actualNumSTSPerChain = <int>(csiv3.csiBufferLength / temp)
        actualNumSTSPerChain = <int>(actualNumSTSPerChain / csiv3.numRx)
        m.numESS = actualNumSTSPerChain - csiv3.numTx
        m.numCSI = 1
        m.ant_sel = csiv3.antSel
        parseCSI9300scidx(scidx, csiv3.packetFormat,
                          csiv3.cbw, csiv3.subcarrierOffset)
        parseCSI9300(csi, csiv3.payload, csiv3.numTones,
                     actualNumSTSPerChain, csiv3.numRx)
    elif csiv3.deviceType == PicoScenesDeviceType.IWL5300:
        m.firmwareVersion = 52
        actualNumSTSPerChain = <int>((csiv3.csiBufferLength - 12) / 60)
        actualNumSTSPerChain = <int>(actualNumSTSPerChain / csiv3.numRx)
        m.numESS = actualNumSTSPerChain - csiv3.numTx
        m.numCSI = 1
        m.ant_sel = csiv3.antSel
        parseCSI5300scidx(scidx, csiv3.packetFormat,
                          csiv3.cbw, csiv3.subcarrierOffset)
        parseCSI5300(csi, csiv3.payload, csiv3.numTones,
                     actualNumSTSPerChain, csiv3.numRx, csiv3.antSel)
    elif csiv3.deviceType == PicoScenesDeviceType.IWLMVM_AX200 or \
        csiv3.deviceType == PicoScenesDeviceType.IWLMVM_AX210:
        pass
        m.firmwareVersion = 67
        m.numESS = 0
        m.numCSI = 1
        m.ant_sel = 0
        parseCSIMVMscidx(scidx, csiv3.packetFormat,
                         csiv3.cbw, csiv3.subcarrierOffset, True)
        parseCSIMVM(csi, csiv3.payload, csiv3.numTones,
                    csiv3.numTx, csiv3.numRx,
                    csiv3.packetFormat, csiv3.cbw, 67, True)
    elif csiv3.deviceType == PicoScenesDeviceType.USRP:
        m.firmwareVersion = 0
        m.numESS = csiv3.numESS
        m.numCSI = csiv3.numCSI
        m.ant_sel = csiv3.antSel
        parseCSIUSRPscidx(scidx, csiv3.payload, csiv3.numTones)
        parseCSIUSRP(csi, csiv3.payload + csiv3.numTones * 2,
                     csiv3.csiBufferLength - csiv3.numTones * 2)


cdef void parse_CSIV4(unsigned char *buf, dtc_CSI_Info *m,
                      np.complex128_t[:, :, :] csi,
                      np.int32_t[:] scidx):
    cdef CSIV4 *csiv4 = <CSIV4*>buf
    cdef int actualNumSTSPerChain
    cdef int temp

    m.DeviceType = csiv4.deviceType
    m.PacketFormat = csiv4.packetFormat
    m.CBW = csiv4.cbw
    m.CarrierFreq = csiv4.carrierFreq
    m.SamplingRate = csiv4.samplingRate
    m.SubcarrierBandwidth = csiv4.subcarrierBandwidth
    m.numTones = csiv4.numTones
    m.numTx = csiv4.numTx
    m.numRx = csiv4.numRx
    if csiv4.deviceType == PicoScenesDeviceType.QCA9300:
        m.firmwareVersion = 0
        temp = 140 if csiv4.cbw == ChannelBandwidthEnum.CBW_20 else 285
        actualNumSTSPerChain = <int>(csiv4.csiBufferLength / temp)
        actualNumSTSPerChain = <int>(actualNumSTSPerChain / csiv4.numRx)
        m.numESS = actualNumSTSPerChain - csiv4.numTx
        m.numCSI = 1
        m.ant_sel = csiv4.antSel
        parseCSI9300scidx(scidx, csiv4.packetFormat,
                          csiv4.cbw, csiv4.subcarrierOffset)
        parseCSI9300(csi, csiv4.payload, csiv4.numTones,
                     actualNumSTSPerChain, csiv4.numRx)
    elif csiv4.deviceType == PicoScenesDeviceType.IWL5300:
        m.firmwareVersion = 52
        actualNumSTSPerChain = <int>((csiv4.csiBufferLength - 12) / 60)
        actualNumSTSPerChain = <int>(actualNumSTSPerChain / csiv4.numRx)
        m.numESS = actualNumSTSPerChain - csiv4.numTx
        m.numCSI = 1
        m.ant_sel = csiv4.antSel
        parseCSI5300scidx(scidx, csiv4.packetFormat,
                          csiv4.cbw, csiv4.subcarrierOffset)
        parseCSI5300(csi, csiv4.payload, csiv4.numTones,
                     actualNumSTSPerChain, csiv4.numRx, csiv4.antSel)
    elif csiv4.deviceType == PicoScenesDeviceType.IWLMVM_AX200 or \
        csiv4.deviceType == PicoScenesDeviceType.IWLMVM_AX210:
        pass
        m.firmwareVersion = csiv4.firmwareVersion
        m.numESS = 0
        m.numCSI = 1
        m.ant_sel = csiv4.antSel
        parseCSIMVMscidx(scidx, csiv4.packetFormat,
                         csiv4.cbw, csiv4.subcarrierOffset, True)
        parseCSIMVM(csi, csiv4.payload, csiv4.numTones,
                    csiv4.numTx, csiv4.numRx,
                    csiv4.packetFormat, csiv4.cbw, csiv4.firmwareVersion, True)
    elif csiv4.deviceType == PicoScenesDeviceType.USRP:
        m.firmwareVersion = 0
        m.numESS = csiv4.numESS
        m.numCSI = csiv4.numCSI
        m.ant_sel = csiv4.antSel
        parseCSIUSRPscidx(scidx, csiv4.payload, csiv4.numTones)
        parseCSIUSRP(csi, csiv4.payload + csiv4.numTones * 2,
                     csiv4.csiBufferLength - csiv4.numTones * 2)


cdef bint parse_MPDU(unsigned char *buf, dtc_MPDU_Info *m,
                     np.uint8_t[:] mpdu, uint32_t length):
    cdef uint32_t i
    m.length = length
    if mpdu.shape[0] < length:
        return False

    for i in range(length):
        mpdu[i] = cu8(buf + i)
    return True


cdef void parse_StandardHeader(unsigned char *buf,
                               dtc_ieee80211_mac_frame_header *m):
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


cdef void parse_PicoScenesHeader(unsigned char *buf,
                                 dtc_PicoScenesFrameHeader *m):
    cdef PicoScenesFrameHeader *psfh = <PicoScenesFrameHeader*>buf
    m.MagicValue = psfh.magicValue
    m.Version = psfh.version
    m.DeviceType = psfh.deviceType
    m.FrameType = psfh.frameType
    m.TaskId = psfh.taskId
    m.TxId = psfh.txId


cdef void parse_RxSBasic(uint16_t versionId, unsigned char *buf,
                         dtc_RXBasic *m):
    if versionId == 0x1:
        parse_RxSBasicV1(buf, m)
    elif versionId == 0x2:
        parse_RxSBasicV2(buf, m)
    elif versionId == 0x3:
        parse_RxSBasicV3(buf, m)
    else:
        pass


cdef void parse_ExtraInfo(uint16_t versionId, unsigned char *buf,
                          dtc_ExtraInfo *m):
    if versionId == 0x1:
        parse_ExtraInfoV1(buf, m)
    else:
        pass


cdef void parse_MVMExtra(uint16_t versionId, unsigned char *buf,
                         dtc_IntelMVMExtrta *m):
    if versionId == 0x1:
        parse_MVMExtraV1(buf, m)
    else:
        pass


cdef void parse_DPASRequest(uint16_t versionId, unsigned char *buf,
                            dtc_DPASRequest *m):
    if versionId == 0x1:
        parse_DPASRequestV1(buf, m)
    elif versionId == 0x2:
        parse_DPASRequestV2(buf, m)
    elif versionId == 0x3:
        parse_DPASRequestV3(buf, m)
    elif versionId == 0x4:
        parse_DPASRequestV4(buf, m)
    else:
        pass


cdef void parse_CSI(uint16_t versionId, unsigned char *buf, dtc_CSI_Info *m,
                    np.complex128_t[:, :, :] csi, np.int32_t[:] scidx):
    if versionId == 0x1:
        parse_CSIV1(buf, m, csi, scidx)
    elif versionId == 0x2:
        parse_CSIV2(buf, m, csi, scidx)
    elif versionId == 0x3:
        parse_CSIV3(buf, m, csi, scidx)
    elif versionId == 0x4:
        parse_CSIV4(buf, m, csi, scidx)
    else:
        pass


cdef void parse_SignalMatrix(uint16_t versionId, unsigned char *buf,
                             dtc_SignalMatrix_Info *m,
                             np.complex128_t[:, :, :] data):
    if versionId == 0x1:
        parse_SignalMatrixV1(buf, m, data)
    else:
        pass


cdef void interp_iq(np.complex128_t *csi_1, np.complex128_t *csi_2,
                    np.float64_t ratio, np.complex128_t *iplcsi):
    """interpolate csi along real and imag (linear)"""
    cdef np.complex128_t csi
    csi = csi_2[0] - csi_1[0]
    csi *= ratio
    csi += csi_1[0]
    iplcsi[0] = csi


cdef void interp_ap(np.complex128_t *csi_1, np.complex128_t *csi_2,
                    np.float64_t ratio, np.complex128_t *iplcsi):
    """interpolate csi along amplitude and phase (linear)"""
    cdef np.float64_t csi_a
    cdef np.float64_t csi_p
    cdef np.float64_t csi_1_p

    csi_a = abs(csi_2[0])- abs(csi_1[0])
    csi_a *= ratio
    csi_a += abs(csi_1[0])

    csi_1_p = atan2(csi_1[0].real, csi_1[0].imag)
    csi_p = atan2(csi_2[0].real, csi_2[0].imag) - csi_1_p
    if csi_p > pi:
        csi_p -= (2 * pi)
    if csi_p < -pi:
        csi_p += (2 * pi)
    csi_p *= ratio
    csi_p += csi_1_p
    iplcsi[0].real = csi_a * cos(csi_p)
    iplcsi[0].imag = csi_a * sin(csi_p)


# Picoscenes


cdef class Picoscenes:
    def __cinit__(self, *argv, **kw):
        pass

    def __init__(self, str file, np.dtype dtype, bint if_report=True,
                 int bufsize=0):
        self.file = file
        self.if_report = if_report
        pk_num = self.get_pknum(bufsize)
        self.cache = np.zeros([pk_num], dtype)
        self.init_memview()

    cpdef read(self):
        self.seek(self.file, 0, 0) 

    cpdef seek(self, file, long pos, long num):
        cdef FILE *f = crfopen(file)
        cdef long lens = getfilesize(f, 0)
        cdef uint32_t field_len = 4
        cdef uint32_t buf_size = 4              # Require: buf_size >= 4
        cdef unsigned char *buf
        if num == 0:
            num = lens

        cdef int count = 0
        cdef size_t l

        buf = <unsigned char *>malloc(buf_size * sizeof(unsigned char))
        while pos < (lens-4):
            buf = crfread(buf, &buf_size, f, &field_len)
            l = fread(buf, sizeof(unsigned char), field_len, f)
            self.parse(buf, <uint32_t>l, count)
            pos += field_len
            count += 1
            if count >= num:
                break
        free(buf)
        fclose(f)
        self.count = count
        if self.if_report:
            printf("%d packets parsed\n", count)
        self.raw = self.cache[:count]

    cpdef pmsg(self, data):
        # This method hasn't been ready
        if self.parse(data, <uint32_t>len(data), 0):
            return
        self.raw = self.cache
        return 0xf300       # status code

    cpdef interpolate_csi(self, name, bint IQ=False):
        """interpolate csi"""
        cdef int i, j, k, g, d, nsc, nrx, ntx
        cdef int max_idx = 0
        cdef int max_value = 0
        cdef np.float64_t ratio
        cdef np.int32_t[:] sci
        cdef dtc_CSI_Info[:] mem_CSI_Info
        cdef np.int32_t[:, :] mem_CSI_scidx
        cdef np.complex128_t[:, :, :, :] mem_CSI_CSI
        if name == 'CSI':
            mem_CSI_Info = self.mem_CSI_Info
            mem_CSI_scidx = self.mem_CSI_SubcarrierIndex
            mem_CSI_CSI = self.mem_CSI_CSI
        elif name == 'LegacyCSI':
            mem_CSI_Info = self.mem_LegacyCSI_Info
            mem_CSI_scidx = self.mem_LegacyCSI_SubcarrierIndex
            mem_CSI_CSI = self.mem_LegacyCSI_CSI
        else:
            pass

        # initialize interpolated_csi and interpolated_scindex
        nsc = <int>mem_CSI_CSI.shape[1]
        nrx = <int>mem_CSI_CSI.shape[2]
        ntx = <int>mem_CSI_CSI.shape[3]
        if nsc == 0 or nrx == 0 or ntx == 0:
            return None
        for i in range(self.count):
            if mem_CSI_Info[i].numTones > max_value:
                max_value = mem_CSI_Info[i].numTones
                max_idx = i
        nsc = mem_CSI_scidx[max_idx, -1] - mem_CSI_scidx[max_idx, 0] + 1
        interpolated_csi = np.zeros([self.count, nsc, nrx, ntx],
                                    dtype=np.complex128)
        interpolated_scindex = np.zeros([self.count, nsc], dtype=np.int32)
        cdef np.complex128_t[:, :, :, :] mem_iplcsi = interpolated_csi
        cdef np.int32_t[:, :] mem_iplsci = interpolated_scindex

        with cython.boundscheck(False):
            for i in range(self.count):
                nsc = mem_CSI_Info[i].numTones
                nrx = mem_CSI_Info[i].numRx
                ntx = mem_CSI_Info[i].numTx + mem_CSI_Info[i].numESS
                sci = mem_CSI_scidx[i, :nsc]
                nsc = sci[-1] - sci[0] + 1

                # interpolate subcarrier index
                for g in range(nsc):
                    mem_iplsci[i, g] = sci[0] + g
                for g in range(nsc, mem_iplsci.shape[1]):
                    mem_iplsci[i, g] = sci[-1]

                # interpolate csi (linear)
                for j in range(nrx):
                    for k in range(ntx):
                        d = 0
                        for g in range(nsc):
                            if g == (sci[d] - sci[0]):
                                mem_iplcsi[i, g, j, k] = mem_CSI_CSI[i, d, j,k]
                                d += 1
                                continue
                            else:
                                ratio = g - (sci[d - 1] - sci[0])
                                ratio /= (sci[d] - sci[d - 1])
                                if IQ:
                                    interp_iq(&mem_CSI_CSI[i, d - 1, j, k],
                                              &mem_CSI_CSI[i, d, j, k],
                                              ratio,
                                              &mem_iplcsi[i, g, j, k])
                                else:
                                    interp_ap(&mem_CSI_CSI[i, d - 1, j, k],
                                              &mem_CSI_CSI[i, d, j, k],
                                              ratio,
                                              &mem_iplcsi[i, g, j, k])
        return interpolated_csi, interpolated_scindex

    cdef void init_memview(self):
        self.mem_StandardHeader = self.cache["StandardHeader"]
        self.mem_RxSBasic = self.cache["RxSBasic"]
        self.mem_RxExtraInfo = self.cache["RxExtraInfo"]
        self.mem_CSI_Info = self.cache["CSI"]["Info"]
        self.mem_MVMExtra = self.cache["MVMExtra"]
        self.mem_DPASRequest = self.cache["DPASRequest"]
        self.mem_PicoScenesHeader = self.cache["PicoScenesHeader"]
        self.mem_TxExtraInfo = self.cache["TxExtraInfo"]
        self.mem_PilotCSI_Info = self.cache["PilotCSI"]["Info"]
        self.mem_LegacyCSI_Info = self.cache["LegacyCSI"]["Info"]
        self.mem_BasebandSignals_Info = self.cache["BasebandSignals"]["Info"]
        self.mem_PreEQSymbols_Info = self.cache["PreEQSymbols"]["Info"]
        self.mem_MPDU_Info = self.cache["MPDU"]["Info"]

        self.mem_CSI_CSI = self.cache["CSI"]["CSI"]
        self.mem_PilotCSI_CSI = self.cache["PilotCSI"]["CSI"]
        self.mem_LegacyCSI_CSI = self.cache["LegacyCSI"]["CSI"]
        self.mem_BasebandSignals_Data = self.cache["BasebandSignals"]["Data"]
        self.mem_PreEQSymbols_Data = self.cache["PreEQSymbols"]["Data"]
        self.mem_MPDU_Data = self.cache["MPDU"]["Data"]

        self.mem_CSI_SubcarrierIndex = self.cache["CSI"]["SubcarrierIndex"]
        self.mem_PilotCSI_SubcarrierIndex = self.cache["PilotCSI"]["SubcarrierIndex"]
        self.mem_LegacyCSI_SubcarrierIndex = self.cache["LegacyCSI"]["SubcarrierIndex"]

    cdef int get_pknum(self, int bufsize):
        cdef int pk_num
        if bufsize == 0:
            if self.file is None:
                self.count = 1
                pk_num = 1
            else:
                pk_num = self.get_count()
        else:
            pk_num = bufsize
        return pk_num

    cdef int get_count(self):
        cdef int count = 0
        cdef long pos = 0
        cdef uint32_t field_len
        cdef size_t l
        cdef FILE *f = crfopen(self.file)
        cdef long lens = getfilesize(f, 0)
        cdef unsigned char buf[4]

        while pos < (lens - 4):
            l = fread(buf, sizeof(unsigned char), 4, f)
            field_len = cu32(buf) + 4
            fseek(f, field_len - 4, SEEK_CUR)

            pos += field_len
            count += 1
        fclose(f)
        return count

    cdef bint parse(self, unsigned char *buf, uint32_t buf_length, int count):
        cdef int cur = 0
        cdef int i, offset
        cdef ModularPicoScenesRxFrameHeader *mpsrfh
        cdef AbstractPicoScenesFrameSegment apsfs
        cdef PicoScenesFrameHeader *psfh
        cdef unsigned char *p
        cdef char *sname
        cdef uint8_t slength

        # ModularPicoScenesRxFrameHeader
        mpsrfh = <ModularPicoScenesRxFrameHeader*>buf
        if mpsrfh.frameLength + 4 != buf_length:
            return False
        if mpsrfh.magicWord != 0x20150315  or mpsrfh.frameVersion != 0x1:
            return False
        cur += sizeof(ModularPicoScenesRxFrameHeader)

        # MUST
        for i in range(mpsrfh.numRxSegments):
            parse_AbstractPicoScenesFrameSegment(buf + cur, &apsfs)
            offset = apsfs.segNameLength + 7
            sname = <char *>apsfs.segmentName
            slength = apsfs.segNameLength
            apsfs.versionId = apsfs.versionId
            p = buf + cur + offset

            if not strncmp(b"RxSBasic", sname, slength):
                parse_RxSBasic(apsfs.versionId, p,
                               &self.mem_RxSBasic[count])
            elif not strncmp(b"ExtraInfo", sname, slength):
                parse_ExtraInfo(apsfs.versionId, p,
                                &self.mem_RxExtraInfo[count])
            elif not strncmp(b"MVMExtra", sname, slength):
                parse_MVMExtra(apsfs.versionId, p,
                               &self.mem_MVMExtra[count])
            elif not strncmp(b"CSI", sname, slength):
                parse_CSI(apsfs.versionId, p,
                          &self.mem_CSI_Info[count],
                          self.mem_CSI_CSI[count],
                          self.mem_CSI_SubcarrierIndex[count])
            elif not strncmp(b"PilotCSI", sname, slength):
                parse_CSI(apsfs.versionId, p,
                          &self.mem_PilotCSI_Info[count],
                          self.mem_PilotCSI_CSI[count],
                          self.mem_PilotCSI_SubcarrierIndex[count])
            elif not strncmp(b"LegacyCSI", sname, slength):
                parse_CSI(apsfs.versionId, p,
                          &self.mem_LegacyCSI_Info[count],
                          self.mem_LegacyCSI_CSI[count],
                          self.mem_LegacyCSI_SubcarrierIndex[count])
            elif not strncmp(b"BasebandSignal", sname, slength):
                parse_SignalMatrix(apsfs.versionId, p,
                                   &self.mem_BasebandSignals_Info[count],
                                   self.mem_BasebandSignals_Data[count])
            elif not strncmp(b"PreEQSymbols", sname, slength):
                parse_SignalMatrix(apsfs.versionId, p,
                                   &self.mem_PreEQSymbols_Info[count],
                                   self.mem_PreEQSymbols_Data[count])
            else:
                pass
            cur += (4 + apsfs.segmentLength)

        # MPDU
        parse_MPDU(buf + cur,
                   &self.mem_MPDU_Info[count],
                   self.mem_MPDU_Data[count],
                   mpsrfh.frameLength + 4 - cur)

        # StandardHeader
        parse_StandardHeader(buf + cur, &self.mem_StandardHeader[count])
        cur += sizeof(ieee80211_mac_frame_header)

        # PicoScenesFrameHeader
        psfh = <PicoScenesFrameHeader*>(buf + cur)
        if psfh.magicValue == 0x20150315:
            parse_PicoScenesHeader(buf + cur,
                                   &self.mem_PicoScenesHeader[count])
            cur += sizeof(PicoScenesFrameHeader)

            # Optional
            for i in range(psfh.numSegments):
                parse_AbstractPicoScenesFrameSegment(buf + cur, &apsfs)
                offset = apsfs.segNameLength + 7
                sname = <char *>apsfs.segmentName
                slength = apsfs.segNameLength
                p = buf + cur + offset

                if not strncmp(b"ExtraInfo", sname, slength):
                    parse_ExtraInfo(apsfs.versionId, p,
                                    &self.mem_TxExtraInfo[count])
                elif not strncmp(b"DPASRequest", sname, slength):
                    parse_DPASRequest(apsfs.versionId, p,
                                      &self.mem_DPASRequest[count])
                else:
                    pass
                cur += (4 + apsfs.segmentLength)
        return True
