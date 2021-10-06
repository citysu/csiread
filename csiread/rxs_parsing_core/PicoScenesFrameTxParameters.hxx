//
// Created by 蒋志平 on 2020/11/6.
//

#ifndef PICOSCENES_PLATFORM_PICOSCENESFRAMETXPARAMETERS_HXX
#define PICOSCENES_PLATFORM_PICOSCENESFRAMETXPARAMETERS_HXX

#include "PicoScenesCommons.hxx"

class PicoScenesFrameTxParameters {
public:
    std::optional<double> preciseTxTime = std::nullopt;
    PacketFormatEnum frameType;
    std::vector<uint8_t> mcs;
    std::vector<uint8_t> numSTS;
    double numAntenna;
    ChannelBandwidthEnum cbw;
    GuardIntervalEnum guardInterval;
    std::vector<ChannelCodingEnum> coding;
    double numExtraSounding;
    bool forceSounding;
    double idleTime;
    double scramblerState;
    double txIQAmplitudeImbalance_dB;
    double txIQPhaseImbalance_rad;
    bool maxPowerScaleTo1;
    double actualSamplingRate;
    double samplingRateOffset;
    double carrierFrequencyOffset;
    double resampleRatio;
    double vhtGroupId;
    std::vector<uint8_t> heAllocationIndex;
    double heLTFType;

    PicoScenesFrameTxParameters() {
        frameType = PacketFormatEnum::PacketFormat_HT;
        mcs = std::vector<uint8_t>(1, 0);
        numSTS = std::vector<uint8_t>(1, 1);
        numAntenna = 1;
        cbw = ChannelBandwidthEnum::CBW_20;
        guardInterval = GuardIntervalEnum::GI_800;
        coding = std::vector<ChannelCodingEnum>(1, ChannelCodingEnum::BCC);
        numExtraSounding = 0;
        forceSounding = true;
        idleTime = 20e-6;
        scramblerState = 39;
        txIQAmplitudeImbalance_dB = 0;
        txIQPhaseImbalance_rad = 0;
        maxPowerScaleTo1 = true;
        actualSamplingRate = 20e6;
        samplingRateOffset = 0;
        carrierFrequencyOffset = 0;
        vhtGroupId = 0;
        heAllocationIndex = std::vector<uint8_t>(1, 0);
        heLTFType = 4;
    }

    std::string toString() const;
};

std::ostream &operator<<(std::ostream &os, const PicoScenesFrameTxParameters &parameters);

#endif //PICOSCENES_PLATFORM_PICOSCENESFRAMETXPARAMETERS_HXX
