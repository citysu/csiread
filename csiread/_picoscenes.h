#ifndef _PICOSCENES_H
#define _PICOSCENES_H

/*
* ModularPicoScenesFrame.hxx
*/
#pragma pack(push, 1)
typedef struct ieee80211_mac_frame_header_frame_control_field {
    uint16_t version: 2,
        type: 2,
        subtype: 4,
        toDS: 1,
        fromDS: 1,
        moreFrags: 1,
        retry: 1,
        power_mgmt: 1,
        more: 1,
        protect: 1,
        order: 1;
} ieee80211_mac_frame_header_frame_control_field;
#pragma pack(pop)


#pragma pack(push, 1)
typedef struct ieee80211_mac_frame_header {
    ieee80211_mac_frame_header_frame_control_field fc;
    uint16_t dur;
    uint8_t addr1[6];
    uint8_t addr2[6];
    uint8_t addr3[6];
    uint16_t frag: 4,
            seq: 12;
} ieee80211_mac_frame_header;
#pragma pack(pop)


#pragma pack(push, 1)
typedef struct PicoScenesFrameHeader {
    uint32_t magicValue;
    uint32_t version;
    uint16_t deviceType;		/* PicoScenesDeviceType */
    uint8_t numSegments;
    uint8_t frameType;
    uint16_t taskId;
    uint16_t txId;
} PicoScenesFrameHeader;
#pragma pack(pop)


#pragma pack(push, 1)
typedef struct ModularPicoScenesRxFrameHeader {
    uint32_t frameLength;
    uint32_t magicWord;
    uint16_t frameVersion;
    uint8_t numRxSegments;
} ModularPicoScenesRxFrameHeader;
#pragma pack(pop)


typedef struct PilotScidx {
    int16_t NonHT20_52[4];
    int16_t HTVHT20_56[4];
    int16_t HTVHT40_114[6];
    int16_t VHT80_242[8];
    int16_t VHT160_484[16];
    int16_t HE20_242[8];
    int16_t HE40_484[16];
    int16_t HE80_996[16];
    int16_t HE160_1992[32];
} PilotScidx;


struct PilotScidx pilot_scidx = {
    .NonHT20_52 = {5, 19, 32, 46},
    .HTVHT20_56 = {7, 21, 34, 48},
    .HTVHT40_114 = {5, 33, 47, 66, 80, 108},
    .VHT80_242 = {19, 47, 83, 111, 130, 158, 194, 222},
    .VHT160_484 = {
        19, 47, 83, 111, 130, 158, 194, 222,
        261, 289, 325, 353, 372, 400, 436, 464},
    .HE20_242 = {6, 32, 74, 100, 141, 167, 209, 235},
    .HE40_484 = {
        6, 32, 74, 100, 140, 166, 208, 234,
        249, 275, 317, 343, 383, 409, 451, 477},
    .HE80_996 = {
        32, 100, 166, 234, 274, 342, 408, 476,
        519, 587, 653, 721, 761, 829, 895, 963},
    .HE160_1992 = {
        32, 100, 166, 234, 274, 342, 408, 476, 519,
        587, 653, 721, 761, 829, 895, 963, 1028, 1096,
        1162, 1230, 1270, 1338, 1404, 1472, 1515, 1583,
        1649, 1717, 1757, 1825, 1891, 1959},
};


/*
* AbstractPicoScenesFrameSegment.hxx
*/
typedef struct AbstractPicoScenesFrameSegment {
    uint32_t segmentLength;
    uint8_t segNameLength;
    uint8_t* segmentName;
    uint16_t versionId;
} AbstractPicoScenesFrameSegment;


/*
* CSISegment.hxx
*/
#pragma pack(push, 1)
typedef struct CSIV1 {
    uint16_t deviceType;		/* PicoScenesDeviceType */
    int8_t packetFormat;		/* PacketFormatEnum */
    uint16_t cbw;				/* ChannelBandwidthEnum */
    uint64_t carrierFreq;
    uint64_t samplingRate;
    uint32_t subcarrierBandwidth;
    uint16_t numTones;
    uint8_t numTx;
    uint8_t numRx;
    uint8_t numESS;
    uint8_t antSel;
    uint32_t csiBufferLength;
    uint8_t payload[0];
} CSIV1;
#pragma pack(pop)


