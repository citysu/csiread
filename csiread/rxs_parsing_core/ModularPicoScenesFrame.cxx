//
// Created by 蒋志平 on 2020/11/6.
//

#include "ModularPicoScenesFrame.hxx"
#include <random>
#include <iomanip>


std::string ieee80211_mac_frame_header::toString() const {
    std::stringstream ss;
    ss << "MACHeader:[dest[4-6]=" << std::nouppercase << std::setfill('0') << std::setw(2) << std::right << std::hex << int(addr1[3]) << ":" << int(addr1[4]) << ":" << int(addr1[5]) << ", ";
    ss << "src[4-6]=" << std::nouppercase << std::setfill('0') << std::setw(2) << std::right << std::hex << int(addr2[3]) << ":" << int(addr2[4]) << ":" << int(addr2[5]) << ", ";
    ss << "seq=" << std::dec << seq << ", frag=" << frag << ", ";
    ss << "mfrags=" << std::to_string(fc.moreFrags) << "]";
    return ss.str();
}

std::ostream &operator<<(std::ostream &os, const ieee80211_mac_frame_header &header) {
    os << header.toString();
    return os;
}

std::optional<PicoScenesFrameHeader> PicoScenesFrameHeader::fromBuffer(const uint8_t *buffer) {
    auto magicValue = *((uint32_t *) (buffer));
    if (magicValue == 0x20150315) {
        auto frameHeader = *((PicoScenesFrameHeader *) (buffer));
        return frameHeader;
    }
    return std::nullopt;
}

std::string PicoScenesFrameHeader::toString() const {
    std::stringstream ss;
    ss << "PSFHeader:[ver=0x" << std::hex << version << std::dec << ", device=" << deviceType << ", numSegs=" << int(numSegments) << ", type=" << int(frameType) << ", taskId=" << int(taskId) << ", txId=" << int(txId) << "]";
    return ss.str();
}

std::ostream &operator<<(std::ostream &os, const PicoScenesFrameHeader &frameHeader) {
    os << frameHeader.toString();
    return os;
}

std::optional<ModularPicoScenesRxFrame> ModularPicoScenesRxFrame::fromBuffer(const uint8_t *buffer, uint32_t bufferLength, bool interpolateCSI) {
    uint32_t pos = 0;
    auto rxFrameHeader = *(ModularPicoScenesRxFrameHeader *) buffer;
    if (rxFrameHeader.frameLength + 4 != bufferLength ||
        rxFrameHeader.magicWord != 0x20150315 ||
        rxFrameHeader.frameVersion != 0x1U) {
        return {};
    }
    pos += sizeof(ModularPicoScenesRxFrameHeader);

    auto frame = ModularPicoScenesRxFrame();
    frame.rxFrameHeader = rxFrameHeader;
    for (auto i = 0; i < frame.rxFrameHeader.numRxSegments; i++) {
        auto[segmentName, segmentLength, versionId, offset] = AbstractPicoScenesFrameSegment::extractSegmentMetaData(buffer + pos, bufferLength - pos);
        if (segmentName == "RxSBasic") {
            frame.rxSBasicSegment.fromBuffer(buffer + pos, segmentLength + 4);
        } else if (segmentName == "ExtraInfo") {
            frame.rxExtraInfoSegment.fromBuffer(buffer + pos, segmentLength + 4);
        } else if (segmentName == "CSI") {
            frame.csiSegment.fromBuffer(buffer + pos, segmentLength + 4);
            if (interpolateCSI) {
                frame.csiSegment.getCSI().interpolateCSI();
            }
        } else if (segmentName == "PilotCSI") {
            frame.pilotCSISegment = CSISegment::createByBuffer(buffer + pos, segmentLength + 4);
        } else if (segmentName == "LegacyCSI") {
            frame.legacyCSISegment = CSISegment::createByBuffer(buffer + pos, segmentLength + 4);
            if (interpolateCSI) {
                frame.legacyCSISegment->getCSI().interpolateCSI();
            }
        } else if (segmentName == "BasebandSignal") {
            frame.basebandSignalSegment = BasebandSignalSegment::createByBuffer(buffer + pos, segmentLength + 4);
        } else if (segmentName == "PreEQSymbols") {
            frame.preEQSymbolsSegment = PreEQSymbolsSegment::createByBuffer(buffer + pos, segmentLength + 4);
        } else {
            frame.rxUnknownSegmentMap.emplace(segmentName, Uint8Vector(buffer + pos, buffer + pos + segmentLength + 4));
        }
        pos += (segmentLength + 4);
    }

    auto mpduPos = pos;
    frame.standardHeader = *((ieee80211_mac_frame_header *) (buffer + pos));
    pos += sizeof(ieee80211_mac_frame_header);

    if (auto PSHeader = PicoScenesFrameHeader::fromBuffer(buffer + pos)) {
        frame.PicoScenesHeader = PSHeader;
        pos += sizeof(PicoScenesFrameHeader);

        for (auto i = 0; i < frame.PicoScenesHeader->numSegments; i++) {
            auto[segmentName, segmentLength, versionId, offset] = AbstractPicoScenesFrameSegment::extractSegmentMetaData(buffer + pos, bufferLength);
            if (segmentName == "ExtraInfo") {
                frame.txExtraInfoSegment = ExtraInfoSegment::createByBuffer(buffer + pos, segmentLength + 4);
            } else if (segmentName == "Payload") {
                frame.payloadSegments.emplace_back(PayloadSegment::createByBuffer(buffer + pos, segmentLength + 4));
            } else {
                frame.txUnknownSegmentMap.emplace(segmentName, Uint8Vector(buffer + pos, buffer + pos + segmentLength + 4));
            }
            pos += segmentLength + 4;
        }
    }

    std::copy(buffer, buffer + bufferLength, std::back_inserter(frame.rawBuffer));
    std::copy(buffer + mpduPos, buffer + bufferLength, std::back_inserter(frame.mpdu));

    return frame;
}

