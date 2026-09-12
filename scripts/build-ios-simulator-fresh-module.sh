#!/usr/bin/env bash
# Build the private fresh RMGE01 module for the iPad Simulator.
# The module is generated from the already verified local DOL; no game data is
# copied into the app bundle by this script.
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
runtime="$root/ref/ModernGekko"
template="$runtime/vendor/dolphin/module-template"
generated="$root/generated/aot/device-fresh/RMGE01_generated"
build="${GALAXYPAD_SIMULATOR_MODULE_BUILD:-$root/generated/build/ios-simulator-fresh-module}"
pgo_profile="${GALAXYPAD_PGO_PROFILE:-}"
pgo_instrument="${GALAXYPAD_PGO_INSTRUMENT:-NO}"
[[ "$build" == /* ]] || build="$root/$build"

[[ -d "$template" ]] || { echo "missing module template: $template" >&2; exit 1; }
[[ -f "$generated/generated.h" && -f "$generated/generated_smc.txt" &&
   -f "$generated/main.dol" ]] || {
  echo "incomplete private AOT output: $generated" >&2
  exit 1
}
[[ "$pgo_instrument" == YES || "$pgo_instrument" == NO ]] || {
  echo "GALAXYPAD_PGO_INSTRUMENT must be YES or NO" >&2
  exit 2
}
[[ "$pgo_instrument" != YES || -z "$pgo_profile" ]] || {
  echo "PGO instrumentation and PGO use are mutually exclusive" >&2
  exit 2
}

cmake_args=(
  -S "$template" -B "$build" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$root/scripts/ios-simulator-toolchain.cmake" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DGAME_ID=RMGE01 -DGENERATED_DIR="$generated" \
  -DGXRUNTIME_DIR="$runtime/vendor/dolphin/GXRuntime" \
  -DCHASSIS_ABI_DIR="$runtime/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp" \
  -DRECOMPCORE_MODULE_ENABLE_IPO=ON -DRECOMPCORE_MODULE_OPT_LEVEL=2
)
if [[ "$pgo_instrument" == YES ]]; then
  cmake_args+=(
    "-DCMAKE_C_FLAGS=-fprofile-instr-generate -fprofile-continuous"
    "-DCMAKE_SHARED_LINKER_FLAGS=-fprofile-instr-generate -fprofile-continuous"
  )
elif [[ -n "$pgo_profile" ]]; then
  [[ "$pgo_profile" == /* ]] || pgo_profile="$root/$pgo_profile"
  [[ -f "$pgo_profile" ]] || { echo "missing PGO profile: $pgo_profile" >&2; exit 1; }
  cmake_args+=(
    "-DCMAKE_C_FLAGS=-fprofile-instr-use=$pgo_profile"
    "-DCMAKE_SHARED_LINKER_FLAGS=-fprofile-instr-use=$pgo_profile"
  )
else
  # CMake retains cached flags when an option is omitted. A reused build
  # directory must really return to unprofiled mode, not keep instrumentation
  # or silently reuse the previous profile.
  cmake_args+=("-DCMAKE_C_FLAGS=" "-DCMAKE_SHARED_LINKER_FLAGS=")
fi
cmake "${cmake_args[@]}"
cmake --build "$build" --parallel "${GALAXYPAD_BUILD_JOBS:-4}"
xcrun vtool -show-build "$build/gRMGE01_recomp.dylib"
shasum -a 256 "$build/gRMGE01_recomp.dylib"
