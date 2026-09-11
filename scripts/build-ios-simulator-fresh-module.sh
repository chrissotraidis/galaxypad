#!/usr/bin/env bash
# Build the private fresh RMGE01 module for the iPad Simulator.
# The module is generated from the already verified local DOL; no game data is
# copied into the app bundle by this script.
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
runtime="$root/ref/ModernGekko"
template="$runtime/vendor/dolphin/module-template"
generated="$root/generated/aot/device-fresh/RMGE01_generated"
build="$root/generated/build/ios-simulator-fresh-module"

[[ -d "$template" ]] || { echo "missing module template: $template" >&2; exit 1; }
[[ -f "$generated/generated.h" && -f "$generated/generated_smc.txt" &&
   -f "$generated/main.dol" ]] || {
  echo "incomplete private AOT output: $generated" >&2
  exit 1
}

cmake -S "$template" -B "$build" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$root/scripts/ios-simulator-toolchain.cmake" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DGAME_ID=RMGE01 -DGENERATED_DIR="$generated" \
  -DGXRUNTIME_DIR="$runtime/vendor/dolphin/GXRuntime" \
  -DCHASSIS_ABI_DIR="$runtime/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp" \
  -DRECOMPCORE_MODULE_ENABLE_IPO=ON -DRECOMPCORE_MODULE_OPT_LEVEL=2
cmake --build "$build" --parallel "${GALAXYPAD_BUILD_JOBS:-4}"
xcrun vtool -show-build "$build/gRMGE01_recomp.dylib"
shasum -a 256 "$build/gRMGE01_recomp.dylib"
