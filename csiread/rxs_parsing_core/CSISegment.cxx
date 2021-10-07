//
// Created by 蒋志平 on 2020/11/5.
//

#include <algorithm>
#include <utility>
#include <deque>
#include "CSISegment.hxx"
#include "preprocessor/generated/CSIPreprocessor.h"

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

CSI CSI::fromQCA9300(const uint8_t *buffer, uint32_t bufferLength, uint8_t numTx, uint8_t numRx, uint8_t numTones, ChannelBandwidthEnum cbw, int16_t subcarrierIndexOffset) {
    uint32_t actualNumSTSPerChain = bufferLength / (cbw == ChannelBandwidthEnum::CBW_20 ? 140 : 285) / numRx; // 56 * 2 * 10 / 8 = 140B , 114 * 2 * 10 / 8 = 285;
    auto csi = CSI{.deviceType = PicoScenesDeviceType::QCA9300,
            .packetFormat = PacketFormatEnum::PacketFormat_HT,
            .cbw = cbw,
            .dimensions = CSIDimension{.numTones = numTones, .numTx = numTx, .numRx = numRx, .numESS = uint8_t(actualNumSTSPerChain - numTx), .numCSI = 1},
            .antSel = 0,
            .subcarrierOffset = subcarrierIndexOffset,
            .subcarrierIndices = getAllSubcarrierIndices(PacketFormatEnum::PacketFormat_HT, cbw),
            .CSIArray = parseQCA9300CSIData(buffer, actualNumSTSPerChain, numRx, numTones),
    };
    std::copy(buffer, buffer + bufferLength, std::back_inserter(csi.rawCSIData));

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

CSI CSI::fromIWLMVM(const uint8_t *buffer, uint32_t bufferLength, uint8_t numTx, uint8_t numRx, uint16_t numTones, PacketFormatEnum format, ChannelBandwidthEnum cbw, int16_t subcarrierIndexOffset, bool skipPilotSubcarriers) {
    if (numTx * numRx * numTones * 4 != bufferLength)
        throw std::runtime_error("Incorrect Intel MVM-based CSI data format.");

    auto totalTones = numRx * numTx * numTones, pos = 0;
    const auto &pilotArray = getPilotSubcarrierIndices(format, cbw);
    const auto &subcarrierIndices = skipPilotSubcarriers ? getDataSubcarrierIndices(format, cbw) : getAllSubcarrierIndices(format, cbw);
    std::vector<std::complex<double>> CSIArray;
    CSIArray.reserve(numTx * numRx * numTones);
    for (auto i = 0, ssI = 0, lastPilotIndex = 0; i < totalTones; i++) {
        auto real = *(int16_t *) (buffer + pos);
        auto imag = *(int16_t *) (buffer + pos + 2);
        pos += 4;

        if (skipPilotSubcarriers) {
            ssI = i % numTones;
            if (ssI == 0)
                lastPilotIndex = 0;
            if (ssI == pilotArray[lastPilotIndex]) {
                lastPilotIndex++;
                continue;
            }
        }

        CSIArray.emplace_back(std::complex<double>(real, imag));
    }

    if (CSIArray.size() != subcarrierIndices.size() * numTx * numRx)
        throw std::runtime_error("Fatal failure in MVM CSI data parsing...");

    auto CSIMatrix = SignalMatrix(CSIArray, std::vector<int32_t>{static_cast<int>(subcarrierIndices.size()), numTx, numRx}, SignalMatrixStorageMajority::ColumnMajor);

    auto csi = CSI{.deviceType = PicoScenesDeviceType::IWLMVM,
            .packetFormat = format,
            .cbw = cbw,
            .dimensions = CSIDimension{.numTones = static_cast<uint16_t>(subcarrierIndices.size()), .numTx = numTx, .numRx = numRx, .numESS = 0, .numCSI = 1},
            .antSel = 0,
            .subcarrierOffset = subcarrierIndexOffset,
            .subcarrierIndices = subcarrierIndices,
            .CSIArray = CSIMatrix
    };
    std::copy(buffer, buffer + bufferLength, std::back_inserter(csi.rawCSIData));

    if (subcarrierIndexOffset != 0) {
        std::transform(csi.subcarrierIndices.begin(), csi.subcarrierIndices.end(), csi.subcarrierIndices.begin(), [=](int16_t index) {
            return index + subcarrierIndexOffset;
        });
    }

    return csi;
}

const std::vector<int16_t> &CSI::getAllSubcarrierIndices(PacketFormatEnum format, ChannelBandwidthEnum cbw) {
    if (format == PacketFormatEnum::PacketFormat_HESU) {
        switch (cbw) {
            case ChannelBandwidthEnum::CBW_20:
                return HE20_242Subcarriers_Indices;
            case ChannelBandwidthEnum::CBW_40:
                return HE40_484Subcarriers_Indices;
            case ChannelBandwidthEnum::CBW_80:
                return HE80_996Subcarriers_Indices;
            case ChannelBandwidthEnum::CBW_160:
                return HE160_1992Subcarriers_Indices;
            default:
                throw std::runtime_error("Unsupported CBW for pilot index computation.");
        }
    }

    if (format == PacketFormatEnum::PacketFormat_VHT) {
        switch (cbw) {
            case ChannelBandwidthEnum::CBW_20:
                return HTVHT20_56Subcarriers_Indices;
            case ChannelBandwidthEnum::CBW_40:
                return HTVHT40_114Subcarriers_Indices;
            case ChannelBandwidthEnum::CBW_80:
                return VHT80_242Subcarriers_Indices;
            case ChannelBandwidthEnum::CBW_160:
                return VHT160_484Subcarriers_Indices;
            default:
                throw std::runtime_error("Unsupported CBW for pilot index computation.");
        }
    }

    if (format == PacketFormatEnum::PacketFormat_HT) {
        switch (cbw) {
            case ChannelBandwidthEnum::CBW_20:
                return HTVHT20_56Subcarriers_Indices;
            case ChannelBandwidthEnum::CBW_40:
                return HTVHT40_114Subcarriers_Indices;
            default:
                throw std::runtime_error("Unsupported CBW for pilot index computation.");
        }
    }

    if (format == PacketFormatEnum::PacketFormat_NonHT) {
        return NonHT20_52Subcarriers_Indices;
    }

    throw std::runtime_error("Unsupported CBW for index computation.");
}

const std::vector<int16_t> &CSI::getPilotSubcarrierIndices(PacketFormatEnum format, ChannelBandwidthEnum cbw) {
    if (format == PacketFormatEnum::PacketFormat_HESU) {
        switch (cbw) {
            case ChannelBandwidthEnum::CBW_20:
                return HE20_242Subcarriers_PilotIndices;
            case ChannelBandwidthEnum::CBW_40:
                return HE40_484Subcarriers_PilotIndices;
            case ChannelBandwidthEnum::CBW_80:
                return HE80_996Subcarriers_PilotIndices;
            case ChannelBandwidthEnum::CBW_160:
                return HE160_1992Subcarriers_PilotIndices;
            default:
                throw std::runtime_error("Unsupported CBW for pilot index computation.");
        }
    }

    if (format == PacketFormatEnum::PacketFormat_VHT) {
        switch (cbw) {
            case ChannelBandwidthEnum::CBW_20:
                return HTVHT20_56Subcarriers_PilotIndices;
            case ChannelBandwidthEnum::CBW_40:
                return HTVHT40_114Subcarriers_PilotIndices;
            case ChannelBandwidthEnum::CBW_80:
                return VHT80_242Subcarriers_PilotIndices;
            case ChannelBandwidthEnum::CBW_160:
                return VHT160_484Subcarriers_PilotIndices;
            default:
                throw std::runtime_error("Unsupported CBW for pilot index computation.");
        }
    }

    if (format == PacketFormatEnum::PacketFormat_HT) {
        switch (cbw) {
            case ChannelBandwidthEnum::CBW_20:
                return HTVHT20_56Subcarriers_PilotIndices;
            case ChannelBandwidthEnum::CBW_40:
                return HTVHT40_114Subcarriers_PilotIndices;
            default:
                throw std::runtime_error("Unsupported CBW for pilot index computation.");
        }
    }

    if (format == PacketFormatEnum::PacketFormat_NonHT) {
        return NonHT20_52Subcarriers_PilotIndices;
    }

    throw std::runtime_error("Unsupported CBW for pilot index computation.");
}

const std::vector<int16_t> &CSI::getDataSubcarrierIndices(PacketFormatEnum format, ChannelBandwidthEnum cbw) {
    if (format == PacketFormatEnum::PacketFormat_HESU) {
        switch (cbw) {
            case ChannelBandwidthEnum::CBW_20:
                return HE20_242Subcarriers_DataIndices;
            case ChannelBandwidthEnum::CBW_40:
                return HE40_484Subcarriers_DataIndices;
            case ChannelBandwidthEnum::CBW_80:
                return HE80_996Subcarriers_DataIndices;
            case ChannelBandwidthEnum::CBW_160:
                return HE160_1992Subcarriers_DataIndices;
            default:
                throw std::runtime_error("Unsupported CBW for pilot index computation.");
        }
    }

    if (format == PacketFormatEnum::PacketFormat_VHT) {
        switch (cbw) {
            case ChannelBandwidthEnum::CBW_20:
                return HTVHT20_56Subcarriers_DataIndices;
            case ChannelBandwidthEnum::CBW_40:
                return HTVHT40_114Subcarriers_DataIndices;
            case ChannelBandwidthEnum::CBW_80:
                return VHT80_242Subcarriers_DataIndices;
            case ChannelBandwidthEnum::CBW_160:
                return VHT160_484Subcarriers_DataIndices;
            default:
                throw std::runtime_error("Unsupported CBW for pilot index computation.");
        }
    }

    if (format == PacketFormatEnum::PacketFormat_HT) {
        switch (cbw) {
            case ChannelBandwidthEnum::CBW_20:
                return HTVHT20_56Subcarriers_DataIndices;
            case ChannelBandwidthEnum::CBW_40:
                return HTVHT40_114Subcarriers_DataIndices;
            default:
                throw std::runtime_error("Unsupported CBW for pilot index computation.");
        }
    }

    if (format == PacketFormatEnum::PacketFormat_NonHT) {
        return NonHT20_52Subcarriers_DataIndices;
    }

    throw std::runtime_error("Unsupported CBW for pilot index computation.");
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
    int16_t subcarrierIndexOffset = *(int16_t *) (buffer + pos);
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
    } else if (deviceType == PicoScenesDeviceType::IWLMVM) {
        auto csi = CSI::fromIWLMVM(buffer + pos, CSIBufferLength, numSTS, numRx, numTone, packetFormat, cbw, subcarrierIndexOffset, true);
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


std::vector<int16_t> CSI::NonHT20_52Subcarriers_Indices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>();
    for (auto i = -26; i <= -1; i++)
        indices.emplace_back(i);
    for (auto i = 1; i <= 26; i++)
        indices.emplace_back(i);

    return indices;
}();

std::vector<int16_t> CSI::HTVHT20_56Subcarriers_Indices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>();
    for (auto i = -28; i <= -1; i++)
        indices.emplace_back(i);
    for (auto i = 1; i <= 28; i++)
        indices.emplace_back(i);

    return indices;
}();

