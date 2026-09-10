#!/usr/bin/env bash
# Compile accepted RMGE01 C for the selected iOS SDK; never select it for macOS.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
case "${GALAXYPAD_IOS_SDK:-iphonesimulator}" in
  iphonesimulator) lane=ios-simulator ;;
  iphoneos) lane=ios-device ;;
  *) echo "GALAXYPAD_IOS_SDK must be iphonesimulator or iphoneos" >&2; exit 2 ;;
esac
module="$(<"$root/generated/modules/RMGE01/active-module.txt")"
[[ "$module" == "$root/generated/"* && -f "$module" ]]
generated="$(dirname "$module")/dolrecomp-output/RMGE01_generated"
profile="$root/generated/pgo/rmge01.profdata"
runtime="$root/ref/ModernGekko/vendor/dolphin"
build="$root/generated/build/$lane-module"
[[ "$(shasum -a 256 "$module" | awk '{print $1}')" == c0021b9f2fad3acc3746b6a582b46935e2f7b60bc38434ad7d485564957c7939 ]]
[[ "$(shasum -a 256 "$generated/main.dol" | awk '{print $1}')" == 2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09 ]]
[[ "$(shasum -a 256 "$profile" | awk '{print $1}')" == f39a3cedeb6c49f35c411356893c619dc347eb1b0bb5986687f25cf81e7d460d ]]
cmake -S "$runtime/module-template" -B "$build" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$root/scripts/$lane-toolchain.cmake" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DGAME_ID=RMGE01 -DGENERATED_DIR="$generated" \
  -DGXRUNTIME_DIR="$runtime/GXRuntime" \
  -DCHASSIS_ABI_DIR="$runtime/Source/Core/Core/PowerPC/StaticRecomp" \
  -DRECOMPCORE_MODULE_ENABLE_IPO=ON -DRECOMPCORE_MODULE_OPT_LEVEL=2 \
  -DCMAKE_C_FLAGS="-fprofile-instr-use=$profile" \
  -DCMAKE_SHARED_LINKER_FLAGS="-fprofile-instr-use=$profile"
cmake --build "$build" --parallel "${GALAXYPAD_BUILD_JOBS:-4}"
xcrun vtool -show-build "$build/gRMGE01_recomp.dylib"
