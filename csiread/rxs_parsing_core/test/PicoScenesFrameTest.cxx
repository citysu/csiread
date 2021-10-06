//
// Created by 蒋志平 on 2019/12/18.
//
#define BOOST_TEST_MODULE Suite_example

#include <boost/test/unit_test.hpp>
#include "../SignalMatrix.hxx"
#include "../PayloadSegment.hxx"


BOOST_AUTO_TEST_SUITE(PicoScenesFrameTest)

    BOOST_AUTO_TEST_CASE(T1) {
        std::vector<int8_t> a;
        for (auto i = 0; i < 24; i++)
            a.emplace_back(i);
        SignalMatrix sm(a, std::vector<int16_t>{4, 3, 2}, SignalMatrixStorageMajority::ColumnMajor);
        sm.normalize();
        for (auto i = 0; i < a.size(); i++) {
            auto coordinates = sm.getCoordinate4Index(i);
            auto newPos = sm.getIndex4Coordinates(coordinates);
            BOOST_TEST(i == newPos);
        }
        auto index = sm.getCoordinate4Index(20);
        auto element50 = sm.valueAt({4, 2});
        auto vout = sm.toBuffer(SignalMatrixStorageMajority::ColumnMajor);
        auto signal = SignalMatrix<int8_t>::fromBuffer(vout, SignalMatrixStorageMajority::RowMajor);
        auto reout = signal.toBuffer(SignalMatrixStorageMajority::RowMajor);
        auto reout2 = signal.toBuffer(SignalMatrixStorageMajority::RowMajor);

    }

    BOOST_AUTO_TEST_CASE(T2) {
        std::vector<std::complex<int16_t>> a;
        for (auto i = 0; i < 24; i++)
            a.emplace_back(std::complex<int16_t>(i, i * 10));
        SignalMatrix sm(a, std::vector<int16_t>{4, 3, 2}, SignalMatrixStorageMajority::ColumnMajor);
        auto smOut = sm.toBuffer();
        auto resignal = SignalMatrix<std::complex<int16_t>>::fromBuffer(smOut);
        auto resignal2 = SignalMatrix<std::complex<int16_t>>::fromBuffer(smOut);

        sm >> "test.bbsignals";
//
        SignalMatrix<std::complex<int16_t>> sm2;
        sm2 << "test.bbsignals";
//
        SignalMatrix<std::complex<int8_t>> sm3;
//        sm3 << "test.bbsignals";
    }

    BOOST_AUTO_TEST_CASE(PayloadSegmentTest) {
        PayloadData data{.dataType = PayloadDataType::RawData, .payloadDescription = "description", .payloadData = std::vector<uint8_t>(50, 10)};

        PayloadSegment segment;
        segment.setPayload(data);
        auto buffer = segment.toBuffer();
        std::cout << segment << std::endl;

        PayloadSegment recovered = PayloadSegment::createByBuffer(buffer.data(), buffer.size());
        std::cout << recovered << std::endl;
    }

BOOST_AUTO_TEST_SUITE_END()