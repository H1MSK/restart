cmake_minimum_required(VERSION 3.0)

project(nn_cmodel)

option(CMAKE_BUILD_TYPE "Build type" "Debug")

if(CMAKE_BUILD_TYPE AND (CMAKE_BUILD_TYPE STREQUAL "Release"))
    message("Build type: Release")
    add_compile_options(-O3)

else()
    message("Build type: Debug")
    add_compile_options(-g -Og)

endif()

include_directories(
    ${PROJECT_SOURCE_DIR}
    ${PROJECT_SOURCE_DIR}/hls_headers
    )

add_library(cmodel_376_17_64_1 SHARED
    top.cpp
)

target_compile_options(cmodel_376_17_64_1 PUBLIC -Wall -Wextra -Wno-unknown-pragmas -fPIC -fvisibility=hidden -std=c++11)
target_compile_definitions(cmodel_376_17_64_1 PUBLIC
    -DOBS_DIM=376
    -DACT_DIM=17
    -DHIDDEN_WIDTH=64
    -DACT_CONTINUOUS=1
)
