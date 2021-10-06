//
// Created by 蒋志平 on 2020/11/5.
//

#include <utility>

#include "AbstractPicoScenesFrameSegment.hxx"

AbstractPicoScenesFrameSegment::AbstractPicoScenesFrameSegment(std::string segmentName, uint16_t segmentVersionId) : segmentName(std::move(segmentName)), segmentVersionId(segmentVersionId) {
}

void AbstractPicoScenesFrameSegment::addField(const std::string &fieldName, const std::vector<uint8_t> &data) {
    fieldMap[fieldName] = data;
    fieldNames.emplace_back(fieldName);
    segmentLength = totalLength();
}

void AbstractPicoScenesFrameSegment::addField(const std::string &fieldName, const uint8_t *buffer, uint32_t bufferLength) {
    fieldMap[fieldName] = std::vector<uint8_t>(buffer, buffer + bufferLength);
    fieldNames.emplace_back(fieldName);
    segmentLength = totalLength();
}

void AbstractPicoScenesFrameSegment::addField(const std::string &fieldName, const std::pair<const uint8_t *, uint32_t> &buffer) {
    fieldMap[fieldName] = std::vector<uint8_t>(buffer.first, buffer.first + buffer.second);
    fieldNames.emplace_back(fieldName);
    segmentLength = totalLength();
}

void AbstractPicoScenesFrameSegment::addField(const std::string &fieldName, const std::pair<std::shared_ptr<uint8_t>, uint32_t> &buffer) {
    fieldMap[fieldName] = std::vector<uint8_t>(buffer.first.get(), buffer.first.get() + buffer.second);
    fieldNames.emplace_back(fieldName);
    segmentLength = totalLength();
}

std::vector<uint8_t> AbstractPicoScenesFrameSegment::getField(const std::string &fieldName) const {
    const auto &field = fieldMap.at(fieldName);
    auto result = std::vector<uint8_t>(field.size());
    getField(fieldName, &result[0], result.size());
    return result;
}

uint32_t AbstractPicoScenesFrameSegment::getField(const std::string &fieldName, uint8_t *buffer, std::optional<uint32_t> capacity) const {
    const auto &field = fieldMap.at(fieldName);
    if (capacity && *capacity < field.size())
        throw std::runtime_error("buffer capacity not enough for copying segment field [" + fieldName + " (" + std::to_string(field.size()) + "B)]");

    std::copy(field.cbegin(), field.cend(), buffer);
    return field.size();
}

void AbstractPicoScenesFrameSegment::removeField(const std::string &fieldName) {
    fieldMap.erase(fieldMap.find(fieldName));
    fieldNames.erase(std::find(fieldNames.cbegin(), fieldNames.cend(), fieldName));
    segmentLength = totalLength();
}

uint32_t AbstractPicoScenesFrameSegment::totalLength() const {
    if (isSuccessfullyDecoded && !rawBuffer.empty())
        return rawBuffer.size() - 4;

    uint32_t length = 0;
    length += segmentName.size();
    length += 1;
    length += sizeof(segmentVersionId);
    for (const auto &field: fieldMap) {
        length += field.second.size();
    }

    return length;
}

std::vector<uint8_t> AbstractPicoScenesFrameSegment::toBuffer(bool totalLengthIncluded) const {
    auto result = std::vector<uint8_t>(totalLength() + (totalLengthIncluded ? 4 : 0));
    toBuffer(totalLengthIncluded, &result[0], result.size());
    return result;
}

uint32_t AbstractPicoScenesFrameSegment::toBuffer(bool totalLengthIncluded, uint8_t *buffer, std::optional<uint32_t> capacity) const {
    if (isSuccessfullyDecoded && !rawBuffer.empty() && rawBuffer.size() == segmentLength + 4) {
        std::copy(rawBuffer.cbegin(), rawBuffer.cend(), buffer);
        return rawBuffer.size();
    }

    uint32_t finalTotalLength = totalLength() + (totalLengthIncluded ? 4 : 0);
    if (capacity && *capacity < finalTotalLength)
        throw std::runtime_error("buffer capacity not enough for PicoScenes frame segment [" + segmentName + " (" + std::to_string(finalTotalLength) + "B)]");

    uint32_t pos = 0;
    // copy totalLength
    if (totalLengthIncluded) {
        *((uint32_t *) (buffer + pos)) = totalLength();
        pos += 4;
    }

    // length of the segment name
    *(buffer + pos++) = segmentName.size();
    // copy the segment name
    std::memcpy(buffer + pos, segmentName.data(), segmentName.size());
    pos += segmentName.size();
    // version Id
    std::memcpy(buffer + pos, &segmentVersionId, sizeof(segmentVersionId));
    pos += sizeof(segmentVersionId);
    // copy fields
    for (const auto &field: fieldNames) {
        const auto &fieldContent = fieldMap.at(field);
        std::copy(fieldContent.cbegin(), fieldContent.cend(), buffer + pos);
        pos += fieldContent.size();
    }

    return pos;
}

std::string AbstractPicoScenesFrameSegment::toString() const {
    return "";
}

std::tuple<std::string, uint32_t, uint16_t, uint32_t> AbstractPicoScenesFrameSegment::extractSegmentMetaData(const uint8_t *buffer, uint32_t bufferLength) {
    uint32_t rxPos = 0;
    uint32_t segmentLength = *(uint32_t *) (buffer + rxPos);
    rxPos += 4;
    if (segmentLength > bufferLength)
        throw std::runtime_error("corrupted segment...");
    auto segNameLength = *(buffer + rxPos++);
    auto segmentName = std::string((char *) (buffer + rxPos), *(char *) (buffer + rxPos + segNameLength - 1) == '\0' ? ((char *) (buffer + rxPos + segNameLength - 1)) : ((char *) (buffer + rxPos + segNameLength)));
    rxPos += segNameLength;
    uint16_t segmentVersionId = *(uint16_t *) (buffer + rxPos);
    rxPos += 2;

    return std::make_tuple(segmentName, segmentLength, segmentVersionId, rxPos);
}

void AbstractPicoScenesFrameSegment::clearFieldCache() {
    fieldNames.clear();
    fieldMap.clear();
    fieldIndices.clear();
}
