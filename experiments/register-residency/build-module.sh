#!/usr/bin/env bash
# Build one iPhoneOS game module with the 7162 module recipe (ThinLTO, -O2 chunks,
# optional PGO profile, void dispatch entry) from a given generated directory.
set -euo pipefail
usage() { echo "usage: $0 GENERATED_DIR RECOMPCORE_DIR BUILD_DIR [PROFDATA]" >&2; exit 2; }
[[ $# -ge 3 ]] || usage
generated="$(cd "$1" && pwd)"; runtime="$(cd "$2" && pwd)"; build="$3"; profile="${4:-}"
root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
[[ ! -e "$build" ]] || { echo "build directory exists: $build" >&2; exit 1; }
flags="-DGALAXYPAD_VOID_DISPATCH=1"
link=""
if [[ -n "$profile" ]]; then
  flags="$flags -fprofile-instr-use=$profile -Wno-profile-instr-out-of-date -Wno-profile-instr-unprofiled"
  link="-fprofile-instr-use=$profile"
fi
cmake -S "$runtime/module-template" -B "$build" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$root/scripts/ios-device-toolchain.cmake" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DCMAKE_C_FLAGS="$flags" -DCMAKE_SHARED_LINKER_FLAGS="$link" \
  -DGAME_ID=RMGE01 -DGENERATED_DIR="$generated" -DGXRUNTIME_DIR="$runtime/GXRuntime" \
  -DCHASSIS_ABI_DIR="$runtime/Source/Core/Core/PowerPC/StaticRecomp" \
  -DRECOMPCORE_MODULE_ENABLE_IPO=ON -DRECOMPCORE_MODULE_OPT_LEVEL=2 >"$build.configure.log"
cmake --build "$build" --parallel "${GALAXYPAD_BUILD_JOBS:-8}" >"$build.build.log" 2>&1
xcrun vtool -show-build "$build/gRMGE01_recomp.dylib" | head -8
shasum -a 256 "$build/gRMGE01_recomp.dylib"
