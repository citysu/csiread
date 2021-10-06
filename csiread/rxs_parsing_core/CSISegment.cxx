//
// Created by 蒋志平 on 2020/11/5.
//

#include <algorithm>
#include <utility>
#include <deque>
#include "CSISegment.hxx"
#include "preprocessor/generated/CSIPreprocessor.h"

// The following definition is for reference use.
//struct QCA9300CSISegmentContentDescriptorV1 {
//    uint16_t deviceType;
//    uint8_t packetFormat;
//    uint16_t cbw;
//uint64_t carrierFreq;
//uint64_t samplingRate;
//uint32_t subcarrierBandwidth;
//    uint16_t numTone;
//    uint8_t numSTS;        /* number of Spatial-time Stream */
//    uint8_t numESS;        /* number of Extra Spatial-time Stream */
//    uint8_t numRx;
//    uint8_t antSel;
//    uint32_t rawDataLength;
//} __attribute__ ((__packed__));
//
//struct IWL5300CSISegmentContentDescriptorV1 {
//    uint16_t deviceType;
//    uint8_t packetFormat;
//    uint16_t cbw;
//uint64_t carrierFreq;
//uint64_t samplingRate;
//uint32_t subcarrierBandwidth;
//    uint16_t numTone;
//    uint8_t numSTS;        /* number of Spatial-time Stream */
//    uint8_t numESS;        /* number of Extra Spatial-time Stream */
//    uint8_t numRx;
//    uint8_t antSel;
//    uint32_t rawDataLength;
//} __attribute__ ((__packed__));


SignalMatrix<std::complex<double>> parseQCA9300CSIData(const uint8_t *csiData, int nSTS, int nRx, int nTones) {
    std::vector<std::complex<double>> CSIArray(nSTS * nRx * nTones);
    parseQCA9300CSIData(CSIArray.begin(), csiData, nSTS, nRx, nTones);
    return SignalMatrix(CSIArray, std::vector<int32_t>{nTones, nSTS, nRx}, SignalMatrixStorageMajority::ColumnMajor);
}

SignalMatrix<std::complex<double>> parseIWL5300CSIData(const uint8_t *payload, int ntx, int nrx, uint8_t ant_sel) {
    std::vector<std::complex<double>> CSIArray(ntx * nrx * 30);
    parseIWL5300CSIData(CSIArray.begin(), payload, ntx, nrx, ant_sel);
    return SignalMatrix(CSIArray, std::vector<int32_t>{30, ntx, nrx}, SignalMatrixStorageMajority::ColumnMajor);
}

std::vector<int16_t> CSI::QCA9300SubcarrierIndices_CBW20 = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>();
    for (auto i = -28; i <= -1; i++)
        indices.emplace_back(i);
    for (auto i = 1; i <= 28; i++)
        indices.emplace_back(i);

    return indices;
}();

std::vector<int16_t> CSI::QCA9300SubcarrierIndices_CBW40 = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>();
    for (auto i = -58; i <= -2; i++)
        indices.emplace_back(i);
    for (auto i = 2; i <= 58; i++)
        indices.emplace_back(i);
    return indices;
}();

std::vector<int16_t> CSI::IWL5300SubcarrierIndices_CBW20 = []() noexcept -> std::vector<int16_t> {
    return std::vector<int16_t>{-28, -26, -24, -22, -20, -18, -16, -14, -12, -10, -8, -6, -4, -2, -1, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 28};
}();

std::vector<int16_t> CSI::IWL5300SubcarrierIndices_CBW40 = []() noexcept -> std::vector<int16_t> {
    return std::vector<int16_t>{-58, -54, -50, -46, -42, -38, -34, -30, -26, -22, -18, -14, -10, -6, -2, 2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 50, 54, 58};
}();

