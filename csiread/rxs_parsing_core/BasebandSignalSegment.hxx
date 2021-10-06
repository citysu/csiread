//
// Created by 蒋志平 on 2020/11/6.
//

#ifndef PICOSCENES_PLATFORM_BASEBANDSIGNALSEGMENT_HXX
#define PICOSCENES_PLATFORM_BASEBANDSIGNALSEGMENT_HXX


#include <functional>
#include "AbstractPicoScenesFrameSegment.hxx"
#include "PicoScenesCommons.hxx"

class BasebandSignalSegment : AbstractPicoScenesFrameSegment {
public:
    BasebandSignalSegment();

    [[maybe_unused]] [[nodiscard]] const SignalMatrix<std::complex<double>> &getSignalMatrix() const;

    void setSignalMatrix(const SignalMatrix<std::complex<double>> &bbsignalsV);

    static BasebandSignalSegment createByBuffer(const uint8_t *buffer, uint32_t bufferLength);

    void fromBuffer(const uint8_t *buffer, uint32_t bufferLength) override;

    [[nodiscard]] std::vector<uint8_t> toBuffer() const override;

    [[nodiscard]] std::string toString() const override;

private:
    static std::map<uint16_t, std::function<SignalMatrix<std::complex<double>>(const uint8_t *, uint32_t)>> versionedSolutionMap;

    static std::map<uint16_t, std::function<SignalMatrix<std::complex<double>>(const uint8_t *, uint32_t)>> initializeSolutionMap() noexcept;

    SignalMatrix<std::complex<double>> bbsignals;
};

std::ostream &operator<<(std::ostream &os, const BasebandSignalSegment &csiSegment);


#endif //PICOSCENES_PLATFORM_BASEBANDSIGNALSEGMENT_HXX