std::vector<int16_t> CSI::HTVHT40_114Subcarriers_Indices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>();
    for (auto i = -58; i <= -2; i++)
        indices.emplace_back(i);
    for (auto i = 2; i <= 58; i++)
        indices.emplace_back(i);
    return indices;
}();

std::vector<int16_t> CSI::VHT80_242Subcarriers_Indices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>();
    for (auto i = -122; i <= -2; i++)
        indices.emplace_back(i);
    for (auto i = 2; i <= 122; i++)
        indices.emplace_back(i);
    return indices;
}();

std::vector<int16_t> CSI::VHT160_484Subcarriers_Indices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>();
    for (auto i = -250; i <= -130; i++)
        indices.emplace_back(i);
    for (auto i = -126; i <= -6; i++)
        indices.emplace_back(i);
    for (auto i = 6; i <= 126; i++)
        indices.emplace_back(i);
    for (auto i = 130; i <= 250; i++)
        indices.emplace_back(i);
    return indices;
}();

std::vector<int16_t> CSI::HE20_242Subcarriers_Indices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>();
    for (auto i = -122; i <= -2; i++)
        indices.emplace_back(i);
    for (auto i = 2; i <= 122; i++)
        indices.emplace_back(i);
    return indices;
}();

std::vector<int16_t> CSI::HE40_484Subcarriers_Indices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>();
    for (auto i = -244; i <= -3; i++)
        indices.emplace_back(i);
    for (auto i = 3; i <= 244; i++)
        indices.emplace_back(i);
    return indices;
}();