CSI CSI::fromQCA9300(const uint8_t *buffer, uint32_t bufferLength, uint8_t numTx, uint8_t numRx, uint8_t numTones, ChannelBandwidthEnum cbw, int16_t subcarrierIndexOffset) {
    uint32_t actualNumSTSPerChain = bufferLength / (cbw == ChannelBandwidthEnum::CBW_20 ? 140 : 285) / numRx; // 56 * 2 * 10 / 8 = 140B , 114 * 2 * 10 / 8 = 285;
    auto csi = CSI{.deviceType = PicoScenesDeviceType::QCA9300,
            .packetFormat = PacketFormatEnum::PacketFormat_HT,
            .cbw = cbw,
            .dimensions = CSIDimension{.numTones = numTones, .numTx = numTx, .numRx = numRx, .numESS = uint8_t(actualNumSTSPerChain - numTx), .numCSI = 1},
            .antSel = 0,
            .subcarrierOffset = subcarrierIndexOffset,
            .CSIArray = parseQCA9300CSIData(buffer, actualNumSTSPerChain, numRx, numTones),
    };
    std::copy(buffer, buffer + bufferLength, std::back_inserter(csi.rawCSIData));
    if (csi.cbw == ChannelBandwidthEnum::CBW_20) {
        csi.subcarrierIndices = CSI::QCA9300SubcarrierIndices_CBW20;
    } else if (csi.cbw == ChannelBandwidthEnum::CBW_40) {
        csi.subcarrierIndices = CSI::QCA9300SubcarrierIndices_CBW40;
    }

    if (subcarrierIndexOffset != 0) {
        std::transform(csi.subcarrierIndices.begin(), csi.subcarrierIndices.end(), csi.subcarrierIndices.begin(), [=](int16_t index) {
            return index + subcarrierIndexOffset;
        });
    }

    return csi;
}

CSI CSI::fromIWL5300(const uint8_t *buffer, uint32_t bufferLength, uint8_t numTx, uint8_t numRx, uint8_t numTones, ChannelBandwidthEnum cbw, int16_t subcarrierIndexOffset, uint8_t ant_sel) {
    uint32_t actualNumSTSPerChain = (bufferLength - 12) / 60 / numRx;
    auto csi = CSI{.deviceType = PicoScenesDeviceType::IWL5300,
            .packetFormat=PacketFormatEnum::PacketFormat_HT,
            .cbw = cbw,
            .dimensions = CSIDimension{.numTones = numTones, .numTx = numTx, .numRx = numRx, .numESS = uint8_t(actualNumSTSPerChain - numTx), .numCSI = 1},
            .antSel = ant_sel,
            .subcarrierOffset = subcarrierIndexOffset,
            .CSIArray = parseIWL5300CSIData(buffer, actualNumSTSPerChain, numRx, ant_sel),
    };
    std::copy(buffer, buffer + bufferLength, std::back_inserter(csi.rawCSIData));
    if (csi.cbw == ChannelBandwidthEnum::CBW_20) {
        csi.subcarrierIndices = CSI::IWL5300SubcarrierIndices_CBW20;
    } else if (csi.cbw == ChannelBandwidthEnum::CBW_40)
        csi.subcarrierIndices = CSI::IWL5300SubcarrierIndices_CBW40;

    if (subcarrierIndexOffset != 0) {
        std::transform(csi.subcarrierIndices.begin(), csi.subcarrierIndices.end(), csi.subcarrierIndices.begin(), [=](int16_t index) {
            return index + subcarrierIndexOffset;
        });
    }

    return csi;
}

