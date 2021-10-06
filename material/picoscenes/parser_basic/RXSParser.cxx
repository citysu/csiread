#include "../rxs_parsing_core/ModularPicoScenesFrame.hxx"

/**
 * This code performs the following 3 things:
 * 1. invokes 'rxs_parsing_core' to parse the raw RXS data entry
 * 2. further translate the result C++ struct into MATLAB mxArray struct
 * 3. return the MATLAB mxArray to MATLAB
 * 
 * The portal of this code is 'mexFunction' at the bottom.
 * 
 */

template <typename ValueType>
mxArray *createScalarMxArray(const ValueType &value) {
    mxClassID classId = mxDOUBLE_CLASS;
    mxArray *valueArray;
    if constexpr (std::is_same<ValueType, double>::value) {
        classId = mxDOUBLE_CLASS;
    } else if constexpr (std::is_same<ValueType, float>::value) {
        classId = mxSINGLE_CLASS;
    } else if constexpr (std::is_same<ValueType, uint64_t>::value) {
        classId = mxUINT64_CLASS;
    } else if constexpr (std::is_same<ValueType, uint32_t>::value) {
        classId = mxUINT32_CLASS;
    } else if constexpr (std::is_same<ValueType, uint16_t>::value) {
        classId = mxUINT16_CLASS;
    } else if constexpr (std::is_same<ValueType, uint8_t>::value) {
        classId = mxUINT8_CLASS;
    } else if constexpr (std::is_same<ValueType, bool>::value) {
        classId = mxUINT8_CLASS;
    } else if constexpr (std::is_same<ValueType, int64_t>::value) {
        classId = mxINT64_CLASS;
    } else if constexpr (std::is_same<ValueType, int32_t>::value) {
        classId = mxINT32_CLASS;
    } else if constexpr (std::is_same<ValueType, int16_t>::value) {
        classId = mxINT16_CLASS;
    } else if constexpr (std::is_same<ValueType, int8_t>::value) {
        classId = mxINT8_CLASS;
    }

    valueArray = mxCreateNumericMatrix(1, 1, classId, mxREAL);
    auto *ptrR = (ValueType *)mxGetPr(valueArray);
    *ptrR = value;
    return valueArray;
}

template <typename TargetType, typename SourceType>
mxArray *copyComplexData2MxArray(const std::complex<SourceType> sourceArray[], mwSize numElements, mwSize ndim, const mwSize * dims) {
    mxArray *targetArray = nullptr;
    if constexpr (std::is_same<SourceType, double>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxDOUBLE_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, float>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxSINGLE_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, uint64_t>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxUINT64_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, uint32_t>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxUINT32_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, uint16_t>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxUINT16_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, uint8_t>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxUINT8_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, int64_t>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxINT64_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, int32_t>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxINT32_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, int16_t>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxINT16_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, int8_t>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxINT8_CLASS, mxCOMPLEX);
    }

    TargetType *realValue, *imagValue;
    realValue = (TargetType *)mxMalloc(numElements * sizeof(TargetType));
    imagValue = (TargetType *)mxMalloc(numElements * sizeof(TargetType));
    for (uint32_t index = 0; index < numElements; index++) {
        realValue[index] = static_cast<TargetType>(sourceArray[index].real());
        imagValue[index] = static_cast<TargetType>(sourceArray[index].imag());
    }
    mxSetPr(targetArray, (double *)realValue);
    mxSetPi(targetArray, (double *)imagValue);

    return targetArray;
}

template <typename TargetType, typename SourceType, bool columnMajor = false>
mxArray *copyData2MxArray(const SourceType sourceArray[], mwSize numElements, mwSize ndim, const mwSize * dims) {
    mxArray *targetArray = nullptr;
    if constexpr (std::is_same<SourceType, double>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxDOUBLE_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, float>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxSINGLE_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, uint64_t>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxUINT64_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, uint32_t>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxUINT32_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, uint16_t>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxUINT16_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, uint8_t>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxUINT8_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, int64_t>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxINT64_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, int32_t>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxINT32_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, int16_t>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxINT16_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, int8_t>::value) {
        targetArray = mxCreateNumericArray(ndim, dims, mxINT8_CLASS, mxREAL);
    }

    TargetType *realValue;
    realValue = (TargetType *)mxMalloc(numElements * sizeof(TargetType));
    for (uint32_t index = 0; index < numElements; index++) {
        realValue[index] = static_cast<TargetType>(sourceArray[index]);
    }
    mxSetPr(targetArray, (double *)realValue);

    return targetArray;
}

