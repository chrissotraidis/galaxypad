#!/usr/bin/env bash
# Profile-only candidate; reuse accepted code and never select/package the output.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
accepted="$root/generated/modules/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-1a7fde44f42859a5"
profile="$root/generated/pgo/opening-decoder-r102.profdata"
build="$root/generated/pgo/decoder-use-r102"
runtime="$root/ref/ModernGekko/vendor/dolphin/GXRuntime"
check_hash() {
  [[ "$(shasum -a 256 "$1" | awk '{print $1}')" == "$2" ]] || {
    echo "Experiment input identity mismatch: $1" >&2; exit 1;
  }
}
check_hash "$profile" b355557fae4d0d826eb131807eca5f6bd95a0f51ac5edec50e15559d8838889b
check_hash "$accepted/gRMGE01_recomp.dylib" 6fba4629eb07e79132a344bc2d68bf9f62627478d5a7dc8a19e1af291942c916
check_hash "$runtime/src/core/cpu_interpreter_float.c" 3026eb10f63667a85dccb6e1fc7df1d2c299058cd636cae6b2c0ca7b02a4806c
CMAKE_NINJA_FORCE_RESPONSE_FILE=1 cmake \
  -S "$root/ref/ModernGekko/vendor/dolphin/module-template" -B "$build" -G Ninja \
  -DGAME_ID=RMGE01 -DGENERATED_DIR="$accepted/dolrecomp-output/RMGE01_generated" \
  -DGXRUNTIME_DIR="$runtime" -DCMAKE_OSX_DEPLOYMENT_TARGET=14.0 \
  -DCMAKE_BUILD_TYPE=Release -DRECOMPCORE_MODULE_ENABLE_IPO=ON \
  -DRECOMPCORE_MODULE_OPT_LEVEL=2 \
  -DCMAKE_C_FLAGS="-fprofile-instr-use=$profile" \
  -DCMAKE_SHARED_LINKER_FLAGS="-fprofile-instr-use=$profile"
cmake --build "$build" --parallel "${GALAXYPAD_JOBS:-4}"
cp "$root/config/decoder-pgo-experiment.txt" "$build/manifest.txt"
if [[ ! -e "$build/dolrecomp-output" ]]; then
  ln -s "$accepted/dolrecomp-output" "$build/dolrecomp-output"
fi
"$root/scripts/audit-module.sh" "$build/gRMGE01_recomp.dylib"
echo "Unselected profile-only candidate: $build/gRMGE01_recomp.dylib"