void CSI::interpolateCSI() {
    coder::array<creal_T, 2U> CSI;
    coder::array<creal_T, 2U> newCSI;
    coder::array<double, 2U> newMag;
    coder::array<double, 2U> newPhase;
    coder::array<short, 1U> interpedIndex_int16;
    coder::array<short, 1U> subcarrierIndex_int16;

    CSI.set_size(dimensions.numTones, (dimensions.numTx + dimensions.numESS) * dimensions.numRx * dimensions.numCSI);
    for (auto toneIndex = 0; toneIndex < CSI.size(0); toneIndex++) {
        for (auto txTrIndex = 0; txTrIndex < CSI.size(1); txTrIndex++) {
            auto pos = toneIndex + txTrIndex * CSI.size(0);
            CSI[pos] = *(creal_T *) (&CSIArray.array[pos]);
        }
    }

    subcarrierIndex_int16.set_size(subcarrierIndices.size());
    for (auto scIndex = 0; scIndex < subcarrierIndex_int16.size(0); scIndex++) {
        subcarrierIndex_int16[scIndex] = subcarrierIndices[scIndex];
    }

    CSIPreprocessor(CSI, subcarrierIndex_int16, newCSI, newMag, newPhase, interpedIndex_int16);

    CSIArray.array.clear();
    std::copy((std::complex<double> *) newCSI.data(), (std::complex<double> *) newCSI.data() + newCSI.numel(), std::back_inserter(CSIArray.array));
    CSIArray.dimensions[0] = newCSI.size(0);

    magnitudeArray.array.clear();
    std::copy((double *) newMag.data(), (double *) newMag.data() + newMag.numel(), std::back_inserter(magnitudeArray.array));
    magnitudeArray.dimensions = CSIArray.dimensions;

    phaseArray.array.clear();
    std::copy((double *) newPhase.data(), (double *) newPhase.data() + newPhase.numel(), std::back_inserter(phaseArray.array));
    phaseArray.dimensions = CSIArray.dimensions;

    subcarrierIndices.clear();
    std::copy((int16_t *) interpedIndex_int16.data(), (int16_t *) interpedIndex_int16.data() + interpedIndex_int16.numel(), std::back_inserter(subcarrierIndices));
    dimensions.numTones = subcarrierIndices.size();
}

std::vector<uint8_t> CSI::toBuffer() {
    if (!rawCSIData.empty()) {
        return rawCSIData;
    }

    auto buffer = std::vector<uint8_t>();
    std::copy((uint8_t *) &deviceType, (uint8_t *) &deviceType + sizeof(deviceType), std::back_inserter(buffer));
    std::copy((uint8_t *) &packetFormat, (uint8_t *) &packetFormat + sizeof(packetFormat), std::back_inserter(buffer));
    std::copy((uint8_t *) &cbw, (uint8_t *) &cbw + sizeof(cbw), std::back_inserter(buffer));
    std::copy((uint8_t *) &carrierFreq, (uint8_t *) &carrierFreq + sizeof(carrierFreq), std::back_inserter(buffer));
    std::copy((uint8_t *) &samplingRate, (uint8_t *) &samplingRate + sizeof(samplingRate), std::back_inserter(buffer));
    std::copy((uint8_t *) &subcarrierBandwidth, (uint8_t *) &subcarrierBandwidth + sizeof(subcarrierBandwidth), std::back_inserter(buffer));
    std::copy((uint8_t *) &dimensions.numTones, (uint8_t *) &dimensions.numTones + sizeof(dimensions.numTones), std::back_inserter(buffer));
    std::copy((uint8_t *) &dimensions.numTx, (uint8_t *) &dimensions.numTx + sizeof(dimensions.numTx), std::back_inserter(buffer));
    std::copy((uint8_t *) &dimensions.numRx, (uint8_t *) &dimensions.numRx + sizeof(dimensions.numRx), std::back_inserter(buffer));
    std::copy((uint8_t *) &dimensions.numESS, (uint8_t *) &dimensions.numESS + sizeof(dimensions.numESS), std::back_inserter(buffer));
    std::copy((uint8_t *) &dimensions.numCSI, (uint8_t *) &dimensions.numCSI + sizeof(dimensions.numCSI), std::back_inserter(buffer));
    std::copy((uint8_t *) &antSel, (uint8_t *) &antSel + sizeof(antSel), std::back_inserter(buffer));
    std::copy((uint8_t *) &subcarrierOffset, (uint8_t *) &subcarrierOffset + sizeof(subcarrierOffset), std::back_inserter(buffer));
    if (deviceType == PicoScenesDeviceType::IWL5300 || deviceType == PicoScenesDeviceType::QCA9300) {
        std::copy(rawCSIData.cbegin(), rawCSIData.cend(), std::back_inserter(buffer));
    } else if (deviceType == PicoScenesDeviceType::USRP) {
        std::vector<uint8_t> subcarrierIndicesBuffer;
        for (const auto &subcarrierIndex: subcarrierIndices) {
            std::copy((uint8_t *) &subcarrierIndex, (uint8_t *) &subcarrierIndex + sizeof(subcarrierIndex), std::back_inserter(subcarrierIndicesBuffer));
        }
        auto csiBuffer = CSIArray.toBuffer();

        uint32_t csiBufferLength = subcarrierIndicesBuffer.size() + csiBuffer.size();
        std::copy((uint8_t *) &csiBufferLength, (uint8_t *) &csiBufferLength + sizeof(csiBufferLength), std::back_inserter(buffer));
        std::copy(subcarrierIndicesBuffer.cbegin(), subcarrierIndicesBuffer.cend(), std::back_inserter(buffer));
        std::copy(csiBuffer.cbegin(), csiBuffer.cend(), std::back_inserter(buffer));
    }

    return buffer;
}