std::string ModularPicoScenesRxFrame::toString() const {
    std::stringstream ss;
    ss << "RxFrame:{";
    ss << rxSBasicSegment.getBasic();
    ss << ", " << rxExtraInfoSegment.getExtraInfo();
    ss << ", Rx" << csiSegment;
    if (pilotCSISegment)
        ss << ", " << *pilotCSISegment;
    if (legacyCSISegment)
        ss << ", " << *legacyCSISegment;
    if (basebandSignalSegment)
        ss << ", " << *basebandSignalSegment;
    if (preEQSymbolsSegment)
        ss << ", " << *preEQSymbolsSegment;
    if (!rxUnknownSegmentMap.empty()) {
        std::stringstream segss;
        segss << "RxSegments:(";
        for (const auto &segment: rxUnknownSegmentMap) {
            segss << segment.first << ":" << segment.second.size() << "B, ";
        }
        auto temp = segss.str();
        temp.erase(temp.end() - 2, temp.end());
        temp.append(")");
        ss << ", " << temp;
    }

    ss << ", " << standardHeader;
    if (PicoScenesHeader)
        ss << ", " << *PicoScenesHeader;
    if (txExtraInfoSegment)
        ss << ", " << txExtraInfoSegment->getExtraInfo();
    if (!payloadSegments.empty()) {
        std::stringstream segss;
        segss << "Payloads:(";
        for (const auto &segment: payloadSegments) {
            segss << segment << ", ";
        }
        auto temp = segss.str();
        temp.erase(temp.end() - 2, temp.end());
        temp.append(")");
        ss << ", " << temp;
    }
    if (!txUnknownSegmentMap.empty()) {
        std::stringstream segss;
        segss << "TxSegments:(";
        for (const auto &segment: txUnknownSegmentMap) {
            segss << segment.first << ":" << segment.second.size() << "B, ";
        }
        auto temp = segss.str();
        temp.erase(temp.end() - 2, temp.end());
        temp.append(")");
        ss << ", " << temp;
    }
    ss << ", MPDU=" << mpdu.size() << "B";
    ss << "}";
    return ss.str();
}

std::optional<ModularPicoScenesRxFrame> ModularPicoScenesRxFrame::concatenateFragmentedPicoScenesRxFrames(const std::vector<ModularPicoScenesRxFrame> &frameQueue) {
    return std::optional<ModularPicoScenesRxFrame>();
}

bool ModularPicoScenesRxFrame::operator==(const ModularPicoScenesRxFrame &rhs) const {
    return false;
}

