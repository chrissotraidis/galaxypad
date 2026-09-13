#!/usr/bin/env bash
# Rebuild from the exact local DOL without the original Mac's private PGO cache.
# This is a new unprofiled candidate, not the historical accepted module.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
runtime="$root/ref/ModernGekko/vendor/dolphin"
generated="$root/generated/aot/device-fresh/RMGE01_generated"
build="$root/generated/build/ios-device-fresh-module"
python3 "$root/scripts/dependency-lock.py"
# The committed DolRecomp fork includes the entry-cycle correction.

cmake -S "$runtime/DolRecomp" -B "$root/generated/build/dolrecomp" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DDOLRECOMP_ENABLE_LLVM=OFF
cmake --build "$root/generated/build/dolrecomp" --target dolrecomp --parallel "${GALAXYPAD_BUILD_JOBS:-4}"
DOLRECOMP_C_CHUNK_INSTRUCTIONS=1024 DOLRECOMP_DISPATCH_LOOKUP=indexed \
  GALAXYPAD_AOT_OUTPUT="$root/generated/aot/device-fresh" \
  bash "$root/scripts/generate-aot.sh"
cp "$generated/RMGE01.h" "$generated/generated.h"
cp "$generated/RMGE01_smc.txt" "$generated/generated_smc.txt"
cp "$root/generated/extracted/run1/sys/main.dol" "$generated/main.dol"
cmake -S "$runtime/module-template" -B "$build" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$root/scripts/ios-device-toolchain.cmake" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DGAME_ID=RMGE01 -DGENERATED_DIR="$generated" \
  -DGXRUNTIME_DIR="$runtime/GXRuntime" \
  -DCHASSIS_ABI_DIR="$runtime/Source/Core/Core/PowerPC/StaticRecomp" \
  -DRECOMPCORE_MODULE_ENABLE_IPO=ON -DRECOMPCORE_MODULE_OPT_LEVEL=2
cmake --build "$build" --parallel "${GALAXYPAD_BUILD_JOBS:-4}"
xcrun vtool -show-build "$build/gRMGE01_recomp.dylib"
shasum -a 256 "$generated/main.dol" "$build/gRMGE01_recomp.dylib"
