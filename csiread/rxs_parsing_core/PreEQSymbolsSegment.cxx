//
// Created by 蒋志平 on 2020/12/19.
//

#include "PreEQSymbolsSegment.hxx"

static auto v1Parser = [](const uint8_t *buffer, uint32_t bufferLength) -> SignalMatrix<std::complex<double>> {
    auto signal = SignalMatrix<std::complex<double>>::fromBuffer(buffer, buffer + bufferLength, SignalMatrixStorageMajority::ColumnMajor);
    return signal;
};

std::map<uint16_t, std::function<SignalMatrix<std::complex<double>>(const uint8_t *, uint32_t)>> PreEQSymbolsSegment::initializeSolutionMap() noexcept {
    return std::map<uint16_t, std::function<SignalMatrix<std::complex<double>>(const uint8_t *, uint32_t)>>{{0x1U, v1Parser}};
}

std::map<uint16_t, std::function<SignalMatrix<std::complex<double>>(const uint8_t *, uint32_t)>> PreEQSymbolsSegment::versionedSolutionMap = initializeSolutionMap();

PreEQSymbolsSegment::PreEQSymbolsSegment() : AbstractPicoScenesFrameSegment("PreEQSymbols", 0x1U) {}

const SignalMatrix<std::complex<double>> &PreEQSymbolsSegment::getPreEqSymbols() const {
    return preEQSymbols;
}

void PreEQSymbolsSegment::setPreEqSymbols(const SignalMatrix<std::complex<double>> &preEqSymbolsV) {
    preEQSymbols = preEqSymbolsV;
    addField("core", preEQSymbols.toBuffer());
}

std::vector<uint8_t> PreEQSymbolsSegment::toBuffer() const {
    return AbstractPicoScenesFrameSegment::toBuffer(true);
}

PreEQSymbolsSegment PreEQSymbolsSegment::createByBuffer(const uint8_t *buffer, uint32_t bufferLength) {
    PreEQSymbolsSegment preEqSymbolsSegment;
    preEqSymbolsSegment.fromBuffer(buffer, bufferLength);
    return preEqSymbolsSegment;
}

void PreEQSymbolsSegment::fromBuffer(const uint8_t *buffer, uint32_t bufferLength) {
    auto[segmentName, segmentLength, versionId, offset] = extractSegmentMetaData(buffer, bufferLength);
    if (segmentName != "PreEQSymbols")
        throw std::runtime_error("PreEQSymbolsSegment cannot parse the segment named " + segmentName + ".");
    if (segmentLength + 4 > bufferLength)
        throw std::underflow_error("PreEQSymbolsSegment cannot parse the segment with less than " + std::to_string(segmentLength + 4) + "B.");
    if (!versionedSolutionMap.count(versionId)) {
        throw std::runtime_error("PreEQSymbolsSegment cannot parse the segment with version v" + std::to_string(versionId) + ".");
    }

    preEQSymbols = versionedSolutionMap.at(versionId)(buffer + offset, bufferLength - offset);
    std::copy(buffer, buffer + bufferLength, std::back_inserter(rawBuffer));
    this->segmentLength = segmentLength;
    isSuccessfullyDecoded = true;
}

std::string PreEQSymbolsSegment::toString() const {
    std::stringstream ss;
    ss << segmentName + ":[" + std::to_string(preEQSymbols.dimensions[0]) + "x" + std::to_string(preEQSymbols.dimensions[1]) + "]";
    auto temp = ss.str();
    return temp;
}

std::ostream &operator<<(std::ostream &os, const PreEQSymbolsSegment &preEqSymbolsSegment) {
    os << preEqSymbolsSegment.toString();
    return os;
}