Uint8Vector ModularPicoScenesRxFrame::toBuffer() const {
    if (!rawBuffer.empty())
        return rawBuffer;

    // Rx segments
    Uint8Vector rxSegmentBuffer;
    auto modularFrameHeader = ModularPicoScenesRxFrameHeader().initialize2Default();
    modularFrameHeader.numRxSegments = 3;
    auto rxsBasicBuffer = rxSBasicSegment.toBuffer();
    auto rxsExtraInfoBuffer = rxExtraInfoSegment.toBuffer();
    auto csiBuffer = csiSegment.toBuffer();
    std::copy(rxsBasicBuffer.cbegin(), rxsBasicBuffer.cend(), std::back_inserter(rxSegmentBuffer));
    std::copy(rxsExtraInfoBuffer.cbegin(), rxsExtraInfoBuffer.cend(), std::back_inserter(rxSegmentBuffer));
    std::copy(csiBuffer.cbegin(), csiBuffer.cend(), std::back_inserter(rxSegmentBuffer));
    if (pilotCSISegment) {
        auto pilotCSIBuffer = pilotCSISegment->toBuffer();
        std::copy(pilotCSIBuffer.cbegin(), pilotCSIBuffer.cend(), std::back_inserter(rxSegmentBuffer));
        modularFrameHeader.numRxSegments++;
    }
    if (legacyCSISegment) {
        auto legacyCSIBuffer = legacyCSISegment->toBuffer();
        std::copy(legacyCSIBuffer.cbegin(), legacyCSIBuffer.cend(), std::back_inserter(rxSegmentBuffer));
        modularFrameHeader.numRxSegments++;
    }
    if (basebandSignalSegment) {
        auto segmentBuffer = basebandSignalSegment->toBuffer();
        std::copy(segmentBuffer.cbegin(), segmentBuffer.cend(), std::back_inserter(rxSegmentBuffer));
        modularFrameHeader.numRxSegments++;
    }
    if (preEQSymbolsSegment) {
        auto segmentBuffer = preEQSymbolsSegment->toBuffer();
        std::copy(segmentBuffer.cbegin(), segmentBuffer.cend(), std::back_inserter(rxSegmentBuffer));
        modularFrameHeader.numRxSegments++;
    }

    // Assembly the full buffer
    Uint8Vector frameBuffer;
    modularFrameHeader.frameLength = sizeof(modularFrameHeader) + rxSegmentBuffer.size() + mpdu.size() - 4;
    std::copy((uint8_t *) &modularFrameHeader, (uint8_t *) &modularFrameHeader + sizeof(ModularPicoScenesRxFrameHeader), std::back_inserter(frameBuffer));
    std::copy(rxSegmentBuffer.cbegin(), rxSegmentBuffer.cend(), std::back_inserter(frameBuffer));
    std::copy(mpdu.cbegin(), mpdu.cend(), std::back_inserter(frameBuffer));
    //// for in-situ validation
//    {
//        auto recovered = ModularPicoScenesRxFrame::fromBuffer(frameBuffer.data(), frameBuffer.size());
//        std::cout<< *recovered <<std::endl;
//    }

    return frameBuffer;
}

std::ostream &operator<<(std::ostream &os, const ModularPicoScenesRxFrame &rxframe) {
    os << rxframe.toString();
    return os;
}

void ModularPicoScenesTxFrame::addSegments(const std::shared_ptr<AbstractPicoScenesFrameSegment> &segment) {
    segments.emplace_back(segment);
    if (!frameHeader)
        frameHeader = PicoScenesFrameHeader();
    frameHeader->numSegments = segments.size();
}

uint32_t ModularPicoScenesTxFrame::totalLength() const {
    uint32_t length = sizeof(decltype(standardHeader)) + (frameHeader ? sizeof(decltype(frameHeader)) : 4); // plus 4 is to avoid NDP skip on QCA9300
    for (const auto &segment : segments) {
        length += segment->totalLength() + 4;
    }
    return length;
}

Uint8Vector ModularPicoScenesTxFrame::toBuffer() const {
    auto bufferLength = totalLength();
    Uint8Vector buffer(bufferLength);
    toBuffer(&buffer[0], bufferLength);
    return buffer;
}

int ModularPicoScenesTxFrame::toBuffer(uint8_t *buffer, uint32_t bufferLength) const {
    if (bufferLength < totalLength())
        throw std::overflow_error("Buffer not long enough for TX frame dumping...");

    memset(buffer, 0, bufferLength);
    memcpy(buffer, &standardHeader, sizeof(ieee80211_mac_frame_header));
    uint32_t pos = sizeof(ieee80211_mac_frame_header);
    if (frameHeader) {
        if (frameHeader->numSegments != segments.size())
            throw std::overflow_error("ModularPicoScenesTxFrame toBuffer method segment number in-consistent!");

        memcpy(buffer + sizeof(ieee80211_mac_frame_header), &frameHeader, sizeof(PicoScenesFrameHeader));
        pos += sizeof(PicoScenesFrameHeader);
        for (const auto &segment : segments) {
            segment->toBuffer(true, buffer + pos);
            pos += segment->totalLength() + 4;
        }
    }

    return pos;
}