std::vector<int16_t> CSI::HE80_996Subcarriers_Indices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>();
    for (auto i = -500; i <= -3; i++)
        indices.emplace_back(i);
    for (auto i = 3; i <= 500; i++)
        indices.emplace_back(i);
    return indices;
}();

std::vector<int16_t> CSI::HE160_1992Subcarriers_Indices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>();
    for (auto i = -1012; i <= -515; i++)
        indices.emplace_back(i);
    for (auto i = -509; i <= -12; i++)
        indices.emplace_back(i);
    for (auto i = 12; i <= 509; i++)
        indices.emplace_back(i);
    for (auto i = 515; i <= 1012; i++)
        indices.emplace_back(i);
    return indices;
}();


std::vector<int16_t> CSI::NonHT20_52Subcarriers_DataIndices = []() noexcept -> std::vector<int16_t> {
    return std::vector<int16_t>{-26, -25, -24, -23, -22, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10, -9, -8, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26};
}();

std::vector<int16_t> CSI::HTVHT20_56Subcarriers_DataIndices = []() noexcept -> std::vector<int16_t> {
    return std::vector<int16_t>{-28, -27, -26, -25, -24, -23, -22, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10, -9, -8, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26, 27, 28};
}();

std::vector<int16_t> CSI::HTVHT40_114Subcarriers_DataIndices = []() noexcept -> std::vector<int16_t> {
    return std::vector<int16_t>{-58, -57, -56, -55, -54, -52, -51, -50, -49, -48, -47, -46, -45, -44, -43, -42, -41, -40, -39, -38, -37, -36, -35, -34, -33, -32, -31, -30, -29, -28, -27, -26, -24, -23, -22, -21, -20, -19, -18, -17, -16, -15, -14, -13, -12, -10, -9, -8, -7, -6, -5, -4, -3, -2, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 54, 55, 56, 57,
                                58};
}();