static auto v1Parser = [](const uint8_t *buffer, uint32_t bufferLength) -> CSI {
    uint32_t pos = 0;

    auto deviceType = (PicoScenesDeviceType) *(uint16_t *) (buffer + pos);
    pos += sizeof(PicoScenesDeviceType);
    PacketFormatEnum packetFormat = *(PacketFormatEnum *) (buffer + pos);
    pos += sizeof(PacketFormatEnum);
    ChannelBandwidthEnum cbw = *(ChannelBandwidthEnum *) (buffer + pos);
    pos += sizeof(ChannelBandwidthEnum);
    auto carrierFreq = *(uint64_t *) (buffer + pos);
    pos += sizeof(uint64_t);
    auto samplingRate = *(uint64_t *) (buffer + pos);
    pos += sizeof(uint64_t);
    auto subcarrierBandwidth = *(uint32_t *) (buffer + pos);
    pos += sizeof(uint32_t);
    uint16_t numTone = *(uint16_t *) (buffer + pos);
    pos += 2;
    uint8_t numSTS = *(uint8_t *) (buffer + pos++);
    uint8_t numRx = *(uint8_t *) (buffer + pos++);
    uint8_t numESS = *(uint8_t *) (buffer + pos++);
    uint8_t antSelByte = *(uint8_t *) (buffer + pos++);
    uint32_t CSIBufferLength = *(uint32_t *) (buffer + pos);
    pos += 4;

    if (deviceType == PicoScenesDeviceType::QCA9300) {
        auto csi = CSI::fromQCA9300(buffer + pos, CSIBufferLength, numSTS, numRx, numTone, cbw, 0);
        csi.carrierFreq = carrierFreq;
        csi.samplingRate = samplingRate;
        csi.subcarrierBandwidth = subcarrierBandwidth;
        return csi;
    } else if (deviceType == PicoScenesDeviceType::IWL5300) {
        auto csi = CSI::fromIWL5300(buffer + pos, CSIBufferLength, numSTS, numRx, numTone, cbw, 0, antSelByte);
        csi.carrierFreq = carrierFreq;
        csi.samplingRate = samplingRate;
        csi.subcarrierBandwidth = subcarrierBandwidth;
        return csi;
    } else if (deviceType == PicoScenesDeviceType::USRP) {
        auto csiBufferStart = pos;
        std::vector<int16_t> subcarrierIndices;
        for (auto i = 0; i < numTone; i++) {
            subcarrierIndices.emplace_back(*(uint16_t *) (buffer + pos));
            pos += 2;
        }
        uint32_t csiArrayLength = CSIBufferLength - 2 * numTone;
        CSI csi{.deviceType = PicoScenesDeviceType::USRP,
                .packetFormat = packetFormat,
                .cbw = cbw,
                .carrierFreq = carrierFreq,
                .samplingRate = samplingRate,
                .subcarrierBandwidth = subcarrierBandwidth,
                .dimensions = CSIDimension{.numTones = numTone, .numTx = numSTS, .numRx = numRx, .numESS = numESS, .numCSI = 1},
                .antSel = 0,
                .subcarrierIndices = subcarrierIndices,
                .CSIArray = SignalMatrix<std::complex<double>>::fromBuffer(buffer + pos, buffer + pos + csiArrayLength, SignalMatrixStorageMajority::ColumnMajor)
        };
        auto csiBufferEnd = pos + csiArrayLength;
        std::copy(buffer + csiBufferStart, buffer + csiBufferEnd, std::back_inserter(csi.rawCSIData));
        return csi;
    }

    throw std::runtime_error("CSISegment cannot decode the given buffer by v1Parser.");
};