#pragma pack(push, 1)
typedef struct CSIV2 {
    uint16_t deviceType;		/* PicoScenesDeviceType */
    int8_t packetFormat;		/* PacketFormatEnum */
    uint16_t cbw;				/* ChannelBandwidthEnum */
    uint64_t carrierFreq;
    uint64_t samplingRate;
    uint32_t subcarrierBandwidth;
    uint16_t numTones;
    uint8_t numTx;
    uint8_t numRx;
    uint8_t numESS;
    uint8_t antSel;
    int16_t subcarrierOffset;
    uint32_t csiBufferLength;
    uint8_t payload[0];
} CSIV2;
#pragma pack(pop)


#pragma pack(push, 1)
typedef struct CSIV3 {
    uint16_t deviceType;		/* PicoScenesDeviceType */
    int8_t packetFormat;		/* PacketFormatEnum */
    uint16_t cbw;				/* ChannelBandwidthEnum */
    uint64_t carrierFreq;
    uint64_t samplingRate;
    uint32_t subcarrierBandwidth;
    uint16_t numTones;
    uint8_t numTx;
    uint8_t numRx;
    uint8_t numESS;
    uint16_t numCSI;
    uint8_t antSel;
    int16_t subcarrierOffset;
    uint32_t csiBufferLength;
    uint8_t payload[0];
} CSIV3;
#pragma pack(pop)


#pragma pack(push, 1)
typedef struct CSIV4 {
    uint16_t deviceType;		/* PicoScenesDeviceType */
    uint8_t firmwareVersion;
    int8_t packetFormat;		/* PacketFormatEnum */
    uint16_t cbw;				/* ChannelBandwidthEnum */
    uint64_t carrierFreq;
    uint64_t samplingRate;
    uint32_t subcarrierBandwidth;
    uint16_t numTones;
    uint8_t numTx;
    uint8_t numRx;
    uint8_t numESS;
    uint16_t numCSI;
    uint8_t antSel;
    int16_t subcarrierOffset;
    uint32_t csiBufferLength;
    uint8_t payload[0];
} CSIV4;
#pragma pack(pop)


/*
* MVMExtraSegment.hxx
*/
#pragma pack(push, 1)
typedef struct IntelMVMParsedCSIHeader {
    uint32_t iqDataSize;
    uint8_t reserved4[4];
    uint32_t ftmClock;
    uint32_t samplingTick2;
    uint8_t reserved16_52[36];
    uint32_t numTones;
    uint8_t reserved60[4];
    uint32_t rssi1;
    uint32_t rssi2;
    uint8_t sourceAddress[6];
    uint8_t reserved74[2];
    uint8_t csiSequence;
    uint8_t reserved77[11];
    uint32_t muClock; // 88
    uint32_t rate_n_flags; // 92
} IntelMVMParsedCSIHeader;
#pragma pack(pop)


#pragma pack(push, 1)
typedef struct IntelMVMExtrta {
    uint16_t CSIHeaderLength;
    IntelMVMParsedCSIHeader parsedHeader;
} IntelMVMExtrta;
#pragma pack(pop)


/*
* DPASRequestSegment.hxx
*/
#pragma pack(push, 1)
typedef struct DPASRequestV1 {
    uint16_t batchId;
    uint16_t batchLength;
    uint16_t sequenceId;
    uint16_t intervalTime;
} DPASRequestV1;
#pragma pack(pop)


#pragma pack(push, 1)
typedef struct DPASRequestV2 {
    uint16_t batchId;
    uint16_t batchLength;
    uint16_t sequenceId;
    uint16_t intervalTime;
    uint16_t intervalStep;
} DPASRequestV2;
#pragma pack(pop)


#pragma pack(push, 1)
typedef struct DPASRequestV3 {
    uint16_t batchId;
    uint16_t batchLength;
    uint16_t sequenceId;
    uint16_t intervalTime;
    uint16_t intervalStep;
    uint16_t deviceType;        /* PicoScenesDeviceType */
    uint64_t carrierFrequency;
    uint32_t samplingFrequency;
} DPASRequestV3;
#pragma pack(pop)


