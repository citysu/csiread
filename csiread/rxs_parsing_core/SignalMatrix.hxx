//
// Created by csi on 11/25/20.
//

#ifndef PICOSCENES_PLATFORM_SIGNALMATRIX_HXX
#define PICOSCENES_PLATFORM_SIGNALMATRIX_HXX

#include <optional>
#include <utility>
#include <vector>
#include <cstdint>
#include <complex>
#include <iterator>
#include <string>
#include <cstring>
#include <numeric>
#include <iostream>
#include <fstream>
#include <algorithm>

enum class SignalMatrixStorageMajority : char {
    RowMajor = 'R',
    ColumnMajor = 'C',
    UndefinedMajority = 'U',
};

template<typename>
struct is_std_complex : std::false_type {
};

template<typename ValueType>
struct is_std_complex<std::complex<ValueType>> : std::true_type {
};

template<typename SignalType = std::complex<double>, typename = std::enable_if_t<std::is_arithmetic_v<SignalType> || is_std_complex<SignalType>::value>>
class SignalMatrix {
    using SignalElementType = typename std::conditional<std::is_arithmetic_v<SignalType>, SignalType, typename std::remove_reference<decltype(std::declval<typename std::conditional<std::is_arithmetic_v<SignalType>, std::complex<SignalType>, SignalType>::type>().real())>::type>::type;
public:

    uint8_t matrixFormatId;
    std::vector<SignalType> array;
    std::vector<int64_t> dimensions;
    SignalMatrixStorageMajority majority = SignalMatrixStorageMajority::UndefinedMajority;

    SignalMatrix() = default;

    template<typename DimensionContainerType>
    SignalMatrix(const std::vector<SignalType> &array, const DimensionContainerType &dimensionsV, SignalMatrixStorageMajority majority = SignalMatrixStorageMajority::UndefinedMajority) : array(array), majority(majority) {
        for (auto it = std::cbegin(dimensionsV); it != std::cend(dimensionsV); it++) {
            dimensions.emplace_back(*it);
        }

        uint64_t sum = std::accumulate(dimensions.cbegin(), dimensions.cend(), 1, std::multiplies<>());
        if (sum != array.size())
            throw std::invalid_argument("SignalMatrix creation failed due to the inconsistent dimensions.");
    }

    SignalType valueAt(std::initializer_list<int64_t> coordinates) {
        return array.at(computeIndex4Coordinates(dimensions, majority, coordinates));
    }

    SignalType valueAt(uint64_t index) {
        return array.at(index);
    }

    uint64_t getIndex4Coordinates(std::vector<int64_t> coordinates) {
        return computeIndex4Coordinates(dimensions, majority, coordinates);
    }

    uint64_t getIndex4Coordinates(std::initializer_list<int64_t> coordinates) {
        return computeIndex4Coordinates(dimensions, majority, coordinates);
    }

    std::vector<int64_t> getCoordinate4Index(uint64_t pos) {
        return computeCoordinate4Index(dimensions, majority, pos);
    }

    std::vector<uint8_t> toBuffer(SignalMatrixStorageMajority outputMajority = SignalMatrixStorageMajority::UndefinedMajority) const {
        std::vector<uint8_t> vout;
        vout.reserve(array.size() * sizeof(SignalType) + 50);
        std::string header_version("BBv2");
        std::copy(header_version.cbegin(), header_version.cend(), std::back_inserter(vout));
        vout.emplace_back(dimensions.size());
        for (const auto &dimension: dimensions) {
            std::copy((uint8_t *) &dimension, ((uint8_t *) &dimension) + sizeof(dimension), std::back_inserter(vout));
        }

        vout.emplace_back(is_std_complex<SignalType>::value ? 'C' : 'R');
        vout.emplace_back(getTypeChar<SignalElementType>());
        vout.emplace_back(sizeof(SignalElementType) * 8);

        outputMajority = outputMajority == SignalMatrixStorageMajority::UndefinedMajority ? majority : outputMajority;
        switch (outputMajority) {
            case SignalMatrixStorageMajority::RowMajor:
                vout.emplace_back('R');
                break;
            case SignalMatrixStorageMajority::ColumnMajor:
                vout.emplace_back('C');
                break;
            case SignalMatrixStorageMajority::UndefinedMajority:
                throw std::runtime_error("SignalMatrix::toBuffer failed due to unsupported storage majority.");
        }

        if (majority == outputMajority) {
            for (const auto &value : array) {
                std::copy((uint8_t *) &value, (uint8_t *) &value + sizeof(SignalType), std::back_inserter(vout));
            }
        } else {
            for (uint64_t i = 0; i < array.size(); i++) {
                auto pos = computePositionUnderInversedMajority(i, dimensions);
                std::copy((uint8_t *) &array[pos], ((uint8_t *) &array[pos]) + sizeof(SignalType), std::back_inserter(vout));
            }
        }

        return vout;
    }