template <typename TargetType, typename SourceType>
mxArray *copyComplexData2MxArray(const std::complex<SourceType> sourceArray[], uint32_t numElements) {
    mxArray *targetArray = nullptr;
    if constexpr (std::is_same<SourceType, double>::value) {
        targetArray = mxCreateNumericMatrix(1, numElements, mxDOUBLE_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, float>::value) {
        targetArray = mxCreateNumericMatrix(1, numElements, mxSINGLE_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, uint64_t>::value) {
        targetArray = mxCreateNumericMatrix(1, numElements, mxUINT64_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, uint32_t>::value) {
        targetArray = mxCreateNumericMatrix(1, numElements, mxUINT32_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, uint16_t>::value) {
        targetArray = mxCreateNumericMatrix(1, numElements, mxUINT16_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, uint8_t>::value) {
        targetArray = mxCreateNumericMatrix(1, numElements, mxUINT8_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, int64_t>::value) {
        targetArray = mxCreateNumericMatrix(1, numElements, mxINT64_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, int32_t>::value) {
        targetArray = mxCreateNumericMatrix(1, numElements, mxINT32_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, int16_t>::value) {
        targetArray = mxCreateNumericMatrix(1, numElements, mxINT16_CLASS, mxCOMPLEX);
    } else if constexpr (std::is_same<SourceType, int8_t>::value) {
        targetArray = mxCreateNumericMatrix(1, numElements, mxINT8_CLASS, mxCOMPLEX);
    }

    TargetType *realValue, *imagValue;
    realValue = (TargetType *)mxMalloc(numElements * sizeof(TargetType));
    imagValue = (TargetType *)mxMalloc(numElements * sizeof(TargetType));
    for (uint32_t index = 0; index < numElements; index++) {
        realValue[index] = static_cast<TargetType>(sourceArray[index].real());
        imagValue[index] = static_cast<TargetType>(sourceArray[index].imag());
    }
    mxSetPr(targetArray, (double *)realValue);
    mxSetPi(targetArray, (double *)imagValue);

    return targetArray;
}

template <typename TargetType, typename SourceType, bool columnMajor = false>
mxArray *copyData2MxArray(const SourceType sourceArray[], uint32_t numElements) {
    mxArray *targetArray = nullptr;
    if constexpr (std::is_same<SourceType, double>::value) {
        targetArray = mxCreateNumericMatrix(columnMajor ? numElements : 1, columnMajor ? 1 : numElements, mxDOUBLE_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, float>::value) {
        targetArray = mxCreateNumericMatrix(columnMajor ? numElements : 1, columnMajor ? 1 : numElements, mxSINGLE_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, uint64_t>::value) {
        targetArray = mxCreateNumericMatrix(columnMajor ? numElements : 1, columnMajor ? 1 : numElements, mxUINT64_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, uint32_t>::value) {
        targetArray = mxCreateNumericMatrix(columnMajor ? numElements : 1, columnMajor ? 1 : numElements, mxUINT32_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, uint16_t>::value) {
        targetArray = mxCreateNumericMatrix(columnMajor ? numElements : 1, columnMajor ? 1 : numElements, mxUINT16_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, uint8_t>::value) {
        targetArray = mxCreateNumericMatrix(columnMajor ? numElements : 1, columnMajor ? 1 : numElements, mxUINT8_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, int64_t>::value) {
        targetArray = mxCreateNumericMatrix(columnMajor ? numElements : 1, columnMajor ? 1 : numElements, mxINT64_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, int32_t>::value) {
        targetArray = mxCreateNumericMatrix(columnMajor ? numElements : 1, columnMajor ? 1 : numElements, mxINT32_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, int16_t>::value) {
        targetArray = mxCreateNumericMatrix(columnMajor ? numElements : 1, columnMajor ? 1 : numElements, mxINT16_CLASS, mxREAL);
    } else if constexpr (std::is_same<SourceType, int8_t>::value) {
        targetArray = mxCreateNumericMatrix(columnMajor ? numElements : 1, columnMajor ? 1 : numElements, mxINT8_CLASS, mxREAL);
    }

    TargetType *realValue;
    realValue = (TargetType *)mxMalloc(numElements * sizeof(TargetType));
    for (uint32_t index = 0; index < numElements; index++) {
        realValue[index] = static_cast<TargetType>(sourceArray[index]);
    }
    mxSetPr(targetArray, (double *)realValue);

    return targetArray;
}

mxArray *convertBasebandSignal2MxArray(const BasebandSignalSegment &bbSegment) {
    auto bbArray = mxCreateNumericMatrix(bbSegment.getSignalMatrix().dimensions[0], bbSegment.getSignalMatrix().dimensions[1], mxDOUBLE_CLASS, mxCOMPLEX);
    auto numElements = bbSegment.getSignalMatrix().array.size();
    auto realValue = (double *)mxMalloc(numElements * sizeof(double));
    auto imagValue = (double *)mxMalloc(numElements * sizeof(double));
    for (uint32_t index = 0; index < numElements; index++) {
        realValue[index] = static_cast<double>(bbSegment.getSignalMatrix().array[index].real());
        imagValue[index] = static_cast<double>(bbSegment.getSignalMatrix().array[index].imag());
    }
    mxSetPr(bbArray, (double *)realValue);
    mxSetPi(bbArray, (double *)imagValue);

    return bbArray;
}

mxArray *convertPreEQSymbols2MxArray(const PreEQSymbolsSegment &preEQSymbolsSegment) {
    std::vector<mwSize> mwDimensions;
    for(const auto &dim: preEQSymbolsSegment.getPreEqSymbols().dimensions) {
        mwDimensions.emplace_back(dim);
    }
    auto preEQArray = mxCreateNumericArray(mwDimensions.size(), mwDimensions.data(), mxDOUBLE_CLASS, mxCOMPLEX);
    auto numElements = preEQSymbolsSegment.getPreEqSymbols().array.size();
    auto realValue = (double *)mxMalloc(numElements * sizeof(double));
    auto imagValue = (double *)mxMalloc(numElements * sizeof(double));
    for (uint32_t index = 0; index < numElements; index++) {
        realValue[index] = static_cast<double>(preEQSymbolsSegment.getPreEqSymbols().array[index].real());
        imagValue[index] = static_cast<double>(preEQSymbolsSegment.getPreEqSymbols().array[index].imag());
    }
    mxSetPr(preEQArray, (double *)realValue);
    mxSetPi(preEQArray, (double *)imagValue);

    return preEQArray;
}

mxArray *convertStandardHeader2MxArray(const ieee80211_mac_frame_header &standardHeader) {
    auto *standardHeaderArray = mxCreateStructMatrix(1, 1, 0, NULL);

    // add Control Field
    auto *controlField = mxCreateStructMatrix(1, 1, 0, NULL);
    mxSetFieldByNumber(controlField, 0, mxAddField(controlField, "Version"), createScalarMxArray(standardHeader.fc.version));
    mxSetFieldByNumber(controlField, 0, mxAddField(controlField, "Type"), createScalarMxArray(standardHeader.fc.type));
    mxSetFieldByNumber(controlField, 0, mxAddField(controlField, "SubType"), createScalarMxArray(standardHeader.fc.subtype));
    mxSetFieldByNumber(controlField, 0, mxAddField(controlField, "ToDS"), createScalarMxArray(standardHeader.fc.toDS));
    mxSetFieldByNumber(controlField, 0, mxAddField(controlField, "FromDS"), createScalarMxArray(standardHeader.fc.fromDS));
    mxSetFieldByNumber(controlField, 0, mxAddField(controlField, "MoreFrags"), createScalarMxArray(standardHeader.fc.moreFrags));
    mxSetFieldByNumber(controlField, 0, mxAddField(controlField, "Retry"), createScalarMxArray(standardHeader.fc.retry));
    mxSetFieldByNumber(controlField, 0, mxAddField(controlField, "PowerManagement"), createScalarMxArray(standardHeader.fc.power_mgmt));
    mxSetFieldByNumber(controlField, 0, mxAddField(controlField, "More"), createScalarMxArray(standardHeader.fc.more));
    mxSetFieldByNumber(controlField, 0, mxAddField(controlField, "Protected"), createScalarMxArray(standardHeader.fc.protect));
    mxSetFieldByNumber(controlField, 0, mxAddField(controlField, "Order"), createScalarMxArray(standardHeader.fc.order));
    mxSetFieldByNumber(standardHeaderArray, 0, mxAddField(standardHeaderArray, "ControlField"), controlField);

    // add 3 MAC addresses
    mxArray *addr1 = mxCreateNumericMatrix(1, 6, mxUINT8_CLASS, mxREAL);
    mxArray *addr2 = mxCreateNumericMatrix(1, 6, mxUINT8_CLASS, mxREAL);
    mxArray *addr3 = mxCreateNumericMatrix(1, 6, mxUINT8_CLASS, mxREAL);
    std::copy(std::begin(standardHeader.addr1), std::end(standardHeader.addr1), (uint8_T *)mxGetPr(addr1));
    std::copy(std::begin(standardHeader.addr2), std::end(standardHeader.addr2), (uint8_T *)mxGetPr(addr2));
    std::copy(std::begin(standardHeader.addr3), std::end(standardHeader.addr3), (uint8_T *)mxGetPr(addr3));
    mxSetFieldByNumber(standardHeaderArray, 0, mxAddField(standardHeaderArray, "Addr1"), addr1);
    mxSetFieldByNumber(standardHeaderArray, 0, mxAddField(standardHeaderArray, "Addr2"), addr2);
    mxSetFieldByNumber(standardHeaderArray, 0, mxAddField(standardHeaderArray, "Addr3"), addr3);

    // add frag and sequence
    mxSetFieldByNumber(standardHeaderArray, 0, mxAddField(standardHeaderArray, "Fragment"), createScalarMxArray(standardHeader.frag));
    mxSetFieldByNumber(standardHeaderArray, 0, mxAddField(standardHeaderArray, "Sequence"), createScalarMxArray(standardHeader.seq));

    return standardHeaderArray;
}

mxArray *convertPicoScenesHeader2MxArray(const PicoScenesFrameHeader &header) {
    auto *PicoScenesFrameHeaderArray = mxCreateStructMatrix(1, 1, 0, NULL);

    // add frag and sequence
    mxSetFieldByNumber(PicoScenesFrameHeaderArray, 0, mxAddField(PicoScenesFrameHeaderArray, "MagicValue"), createScalarMxArray(header.magicValue));
    mxSetFieldByNumber(PicoScenesFrameHeaderArray, 0, mxAddField(PicoScenesFrameHeaderArray, "Version"), createScalarMxArray(header.version));
    mxSetFieldByNumber(PicoScenesFrameHeaderArray, 0, mxAddField(PicoScenesFrameHeaderArray, "DeviceType"), createScalarMxArray(uint16_t(header.deviceType)));
    mxSetFieldByNumber(PicoScenesFrameHeaderArray, 0, mxAddField(PicoScenesFrameHeaderArray, "FrameType"), createScalarMxArray(header.frameType));
    mxSetFieldByNumber(PicoScenesFrameHeaderArray, 0, mxAddField(PicoScenesFrameHeaderArray, "TaskId"), createScalarMxArray(header.taskId));
    mxSetFieldByNumber(PicoScenesFrameHeaderArray, 0, mxAddField(PicoScenesFrameHeaderArray, "TxId"), createScalarMxArray(header.txId));

    return PicoScenesFrameHeaderArray;
}

mxArray *convertRxSBasic2MxArray(const RxSBasic &basic) {
    auto *rxsArray = mxCreateStructMatrix(1, 1, 0, NULL);
    mxSetFieldByNumber(rxsArray, 0, mxAddField(rxsArray, "deviceType"), createScalarMxArray(basic.deviceType));
    mxSetFieldByNumber(rxsArray, 0, mxAddField(rxsArray, "timestamp"), createScalarMxArray(basic.tstamp));
    mxSetFieldByNumber(rxsArray, 0, mxAddField(rxsArray, "centerFreq"), createScalarMxArray(basic.centerFreq));
    mxSetFieldByNumber(rxsArray, 0, mxAddField(rxsArray, "controlFreq"), createScalarMxArray(basic.controlFreq));
    mxSetFieldByNumber(rxsArray, 0, mxAddField(rxsArray, "CBW"), createScalarMxArray(basic.cbw));
    mxSetFieldByNumber(rxsArray, 0, mxAddField(rxsArray, "packetFormat"), createScalarMxArray(basic.packetFormat));
    mxSetFieldByNumber(rxsArray, 0, mxAddField(rxsArray, "packetCBW"), createScalarMxArray(basic.pkt_cbw));
    mxSetFieldByNumber(rxsArray, 0, mxAddField(rxsArray, "GI"), createScalarMxArray(basic.guardInterval));
    mxSetFieldByNumber(rxsArray, 0, mxAddField(rxsArray, "MCS"), createScalarMxArray(basic.mcs));
    mxSetFieldByNumber(rxsArray, 0, mxAddField(rxsArray, "numSTS"), createScalarMxArray(basic.numSTS));
    mxSetFieldByNumber(rxsArray, 0, mxAddField(rxsArray, "numESS"), createScalarMxArray(basic.numESS));
    mxSetFieldByNumber(rxsArray, 0, mxAddField(rxsArray, "numRx"), createScalarMxArray(basic.numRx));
    mxSetFieldByNumber(rxsArray, 0, mxAddField(rxsArray, "noiseFloor"), createScalarMxArray(basic.noiseFloor));
    mxSetFieldByNumber(rxsArray, 0, mxAddField(rxsArray, "rssi"), createScalarMxArray(basic.rssi));
    mxSetFieldByNumber(rxsArray, 0, mxAddField(rxsArray, "rssi1"), createScalarMxArray(basic.rssi_ctl0));
    mxSetFieldByNumber(rxsArray, 0, mxAddField(rxsArray, "rssi2"), createScalarMxArray(basic.rssi_ctl1));
    mxSetFieldByNumber(rxsArray, 0, mxAddField(rxsArray, "rssi3"), createScalarMxArray(basic.rssi_ctl2));

    return rxsArray;
}

void transformExtraInfo2MatlabStruct(const ExtraInfo &ei, mxArray *mxExtraInfo) {
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasLength"), createScalarMxArray(ei.hasLength));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasVersion"), createScalarMxArray(ei.hasVersion));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasMacAddr_cur"), createScalarMxArray(ei.hasMacAddr_cur));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasMacAddr_rom"), createScalarMxArray(ei.hasMacAddr_rom));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasChansel"), createScalarMxArray(ei.hasChansel));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasBMode"), createScalarMxArray(ei.hasBMode));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasEVM"), createScalarMxArray(ei.hasEVM));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasTxChainMask"), createScalarMxArray(ei.hasTxChainMask));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasRxChainMask"), createScalarMxArray(ei.hasRxChainMask));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasTxpower"), createScalarMxArray(ei.hasTxpower));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasCFO"), createScalarMxArray(ei.hasCFO));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasTxTSF"), createScalarMxArray(ei.hasTxTSF));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasLastHwTxTSF"), createScalarMxArray(ei.hasLastHWTxTSF));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasChannelFlags"), createScalarMxArray(ei.hasChannelFlags));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasTxNess"), createScalarMxArray(ei.hasTxNess));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasTuningPolicy"), createScalarMxArray(ei.hasTuningPolicy));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasPLLRate"), createScalarMxArray(ei.hasPLLRate));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasPLLClkSel"), createScalarMxArray(ei.hasPLLClkSel));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasPLLRefDiv"), createScalarMxArray(ei.hasPLLRefDiv));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasAGC"), createScalarMxArray(ei.hasAGC));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasAntennaSelection"), createScalarMxArray(ei.hasAntennaSelection));
    mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "hasSamplingRate"), createScalarMxArray(ei.hasSamplingRate));

    if (ei.hasLength) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "length"), createScalarMxArray(ei.length));
    }
    if (ei.hasVersion) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "version"), createScalarMxArray(ei.version));
    }
    if (ei.hasMacAddr_cur) {
        mxArray *macaddr_cur = mxCreateNumericMatrix(1, 3, mxUINT8_CLASS, mxREAL);
        auto *ptrR = (uint8_T *)mxGetPr(macaddr_cur);
        ptrR[0] = ei.macaddr_cur[0];
        ptrR[1] = ei.macaddr_cur[1];
        ptrR[2] = ei.macaddr_cur[2];
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "macaddr_cur"), macaddr_cur);
    }
    if (ei.hasMacAddr_rom) {
        mxArray *macaddr_rom = mxCreateNumericMatrix(1, 3, mxUINT8_CLASS, mxREAL);
        auto *ptrR = (uint8_T *)mxGetPr(macaddr_rom);
        ptrR[0] = ei.macaddr_rom[0];
        ptrR[1] = ei.macaddr_rom[1];
        ptrR[2] = ei.macaddr_rom[2];
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "macaddr_rom"), macaddr_rom);
    }
    if (ei.hasChansel) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "chansel"), createScalarMxArray(ei.chansel));
    }
    if (ei.hasBMode) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "bmode"), createScalarMxArray(ei.bmode));
    }
    if (ei.hasEVM) {
        auto *evmMxArray = mxCreateNumericMatrix(1, 18, mxINT8_CLASS, mxREAL);
        auto *ptrR = (int8_T *)mxGetPr(evmMxArray);
        for (auto i = 0; i < 18; i++) {
            ptrR[i] = ei.evm[i];
        }
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "evm"), evmMxArray);
    }
    if (ei.hasTxChainMask) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "tx_chainmask"), createScalarMxArray(ei.txChainMask));
    }
    if (ei.hasRxChainMask) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "rx_chainmask"), createScalarMxArray(ei.rxChainMask));
    }
    if (ei.hasTxpower) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "txpower"), createScalarMxArray(ei.txpower));
    }
    if (ei.hasCF) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "cf"), createScalarMxArray(ei.cf));
    }
    if (ei.hasTxTSF) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "txtsf"), createScalarMxArray(ei.txTSF));
    }
    if (ei.hasLastHWTxTSF) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "last_txtsf"), createScalarMxArray(ei.lastHwTxTSF));
    }
    if (ei.hasChannelFlags) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "channel_flags"), createScalarMxArray(ei.channelFlags));
    }
    if (ei.hasTxNess) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "tx_ness"), createScalarMxArray(ei.tx_ness));
    }
    if (ei.hasTuningPolicy) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "tuning_policy"), createScalarMxArray(uint8_t(ei.tuningPolicy)));
    }
    if (ei.hasPLLRate) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "pll_rate"), createScalarMxArray(ei.pll_rate));
    }
    if (ei.hasPLLClkSel) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "pll_clock_select"), createScalarMxArray(ei.pll_clock_select));
    }
    if (ei.hasPLLRefDiv) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "pll_refdiv"), createScalarMxArray(ei.pll_refdiv));
    }
    if (ei.hasAGC) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "agc"), createScalarMxArray(ei.agc));
    }
    if (ei.hasAntennaSelection) {
        auto *antSelMxArray = mxCreateNumericMatrix(1, 3, mxUINT8_CLASS, mxREAL);
        auto *ptrR = (int8_T *)mxGetPr(antSelMxArray);
        for (auto i = 0; i < 3; i++) {
            ptrR[i] = ei.ant_sel[i];
        }
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "ant_sel"), antSelMxArray);
    }
    if (ei.hasSamplingRate) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "sf"), createScalarMxArray(ei.samplingRate));
    }
    if (ei.hasCFO) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "cfo"), createScalarMxArray(double(ei.cfo)));
    }
    if (ei.hasSFO) {
        mxSetFieldByNumber(mxExtraInfo, 0, mxAddField(mxExtraInfo, "sfo"), createScalarMxArray(double(ei.sfo)));
    }
}

