//
// Created by 蒋志平 on 2020/11/6.
//

#ifndef PICOSCENES_PLATFORM_PICOSCENESCOMMONS_HXX
#define PICOSCENES_PLATFORM_PICOSCENESCOMMONS_HXX

#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <complex>
#include <numeric>
#include "SignalMatrix.hxx"

#ifdef BUILD_WITH_MEX
#include "mex.h"
#define printf mexPrintf
#endif

using ComplexData = std::complex<double>;
using ComplexFloatData = std::complex<float>;
using ComplexArray = std::vector<ComplexData>;
using ComplexFloatArray = std::vector<ComplexData>;
using Uint8Vector = std::vector<uint8_t>;

enum class PicoScenesDeviceType : uint16_t {
    QCA9300 = 0x9300,
    IWL5300 = 0x5300,
    IWLMVM = 0x2000,
    MAC80211Compatible = 0x802,
    USRP = 0x1234,
    VirtualSDR = 0x1000,
    Unknown = 0x404
};

std::string DeviceType2String(PicoScenesDeviceType type);

std::ostream &operator<<(std::ostream &os, const PicoScenesDeviceType &deviceType);

enum class PacketFormatEnum : int8_t {
    PacketFormat_NonHT = 0,
    PacketFormat_HT = 1,
    PacketFormat_VHT = 2,
    PacketFormat_HESU = 3,
    PacketFormat_HEMU = 4,
    PacketFormat_Unknown = -1
};

std::string PacketFormat2String(PacketFormatEnum format);

std::ostream &operator<<(std::ostream &os, const PacketFormatEnum &format);

enum class ChannelBandwidthEnum : uint16_t {
    CBW_5 = 5,
    CBW_10 = 10,
    CBW_20 = 20,
    CBW_40 = 40,
    CBW_80 = 80,
    CBW_160 = 160,
};

std::string ChannelBandwidth2String(ChannelBandwidthEnum cbw);

std::ostream &operator<<(std::ostream &os, const ChannelBandwidthEnum &cbw);

enum class ChannelModeEnum : uint8_t {
    HT20 = 8,
    HT40_MINUS = 24,
    HT40_PLUS = 40,
};

std::string channelModel2String(ChannelModeEnum mode);

std::ostream &operator<<(std::ostream &os, const ChannelModeEnum &channelMode);

enum class GuardIntervalEnum : uint16_t {
    GI_400 = 400,
    GI_800 = 800,
    GI_1600 = 1600,
    GI_3200 = 3200
};


std::string GuardInterval2String(GuardIntervalEnum gi);

std::ostream &operator<<(std::ostream &os, const GuardIntervalEnum &gi);

enum class ChannelCodingEnum : uint8_t {
    BCC = 0,
    LDPC = 1,
};

std::string ChannelCoding2String(ChannelCodingEnum coding);

std::ostream &operator<<(std::ostream &os, const ChannelCodingEnum &coding);


#endif //PICOSCENES_PLATFORM_PICOSCENESCOMMONS_HXX