static auto v2Parser = [](const uint8_t *buffer, uint32_t bufferLength) -> CSI { // add subcarrierOffset
    uint32_t pos = 0;

    auto deviceType = (PicoScenesDeviceType) *(uint16_t *) (buffer + pos);
    pos += sizeof(PicoScenesDeviceType);
    PacketFormatEnum packetFormat = *(PacketFormatEnum *) (buffer + pos);
    pos += sizeof(PacketFormatEnum);
    ChannelBandwidthEnum cbw = *(ChannelBandwidthEnum *) (buffer + pos);
    pos += sizeof(ChannelBandwidthEnum);
    auto carrierFreq = *(uint64_t *) (buffer + pos);
    pos += sizeof(uint64_t);
    auto samplingRate = *(uint64_t *) (buffer + pos);
    pos += sizeof(uint64_t);
    auto subcarrierBandwidth = *(uint32_t *) (buffer + pos);
    pos += sizeof(uint32_t);
    uint16_t numTone = *(uint16_t *) (buffer + pos);
    pos += 2;
    uint8_t numSTS = *(uint8_t *) (buffer + pos++);
    uint8_t numRx = *(uint8_t *) (buffer + pos++);
    uint8_t numESS = *(uint8_t *) (buffer + pos++);
    uint8_t antSelByte = *(uint8_t *) (buffer + pos++);
    uint16_t subcarrierIndexOffset = *(uint16_t *) (buffer + pos);
    pos += 2;
    uint32_t CSIBufferLength = *(uint32_t *) (buffer + pos);
    pos += 4;

    if (deviceType == PicoScenesDeviceType::QCA9300) {
        auto csi = CSI::fromQCA9300(buffer + pos, CSIBufferLength, numSTS, numRx, numTone, cbw, subcarrierIndexOffset);
        csi.carrierFreq = carrierFreq;
        csi.samplingRate = samplingRate;
        csi.subcarrierBandwidth = subcarrierBandwidth;
        return csi;
    } else if (deviceType == PicoScenesDeviceType::IWL5300) {
        auto csi = CSI::fromIWL5300(buffer + pos, CSIBufferLength, numSTS, numRx, numTone, cbw, subcarrierIndexOffset, antSelByte);
        csi.carrierFreq = carrierFreq;
        csi.samplingRate = samplingRate;
        csi.subcarrierBandwidth = subcarrierBandwidth;
        return csi;
    } else if (deviceType == PicoScenesDeviceType::USRP) {
        auto csiBufferStart = pos;
        std::vector<int16_t> subcarrierIndices;
        for (auto i = 0; i < numTone; i++) {
            subcarrierIndices.emplace_back(*(uint16_t *) (buffer + pos));
            pos += 2;
        }
        uint32_t csiArrayLength = CSIBufferLength - 2 * numTone;
        CSI csi{.deviceType = PicoScenesDeviceType::USRP,
                .packetFormat = packetFormat,
                .cbw = cbw,
                .carrierFreq = carrierFreq,
                .samplingRate = samplingRate,
                .subcarrierBandwidth = subcarrierBandwidth,
                .dimensions = CSIDimension{.numTones = numTone, .numTx = numSTS, .numRx = numRx, .numESS = numESS, .numCSI = 1},
                .antSel = 0,
                .subcarrierIndices = subcarrierIndices,
                .CSIArray = SignalMatrix<std::complex<double>>::fromBuffer(buffer + pos, buffer + pos + csiArrayLength, SignalMatrixStorageMajority::ColumnMajor)
        };
        auto csiBufferEnd = pos + csiArrayLength;
        std::copy(buffer + csiBufferStart, buffer + csiBufferEnd, std::back_inserter(csi.rawCSIData));
        return csi;
    }

    throw std::runtime_error("CSISegment cannot decode the given buffer by v2Parser.");
};

