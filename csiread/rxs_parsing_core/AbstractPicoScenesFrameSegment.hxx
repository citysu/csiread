//
// Created by 蒋志平 on 2020/11/5.
//

#ifndef PICOSCENES_PLATFORM_ABSTRACTPICOSCENESFRAMESEGMENT_HXX
#define PICOSCENES_PLATFORM_ABSTRACTPICOSCENESFRAMESEGMENT_HXX

#include <algorithm>
#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <type_traits>
#include <tuple>
#include <memory>
#include <cstring>

class AbstractPicoScenesFrameSegment {
public:
    std::string segmentName;
    uint16_t segmentVersionId;
    uint32_t segmentLength = 0;
    std::vector<uint8_t> rawBuffer;

    AbstractPicoScenesFrameSegment(std::string segmentName, uint16_t segmentVersionId);

    template<typename ValueType, typename = std::enable_if<std::is_fundamental_v<ValueType>>>
    void addField(const std::string &fieldName, ValueType value) {
        addField(fieldName, (uint8_t *) &value, sizeof(value));
    }

    void addField(const std::string &fieldName, const std::vector<uint8_t> &data);

    void addField(const std::string &fieldName, const uint8_t *buffer, uint32_t bufferLength);

    void addField(const std::string &fieldName, const std::pair<const uint8_t *, uint32_t> &buffer);

    void addField(const std::string &fieldName, const std::pair<std::shared_ptr<uint8_t>, uint32_t> &buffer);

    std::vector<uint8_t> getField(const std::string &fieldName) const;

    uint32_t getField(const std::string &fieldName, uint8_t *buffer, std::optional<uint32_t> capacity) const;

    void removeField(const std::string &fieldName);

    uint32_t totalLength() const;

    virtual std::vector<uint8_t> toBuffer() const = 0;

    virtual std::vector<uint8_t> toBuffer(bool totalLengthIncluded) const;

    virtual uint32_t toBuffer(bool totalLengthIncluded, uint8_t *buffer, std::optional<uint32_t> capacity = std::nullopt) const;

    virtual void fromBuffer(const uint8_t *buffer, uint32_t bufferLength) = 0;

    void clearFieldCache();

    static std::tuple<std::string, uint32_t, uint16_t, uint32_t> extractSegmentMetaData(const uint8_t *buffer, uint32_t bufferLength);

    virtual std::string toString() const;

    virtual ~AbstractPicoScenesFrameSegment() {};

protected:
    std::vector<std::string> fieldNames; // fieldMap is not ordered by the insertion, so we need another list to hold the input order.
    std::map<std::string, std::vector<uint8_t>> fieldMap;
    std::map<std::string, std::pair<uint32_t, uint32_t>> fieldIndices;
    bool isSuccessfullyDecoded = false;
};


#endif //PICOSCENES_PLATFORM_ABSTRACTPICOSCENESFRAMESEGMENT_HXX