#pragma pack(push, 1)
typedef struct DPASRequestV4 {
    uint8_t  requestMode;
    uint16_t batchId;
    uint16_t batchLength;
    uint16_t sequenceId;
    uint16_t intervalTime;
    uint16_t intervalStep;
    uint16_t deviceType;        /* PicoScenesDeviceType */
    uint16_t deviceSubtype;
    uint64_t carrierFrequency;
    uint32_t samplingFrequency;
} DPASRequestV4;
#pragma pack(pop)


/*
* PicoScenesCommons.hxx
*/
typedef enum PicoScenesDeviceType {
    QCA9300 = 0x9300,
    IWL5300 = 0x5300,
    IWLMVM_AX200 = 0x2000,
    IWLMVM_AX210 = 0x2100,
    MAC80211Compatible = 0x802,
    USRP = 0x1234,
    VirtualSDR = 0x1000,
    Unknown = 0x404
} PicoScenesDeviceType;		/* uint16_t */


typedef enum PacketFormatEnum {
    PacketFormat_NonHT = 0,
    PacketFormat_HT = 1,
    PacketFormat_VHT = 2,
    PacketFormat_HESU = 3,
    PacketFormat_HEMU = 4,
    PacketFormat_Unknown = -1
} PacketFormatEnum;			/* int8_t */


typedef enum ChannelBandwidthEnum {
    CBW_5 = 5,
    CBW_10 = 10,
    CBW_20 = 20,
    CBW_40 = 40,
    CBW_80 = 80,
    CBW_160 = 160,
} ChannelBandwidthEnum;		/* uint16_t */


typedef enum ChannelModeEnum {
    HT20 = 8,
    HT40_MINUS = 24,
    HT40_PLUS = 40,
} ChannelModeEnum;			/* uint8_t */


typedef enum GuardIntervalEnum {
    GI_400 = 400,
    GI_800 = 800,
    GI_1600 = 1600,
    GI_3200 = 3200
} GuardIntervalEnum;		/* uint16_t */


typedef enum ChannelCodingEnum {
    BCC = 0,
    LDPC = 1,
} ChannelCodingEnum;		/* uint8_t */


/*
* RXSExtraInfo.hxx
*/
typedef enum AtherosCFTuningPolicy {
    CFTuningByChansel = 30,
    CFTuningByFastCC,
    CFTuningByHardwareReset,
    CFTuningByDefault,
} AtherosCFTuningPolicy;	/* uint8_t */


#pragma pack(push, 1)
typedef struct FeatureCode {
    uint32_t hasVersion: 1, 
        hasLength: 1,
        hasMacAddr_cur: 1,
        hasMacAddr_rom: 1,
        hasChansel: 1,
        hasBMode: 1,
        hasEVM: 1,
        hasTxChainMask: 1,
        hasRxChainMask: 1,
        hasTxpower: 1,
        hasCF: 1,
        hasTxTSF: 1,
        hasLastHWTxTSF: 1,
        hasChannelFlags: 1,
        hasTxNess: 1,
        hasTuningPolicy: 1,
        hasPLLRate: 1,
        hasPLLRefDiv: 1,
        hasPLLClkSel: 1,
        hasAGC: 1,
        hasAntennaSelection: 1,
        hasSamplingRate: 1,
        hasCFO: 1,
        hasSFO: 1,
        hasTemperature: 1;
} FeatureCode;
#pragma pack(pop)


typedef struct ExtraInfo {
    FeatureCode featureCode;
    uint16_t length;
    uint64_t version;
    uint8_t macaddr_rom[6];
    uint8_t macaddr_cur[6];
    uint32_t chansel;
    uint8_t bmode;
    int8_t evm[20];
    uint8_t txChainMask;
    uint8_t rxChainMask;
    uint8_t txpower;
    uint64_t cf;
    uint32_t txTSF;
    uint32_t lastHwTxTSF;
    uint16_t channelFlags;
    uint8_t tx_ness;
    uint8_t tuningPolicy;		/* AtherosCFTuningPolicy */
    uint16_t pll_rate;
    uint8_t pll_refdiv;
    uint8_t pll_clock_select;
    uint8_t agc;
    uint8_t ant_sel[3];
    uint64_t samplingRate;
    int32_t cfo;
    int32_t sfo;
    int8_t temperature;
} ExtraInfo;

