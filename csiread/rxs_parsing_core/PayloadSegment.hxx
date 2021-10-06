//
// Created by csi on 12/13/20.
//

#ifndef PICOSCENES_PLATFORM_PAYLOADSEGMENT_HXX
#define PICOSCENES_PLATFORM_PAYLOADSEGMENT_HXX

#include <functional>
#include "AbstractPicoScenesFrameSegment.hxx"
#include "PicoScenesCommons.hxx"

enum class PayloadDataType : uint8_t {
    RawData = 0,
    SegmentData,
    SignalMatrix,
    CSIData,
    FullMSDUPacket,
    FullPicoScenesPacket,
};

std::ostream &operator<<(std::ostream &os, const PayloadDataType &payloadDataType);


class PayloadData {
public:
    PayloadDataType dataType = PayloadDataType::RawData;
    std::string payloadDescription;
    std::vector<uint8_t> payloadData;

    std::vector<uint8_t> toBuffer();

    static PayloadData fromBuffer(const uint8_t *buffer, uint32_t bufferLength);

    static PayloadData fromBuffer(const std::vector<uint8_t> &buffer);
};

class PayloadSegment : public AbstractPicoScenesFrameSegment {

public:
    PayloadSegment();

    PayloadSegment(const std::string &description, const std::vector<uint8_t> &payload, std::optional<PayloadDataType> payloadType = std::nullopt);

    std::vector<uint8_t> toBuffer() const override;

    static PayloadSegment createByBuffer(const uint8_t *buffer, uint32_t bufferLength);

    void fromBuffer(const uint8_t *buffer, uint32_t bufferLength) override;

    const PayloadData &getPayload() const;

    void setPayload(const PayloadData &payload);

    std::string toString() const override;

private:

    static std::map<uint16_t, std::function<PayloadData(const uint8_t *, uint32_t)>> versionedSolutionMap;

    static std::map<uint16_t, std::function<PayloadData(const uint8_t *, uint32_t)>> initializeSolutionMap() noexcept;

    PayloadData payload;
};

std::ostream &operator<<(std::ostream &os, const PayloadSegment &payloadSegment);


#endif //PICOSCENES_PLATFORM_PAYLOADSEGMENT_HXX
