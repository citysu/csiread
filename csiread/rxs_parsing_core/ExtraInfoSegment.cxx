//
// Created by 蒋志平 on 2020/11/6.
//

#include "ExtraInfoSegment.hxx"

static auto v1Parser = [](const uint8_t *buffer, uint32_t bufferLength) -> ExtraInfo {
    if (auto eiOpt = ExtraInfo::fromBuffer(buffer, 0)) {
        auto calculatedLength = eiOpt->calculateBufferLength();
        if (calculatedLength != bufferLength - 4)
            throw std::runtime_error("ExtraInfoSegment cannot decode due to the mismatched buffer length.");
        return eiOpt.value();
    }

    throw std::runtime_error("ExtraInfoSegment cannot decode the given buffer.");
};

std::map<uint16_t, std::function<ExtraInfo(const uint8_t *, uint32_t)>> ExtraInfoSegment::versionedSolutionMap = initializeSolutionMap();

std::map<uint16_t, std::function<ExtraInfo(const uint8_t *, uint32_t)>> ExtraInfoSegment::initializeSolutionMap() noexcept {
    return std::map<uint16_t, std::function<ExtraInfo(const uint8_t *, uint32_t)>>{{0x1U, v1Parser}};
}

ExtraInfoSegment::ExtraInfoSegment() : AbstractPicoScenesFrameSegment("ExtraInfo", 0x1U) {}

ExtraInfoSegment::ExtraInfoSegment(const ExtraInfo &extraInfoV) : ExtraInfoSegment() {
    extraInfo = extraInfoV;
    addField("EI", extraInfoV.toBuffer());
}

void ExtraInfoSegment::fromBuffer(const uint8_t *buffer, uint32_t bufferLength) {
    auto[segmentName, segmentLength, versionId, offset] = extractSegmentMetaData(buffer, bufferLength);
    if (segmentName != "ExtraInfo")
        throw std::runtime_error("ExtraInfoSegment cannot parse the segment named " + segmentName + ".");
    if (segmentLength + 4 > bufferLength)
        throw std::underflow_error("ExtraInfoSegment cannot parse the segment with less than " + std::to_string(segmentLength + 4) + "B.");
    if (!versionedSolutionMap.count(versionId)) {
        throw std::runtime_error("ExtraInfoSegment cannot parse the segment with version v" + std::to_string(versionId) + ".");
    }

    extraInfo = versionedSolutionMap.at(versionId)(buffer + offset, bufferLength - offset);
    std::copy(buffer, buffer + bufferLength, std::back_inserter(rawBuffer));
    this->segmentLength = segmentLength;
    isSuccessfullyDecoded = true;
}

ExtraInfoSegment ExtraInfoSegment::createByBuffer(const uint8_t *buffer, uint32_t bufferLength) {
    ExtraInfoSegment extraInfoSegment;
    extraInfoSegment.fromBuffer(buffer, bufferLength);
    return extraInfoSegment;
}

std::vector<uint8_t> ExtraInfoSegment::toBuffer() const {
    return AbstractPicoScenesFrameSegment::toBuffer(true);
}

const ExtraInfo &ExtraInfoSegment::getExtraInfo() const {
    return extraInfo;
}

void ExtraInfoSegment::setExtraInfo(const ExtraInfo &extraInfo) {
    ExtraInfoSegment::extraInfo = extraInfo;
    clearFieldCache();
    addField("core", extraInfo.toBuffer());
}
