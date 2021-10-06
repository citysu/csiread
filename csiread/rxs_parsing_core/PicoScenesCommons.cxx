//
// Created by 蒋志平 on 2020/11/6.
//

#include "PicoScenesCommons.hxx"

std::string DeviceType2String(PicoScenesDeviceType type) {
    switch (type) {
        case PicoScenesDeviceType::QCA9300:
            return "QCA9300";
        case PicoScenesDeviceType::IWL5300:
            return "IWL5300";
        case PicoScenesDeviceType::MAC80211Compatible:
            return "MAC80211 Compatible NIC";
        case PicoScenesDeviceType::USRP:
            return "USRP(SDR)";
        case PicoScenesDeviceType::VirtualSDR:
            return "Virtual(SDR)";
        case PicoScenesDeviceType::Unknown:
            return "Unknown";
        default:
            throw std::runtime_error("unrecognized PicoScenesDeviceType.");
    }
}


std::string PacketFormat2String(PacketFormatEnum format) {
    switch (format) {
        case PacketFormatEnum::PacketFormat_NonHT:
            return "NonHT";
        case PacketFormatEnum::PacketFormat_HT:
            return "HT";
        case PacketFormatEnum::PacketFormat_VHT:
            return "VHT";
        case PacketFormatEnum::PacketFormat_HESU:
            return "HE-SU";
        case PacketFormatEnum::PacketFormat_HEMU:
            return "HE-MU";
        default:
            throw std::runtime_error("unrecognized packet format.");
    }
}

std::string ChannelBandwidth2String(ChannelBandwidthEnum cbw) {
    switch (cbw) {
        case ChannelBandwidthEnum::CBW_5:
            return "5";
        case ChannelBandwidthEnum::CBW_10:
            return "10";
        case ChannelBandwidthEnum::CBW_20:
            return "20";
        case ChannelBandwidthEnum::CBW_40:
            return "40";
        case ChannelBandwidthEnum::CBW_80:
            return "80";
        case ChannelBandwidthEnum::CBW_160:
            return "160";
        default:
            throw std::runtime_error("Unsupported ChannelBandwidthEnum...");
    }
}

std::string channelModel2String(ChannelModeEnum mode) {
    switch (mode) {
        case ChannelModeEnum::HT40_PLUS:
            return "HT40_PLUS";
        case ChannelModeEnum::HT40_MINUS:
            return "HT40_MINUS";
        case ChannelModeEnum::HT20:
            return "HT20";
    }
    return "channel mode error.";
}

std::string GuardInterval2String(GuardIntervalEnum gi) {
    switch (gi) {
        case GuardIntervalEnum::GI_400:
            return "0.4us";
        case GuardIntervalEnum::GI_800:
            return "0.8us";
        case GuardIntervalEnum::GI_1600:
            return "1.6us";
        case GuardIntervalEnum::GI_3200:
            return "3.2us";
        default:
            throw std::runtime_error("Unsupported GuardIntervalEnum...");
    }
}

std::string ChannelCoding2String(ChannelCodingEnum coding) {
    switch (coding) {
        case ChannelCodingEnum::LDPC:
            return "LDPC";
        case ChannelCodingEnum::BCC:
            return "BCC";
        default:
            throw std::runtime_error("Unsupported ChannelCodingEnum...");
    }
}

std::ostream &operator<<(std::ostream &os, const PicoScenesDeviceType &deviceType) {
    os << DeviceType2String(deviceType);
    return os;
}

std::ostream &operator<<(std::ostream &os, const PacketFormatEnum &format) {
    os << PacketFormat2String(format);
    return os;
}

std::ostream &operator<<(std::ostream &os, const ChannelBandwidthEnum &cbw) {
    os << ChannelBandwidth2String(cbw);
    return os;
}

std::ostream &operator<<(std::ostream &os, const ChannelModeEnum &channelMode) {
    os << channelModel2String(channelMode);
    return os;
}

std::ostream &operator<<(std::ostream &os, const GuardIntervalEnum &gi) {
    os << GuardInterval2String(gi);
    return os;
}

std::ostream &operator<<(std::ostream &os, const ChannelCodingEnum &coding) {
    os << ChannelCoding2String(coding);
    return os;
}