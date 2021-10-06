//
// Created by 蒋志平 on 2020/11/6.
//

#ifndef PICOSCENES_PLATFORM_RXSBASICSEGMENT_HXX
#define PICOSCENES_PLATFORM_RXSBASICSEGMENT_HXX

#include <functional>
#include "AbstractPicoScenesFrameSegment.hxx"
#include "PicoScenesCommons.hxx"

struct RxSBasic {
    uint16_t deviceType;    /* device type code */
    uint64_t tstamp;        /* h/w assigned timestamp */
    int16_t centerFreq;     /* receiving channel frequency */
    int16_t controlFreq;    /* control channel frequency */
    uint16_t cbw;           /* channel bandwidth [20, 40, 80, 160] */
    uint8_t packetFormat;   /* 0 for NonHT, 1 for HT, 2 for VHT, 3 for HE-SU, 4 for HE-MU */
    uint16_t pkt_cbw;       /* packet CBW [20, 40, 80, 160] */
    uint16_t guardInterval; /* 400/800/1600/3200ns */
    uint8_t mcs;
    uint8_t numSTS;
    uint8_t numESS;
    uint8_t numRx;
    uint8_t numUser;
    uint8_t userIndex;
    int8_t noiseFloor;   /* noise floor */
    int8_t rssi;        /* rx frame RSSI */
    int8_t rssi_ctl0;   /* rx frame RSSI [ctl, chain 0] */
    int8_t rssi_ctl1;   /* rx frame RSSI [ctl, chain 1] */
    int8_t rssi_ctl2;   /* rx frame RSSI [ctl, chain 2] */
    [[nodiscard]] std::string toString() const;

    std::vector<uint8_t> toBuffer();

} __attribute__ ((__packed__));

std::ostream &operator<<(std::ostream &os, const RxSBasic &rxSBasic);


class RxSBasicSegment : public AbstractPicoScenesFrameSegment {

public:
    RxSBasicSegment();

    static RxSBasicSegment createByBuffer(const uint8_t *buffer, uint32_t bufferLength);

    void fromBuffer(const uint8_t *buffer, uint32_t bufferLength) override;

    std::vector<uint8_t> toBuffer() const override;

    const RxSBasic &getBasic() const;

    void setBasic(const RxSBasic &basic);

private:
    static std::map<uint16_t, std::function<RxSBasic(const uint8_t *, uint32_t)>> versionedSolutionMap;

    static std::map<uint16_t, std::function<RxSBasic(const uint8_t *, uint32_t)>> initializeSolutionMap() noexcept;

    RxSBasic basic{};
};

#endif //PICOSCENES_PLATFORM_RXSBASICSEGMENT_HXX