static auto v3Parser = [](const uint8_t *buffer, uint32_t bufferLength) -> CSI { // add numCSI
    uint32_t pos = 0;

    auto deviceType = (PicoScenesDeviceType) *(uint16_t *) (buffer + pos);
    pos += sizeof(PicoScenesDeviceType);
    PacketFormatEnum packetFormat = *(PacketFormatEnum *) (buffer + pos);
    pos += sizeof(PacketFormatEnum);
    ChannelBandwidthEnum cbw = *(ChannelBandwidthEnum *) (buffer + pos);
    pos += sizeof(ChannelBandwidthEnum);
    auto carrierFreq = *(uint64_t *) (buffer + pos);
    pos += sizeof(uint64_t);
    auto samplingRate = *(uint64_t *) (buffer + pos);
    pos += sizeof(uint64_t);
    auto subcarrierBandwidth = *(uint32_t *) (buffer + pos);
    pos += sizeof(uint32_t);
    uint16_t numTone = *(uint16_t *) (buffer + pos);
    pos += 2;
    uint8_t numSTS = *(uint8_t *) (buffer + pos++);
    uint8_t numRx = *(uint8_t *) (buffer + pos++);
    uint8_t numESS = *(uint8_t *) (buffer + pos++);
    uint8_t numCSI = *(uint16_t *) (buffer + pos);
    pos += 2;
    uint8_t antSelByte = *(uint8_t *) (buffer + pos++);
    uint16_t subcarrierIndexOffset = *(uint16_t *) (buffer + pos);
    pos += 2;
    uint32_t CSIBufferLength = *(uint32_t *) (buffer + pos);
    pos += 4;

    if (deviceType == PicoScenesDeviceType::QCA9300) {
        auto csi = CSI::fromQCA9300(buffer + pos, CSIBufferLength, numSTS, numRx, numTone, cbw, subcarrierIndexOffset);
        csi.carrierFreq = carrierFreq;
        csi.samplingRate = samplingRate;
        csi.subcarrierBandwidth = subcarrierBandwidth;
        return csi;
    } else if (deviceType == PicoScenesDeviceType::IWL5300) {
        auto csi = CSI::fromIWL5300(buffer + pos, CSIBufferLength, numSTS, numRx, numTone, cbw, subcarrierIndexOffset, antSelByte);
        csi.carrierFreq = carrierFreq;
        csi.samplingRate = samplingRate;
        csi.subcarrierBandwidth = subcarrierBandwidth;
        return csi;
    } else if (deviceType == PicoScenesDeviceType::USRP) {
        auto csiBufferStart = pos;
        std::vector<int16_t> subcarrierIndices;
        for (auto i = 0; i < numTone; i++) {
            subcarrierIndices.emplace_back(*(uint16_t *) (buffer + pos));
            pos += 2;
        }
        uint32_t csiArrayLength = CSIBufferLength - 2 * numTone;
        CSI csi{.deviceType = PicoScenesDeviceType::USRP,
                .packetFormat = packetFormat,
                .cbw = cbw,
                .carrierFreq = carrierFreq,
                .samplingRate = samplingRate,
                .subcarrierBandwidth = subcarrierBandwidth,
                .dimensions = CSIDimension{.numTones = numTone, .numTx = numSTS, .numRx = numRx, .numESS = numESS, .numCSI = numCSI},
                .antSel = 0,
                .subcarrierIndices = subcarrierIndices,
                .CSIArray = SignalMatrix<std::complex<double>>::fromBuffer(buffer + pos, buffer + pos + csiArrayLength, SignalMatrixStorageMajority::ColumnMajor)
        };
        auto csiBufferEnd = pos + csiArrayLength;
        std::copy(buffer + csiBufferStart, buffer + csiBufferEnd, std::back_inserter(csi.rawCSIData));
        return csi;
    }

    throw std::runtime_error("CSISegment cannot decode the given buffer by v3Parser.");
};

