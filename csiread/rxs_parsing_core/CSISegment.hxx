//
// Created by 蒋志平 on 2020/11/5.
//

#ifndef PICOSCENES_PLATFORM_CSISEGMENT_HXX
#define PICOSCENES_PLATFORM_CSISEGMENT_HXX

#include <functional>
#include "AbstractPicoScenesFrameSegment.hxx"
#include "PicoScenesCommons.hxx"


template<typename Iterator>
void parseQCA9300CSIData(Iterator outputArray, const uint8_t *csiData, int nSTS, int nRx, int nTones) {

    auto parse10bitsValues = [](const uint8_t rawByte[5], int outputArray[4]) {
        static uint16_t negativeSignBit = (1 << (10 - 1));
        static uint16_t minNegativeValue = (1 << 10);
        outputArray[0] = ((rawByte[0] & 0xffU) >> 0U) + ((rawByte[1] & 0x03u) << 8u);
        outputArray[1] = ((rawByte[1] & 0xfcU) >> 2U) + ((rawByte[2] & 0x0fU) << 6U);
        outputArray[2] = ((rawByte[2] & 0xf0U) >> 4U) + ((rawByte[3] & 0x3fU) << 4U);
        outputArray[3] = ((rawByte[3] & 0xc0U) >> 6U) + ((rawByte[4] & 0xffU) << 2U);
        for (auto i = 0; i < 4; i++) {
            if (outputArray[i] & negativeSignBit)
                outputArray[i] -= minNegativeValue;
        }
    };

    int valuePos, pos, rxIndex, txIndex, toneIndex, totalTones = nRx * nSTS * nTones;
    int tempArray[4];
    for (auto i = 0; i < totalTones / 2; i++) {
        parse10bitsValues(csiData + i * 5, tempArray);

        valuePos = i * 2;
        rxIndex = valuePos % nRx;
        txIndex = (valuePos / nRx) % nSTS;
        toneIndex = valuePos / (nRx * nSTS);
        pos = rxIndex * (nSTS * nTones) + txIndex * nTones + toneIndex;
        outputArray[pos].real(tempArray[1]);
        outputArray[pos].imag(tempArray[0]);

        valuePos = i * 2 + 1;
        rxIndex = valuePos % nRx;
        txIndex = (valuePos / nRx) % nSTS;
        toneIndex = valuePos / (nRx * nSTS);
        pos = rxIndex * (nSTS * nTones) + txIndex * nTones + toneIndex;
        outputArray[pos].real(tempArray[3]);
        outputArray[pos].imag(tempArray[2]);
    }
}

template<typename T>
std::vector<size_t> sort_indexes(const std::vector<T> &v) {

    // initialize original index locations
    std::vector<size_t> idx(v.size());
    std::iota(idx.begin(), idx.end(), 0);

    // sort indexes based on comparing values in v
    std::sort(idx.begin(), idx.end(),
              [&v](size_t i1, size_t i2) { return v[i1] < v[i2]; });

    return idx;
}