std::vector<int16_t> CSI::VHT80_242Subcarriers_DataIndices = []() noexcept -> std::vector<int16_t> {
    return std::vector<int16_t>{-122, -121, -120, -119, -118, -117, -116, -115, -114, -113, -112, -111, -110, -109, -108, -107, -106, -105, -104, -102, -101, -100, -99, -98, -97, -96, -95, -94, -93, -92, -91, -90, -89, -88, -87, -86, -85, -84, -83, -82, -81, -80, -79, -78, -77, -76, -74, -73, -72, -71, -70, -69, -68, -67, -66, -65, -64, -63, -62, -61, -60, -59, -58, -57, -56, -55, -54, -53, -52, -51, -50, -49, -48, -47, -46, -45, -44, -43, -42, -41, -40, -38, -37, -36, -35, -34, -33, -32, -31,
                                -30, -29, -28, -27, -26, -25, -24, -23, -22, -21, -20, -19, -18, -17, -16, -15, -14, -13, -12, -10, -9, -8, -7, -6, -5, -4, -3, -2, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
                                91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122};
}();

std::vector<int16_t> CSI::VHT160_484Subcarriers_DataIndices = []() noexcept -> std::vector<int16_t> {
    return std::vector<int16_t>{-250, -249, -248, -247, -246, -245, -244, -243, -242, -241, -240, -239, -238, -237, -236, -235, -234, -233, -232, -230, -229, -228, -227, -226, -225, -224, -223, -222, -221, -220, -219, -218, -217, -216, -215, -214, -213, -212, -211, -210, -209, -208, -207, -206, -205, -204, -202, -201, -200, -199, -198, -197, -196, -195, -194, -193, -192, -191, -190, -189, -188, -187, -186, -185, -184, -183, -182, -181, -180, -179, -178, -177, -176, -175, -174, -173, -172, -171,
                                -170, -169, -168, -166, -165, -164, -163, -162, -161, -160, -159, -158, -157, -156, -155, -154, -153, -152, -151, -150, -149, -148, -147, -146, -145, -144, -143, -142, -141, -140, -138, -137, -136, -135, -134, -133, -132, -131, -130, -126, -125, -124, -123, -122, -121, -120, -119, -118, -116, -115, -114, -113, -112, -111, -110, -109, -108, -107, -106, -105, -104, -103, -102, -101, -100, -99, -98, -97, -96, -95, -94, -93, -92, -91, -90, -88, -87, -86, -85, -84,
                                -83, -82, -81, -80, -79, -78, -77, -76, -75, -74, -73, -72, -71, -70, -69, -68, -67, -66, -65, -64, -63, -62, -61, -60, -59, -58, -57, -56, -55, -54, -52, -51, -50, -49, -48, -47, -46, -45, -44, -43, -42, -41, -40, -39, -38, -37, -36, -35, -34, -33, -32, -31, -30, -29, -28, -27, -26, -24, -23, -22, -21, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10, -9, -8, -7, -6, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 28, 29, 30,
                                31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 118, 119, 120, 121, 122, 123, 124, 125, 126, 130, 131, 132, 133, 134, 135, 136, 137, 138, 140, 141, 142, 143, 144,
                                145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 232, 233, 234, 235, 236, 237, 238, 239, 240,
                                241, 242, 243, 244, 245, 246, 247, 248, 249, 250};
}();