void ModularPicoScenesTxFrame::reset() {
    standardHeader = ieee80211_mac_frame_header();
    frameHeader = PicoScenesFrameHeader();
    txParameters = PicoScenesFrameTxParameters();
    segments.clear();
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setMoreFrags() {
    standardHeader.fc.moreFrags = 1;
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setFragNumber(uint8_t fragNumber) {
    standardHeader.frag = fragNumber;
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setRetry() {
    standardHeader.fc.retry = 1;
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setDeviceType(PicoScenesDeviceType deviceType) {
    if (!frameHeader)
        frameHeader = PicoScenesFrameHeader();
    frameHeader->deviceType = deviceType;
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setTaskId(uint16_t taskId) {
    if (!frameHeader)
        frameHeader = PicoScenesFrameHeader();
    frameHeader->taskId = taskId;
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setTxId(uint16_t txId) {
    if (!frameHeader)
        frameHeader = PicoScenesFrameHeader();
    frameHeader->txId = txId;
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setRandomTaskId() {
    static std::random_device r;
    static std::default_random_engine randomEngine(r());
    static std::uniform_int_distribution<uint16_t> randomGenerator(10000, UINT16_MAX);
    auto newValue = randomGenerator(randomEngine);
    setTaskId(newValue);
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setPicoScenesFrameType(uint8_t frameType) {
    if (!frameHeader)
        frameHeader = PicoScenesFrameHeader();
    frameHeader->frameType = frameType;
    return *this;
}

[[maybe_unused]] ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setFrameFormat(PacketFormatEnum format) {
    txParameters.frameType = format;
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setChannelBandwidth(const ChannelBandwidthEnum &cbw) {
    txParameters.cbw = cbw;
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setGuardInterval(GuardIntervalEnum guardInterval) {
    txParameters.guardInterval = guardInterval;
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setMCS(uint8_t mcs) {
    txParameters.mcs.clear();
    txParameters.mcs.emplace_back(mcs);
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setNumSTS(uint8_t numSTS) {
    txParameters.numSTS.clear();
    txParameters.numSTS.emplace_back(numSTS);
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setNumSTS(const std::vector<uint8_t> &numSTSs) {
    txParameters.numSTS = numSTSs;
    return *this;
}


[[maybe_unused]] ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setMCS(const std::vector<uint8_t> &mcs) {
    txParameters.mcs = mcs;
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setDestinationAddress(const uint8_t macAddr[6]) {
    memcpy(standardHeader.addr1, macAddr, 6);
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setSourceAddress(const uint8_t macAddr[6]) {
    memcpy(standardHeader.addr2, macAddr, 6);
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::set3rdAddress(const uint8_t macAddr[6]) {
    memcpy(standardHeader.addr3, macAddr, 6);
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setForceSounding(bool forceSounding) {
    txParameters.forceSounding = forceSounding;
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setNumExtraSounding(uint8_t numExtraSounding) {
    txParameters.numExtraSounding = numExtraSounding;
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setChannelCoding(ChannelCodingEnum codings) {
    txParameters.coding.clear();
    txParameters.coding.emplace_back(codings);
    return *this;
}

ModularPicoScenesTxFrame &ModularPicoScenesTxFrame::setChannelCoding(const std::vector<ChannelCodingEnum> &channelCoding) {
    txParameters.coding = channelCoding;
    return *this;
}

std::string ModularPicoScenesTxFrame::toString() const {
    std::stringstream ss;
    ss << "TxFrame:{" << standardHeader;
    if (frameHeader)
        ss << ", " << *frameHeader;
    ss << ", " << txParameters;

    if (!segments.empty()) {
        std::stringstream segss;
        segss << "Segments:(";
        for (const auto &segment: segments) {
            segss << segment->segmentName << ":" << segment->totalLength() << "B, ";
        }
        auto temp = segss.str();
        temp.erase(temp.end() - 2, temp.end());
        temp.append(")");
        ss << ", " << temp;
    }
    ss << "}";
    return ss.str();
}

void ModularPicoScenesTxFrame::appendAMPDUFrames(const ModularPicoScenesTxFrame &frame) {
    AMPDUFrames.emplace_back(frame);
}

std::ostream &operator<<(std::ostream &os, const ModularPicoScenesTxFrame &txframe) {
    os << txframe.toString();
    return os;
}
