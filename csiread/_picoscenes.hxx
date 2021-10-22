#ifndef _PICOSCENES_H
#define _PICOSCENES_H

/*
* ModularPicoScenesFrame.hxx
*/
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
} __attribute__ ((__packed__)) ieee80211_mac_frame_header_frame_control_field;


typedef struct ieee80211_mac_frame_header {
    ieee80211_mac_frame_header_frame_control_field fc;
    uint16_t dur;
    uint8_t addr1[6];
    uint8_t addr2[6];
    uint8_t addr3[6];
    uint16_t frag: 4,
            seq: 12;
} __attribute__ ((__packed__)) ieee80211_mac_frame_header;


typedef struct PicoScenesFrameHeader {
    uint32_t magicValue;
    uint32_t version;
    uint16_t deviceType;		/* PicoScenesDeviceType */
    uint8_t numSegments;
    uint8_t frameType;
    uint16_t taskId;
    uint16_t txId;
} __attribute__ ((__packed__)) PicoScenesFrameHeader;


typedef struct ModularPicoScenesRxFrameHeader {
    uint32_t frameLength;
    uint32_t magicWord;
    uint16_t frameVersion;
    uint8_t numRxSegments;
} __attribute__ ((__packed__)) ModularPicoScenesRxFrameHeader;


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
} __attribute__ ((__packed__)) CSIV1;


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
} __attribute__ ((__packed__)) CSIV2;


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
} __attribute__ ((__packed__)) CSIV3;


/*
* MVMExtraSegment.hxx
*/
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
} __attribute__ ((__packed__)) IntelMVMParsedCSIHeader;


typedef struct IntelMVMExtrta {
	uint16_t CSIHeaderLength;
	IntelMVMParsedCSIHeader parsedHeader;
} __attribute__ ((__packed__)) IntelMVMExtrta;


/*
* PicoScenesCommons.hxx
*/
typedef enum PicoScenesDeviceType {
	QCA9300 = 0x9300,
    IWL5300 = 0x5300,
    IWLMVM = 0x2000,
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
			hasPreciseTxTiming: 1;
} __attribute__ ((__packed__)) FeatureCode;


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
    double preciseTxTiming;
} ExtraInfo;

/*
* RxSBasicSegment.hxx
*/
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
} __attribute__ ((__packed__)) RxSBasicV1;


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
} __attribute__ ((__packed__)) RxSBasicV2;


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
} __attribute__ ((__packed__)) RxSBasicV3;


#endif