std::vector<int16_t> CSI::HE20_242Subcarriers_DataIndices = []() noexcept -> std::vector<int16_t> {
    return std::vector<int16_t>{-122, -121, -120, -119, -118, -117, -115, -114, -113, -112, -111, -110, -109, -108, -107, -106, -105, -104, -103, -102, -101, -100, -99, -98, -97, -96, -95, -94, -93, -92, -91, -89, -88, -87, -86, -85, -84, -83, -82, -81, -80, -79, -78, -77, -76, -75, -74, -73, -72, -71, -70, -69, -68, -67, -66, -65, -64, -63, -62, -61, -60, -59, -58, -57, -56, -55, -54, -53, -52, -51, -50, -49, -47, -46, -45, -44, -43, -42, -41, -40, -39, -38, -37, -36, -35, -34, -33, -32, -31,
                                -30, -29, -28, -27, -26, -25, -24, -23, -21, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
                                91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 117, 118, 119, 120, 121, 122};
}();

std::vector<int16_t> CSI::HE40_484Subcarriers_DataIndices = []() noexcept -> std::vector<int16_t> {
    return std::vector<int16_t>{-244, -243, -242, -241, -240, -239, -237, -236, -235, -234, -233, -232, -231, -230, -229, -228, -227, -226, -225, -224, -223, -222, -221, -220, -219, -218, -217, -216, -215, -214, -213, -211, -210, -209, -208, -207, -206, -205, -204, -203, -202, -201, -200, -199, -198, -197, -196, -195, -194, -193, -192, -191, -190, -189, -188, -187, -186, -185, -184, -183, -182, -181, -180, -179, -178, -177, -176, -175, -174, -173, -172, -171, -169, -168, -167, -166, -165, -164,
                                -163, -162, -161, -160, -159, -158, -157, -156, -155, -154, -153, -152, -151, -150, -149, -148, -147, -146, -145, -143, -142, -141, -140, -139, -138, -137, -136, -135, -134, -133, -132, -131, -130, -129, -128, -127, -126, -125, -124, -123, -122, -121, -120, -119, -118, -117, -116, -115, -114, -113, -112, -111, -110, -109, -108, -107, -106, -105, -103, -102, -101, -100, -99, -98, -97, -96, -95, -94, -93, -92, -91, -90, -89, -88, -87, -86, -85, -84, -83, -82, -81,
                                -80, -79, -77, -76, -75, -74, -73, -72, -71, -70, -69, -68, -67, -66, -65, -64, -63, -62, -61, -60, -59, -58, -57, -56, -55, -54, -53, -52, -51, -50, -49, -48, -47, -46, -45, -44, -43, -42, -41, -40, -39, -38, -37, -35, -34, -33, -32, -31, -30, -29, -28, -27, -26, -25, -24, -23, -22, -21, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -9, -8, -7, -6, -5, -4, -3, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                                31, 32, 33, 34, 35, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140,
                                141, 142, 143, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236,
                                237, 239, 240, 241, 242, 243, 244};
}();