template<typename Iterator>
void parseIWL5300CSIData(Iterator csi_matrix, const uint8_t *payload, int ntx, int nrx, uint8_t ant_sel) {

    auto positionComputationWRTPermutation = [](int ntx, int num_tones, int ntxIdx, int nrxIdx, int subcarrierIdx, std::optional<Uint8Vector> ant_sel) -> int {
        auto new_nrxIdx = nrxIdx;
        if (ant_sel && !ant_sel->empty()) {
            auto sorted_indexes = sort_indexes(*ant_sel);
            auto sorted_indexes2 = sort_indexes(sorted_indexes); // double sort, shit but works !
            new_nrxIdx = sorted_indexes2[nrxIdx];
        }

        return new_nrxIdx * (ntx * num_tones) + ntxIdx * num_tones + subcarrierIdx;
    };

    std::vector<uint8_t> antSelVector = [&](uint8_t ant_sel) {
        auto v = std::vector<uint8_t>();
        if (nrx > 1) {
            v.emplace_back(static_cast<unsigned char>(((unsigned) ant_sel & 0x1U) + 1));
            v.emplace_back(static_cast<unsigned char>((((unsigned) ant_sel >> 0x2U) & 0x3U) + 1));
        };
        if (nrx > 2)
            v.emplace_back(static_cast<unsigned char>((((unsigned) ant_sel >> 0x4U) & 0x3U) + 1));
        return v;
    }(ant_sel);

    uint32_t index = 0;
    uint8_t remainder;

//    auto position = 0;
    for (auto subcarrierIdx = 0; subcarrierIdx < 30; subcarrierIdx++) {
        index += 3;
        remainder = index % 8;

        for (auto nrxIdx = 0; nrxIdx < nrx; nrxIdx++) {
            for (auto ntxIdx = 0; ntxIdx < ntx; ntxIdx++) {
                auto position = positionComputationWRTPermutation(ntx, 30, ntxIdx, nrxIdx, subcarrierIdx, antSelVector);
                char tmp1 = (payload[index / 8] >> remainder) | (payload[index / 8 + 1] << (8 - remainder));
                char tmp2 = (payload[index / 8 + 1] >> remainder) | (payload[index / 8 + 2] << (8 - remainder));
                csi_matrix[position].real((double) tmp1);
                csi_matrix[position].imag((double) tmp2);
                index += 16;
            }
        }
    }
}

//class IntelMVMCSIHeader {
//public:
//    uint32_t iqDataSize{};
//    uint8_t reserved4[4];
//    uint32_t samplingTick;
//    uint32_t samplingTick2;
//    uint8_t reserved16_52[36];
//    uint32_t numTones;
//    uint8_t reserved60[4];
//    uint32_t rssi1;
//    uint32_t rssi2;
//    uint8_t sourceAddress[6];
//    uint8_t reserved74[2];
//    uint8_t csiSequence;
//    uint8_t reserved77[11];
//    uint32_t macTime; // 88
//    uint32_t rate_n_flags; // 92
//} __attribute__ ((__packed__));

class CSIDimension {
public:
    uint16_t numTones = 1;
    uint8_t numTx = 1;
    uint8_t numRx = 1;
    uint8_t numESS = 0;
    uint16_t numCSI = 1;

    inline uint16_t numStreamsPerCSI() {
        return (numTx + numESS) * numRx;
    }

    inline uint16_t numTotalSubcarriersPerCSI() {
        return numStreamsPerCSI() * numTones;
    }

    inline uint16_t numStreamsAll() {
        return (numTx + numESS) * numRx * numCSI;
    }

    inline uint16_t numTotalSubcarriersAll() {
        return numStreamsAll() * numTones;
    }
};

class CSI {
public:
    PicoScenesDeviceType deviceType;
    PacketFormatEnum packetFormat;
    ChannelBandwidthEnum cbw;
    uint64_t carrierFreq;
    uint64_t samplingRate;
    uint32_t subcarrierBandwidth;
    CSIDimension dimensions;
    uint8_t antSel;
    int16_t subcarrierOffset;
    std::vector<int16_t> subcarrierIndices;
    SignalMatrix<std::complex<double>> CSIArray;
    SignalMatrix<double> magnitudeArray;
    SignalMatrix<double> phaseArray;

    Uint8Vector rawCSIData;

    void interpolateCSI();

    std::vector<uint8_t> toBuffer();

    static CSI fromQCA9300(const uint8_t *buffer, uint32_t bufferLength, uint8_t numTx, uint8_t numRx, uint8_t numTones, ChannelBandwidthEnum cbw, int16_t subcarrierIndexOffset);

    static CSI fromIWL5300(const uint8_t *buffer, uint32_t bufferLength, uint8_t numTx, uint8_t numRx, uint8_t numTones, ChannelBandwidthEnum cbw, int16_t subcarrierIndexOffset, uint8_t ant_sel);

    static CSI fromIWLMVM(const uint8_t *buffer, uint32_t bufferLength, uint8_t numTx, uint8_t numRx, uint16_t numTones, PacketFormatEnum format, ChannelBandwidthEnum cbw, int16_t subcarrierIndexOffset, bool skipPilotSubcarriers = true);

