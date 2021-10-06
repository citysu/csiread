//
// Created by csi on 9/9/21.
//

#ifndef PICOSCENES_PLATFORM_MVMEXTRASEGMENT_HXX
#define PICOSCENES_PLATFORM_MVMEXTRASEGMENT_HXX

#include "AbstractPicoScenesFrameSegment.hxx"
#include "PicoScenesCommons.hxx"

class IntelMVMParsedCSIHeader {
public:
    uint32_t iqDataSize{};
    uint8_t reserved4[4];
    uint32_t ftmClock;
    uint32_t samplingTick2;
    uint8_t reserved16_52[36];
    uint32_t numTones;
    uint8_t reserved60[4];
    uint32_t rssi1;
    uint32_t rssi2;
    uint8_t sourceAddress[6];
    uint8_t reserved74[2];
    uint8_t csiSequence;
    uint8_t reserved77[11];
    uint32_t muClock; // 88
    uint32_t rate_n_flags; // 92
} __attribute__ ((__packed__));

class IntelMVMExtrta {
public:
    uint16_t CSIHeaderLength;
    std::vector<uint8_t> CSIHeader;
    IntelMVMParsedCSIHeader parsedHeader;
};


class MVMExtraSegment : public AbstractPicoScenesFrameSegment {
public:
    MVMExtraSegment();

    static MVMExtraSegment createByBuffer(const uint8_t *buffer, uint32_t bufferLength);

    void fromBuffer(const uint8_t *buffer, uint32_t bufferLength) override;

    std::vector<uint8_t> toBuffer() const override;

    [[nodiscard]] std::string toString() const override;
    
    const IntelMVMExtrta &getMvmExtra() const;

private:
    static std::map<uint16_t, std::function<IntelMVMExtrta(const uint8_t *, uint32_t)>> versionedSolutionMap;

    static std::map<uint16_t, std::function<IntelMVMExtrta(const uint8_t *, uint32_t)>> initializeSolutionMap() noexcept;

    IntelMVMExtrta mvmExtra;
};

std::ostream &operator<<(std::ostream &os, const MVMExtraSegment &mvmSegment);


#endif //PICOSCENES_PLATFORM_MVMEXTRASEGMENT_HXX