std::vector<int16_t> CSI::HE80_996Subcarriers_DataIndices = []() noexcept -> std::vector<int16_t> {
    return std::vector<int16_t>{-500, -499, -498, -497, -496, -495, -494, -493, -492, -491, -490, -489, -488, -487, -486, -485, -484, -483, -482, -481, -480, -479, -478, -477, -476, -475, -474, -473, -472, -471, -470, -469, -467, -466, -465, -464, -463, -462, -461, -460, -459, -458, -457, -456, -455, -454, -453, -452, -451, -450, -449, -448, -447, -446, -445, -444, -443, -442, -441, -440, -439, -438, -437, -436, -435, -434, -433, -432, -431, -430, -429, -428, -427, -426, -425, -424, -423, -422,
                                -421, -420, -419, -418, -417, -416, -415, -414, -413, -412, -411, -410, -409, -408, -407, -406, -405, -404, -403, -402, -401, -399, -398, -397, -396, -395, -394, -393, -392, -391, -390, -389, -388, -387, -386, -385, -384, -383, -382, -381, -380, -379, -378, -377, -376, -375, -374, -373, -372, -371, -370, -369, -368, -367, -366, -365, -364, -363, -362, -361, -360, -359, -358, -357, -356, -355, -354, -353, -352, -351, -350, -349, -348, -347, -346, -345, -344, -343,
                                -342, -341, -340, -339, -338, -337, -336, -335, -333, -332, -331, -330, -329, -328, -327, -326, -325, -324, -323, -322, -321, -320, -319, -318, -317, -316, -315, -314, -313, -312, -311, -310, -309, -308, -307, -306, -305, -304, -303, -302, -301, -300, -299, -298, -297, -296, -295, -294, -293, -292, -291, -290, -289, -288, -287, -286, -285, -284, -283, -282, -281, -280, -279, -278, -277, -276, -275, -274, -273, -272, -271, -270, -269, -268, -267, -265, -264, -263,
                                -262, -261, -260, -259, -258, -257, -256, -255, -254, -253, -252, -251, -250, -249, -248, -247, -246, -245, -244, -243, -242, -241, -240, -239, -238, -237, -236, -235, -234, -233, -232, -231, -230, -229, -228, -227, -225, -224, -223, -222, -221, -220, -219, -218, -217, -216, -215, -214, -213, -212, -211, -210, -209, -208, -207, -206, -205, -204, -203, -202, -201, -200, -199, -198, -197, -196, -195, -194, -193, -192, -191, -190, -189, -188, -187, -186, -185, -184,
                                -183, -182, -181, -180, -179, -178, -177, -176, -175, -174, -173, -172, -171, -170, -169, -168, -167, -166, -165, -164, -163, -162, -161, -160, -159, -157, -156, -155, -154, -153, -152, -151, -150, -149, -148, -147, -146, -145, -144, -143, -142, -141, -140, -139, -138, -137, -136, -135, -134, -133, -132, -131, -130, -129, -128, -127, -126, -125, -124, -123, -122, -121, -120, -119, -118, -117, -116, -115, -114, -113, -112, -111, -110, -109, -108, -107, -106, -105,
                                -104, -103, -102, -101, -100, -99, -98, -97, -96, -95, -94, -93, -91, -90, -89, -88, -87, -86, -85, -84, -83, -82, -81, -80, -79, -78, -77, -76, -75, -74, -73, -72, -71, -70, -69, -68, -67, -66, -65, -64, -63, -62, -61, -60, -59, -58, -57, -56, -55, -54, -53, -52, -51, -50, -49, -48, -47, -46, -45, -44, -43, -42, -41, -40, -39, -38, -37, -36, -35, -34, -33, -32, -31, -30, -29, -28, -27, -26, -25, -23, -22, -21, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11,
                                -10, -9, -8, -7, -6, -5, -4, -3, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
                                112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205,
                                206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300,
                                301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394,
                                395, 396, 397, 398, 399, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489,
                                490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500};
}();

