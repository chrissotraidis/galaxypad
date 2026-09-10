#!/usr/bin/env bash
# Isolated experiment using the accepted generated chunks; never selects a module.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
source_runtime="$root/ref/ModernGekko/vendor/dolphin/GXRuntime"
experiment="$root/generated/ps-finite-r96"
accepted="$root/generated/modules/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-1a7fde44f42859a5"
patch_file="$root/patches/experiments/ps-finite-add-sub.patch"
check_hash() {
  [[ "$(shasum -a 256 "$1" | awk '{print $1}')" == "$2" ]] || {
    echo "Experiment input identity mismatch: $1" >&2; exit 1;
  }
}
check_hash "$source_runtime/src/core/cpu_interpreter_float.c" 3026eb10f63667a85dccb6e1fc7df1d2c299058cd636cae6b2c0ca7b02a4806c
check_hash "$patch_file" 45cdbc809b05099eac50b52845f0ec6a9dccd7379a62cf7d00fc4651c90120b2
check_hash "$accepted/gRMGE01_recomp.dylib" 6fba4629eb07e79132a344bc2d68bf9f62627478d5a7dc8a19e1af291942c916
check_hash "$root/generated/pgo/rmge01.profdata" f39a3cedeb6c49f35c411356893c619dc347eb1b0bb5986687f25cf81e7d460d
mkdir -p "$experiment"
if [[ ! -d "$experiment/GXRuntime" ]]; then
  cp -R "$source_runtime" "$experiment/GXRuntime"
  git -C "$experiment/GXRuntime" apply "$patch_file"
fi
check_hash "$experiment/GXRuntime/src/core/cpu_interpreter_float.c" 707f6d0a1330e7ab5a9ee815cc9ba39a3f678f398e0b7fd4a27a9a8ca67b34ba
python3 "$root/tests/test-ps-finite-candidate.py" "$experiment/GXRuntime/src/core/cpu_interpreter_float.c"
CMAKE_NINJA_FORCE_RESPONSE_FILE=1 cmake \
  -S "$root/ref/ModernGekko/vendor/dolphin/module-template" \
  -B "$experiment/module-build" -G Ninja -DGAME_ID=RMGE01 \
  -DGENERATED_DIR="$accepted/dolrecomp-output/RMGE01_generated" \
  -DGXRUNTIME_DIR="$experiment/GXRuntime" -DCMAKE_OSX_DEPLOYMENT_TARGET=14.0 \
  -DCMAKE_BUILD_TYPE=Release -DRECOMPCORE_MODULE_ENABLE_IPO=ON \
  -DRECOMPCORE_MODULE_OPT_LEVEL=2 \
  -DCMAKE_C_FLAGS="-fprofile-instr-use=$root/generated/pgo/rmge01.profdata"
cmake --build "$experiment/module-build" --parallel 4
cp "$root/config/ps-finite-experiment.txt" "$experiment/module-build/manifest.txt"
if [[ ! -e "$experiment/module-build/dolrecomp-output" ]]; then
  ln -s "$accepted/dolrecomp-output" "$experiment/module-build/dolrecomp-output"
fi
"$root/scripts/audit-module.sh" "$experiment/module-build/gRMGE01_recomp.dylib"
echo "Candidate only: $experiment/module-build/gRMGE01_recomp.dylib"