mxArray *convertExtraInfo2MxArray(const ExtraInfo &ei) {
    auto *array = mxCreateStructMatrix(1, 1, 0, NULL);
    transformExtraInfo2MatlabStruct(ei, array);
    return array;
}

mxArray *convertCSISegment2MxArray(const CSISegment &csiSegment) {
    mxArray *groupCell = mxCreateStructMatrix(1, 1, 0, NULL);
    for (uint32_t csiGroupIndex = 0; csiGroupIndex < 1; csiGroupIndex++) {
        const auto &csi = csiSegment.getCSI();

        mxSetFieldByNumber(groupCell, csiGroupIndex, mxAddField(groupCell, "DeviceType"), createScalarMxArray(double(csi.deviceType)));
        mxSetFieldByNumber(groupCell, csiGroupIndex, mxAddField(groupCell, "PacketFormat"), createScalarMxArray(double(csi.packetFormat)));
        mxSetFieldByNumber(groupCell, csiGroupIndex, mxAddField(groupCell, "CBW"), createScalarMxArray(double(csi.cbw)));
        mxSetFieldByNumber(groupCell, csiGroupIndex, mxAddField(groupCell, "CarrierFreq"), createScalarMxArray(double(csi.carrierFreq)));
        mxSetFieldByNumber(groupCell, csiGroupIndex, mxAddField(groupCell, "SamplingRate"), createScalarMxArray(double(csi.samplingRate)));
        mxSetFieldByNumber(groupCell, csiGroupIndex, mxAddField(groupCell, "SubcarrierBandwidth"), createScalarMxArray(double(csi.subcarrierBandwidth)));
        mxSetFieldByNumber(groupCell, csiGroupIndex, mxAddField(groupCell, "numTones"), createScalarMxArray(csi.dimensions.numTones));
        mxSetFieldByNumber(groupCell, csiGroupIndex, mxAddField(groupCell, "numTx"), createScalarMxArray(csi.dimensions.numTx));
        mxSetFieldByNumber(groupCell, csiGroupIndex, mxAddField(groupCell, "numRx"), createScalarMxArray(csi.dimensions.numRx));
        mxSetFieldByNumber(groupCell, csiGroupIndex, mxAddField(groupCell, "numESS"), createScalarMxArray(csi.dimensions.numESS));
        mxSetFieldByNumber(groupCell, csiGroupIndex, mxAddField(groupCell, "numCSI"), createScalarMxArray(csi.dimensions.numCSI));
        mxSetFieldByNumber(groupCell, csiGroupIndex, mxAddField(groupCell, "ant_sel"), createScalarMxArray(csi.dimensions.numESS));

        std::vector<mwSize> sizes {csi.dimensions.numTones, mwSize(csi.dimensions.numTx + csi.dimensions.numESS), csi.dimensions.numRx, csi.dimensions.numCSI};

        /*
        * csiData is essentially an N_{sc} x N_{sts} x N_{rx} x N_{CSI} 4-D matrix; The output order is the 1-D reshaped output format, like reshape(csiData, [], 1);
        */
        auto *CSIData = copyComplexData2MxArray<double, double>(&csi.CSIArray.array[0], csi.CSIArray.array.size());
        mxSetFieldByNumber(groupCell, csiGroupIndex, mxAddField(groupCell, "CSI"), CSIData);

        auto *magData = copyData2MxArray<double, double>(&csi.magnitudeArray.array[0], csi.magnitudeArray.array.size());
        mxSetFieldByNumber(groupCell, csiGroupIndex, mxAddField(groupCell, "Mag"), magData);

        auto *phaseData = copyData2MxArray<double, double>(&csi.phaseArray.array[0], csi.phaseArray.array.size());
        mxSetFieldByNumber(groupCell, csiGroupIndex, mxAddField(groupCell, "Phase"), phaseData);

        auto *indexData = copyData2MxArray<int16_t, int16_t>(&csi.subcarrierIndices[0], csi.subcarrierIndices.size());
        mxSetFieldByNumber(groupCell, csiGroupIndex, mxAddField(groupCell, "SubcarrierIndex"), indexData);
    }

    return groupCell;
}

