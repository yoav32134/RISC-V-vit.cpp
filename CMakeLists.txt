cmake_minimum_required(VERSION 3.12)
enable_language(ASM)
project(vit
        DESCRIPTION "Inference Vision Transformer (ViT) in plain C/C++ with ggml"
        HOMEPAGE_URL "https://github.com/staghado/vit.cpp")

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if (NOT XCODE AND NOT MSVC AND NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
    set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Set the compiler flags, modify here if needed!
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O0 -g")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O0 -g")


# Additional flags for C++ (the ffast-math is to be used with caution!)
# set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -ffast-math")

# deps
add_subdirectory(ggml)

# vit executable
add_executable(${PROJECT_NAME} main.cpp vit.cpp)
target_link_options(${PROJECT_NAME} PRIVATE
        -T${CMAKE_SOURCE_DIR}/link.ld
)

target_sources(${PROJECT_NAME} PUBLIC
        crt.S
        start.c
        ccp_runtime.c
        alloc_compat.c
        sys_sbrk.c
        uart.c
        semihost-sys_fdtable.c
        semihost-sys_open.c
        semihost-sys_read.c
        semihost-sys_close.c
        semihost-sys_lseek.c
)

target_include_directories(${PROJECT_NAME} PRIVATE semihost/include)
target_link_libraries(${PROJECT_NAME} PUBLIC ggml)
target_include_directories(${PROJECT_NAME} PUBLIC .)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_11)

# quantize executable
option(BUILD_QUANTIZE "Build the quantization executable" ON)

if (BUILD_QUANTIZE)
    add_executable(quantize quantize.cpp)
    target_link_libraries(quantize PUBLIC ggml)
    target_include_directories(quantize PUBLIC .)
    target_compile_features(quantize PUBLIC cxx_std_11)
endif()

# benchmark executable (optional)
option(BUILD_BENCHMARK "Build the benchmark executable" OFF)

if(BUILD_BENCHMARK)
    find_package(nlohmann_json 3.2.0 REQUIRED)  # JSON package needed for benchmark

    # JSON package needed for benchmark
    add_executable(benchmark tests/benchmark.cpp vit.cpp)
    target_link_libraries(benchmark PRIVATE nlohmann_json::nlohmann_json)
    target_link_libraries(benchmark PUBLIC ggml)
    target_include_directories(benchmark PUBLIC .)
    target_compile_features(benchmark PUBLIC cxx_std_17)
endif()

target_compile_definitions(${PROJECT_NAME} PRIVATE
        MICRO_OS_PLUS_INCLUDE_SEMIHOSTING_SYSCALLS
)