//
// Created by csi on 12/13/20.
//

#include "PayloadSegment.hxx"


std::ostream &operator<<(std::ostream &os, const PayloadDataType &payloadDataType) {
    switch (payloadDataType) {
        case PayloadDataType::RawData:
            os << "RawData";
            break;
        case PayloadDataType::SignalMatrix:
            os << "Signal";
            break;
        case PayloadDataType::CSIData:
            os << "CSI";
            break;
        case PayloadDataType::SegmentData:
            os << "Segment";
            break;
        case PayloadDataType::FullMSDUPacket:
            os << "MSDU";
            break;
        case PayloadDataType::FullPicoScenesPacket:
            os << "FullPicoScenes";
            break;
    }
    return os;
}

std::vector<uint8_t> PayloadData::toBuffer() {
    auto buffer = std::vector<uint8_t>();
    uint32_t totalLength = sizeof(dataType) + 1 + payloadDescription.length() + 4 + payloadData.size();
    std::copy((uint8_t *) &totalLength, (uint8_t *) &totalLength + sizeof(totalLength), std::back_inserter(buffer));
    std::copy((uint8_t *) &dataType, (uint8_t *) &dataType + sizeof(dataType), std::back_inserter(buffer));
    uint8_t descriptionLength = payloadDescription.length();
    std::copy((uint8_t *) &descriptionLength, (uint8_t *) &descriptionLength + sizeof(descriptionLength), std::back_inserter(buffer));
    std::copy((uint8_t *) payloadDescription.data(), (uint8_t *) payloadDescription.data() + payloadDescription.length(), std::back_inserter(buffer));
    uint32_t payloadLength = payloadData.size();
    std::copy((uint8_t *) &payloadLength, (uint8_t *) &payloadLength + sizeof(payloadLength), std::back_inserter(buffer));
    std::copy(payloadData.cbegin(), payloadData.cend(), std::back_inserter(buffer));

    return buffer;
}

PayloadData PayloadData::fromBuffer(const uint8_t *buffer, uint32_t bufferLength) {
    uint32_t payloadTotalLength = *(uint32_t *) buffer;
    if (payloadTotalLength != bufferLength - 4)
        throw std::runtime_error("Payload length inconsistent");

    auto pos = 4;
    PayloadData payload;
    payload.dataType = *(PayloadDataType *) (buffer + pos);
    pos += sizeof(PayloadDataType);
    auto descriptionLength = *(uint8_t *) (buffer + pos++);
    payload.payloadDescription = std::string((char *) (buffer + pos), (char *) (buffer + pos + descriptionLength));
    pos += descriptionLength;
    auto payloadLength = *(uint32_t *) (buffer + pos);
    pos += 4;
    std::copy(buffer + pos, buffer + pos + payloadLength, std::back_inserter(payload.payloadData));
    return payload;
}

PayloadData PayloadData::fromBuffer(const std::vector<uint8_t> &buffer) {
    return fromBuffer(buffer.data(), buffer.size());
}

static auto v1Parser = [](const uint8_t *buffer, uint32_t bufferLength) -> PayloadData {
    return PayloadData::fromBuffer(buffer, bufferLength);
};

std::map<uint16_t, std::function<PayloadData(const uint8_t *, uint32_t)>> PayloadSegment::versionedSolutionMap = initializeSolutionMap();

std::map<uint16_t, std::function<PayloadData(const uint8_t *, uint32_t)>> PayloadSegment::initializeSolutionMap() noexcept {
    return std::map<uint16_t, std::function<PayloadData(const uint8_t *, uint32_t)>>{{0x1U, v1Parser}};
}

PayloadSegment::PayloadSegment() : AbstractPicoScenesFrameSegment("Payload", 0x1U) {}

PayloadSegment::PayloadSegment(const std::string &description, const std::vector<uint8_t> &payload, std::optional<PayloadDataType> payloadType) : PayloadSegment() {
    PayloadData payloadData{.dataType = payloadType.value_or(PayloadDataType::RawData),
            .payloadDescription = description,
            .payloadData = payload};
    setPayload(payloadData);
}

std::vector<uint8_t> PayloadSegment::toBuffer() const {
    return AbstractPicoScenesFrameSegment::toBuffer(true);
}

void PayloadSegment::fromBuffer(const uint8_t *buffer, uint32_t bufferLength) {
    auto[segmentName, segmentLength, versionId, offset] = extractSegmentMetaData(buffer, bufferLength);
    if (segmentName != "Payload")
        throw std::runtime_error("PayloadSegment cannot parse the segment named " + segmentName + ".");
    if (segmentLength + 4 > bufferLength)
        throw std::underflow_error("PayloadSegment cannot parse the segment with less than " + std::to_string(segmentLength + 4) + "B.");
    if (!versionedSolutionMap.count(versionId)) {
        throw std::runtime_error("PayloadSegment cannot parse the segment with version v" + std::to_string(versionId) + ".");
    }

    payload = versionedSolutionMap.at(versionId)(buffer + offset, bufferLength - offset);
    std::copy(buffer, buffer + bufferLength, std::back_inserter(rawBuffer));
    this->segmentLength = segmentLength;
    isSuccessfullyDecoded = true;
}

PayloadSegment PayloadSegment::createByBuffer(const uint8_t *buffer, uint32_t bufferLength) {
    PayloadSegment payloadSegment;
    payloadSegment.fromBuffer(buffer, bufferLength);
    return payloadSegment;
}

const PayloadData &PayloadSegment::getPayload() const {
    return payload;
}

void PayloadSegment::setPayload(const PayloadData &payloadV) {
    payload = payloadV;
    clearFieldCache();
    addField("core", payload.toBuffer());
}

std::string PayloadSegment::toString() const {
    std::stringstream ss;
    ss << segmentName + ":[";
    ss << "Type=" << payload.dataType << ", Description=" << payload.payloadDescription << ", length=" << std::to_string(payload.payloadData.size()) + "B]";
    auto temp = ss.str();
    temp.erase(temp.end() - 2, temp.end());
    temp.append("]");
    return temp;
}

std::ostream &operator<<(std::ostream &os, const PayloadSegment &payloadSegment) {
    os << payloadSegment.toString();
    return os;
}