    template<typename ContainerType, typename = std::enable_if_t<std::is_same_v<typename ContainerType::value_type, uint8_t>>>
    static SignalMatrix<SignalType> fromBuffer(const ContainerType &container, SignalMatrixStorageMajority storageMajority = SignalMatrixStorageMajority::UndefinedMajority) {
        return fromBuffer(container.begin(), container.end(), storageMajority);
    }

    template<typename Iterator, typename = std::enable_if_t<std::is_same_v<typename std::iterator_traits<Iterator>::value_type, uint8_t>>>
    static SignalMatrix<SignalType> fromBuffer(Iterator begin, Iterator end, SignalMatrixStorageMajority storageMajority) {
        if (!verifyCompatibility(begin)) {
            throw std::runtime_error("Incompatible SignalMatrix format");
        }

        auto matrixVersion = getMatrixVersionId(begin);
        begin += 4;
        SignalMatrix<SignalType> signal;
        uint8_t numDimensions = *begin++;
        for (auto i = 0; i < numDimensions; i++) {
            if (matrixVersion == 1) {
                auto v = *(uint32_t *) (&(*begin));
                signal.dimensions.emplace_back(v);
                begin += 4;
            } else if (matrixVersion == 2) {
                auto v = *(uint64_t *) (&(*begin));
                signal.dimensions.emplace_back(v);
                begin += 8;
            }
        }
        auto complexChar = (char) *begin++;
        auto inputComplexityChar = (is_std_complex<SignalType>::value ? 'C' : 'R');
        if (inputComplexityChar != complexChar) {
            throw std::runtime_error("Incompatible SignalMatrix complexity");
        }

        auto typeChar = (char) *begin++;
        if (typeChar != getTypeChar<SignalElementType>()) {
            throw std::runtime_error("Incompatible SignalMatrix value type");
        }

        auto numTypeBits = *begin++;
        if (numTypeBits != sizeof(SignalElementType) * 8) {
            throw std::runtime_error("Incompatible SignalMatrix value sizeof");
        }

        auto majorityChar = (char) *begin++;
        auto inputMajority = SignalMatrixStorageMajority(majorityChar);
        signal.majority = (storageMajority == SignalMatrixStorageMajority::UndefinedMajority ? inputMajority : storageMajority);

        auto numel = std::accumulate(signal.dimensions.cbegin(), signal.dimensions.cend(), 1, std::multiplies<>());
        auto distanceIterator = (uint64_t) std::distance(begin, end);
        if (distanceIterator != numel * sizeof(SignalType))
            throw std::runtime_error("Inconsistent SignalMatrix data buffer");
        signal.array.resize(numel);

        if (signal.majority == inputMajority) {
            for (auto i = 0; i < numel; i++) {
                signal.array[i] = *(SignalType *) (&(*begin));
                begin += sizeof(SignalType);
            }
        } else {
            for (auto i = 0; i < numel; i++) {
                auto newPos = computePositionUnderInversedMajority(i, signal.dimensions);
                signal.array[newPos] = *(SignalType *) (&(*begin));
                begin += sizeof(SignalType);
            }
        }

        return signal;
    }

    double normalize(double normBaseValue = std::is_floating_point_v<SignalElementType> ? 1.0 : std::numeric_limits<SignalElementType>::max()) {
        const auto &maxValue = std::max_element(array.cbegin(), array.cend(), [](const SignalType &left, const SignalType &right) {
            return std::abs(left) < std::abs(right);
        });
        auto scaleFactor = normBaseValue / std::abs(*maxValue);


        std::transform(array.cbegin(), array.cend(), array.begin(), [scaleFactor](const SignalType &signalVlaue) {
            auto newValue = signalVlaue * scaleFactor;
            return newValue;
        });

        return scaleFactor;
    }

    static SignalMatrix<SignalType> fromFile(const std::string &filePath) {
        auto inputStream = std::ifstream(filePath, std::ios::binary | std::ios::in);
        std::vector<uint8_t> buffer(std::istreambuf_iterator<char>(inputStream), {});
        auto parseResult = SignalMatrix<SignalType>::fromBuffer(buffer, SignalMatrixStorageMajority::UndefinedMajority);
        return parseResult;
    }

    void dump2File(const std::string &filePath, SignalMatrixStorageMajority outputMajority = SignalMatrixStorageMajority::UndefinedMajority) const {
        auto outputStream = std::ofstream(filePath, std::ios::binary | std::ios::out);
        auto bufferV = toBuffer(outputMajority);
        std::ostream_iterator<uint8_t> ostreamIterator(outputStream);
        std::copy(bufferV.cbegin(), bufferV.cend(), ostreamIterator);
        outputStream.flush();
        outputStream.close();
    }

private:
    template<typename Iterator>
    static bool verifyCompatibility(const Iterator &inputBegin) {
        char fileHeader[3];
        char fileVersion[3];
        memset(fileHeader, 0, sizeof(fileHeader));
        memset(fileVersion, 0, sizeof(fileVersion));
        auto begin = inputBegin;
        std::copy(begin, begin + 2, std::begin(fileHeader));
        begin += 2;
        std::copy(begin, begin + 2, std::begin(fileVersion));
        begin += 2;
        return std::strcmp(fileHeader, "BB") == 0 && (std::strcmp(fileVersion, "v1") == 0 || std::strcmp(fileVersion, "v2") == 0);
    }