mxArray *convertMVMExtraSegment2MXArray(const IntelMVMParsedCSIHeader &mvmHeader) {
    auto *mvmExtraArray = mxCreateStructMatrix(1, 1, 0, NULL);
    mxSetFieldByNumber(mvmExtraArray, 0, mxAddField(mvmExtraArray, "FMTClock"), createScalarMxArray(mvmHeader.ftmClock));
    mxSetFieldByNumber(mvmExtraArray, 0, mxAddField(mvmExtraArray, "usClock"), createScalarMxArray(mvmHeader.muClock));
    mxSetFieldByNumber(mvmExtraArray, 0, mxAddField(mvmExtraArray, "RateNFlags"), createScalarMxArray(mvmHeader.rate_n_flags));
    return mvmExtraArray;
}

void convertPicoScenesFrame2Struct(ModularPicoScenesRxFrame &frame, mxArray *outCell, int index) {
    auto *standardHeaderArray = convertStandardHeader2MxArray(frame.standardHeader);
    mxSetFieldByNumber(outCell, index, mxAddField(outCell, "StandardHeader"), standardHeaderArray);

    auto *basicArray = convertRxSBasic2MxArray(frame.rxSBasicSegment.getBasic());
    mxSetFieldByNumber(outCell, index, mxAddField(outCell, "RxSBasic"), basicArray);

    auto *rxExtraInfoArray = convertExtraInfo2MxArray(frame.rxExtraInfoSegment.getExtraInfo());
    mxSetFieldByNumber(outCell, index, mxAddField(outCell, "RxExtraInfo"), rxExtraInfoArray);

    if (frame.mvmExtraSegment) {
        auto *mvmExtraArray = convertMVMExtraSegment2MXArray(frame.mvmExtraSegment->getMvmExtra().parsedHeader);
        mxSetFieldByNumber(outCell, index, mxAddField(outCell, "MVMExtra"), mvmExtraArray);
    }

    auto *rxCSIGroups = convertCSISegment2MxArray(frame.csiSegment);
    mxSetFieldByNumber(outCell, index, mxAddField(outCell, "CSI"), rxCSIGroups);

    if (frame.PicoScenesHeader) {
        auto *header = convertPicoScenesHeader2MxArray(*frame.PicoScenesHeader);
        mxSetFieldByNumber(outCell, index, mxAddField(outCell, "PicoScenesHeader"), header);
    } else {
        mxSetFieldByNumber(outCell, index, mxAddField(outCell, "PicoScenesHeader"), mxCreateStructMatrix(1, 1, 0, NULL));
    }

    if (frame.txExtraInfoSegment) {
        auto *txExtraInfoArray = convertExtraInfo2MxArray(frame.txExtraInfoSegment->getExtraInfo());
        mxSetFieldByNumber(outCell, index, mxAddField(outCell, "TxExtraInfo"), txExtraInfoArray);
    } else {
        mxSetFieldByNumber(outCell, index, mxAddField(outCell, "TxExtraInfo"), mxCreateStructMatrix(1, 1, 0, NULL));
    }

    if (frame.pilotCSISegment) {
        if (frame.pilotCSISegment && !frame.pilotCSISegment->getCSI().CSIArray.dimensions.empty() && frame.pilotCSISegment->getCSI().magnitudeArray.dimensions.empty()) {
            std::for_each(frame.pilotCSISegment->getCSI().CSIArray.array.cbegin(), frame.pilotCSISegment->getCSI().CSIArray.array.cend(), [&](const std::complex<double> &csi) {
                frame.pilotCSISegment->getCSI().magnitudeArray.array.emplace_back(std::abs(csi));
                frame.pilotCSISegment->getCSI().phaseArray.array.emplace_back(std::arg(csi));
            });
            frame.pilotCSISegment->getCSI().magnitudeArray.dimensions = frame.pilotCSISegment->getCSI().CSIArray.dimensions;
            frame.pilotCSISegment->getCSI().phaseArray.dimensions = frame.pilotCSISegment->getCSI().CSIArray.dimensions;
        }
        auto *pilotCSICSIGroup = convertCSISegment2MxArray(*frame.pilotCSISegment);
        mxSetFieldByNumber(outCell, index, mxAddField(outCell, "PilotCSI"), pilotCSICSIGroup);
    }

    if (frame.legacyCSISegment) {
        auto *legacyRxCSIGroup = convertCSISegment2MxArray(*frame.legacyCSISegment);
        mxSetFieldByNumber(outCell, index, mxAddField(outCell, "LegacyCSI"), legacyRxCSIGroup);
    }

    if (frame.basebandSignalSegment) {
        auto *basebandSignal = convertBasebandSignal2MxArray(*frame.basebandSignalSegment);
        mxSetFieldByNumber(outCell, index, mxAddField(outCell, "BasebandSignals"), basebandSignal);
    }

    if (frame.preEQSymbolsSegment) {
        auto *preEQSymbols = convertPreEQSymbols2MxArray(*frame.preEQSymbolsSegment);
        mxSetFieldByNumber(outCell, index, mxAddField(outCell, "PreEQSymbols"), preEQSymbols);
    }

    auto *mpduData = copyData2MxArray<uint8_t, uint8_t, true>(frame.mpdu.data(), frame.mpdu.size());
        mxSetFieldByNumber(outCell, index, mxAddField(outCell, "MPDU"), mpduData);
}

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]) {
    /* check for proper number of arguments */
    if (nrhs != 1) {
        mexErrMsgIdAndTxt("Wi-Fi Sensing Toolbox :read_csi:nrhs", "One input required.");
    }
    if (nlhs != 1) {
        mexErrMsgIdAndTxt("Wi-Fi Sensing Toolbox:read_csi:nlhs", "One output required.");
    }
    /* make sure the input argument is a char array */
    if (!mxIsClass(prhs[0], "uint8")) {
        mexErrMsgIdAndTxt("Wi-Fi Sensing Toolbox:read_csi:notBytes", "Input must be a char array");
    }

    uint8_T *inBytes = (uint8_T *)mxGetData(prhs[0]);
    auto bufferLength = mxGetNumberOfElements(prhs[0]);
    if (auto frame = ModularPicoScenesRxFrame::fromBuffer(inBytes, bufferLength, true)) {
        // std::stringstream ss;
        // ss << *frame;
        // printf("rxframe: %s\n", ss.str().c_str());
        mxArray *result;
        if (auto echoProbeReplyIt = std::find_if(frame->payloadSegments.cbegin(), frame->payloadSegments.cend(), [](const PayloadSegment &payloadSegment) {
                return payloadSegment.getPayload().payloadDescription == "EchoProbeReplyCSI" || payloadSegment.getPayload().payloadDescription == "EchoProbeReplyFull";
            });
            echoProbeReplyIt != frame->payloadSegments.cend()) {
            result = mxCreateStructMatrix(2, 1, 0, NULL);
        } else {
            result = mxCreateStructMatrix(1, 1, 0, NULL);
        }

        convertPicoScenesFrame2Struct(*frame, result, 0);

        if (auto echoProbeCSIPayloadIt = std::find_if(frame->payloadSegments.cbegin(), frame->payloadSegments.cend(), [](const PayloadSegment &payloadSegment) {
                return payloadSegment.getPayload().payloadDescription == "EchoProbeReplyCSI";
            });
            echoProbeCSIPayloadIt != frame->payloadSegments.cend()) {
            convertPicoScenesFrame2Struct(*frame, result, 1);  // fake the ack frame for the structual simplicity
            const auto &csiPayload = echoProbeCSIPayloadIt->getPayload().payloadData;
            auto txCSISegment = CSISegment::createByBuffer(csiPayload.data(), csiPayload.size());
            txCSISegment.getCSI().interpolateCSI();
            auto *rxCSIGroups = convertCSISegment2MxArray(txCSISegment);
            mxSetFieldByNumber(result, 1, mxAddField(result, "CSI"), rxCSIGroups);
        }

        if (auto echoProbeFullPacketIt = std::find_if(frame->payloadSegments.cbegin(), frame->payloadSegments.cend(), [](const PayloadSegment &payloadSegment) {
                return payloadSegment.getPayload().payloadDescription == "EchoProbeReplyFull";
            });
            echoProbeFullPacketIt != frame->payloadSegments.cend()) {
            const auto &rxFrameBuffer = echoProbeFullPacketIt->getPayload().payloadData;
            if (auto initiatingFrame = ModularPicoScenesRxFrame::fromBuffer(rxFrameBuffer.data(), rxFrameBuffer.size(), true)) {
                convertPicoScenesFrame2Struct(*initiatingFrame, result, 1);
            }
        }

        plhs[0] = result;
    } else {
        mxArray *emptyArray = mxCreateStructMatrix(1, 1, 0, NULL);
        plhs[0] = emptyArray;
    }
}