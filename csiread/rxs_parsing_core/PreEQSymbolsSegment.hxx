//
// Created by 蒋志平 on 2020/12/19.
//

#ifndef PICOSCENES_PLATFORM_PREEQSYMBOLSSEGMENT_HXX
#define PICOSCENES_PLATFORM_PREEQSYMBOLSSEGMENT_HXX

#include <functional>
#include "AbstractPicoScenesFrameSegment.hxx"
#include "PicoScenesCommons.hxx"

class PreEQSymbolsSegment : AbstractPicoScenesFrameSegment {
public:
    PreEQSymbolsSegment();

    [[nodiscard]] const SignalMatrix<std::complex<double>> &getPreEqSymbols() const;

    void setPreEqSymbols(const SignalMatrix<std::complex<double>> &preEqSymbols);

    [[nodiscard]] std::vector<uint8_t> toBuffer() const override;

    static PreEQSymbolsSegment createByBuffer(const uint8_t *buffer, uint32_t bufferLength);

    void fromBuffer(const uint8_t *buffer, uint32_t bufferLength) override;

    [[nodiscard]] std::string toString() const override;

private:
    static std::map<uint16_t, std::function<SignalMatrix<std::complex<double>>(const uint8_t *, uint32_t)>> versionedSolutionMap;

    static std::map<uint16_t, std::function<SignalMatrix<std::complex<double>>(const uint8_t *, uint32_t)>> initializeSolutionMap() noexcept;

    SignalMatrix<std::complex<double>> preEQSymbols;
};

std::ostream &operator<<(std::ostream &os, const PreEQSymbolsSegment &preEqSymbolsSegment);

#endif //PICOSCENES_PLATFORM_PREEQSYMBOLSSEGMENT_HXX
