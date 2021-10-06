//
// Created by 蒋志平 on 2020/11/6.
//

#include "PicoScenesFrameTxParameters.hxx"


std::string PicoScenesFrameTxParameters::toString() const {
    std::stringstream ss;
    ss << "tx_param[type=" << PacketFormat2String(frameType) << ", CBW=" << ChannelBandwidth2String(cbw) << ", MCS=" << std::to_string(mcs[0]) << ", numSTS=" << int(numSTS[0]) << ", numESS=" << int(numExtraSounding) << ", coding=" << ChannelCoding2String(coding[0]) << ", GI=" << GuardInterval2String(guardInterval) << ", sounding(11n)=" << forceSounding << (preciseTxTime ? ", TxTime="+ std::to_string(*preciseTxTime) : "") << "]";
    return ss.str();
}

std::ostream &operator<<(std::ostream &os, const PicoScenesFrameTxParameters &parameters) {
    os << parameters.toString();
    return os;
}
