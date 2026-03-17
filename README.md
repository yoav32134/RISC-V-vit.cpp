# RISC-V-vit.cpp — RISC-V Bare Metal Port

This repository contains a modified version of **vit.cpp** adapted to run on **RISC-V bare-metal systems**.

Original project:
https://github.com/staghado/vit.cpp

Changes in this port:

* Removed threading
* Removed timer functionality
* Added files required for startup in a bare-metal environment

---

## How to run (QEMU on Ubuntu)

First, get the model. You can use one of the models that I made or look at the vit.cpp repository for available models.
After you know which model to use, change the `vit_params` struct to use them.

Then build it using this command:

```bash
rm -rf build
cmake -B build \
  -DCMAKE_TOOLCHAIN_FILE=toolchain-riscv64-baremetal.cmake \
  -DTOOLCHAIN_ROOT=/path/to/riscv \
  -DBUILD_QUANTIZE=OFF
cmake --build build -j
```

Run it using this command from the build directory:

```bash
qemu-system-riscv64 \
-machine virt \
-nographic \
-bios none \
-kernel bin/vit \
-semihosting
```

You must have QEMU installed and the RISC-V compilers.

WARNING: most of the stuff here was made with my paths, so it might break when you use it.

For any other instructions just follow the vit.cpp README.