    template<typename Iterator>
    static uint8_t getMatrixVersionId(const Iterator &begin) {
        uint8_t fileVersionId;
        std::copy(begin + 3, begin + 4, &fileVersionId);
        return fileVersionId - 48;
    }

    template<typename TypeForChecking>
    static char getTypeChar() {
        if (std::is_same_v<TypeForChecking, float>) { return 'F'; }
        else if (std::is_same_v<TypeForChecking, double>) { return 'D'; }
        else if (std::is_same_v<TypeForChecking, uint8_t>) { return 'U'; }
        else if (std::is_same_v<TypeForChecking, uint16_t>) { return 'U'; }
        else if (std::is_same_v<TypeForChecking, uint32_t>) { return 'U'; }
        else if (std::is_same_v<TypeForChecking, uint64_t>) { return 'U'; }
        else if (std::is_same_v<TypeForChecking, int8_t>) { return 'I'; }
        else if (std::is_same_v<TypeForChecking, int16_t>) { return 'I'; }
        else if (std::is_same_v<TypeForChecking, int32_t>) { return 'I'; }
        else if (std::is_same_v<TypeForChecking, int64_t>) { return 'I'; }
        else if (std::is_same_v<TypeForChecking, char>) { return 'C'; }
        else if (std::is_same_v<TypeForChecking, bool>) { return 'L'; }
        throw std::runtime_error("BBSignalsFileWriter: unsupported element type.");
    };

    static uint64_t computeIndex4Coordinates(const std::vector<int64_t> &originalDimensions, SignalMatrixStorageMajority majorityV, const std::vector<int64_t> &coordinates) {
        auto dimensions = originalDimensions;
        auto coord = coordinates;
        if (majorityV == SignalMatrixStorageMajority::ColumnMajor) {
            std::reverse(coord.begin(), coord.end());
            std::reverse(dimensions.begin(), dimensions.end());
        }

        uint64_t pos = 0;
        for (auto i = 0; i < coord.size(); i++) {
            auto numElementsPerDimension = std::accumulate(dimensions.cbegin(), dimensions.cbegin() + i, 1, std::multiplies<>());
            pos += numElementsPerDimension * coord[i];
        }
        return pos;
    }

    static std::vector<int64_t> computeCoordinate4Index(const std::vector<int64_t> &originalDimensions, SignalMatrixStorageMajority majorityV, uint64_t pos) {
        std::vector<int64_t> coordinates(originalDimensions.size());
        auto dimensions = originalDimensions;
        auto inputPos = pos;

        if (majorityV == SignalMatrixStorageMajority::ColumnMajor) {
            std::reverse(dimensions.begin(), dimensions.end());
        }

        for (int64_t i = dimensions.size() - 1; i >= 0; i--) {
            auto numElementsPerDimension = std::accumulate(dimensions.cbegin(), dimensions.cbegin() + i, 1, std::multiplies<>());
            coordinates[i] = inputPos / numElementsPerDimension;
            inputPos %= numElementsPerDimension;
        }

        if (majorityV == SignalMatrixStorageMajority::ColumnMajor) {
            std::reverse(coordinates.begin(), coordinates.end());
        }

        return coordinates;
    }

    static uint64_t computePositionUnderInversedMajority(uint64_t newPos, const std::vector<int64_t> &originalDimensions) {
        auto revD = originalDimensions;
        std::reverse(revD.begin(), revD.end());
        std::vector<uint64_t> coordinates(revD.size(), 0);
        auto inputPos = newPos;
        for (uint64_t i = 1; i <= revD.size(); i++) {
            auto numElementsPerDimension = std::accumulate(revD.cbegin(), revD.cend() - i, 1, std::multiplies<>());
            coordinates[originalDimensions.size() - i] = inputPos / numElementsPerDimension;
            inputPos %= numElementsPerDimension;
        }
        auto oldCoordinates = coordinates;
        std::reverse(oldCoordinates.begin(), oldCoordinates.end());

        auto oldPos = 0;
        for (uint64_t i = 0; i < coordinates.size(); i++) {
            auto numElementsPerDimension = std::accumulate(originalDimensions.cbegin(), originalDimensions.cbegin() + i, 1, std::multiplies<>());
            oldPos += numElementsPerDimension * oldCoordinates[i];
        }

        return oldPos;
    };
};

template<typename SignalType>
void operator<<(SignalMatrix<SignalType> &signalMatrix, const std::string &filePath) {
    signalMatrix = SignalMatrix<SignalType>::fromFile(filePath);
};


template<typename SignalType>
void operator>>(const SignalMatrix<SignalType> &signalMatrix, const std::string &filePath) {
    signalMatrix.dump2File(filePath);
};


#endif //PICOSCENES_PLATFORM_SIGNALMATRIX_HXX
