//
// Created by csi on 9/9/21.
//

#include "MVMExtraSegment.hxx"


static auto v1Parser = [](const uint8_t *buffer, uint32_t bufferLength) -> IntelMVMExtrta {
    uint32_t pos = 0;
    auto extra = IntelMVMExtrta();
    extra.CSIHeaderLength = *(uint16_t *) (buffer + pos);
    pos += 2;
    if (bufferLength - pos < extra.CSIHeaderLength)
        throw std::runtime_error("MVMExtraSegment v1Parser cannot parse the segment with insufficient buffer length.");

    std::copy(buffer + pos, buffer + pos + extra.CSIHeaderLength, std::back_inserter(extra.CSIHeader));
    pos += extra.CSIHeaderLength;
    extra.parsedHeader = *(IntelMVMParsedCSIHeader *) extra.CSIHeader.data();
//    std::cout << "CSIHeader content_len:" << extra.parsedHeader.iqDataSize << " numTone:" << extra.parsedHeader.numTones << std::endl;
    return extra;
};

std::map<uint16_t, std::function<IntelMVMExtrta(const uint8_t *, uint32_t)>> MVMExtraSegment::versionedSolutionMap = initializeSolutionMap();

std::map<uint16_t, std::function<IntelMVMExtrta(const uint8_t *, uint32_t)>> MVMExtraSegment::initializeSolutionMap() noexcept {
    std::map<uint16_t, std::function<IntelMVMExtrta(const uint8_t *, uint32_t)>> map;
    map.emplace(0x1U, v1Parser);
    return map;
}

MVMExtraSegment::MVMExtraSegment() : AbstractPicoScenesFrameSegment("MVMExtra", 0x1U) {}

void MVMExtraSegment::fromBuffer(const uint8_t *buffer, uint32_t bufferLength) {
    auto[segmentName, segmentLength, versionId, offset] = extractSegmentMetaData(buffer, bufferLength);
    if (segmentName != "MVMExtra")
        throw std::runtime_error("MVMExtraSegment cannot parse the segment named " + segmentName + ".");
    if (segmentLength + 4 > bufferLength)
        throw std::underflow_error("MVMExtraSegment cannot parse the segment with less than " + std::to_string(segmentLength + 4) + "B.");
    if (!versionedSolutionMap.count(versionId)) {
        throw std::runtime_error("MVMExtraSegment cannot parse the segment with version v" + std::to_string(versionId) + ".");
    }

    mvmExtra = versionedSolutionMap.at(versionId)(buffer + offset, bufferLength - offset);
    std::copy(buffer, buffer + bufferLength, std::back_inserter(rawBuffer));
    this->segmentLength = segmentLength;
    isSuccessfullyDecoded = true;
}

MVMExtraSegment MVMExtraSegment::createByBuffer(const uint8_t *buffer, uint32_t bufferLength) {
    MVMExtraSegment mvmExtraSegment;
    mvmExtraSegment.fromBuffer(buffer, bufferLength);
    return mvmExtraSegment;
}

std::vector<uint8_t> MVMExtraSegment::toBuffer() const {
    return AbstractPicoScenesFrameSegment::toBuffer(true);
}

std::string MVMExtraSegment::toString() const {
    std::stringstream ss;
    ss << segmentName + ":[";
    ss << "hdr_len=" << mvmExtra.CSIHeaderLength << ", csi_len=" << mvmExtra.parsedHeader.iqDataSize << "B, num_tone=" << mvmExtra.parsedHeader.numTones << ", rate_n_flags=0x" << std::hex << mvmExtra.parsedHeader.rate_n_flags << ", ftm_clock=" << std::dec << mvmExtra.parsedHeader.ftmClock << ", mu_clock=" << mvmExtra.parsedHeader.muClock << "]";
    auto temp = ss.str();
    return temp;
}

std::ostream &operator<<(std::ostream &os, const MVMExtraSegment &mvmSegment) {
    os << mvmSegment.toString();
    return os;
}

const IntelMVMExtrta &MVMExtraSegment::getMvmExtra() const {
    return mvmExtra;
}