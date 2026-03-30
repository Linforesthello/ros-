cmake_minimum_required(VERSION 3.1.0)
project(my_motor_project)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")

include_directories(include)
link_directories(${CMAKE_SOURCE_DIR}/lib)

if(CMAKE_HOST_SYSTEM_PROCESSOR MATCHES "aarch64")
    set(EXTRA_LIBS libUnitreeMotorSDK_Arm64.so)
else()
    set(EXTRA_LIBS libUnitreeMotorSDK_Linux64.so)
endif()

set(CMAKE_BUILD_RPATH "${CMAKE_SOURCE_DIR}/lib")


add_executable(LocationMode_8010t1 src/LocationMode_8010t1.cpp)
target_link_libraries(LocationMode_8010t1 ${EXTRA_LIBS})

add_executable(StopMode_8010t1 src/StopMode_8010t1.cpp)
target_link_libraries(StopMode_8010t1 ${EXTRA_LIBS})

add_executable(example_goM8010_6_motor src/example_goM8010_6_motor.cpp)
target_link_libraries(example_goM8010_6_motor ${EXTRA_LIBS})