std::map<uint16_t, std::function<CSI(const uint8_t *, uint32_t)>> CSISegment::versionedSolutionMap = initializeSolutionMap();

std::map<uint16_t, std::function<CSI(const uint8_t *, uint32_t)>> CSISegment::initializeSolutionMap() noexcept {
    return std::map<uint16_t, std::function<CSI(const uint8_t *, uint32_t)>>{{0x1U, v1Parser},
                                                                             {0x2U, v2Parser},
                                                                             {0x3U, v3Parser}};
}

CSISegment::CSISegment() : AbstractPicoScenesFrameSegment("CSI", 0x3U) {

}

void CSISegment::fromBuffer(const uint8_t *buffer, uint32_t bufferLength) {
    auto[segmentName, segmentLength, versionId, offset] = extractSegmentMetaData(buffer, bufferLength);
    if (segmentName != "CSI" && segmentName != "LegacyCSI" && segmentName != "PilotCSI")
        throw std::runtime_error("CSISegment cannot parse the segment named " + segmentName + ".");
    if (segmentLength + 4 > bufferLength)
        throw std::underflow_error("CSISegment cannot parse the segment with less than " + std::to_string(segmentLength + 4) + "B.");
    if (!versionedSolutionMap.count(versionId)) {
        throw std::runtime_error("CSISegment cannot parse the segment with version v" + std::to_string(versionId) + ".");
    }

    csi = versionedSolutionMap.at(versionId)(buffer + offset, bufferLength - offset);
    std::copy(buffer, buffer + bufferLength, std::back_inserter(rawBuffer));
    this->segmentLength = segmentLength;
    this->segmentName = segmentName;
    isSuccessfullyDecoded = true;
}

CSISegment CSISegment::createByBuffer(const uint8_t *buffer, uint32_t bufferLength) {
    CSISegment csiSegment;
    csiSegment.fromBuffer(buffer, bufferLength);
    return csiSegment;
}

std::string CSISegment::toString() const {
    std::stringstream ss;
    ss << segmentName + ":[";
    ss << "(device=" << csi.deviceType << ", format=" << csi.packetFormat << ", CBW=" << csi.cbw << ", cf=" << std::to_string((double) csi.carrierFreq / 1e6) << " MHz" << ", sf=" << std::to_string((double) csi.samplingRate / 1e6) << " MHz" ", subcarrierBW=" << std::to_string((double) csi.subcarrierBandwidth / 1e3) << " kHz"
       << ", dim(nTones,nSTS,nESS,nRx,nCSI)=(" + std::to_string(csi.dimensions.numTones) + "," + std::to_string(csi.dimensions.numTx) + "," + std::to_string(csi.dimensions.numESS) + "," + std::to_string(csi.dimensions.numRx) + "," + std::to_string(csi.dimensions.numCSI) + "), raw=" + std::to_string(csi.rawCSIData.size()) + "B)]";
    auto temp = ss.str();
    temp.erase(temp.end() - 2, temp.end());
    temp.append("]");
    return temp;
}

std::vector<uint8_t> CSISegment::toBuffer() const {
    return AbstractPicoScenesFrameSegment::toBuffer(true);
}

const CSI &CSISegment::getCSI() const {
    return csi;
}

CSI &CSISegment::getCSI() {
    return csi;
}

void CSISegment::setCSI(const CSI &csiV) {
    csi = csiV;
    clearFieldCache();
    addField("core", csi.toBuffer());
}

std::ostream &operator<<(std::ostream &os, const CSISegment &csiSegment) {
    os << csiSegment.toString();
    return os;
}