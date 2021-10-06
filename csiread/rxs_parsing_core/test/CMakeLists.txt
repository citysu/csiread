find_package(Boost COMPONENTS system filesystem thread program_options regex chrono iostreams unit_test_framework REQUIRED)

add_executable(PicoScenesFrameTest PicoScenesFrameTest.cxx)
target_link_libraries(PicoScenesFrameTest rxs_parsing ${Boost_LIBRARIES})
