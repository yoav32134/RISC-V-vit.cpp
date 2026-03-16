set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR riscv64)

set(TOOLCHAIN_ROOT "/home/yoav/riscv-medany")
set(TARGET_TRIPLE "riscv64-unknown-elf")
set(SYSROOT "${TOOLCHAIN_ROOT}/${TARGET_TRIPLE}")

set(CMAKE_C_COMPILER   "${TOOLCHAIN_ROOT}/bin/${TARGET_TRIPLE}-gcc")
set(CMAKE_CXX_COMPILER "${TOOLCHAIN_ROOT}/bin/${TARGET_TRIPLE}-g++")
set(CMAKE_ASM_COMPILER "${TOOLCHAIN_ROOT}/bin/${TARGET_TRIPLE}-gcc")

set(CMAKE_C_COMPILER_TARGET   "${TARGET_TRIPLE}")
set(CMAKE_CXX_COMPILER_TARGET "${TARGET_TRIPLE}")
set(CMAKE_ASM_COMPILER_TARGET "${TARGET_TRIPLE}")

set(CMAKE_SYSROOT "${SYSROOT}")
set(CMAKE_FIND_ROOT_PATH "${SYSROOT}")

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

set(RISCV_ABI  "lp64d")
#set(RISCV_ARCH "rv64gc_zfh") might do in the future if F16 arithmetic is available
set(RISCV_ARCH "rv64gc")

set(RISCV_COMMON_FLAGS "-march=${RISCV_ARCH} -mabi=${RISCV_ABI} -mcmodel=medany")

set(CMAKE_C_FLAGS_INIT
    "${RISCV_COMMON_FLAGS} -ffreestanding")

set(CMAKE_CXX_FLAGS_INIT
    "${RISCV_COMMON_FLAGS} -fno-exceptions -fno-rtti -fno-threadsafe-statics -fno-use-cxa-atexit -fno-unwind-tables -fno-asynchronous-unwind-tables")

set(CMAKE_ASM_FLAGS_INIT
    "${RISCV_COMMON_FLAGS}")

set(CMAKE_EXE_LINKER_FLAGS_INIT
    "-nostartfiles")