/*
* RxSBasicSegment.hxx
*/
#pragma pack(push, 1)
typedef struct RxSBasicV1 {
    uint16_t deviceType;    /* device type code */
    uint64_t tstamp;        /* h/w assigned timestamp */
    int16_t centerFreq;     /* receiving channel frequency */
    uint8_t packetFormat;   /* 0 for NonHT, 1 for HT, 2 for VHT, 3 for HE-SU, 4 for HE-MU */
    uint16_t cbw;           /* channel bandwidth [20, 40, 80, 160] */
    uint16_t guardInterval; /* 400/800/1600/3200ns */
    uint8_t mcs;
    uint8_t numSTS;
    uint8_t numESS;
    uint8_t numRx;
    int8_t noiseFloor;   	/* noise floor */
    int8_t rssi;        	/* rx frame RSSI */
    int8_t rssi_ctl0;   	/* rx frame RSSI [ctl, chain 0] */
    int8_t rssi_ctl1;   	/* rx frame RSSI [ctl, chain 1] */
    int8_t rssi_ctl2;   	/* rx frame RSSI [ctl, chain 2] */
} RxSBasicV1;
#pragma pack(pop)


#pragma pack(push, 1)
typedef struct RxSBasicV2 {
    uint16_t deviceType;    /* device type code */
    uint64_t tstamp;        /* h/w assigned timestamp */
    int16_t centerFreq;     /* receiving channel frequency */
    uint8_t packetFormat;   /* 0 for NonHT, 1 for HT, 2 for VHT, 3 for HE-SU, 4 for HE-MU */
    uint16_t cbw;           /* channel bandwidth [20, 40, 80, 160] */
    uint16_t guardInterval; /* 400/800/1600/3200ns */
    uint8_t mcs;
    uint8_t numSTS;
    uint8_t numESS;
    uint8_t numRx;
    uint8_t numUser;
    uint8_t userIndex;
    int8_t noiseFloor;   	/* noise floor */
    int8_t rssi;        	/* rx frame RSSI */
    int8_t rssi_ctl0;   	/* rx frame RSSI [ctl, chain 0] */
    int8_t rssi_ctl1;   	/* rx frame RSSI [ctl, chain 1] */
    int8_t rssi_ctl2;   	/* rx frame RSSI [ctl, chain 2] */
} RxSBasicV2;
#pragma pack(pop)


#pragma pack(push, 1)
typedef struct RxSBasicV3 {
    uint16_t deviceType;    /* device type code */
    uint64_t tstamp;        /* h/w assigned timestamp */
    int16_t centerFreq;     /* receiving channel frequency */
    int16_t controlFreq;    /* control channel frequency */
    uint16_t cbw;           /* channel bandwidth [20, 40, 80, 160] */
    uint8_t packetFormat;   /* 0 for NonHT, 1 for HT, 2 for VHT, 3 for HE-SU, 4 for HE-MU */
    uint16_t pkt_cbw;       /* packet CBW [20, 40, 80, 160] */
    uint16_t guardInterval; /* 400/800/1600/3200ns */
    uint8_t mcs;
    uint8_t numSTS;
    uint8_t numESS;
    uint8_t numRx;
    uint8_t numUser;
    uint8_t userIndex;
    int8_t noiseFloor;   	/* noise floor */
    int8_t rssi;        	/* rx frame RSSI */
    int8_t rssi_ctl0;   	/* rx frame RSSI [ctl, chain 0] */
    int8_t rssi_ctl1;   	/* rx frame RSSI [ctl, chain 1] */
    int8_t rssi_ctl2;   	/* rx frame RSSI [ctl, chain 2] */
} RxSBasicV3;
#pragma pack(pop)


#endif