    template<typename OutputValueType, typename InputValueType>
    static std::vector<std::complex<OutputValueType>> convertCSIArrayType(const std::vector<std::complex<InputValueType>> &inputArray) {
        std::vector<std::complex<OutputValueType>> outputArray(inputArray.size());
        for (auto i = 0; i < inputArray.size(); i++) {
            outputArray[i] = std::complex<OutputValueType>(inputArray[i].real(), inputArray[i].imag());
        }
        return outputArray;
    }

private:
    static std::vector<int16_t> NonHT20_52Subcarriers_Indices;
    static std::vector<int16_t> HTVHT20_56Subcarriers_Indices;
    static std::vector<int16_t> HTVHT40_114Subcarriers_Indices;
    static std::vector<int16_t> VHT80_242Subcarriers_Indices;
    static std::vector<int16_t> VHT160_484Subcarriers_Indices;
    static std::vector<int16_t> HE20_242Subcarriers_Indices;
    static std::vector<int16_t> HE40_484Subcarriers_Indices;
    static std::vector<int16_t> HE80_996Subcarriers_Indices;
    static std::vector<int16_t> HE160_1992Subcarriers_Indices;

    static std::vector<int16_t> NonHT20_52Subcarriers_DataIndices;
    static std::vector<int16_t> HTVHT20_56Subcarriers_DataIndices;
    static std::vector<int16_t> HTVHT40_114Subcarriers_DataIndices;
    static std::vector<int16_t> VHT80_242Subcarriers_DataIndices;
    static std::vector<int16_t> VHT160_484Subcarriers_DataIndices;
    static std::vector<int16_t> HE20_242Subcarriers_DataIndices;
    static std::vector<int16_t> HE40_484Subcarriers_DataIndices;
    static std::vector<int16_t> HE80_996Subcarriers_DataIndices;
    static std::vector<int16_t> HE160_1992Subcarriers_DataIndices;

    static std::vector<int16_t> NonHT20_52Subcarriers_PilotIndices;
    static std::vector<int16_t> HTVHT20_56Subcarriers_PilotIndices;
    static std::vector<int16_t> HTVHT40_114Subcarriers_PilotIndices;
    static std::vector<int16_t> VHT80_242Subcarriers_PilotIndices;
    static std::vector<int16_t> VHT160_484Subcarriers_PilotIndices;
    static std::vector<int16_t> HE20_242Subcarriers_PilotIndices;
    static std::vector<int16_t> HE40_484Subcarriers_PilotIndices;
    static std::vector<int16_t> HE80_996Subcarriers_PilotIndices;
    static std::vector<int16_t> HE160_1992Subcarriers_PilotIndices;

    static std::vector<int16_t> IWL5300SubcarrierIndices_CBW20;
    static std::vector<int16_t> IWL5300SubcarrierIndices_CBW40;

    static const std::vector<int16_t> &getAllSubcarrierIndices(PacketFormatEnum format, ChannelBandwidthEnum cbw);

    static const std::vector<int16_t> &getPilotSubcarrierIndices(PacketFormatEnum format, ChannelBandwidthEnum cbw);

    static const std::vector<int16_t> &getDataSubcarrierIndices(PacketFormatEnum format, ChannelBandwidthEnum cbw);

};

class CSISegment : public AbstractPicoScenesFrameSegment {
public:
    CSISegment();

    static CSISegment createByBuffer(const uint8_t *buffer, uint32_t bufferLength);

    [[nodiscard]] std::vector<uint8_t> toBuffer() const override;

    void fromBuffer(const uint8_t *buffer, uint32_t bufferLength) override;

    [[nodiscard]] std::string toString() const override;

    CSI &getCSI();

    [[nodiscard]] const CSI &getCSI() const;

    void setCSI(const CSI &csi);

private:
    static std::map<uint16_t, std::function<CSI(const uint8_t *, uint32_t)>> versionedSolutionMap;

    static std::map<uint16_t, std::function<CSI(const uint8_t *, uint32_t)>> initializeSolutionMap() noexcept;

    CSI csi;
};

std::ostream &operator<<(std::ostream &os, const CSISegment &csiSegment);

#endif //PICOSCENES_PLATFORM_CSISEGMENT_HXX
