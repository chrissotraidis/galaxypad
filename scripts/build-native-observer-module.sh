#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
candidate="$root/generated/native-observer-r562"
runtime="$root/ref/ModernGekko/vendor/dolphin"
profile="$root/generated/pgo/rmge01.profdata"
[[ -f "$candidate/manifest.json" ]]
python3 "$root/scripts/prepare-native-observer.py" --verify
[[ "$(shasum -a 256 "$profile" | awk '{print $1}')" == f39a3cedeb6c49f35c411356893c619dc347eb1b0bb5986687f25cf81e7d460d ]]
cmake -S "$runtime/module-template" -B "$candidate/build" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$root/scripts/ios-simulator-toolchain.cmake" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DGAME_ID=RMGE01 -DGENERATED_DIR="$candidate/RMGE01_generated" \
  -DGXRUNTIME_DIR="$runtime/GXRuntime" \
  -DCHASSIS_ABI_DIR="$runtime/Source/Core/Core/PowerPC/StaticRecomp" \
  -DGALAXYPAD_OBSERVER_ROOT="$root" \
  -DCMAKE_PROJECT_INCLUDE="$root/scripts/native-observer-module.cmake" \
  -DRECOMPCORE_MODULE_ENABLE_IPO=ON -DRECOMPCORE_MODULE_OPT_LEVEL=2 \
  -DCMAKE_C_FLAGS="-fprofile-instr-use=$profile" \
  -DCMAKE_SHARED_LINKER_FLAGS="-fprofile-instr-use=$profile"
cmake --build "$candidate/build" --parallel 2
xcrun vtool -show-build "$candidate/build/gRMGE01_recomp.dylib"