std::vector<int16_t> CSI::HE160_1992Subcarriers_DataIndices = []() noexcept -> std::vector<int16_t> {
    return std::vector<int16_t>{-1012, -1011, -1010, -1009, -1008, -1007, -1006, -1005, -1004, -1003, -1002, -1001, -1000, -999, -998, -997, -996, -995, -994, -993, -992, -991, -990, -989, -988, -987, -986, -985, -984, -983, -982, -981, -979, -978, -977, -976, -975, -974, -973, -972, -971, -970, -969, -968, -967, -966, -965, -964, -963, -962, -961, -960, -959, -958, -957, -956, -955, -954, -953, -952, -951, -950, -949, -948, -947, -946, -945, -944, -943, -942, -941, -940, -939, -938, -937, -936,
                                -935, -934, -933, -932, -931, -930, -929, -928, -927, -926, -925, -924, -923, -922, -921, -920, -919, -918, -917, -916, -915, -914, -913, -911, -910, -909, -908, -907, -906, -905, -904, -903, -902, -901, -900, -899, -898, -897, -896, -895, -894, -893, -892, -891, -890, -889, -888, -887, -886, -885, -884, -883, -882, -881, -880, -879, -878, -877, -876, -875, -874, -873, -872, -871, -870, -869, -868, -867, -866, -865, -864, -863, -862, -861, -860, -859, -858, -857,
                                -856, -855, -854, -853, -852, -851, -850, -849, -848, -847, -845, -844, -843, -842, -841, -840, -839, -838, -837, -836, -835, -834, -833, -832, -831, -830, -829, -828, -827, -826, -825, -824, -823, -822, -821, -820, -819, -818, -817, -816, -815, -814, -813, -812, -811, -810, -809, -808, -807, -806, -805, -804, -803, -802, -801, -800, -799, -798, -797, -796, -795, -794, -793, -792, -791, -790, -789, -788, -787, -786, -785, -784, -783, -782, -781, -780, -779, -777,
                                -776, -775, -774, -773, -772, -771, -770, -769, -768, -767, -766, -765, -764, -763, -762, -761, -760, -759, -758, -757, -756, -755, -754, -753, -752, -751, -750, -749, -748, -747, -746, -745, -744, -743, -742, -741, -740, -739, -737, -736, -735, -734, -733, -732, -731, -730, -729, -728, -727, -726, -725, -724, -723, -722, -721, -720, -719, -718, -717, -716, -715, -714, -713, -712, -711, -710, -709, -708, -707, -706, -705, -704, -703, -702, -701, -700, -699, -698,
                                -697, -696, -695, -694, -693, -692, -691, -690, -689, -688, -687, -686, -685, -684, -683, -682, -681, -680, -679, -678, -677, -676, -675, -674, -673, -672, -671, -669, -668, -667, -666, -665, -664, -663, -662, -661, -660, -659, -658, -657, -656, -655, -654, -653, -652, -651, -650, -649, -648, -647, -646, -645, -644, -643, -642, -641, -640, -639, -638, -637, -636, -635, -634, -633, -632, -631, -630, -629, -628, -627, -626, -625, -624, -623, -622, -621, -620, -619,
                                -618, -617, -616, -615, -614, -613, -612, -611, -610, -609, -608, -607, -606, -605, -603, -602, -601, -600, -599, -598, -597, -596, -595, -594, -593, -592, -591, -590, -589, -588, -587, -586, -585, -584, -583, -582, -581, -580, -579, -578, -577, -576, -575, -574, -573, -572, -571, -570, -569, -568, -567, -566, -565, -564, -563, -562, -561, -560, -559, -558, -557, -556, -555, -554, -553, -552, -551, -550, -549, -548, -547, -546, -545, -544, -543, -542, -541, -540,
                                -539, -538, -537, -535, -534, -533, -532, -531, -530, -529, -528, -527, -526, -525, -524, -523, -522, -521, -520, -519, -518, -517, -516, -515, -509, -508, -507, -506, -505, -504, -503, -502, -501, -500, -499, -498, -497, -496, -495, -494, -493, -492, -491, -490, -489, -487, -486, -485, -484, -483, -482, -481, -480, -479, -478, -477, -476, -475, -474, -473, -472, -471, -470, -469, -468, -467, -466, -465, -464, -463, -462, -461, -460, -459, -458, -457, -456, -455,
                                -454, -453, -452, -451, -450, -449, -448, -447, -446, -445, -444, -443, -442, -441, -440, -439, -438, -437, -436, -435, -434, -433, -432, -431, -430, -429, -428, -427, -426, -425, -424, -423, -422, -421, -419, -418, -417, -416, -415, -414, -413, -412, -411, -410, -409, -408, -407, -406, -405, -404, -403, -402, -401, -400, -399, -398, -397, -396, -395, -394, -393, -392, -391, -390, -389, -388, -387, -386, -385, -384, -383, -382, -381, -380, -379, -378, -377, -376,
                                -375, -374, -373, -372, -371, -370, -369, -368, -367, -366, -365, -364, -363, -362, -361, -360, -359, -358, -357, -356, -355, -353, -352, -351, -350, -349, -348, -347, -346, -345, -344, -343, -342, -341, -340, -339, -338, -337, -336, -335, -334, -333, -332, -331, -330, -329, -328, -327, -326, -325, -324, -323, -322, -321, -320, -319, -318, -317, -316, -315, -314, -313, -312, -311, -310, -309, -308, -307, -306, -305, -304, -303, -302, -301, -300, -299, -298, -297,
                                -296, -295, -294, -293, -292, -291, -290, -289, -288, -287, -285, -284, -283, -282, -281, -280, -279, -278, -277, -276, -275, -274, -273, -272, -271, -270, -269, -268, -267, -266, -265, -264, -263, -262, -261, -260, -259, -258, -257, -256, -255, -254, -253, -252, -251, -250, -249, -248, -247, -245, -244, -243, -242, -241, -240, -239, -238, -237, -236, -235, -234, -233, -232, -231, -230, -229, -228, -227, -226, -225, -224, -223, -222, -221, -220, -219, -218, -217,
                                -216, -215, -214, -213, -212, -211, -210, -209, -208, -207, -206, -205, -204, -203, -202, -201, -200, -199, -198, -197, -196, -195, -194, -193, -192, -191, -190, -189, -188, -187, -186, -185, -184, -183, -182, -181, -180, -179, -177, -176, -175, -174, -173, -172, -171, -170, -169, -168, -167, -166, -165, -164, -163, -162, -161, -160, -159, -158, -157, -156, -155, -154, -153, -152, -151, -150, -149, -148, -147, -146, -145, -144, -143, -142, -141, -140, -139, -138,
                                -137, -136, -135, -134, -133, -132, -131, -130, -129, -128, -127, -126, -125, -124, -123, -122, -121, -120, -119, -118, -117, -116, -115, -114, -113, -111, -110, -109, -108, -107, -106, -105, -104, -103, -102, -101, -100, -99, -98, -97, -96, -95, -94, -93, -92, -91, -90, -89, -88, -87, -86, -85, -84, -83, -82, -81, -80, -79, -78, -77, -76, -75, -74, -73, -72, -71, -70, -69, -68, -67, -66, -65, -64, -63, -62, -61, -60, -59, -58, -57, -56, -55, -54, -53, -52, -51,
                                -50, -49, -48, -47, -46, -45, -43, -42, -41, -40, -39, -38, -37, -36, -35, -34, -33, -32, -31, -30, -29, -28, -27, -26, -25, -24, -23, -22, -21, -20, -19, -18, -17, -16, -15, -14, -13, -12, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81,
                                82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 179, 180,
                                181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274,
                                275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369,
                                370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463,
                                464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563,
                                564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 655, 656, 657,
                                658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 739, 740, 741, 742, 743, 744, 745, 746, 747, 748, 749, 750, 751, 752,
                                753, 754, 755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790, 791, 792, 793, 794, 795, 796, 797, 798, 799, 800, 801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 813, 814, 815, 816, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828, 829, 830, 831, 832, 833, 834, 835, 836, 837, 838, 839, 840, 841, 842, 843, 844, 845, 847,
                                848, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 874, 875, 876, 877, 878, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 909, 910, 911, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941,
                                942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977, 978, 979, 981, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012};
}();

