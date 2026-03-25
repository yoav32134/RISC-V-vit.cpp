# RISC-V-vit.cpp — RISC-V Bare Metal Port

This repository contains a modified version of **vit.cpp** adapted to run on **RISC-V bare-metal systems**.

Original project:
https://github.com/staghado/vit.cpp

Changes in this port:

* Removed threading
* Removed timer functionality
* Added files required for startup in a bare-metal environment
* Added option for one git quantization

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

## QAT


I added support for quantization-aware training (QAT) for the `q4_0` format.

To recreate the results, first download the ImageNet-1K dataset from the Kaggle ImageNet Object Localization Challenge:

https://www.kaggle.com/c/imagenet-object-localization-challenge

Then run the following scripts:
- `get_vals.py`
- `train.py`

## results for different quantization on vit_tiny
| model    | acc@1 | acc@5 | cycle count x86 | model size MB | cycle count risc-v | comments             |
|----------|-------|-------|-----------------|---------------|--------------------|----------------------|
| F32      | 78.44 | 94.54 |                 | 22.9          |                    | Pytorch-image-models |
| F32      | 78.19 | 94.41 | 297453          | 22.9          |                    |                      |
| q8_0     | 78.18 | 94.41 | 260454          | 6.7           |                    |                      |
| q4_1     | 75.93 | 93.53 | 272019          | 4.3           |                    |                      |
| q4_0     | 75.67 | 93.18 | 276482          | 4             |                    |                      |
| q4_0 QAT | 76.78 | 93.83 | 276482          | 4             |                    |                      |