std::vector<int16_t> CSI::NonHT20_52Subcarriers_PilotIndices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>{5, 19, 32, 46};
    return indices;
}();

std::vector<int16_t> CSI::HTVHT20_56Subcarriers_PilotIndices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>{7, 21, 34, 48};
    return indices;
}();

std::vector<int16_t> CSI::HTVHT40_114Subcarriers_PilotIndices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>{5, 33, 47, 66, 80, 108};
    return indices;
}();

std::vector<int16_t> CSI::VHT80_242Subcarriers_PilotIndices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>{19, 47, 83, 111, 130, 158, 194, 222};
    return indices;
}();

std::vector<int16_t> CSI::VHT160_484Subcarriers_PilotIndices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>{19, 47, 83, 111, 130, 158, 194, 222, 261, 289, 325, 353, 372, 400, 436, 464};
    return indices;
}();

std::vector<int16_t> CSI::HE20_242Subcarriers_PilotIndices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>{6, 32, 74, 100, 141, 167, 209, 235};
    return indices;
}();

std::vector<int16_t> CSI::HE40_484Subcarriers_PilotIndices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>{6, 32, 74, 100, 140, 166, 208, 234, 249, 275, 317, 343, 383, 409, 451, 477};
    return indices;
}();

std::vector<int16_t> CSI::HE80_996Subcarriers_PilotIndices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>{32, 100, 166, 234, 274, 342, 408, 476, 519, 587, 653, 721, 761, 829, 895, 963};
    return indices;
}();

std::vector<int16_t> CSI::HE160_1992Subcarriers_PilotIndices = []() noexcept -> std::vector<int16_t> {
    auto indices = std::vector<int16_t>{32, 100, 166, 234, 274, 342, 408, 476, 519, 587, 653, 721, 761, 829, 895, 963, 1028, 1096, 1162, 1230, 1270, 1338, 1404, 1472, 1515, 1583, 1649, 1717, 1757, 1825, 1891, 1959};
    return indices;
}();

std::vector<int16_t> CSI::IWL5300SubcarrierIndices_CBW20 = []() noexcept -> std::vector<int16_t> {
    return std::vector<int16_t>{-28, -26, -24, -22, -20, -18, -16, -14, -12, -10, -8, -6, -4, -2, -1, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 28};
}();

std::vector<int16_t> CSI::IWL5300SubcarrierIndices_CBW40 = []() noexcept -> std::vector<int16_t> {
    return std::vector<int16_t>{-58, -54, -50, -46, -42, -38, -34, -30, -26, -22, -18, -14, -10, -6, -2, 2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 50, 54, 58};
}();

