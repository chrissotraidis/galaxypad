#!/usr/bin/env bash
# Build the paired-store candidate without regenerating or selecting game code.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
experiment="$root/generated/lc-pair-r116"
accepted="$root/generated/modules/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-1a7fde44f42859a5"
profile="$root/generated/pgo/rmge01.profdata"
check_hash() {
  [[ "$(shasum -a 256 "$1" | awk '{print $1}')" == "$2" ]] || {
    echo "Experiment identity mismatch: $1" >&2; exit 1;
  }
}
check_hash "$experiment/GalaxyPadRunner" 6dde0e4dea8621dc1064666e0da6bfb6258535b72e7121def485752521519ed6
check_hash "$experiment/GXRuntime/src/core/cpu.c" 1350d1196b38b147477890ef0dc59d5d9e389a55a169d51913fc033be34edb69
check_hash "$experiment/GXRuntime/src/core/cpu_interpreter_float.c" 3026eb10f63667a85dccb6e1fc7df1d2c299058cd636cae6b2c0ca7b02a4806c
check_hash "$accepted/gRMGE01_recomp.dylib" 6fba4629eb07e79132a344bc2d68bf9f62627478d5a7dc8a19e1af291942c916
check_hash "$profile" f39a3cedeb6c49f35c411356893c619dc347eb1b0bb5986687f25cf81e7d460d
python3 "$root/tests/test-lc-pair-store.py" "$experiment/GXRuntime/src/core/cpu.c"
CMAKE_NINJA_FORCE_RESPONSE_FILE=1 cmake \
  -S "$root/ref/ModernGekko/vendor/dolphin/module-template" \
  -B "$experiment/module-build" -G Ninja -DGAME_ID=RMGE01 \
  -DGENERATED_DIR="$accepted/dolrecomp-output/RMGE01_generated" \
  -DGXRUNTIME_DIR="$experiment/GXRuntime" -DCMAKE_OSX_DEPLOYMENT_TARGET=14.0 \
  -DCMAKE_BUILD_TYPE=Release -DRECOMPCORE_MODULE_ENABLE_IPO=ON \
  -DRECOMPCORE_MODULE_OPT_LEVEL=2 \
  -DCMAKE_C_FLAGS="-fprofile-instr-use=$profile" \
  -DCMAKE_SHARED_LINKER_FLAGS="-fprofile-instr-use=$profile"
cmake --build "$experiment/module-build" --parallel 4
cp "$root/config/lc-pair-experiment.txt" "$experiment/module-build/manifest.txt"
if [[ ! -e "$experiment/module-build/dolrecomp-output" ]]; then
  ln -s "$accepted/dolrecomp-output" "$experiment/module-build/dolrecomp-output"
fi
"$root/scripts/audit-module.sh" "$experiment/module-build/gRMGE01_recomp.dylib"
shasum -a 256 "$experiment/module-build/gRMGE01_recomp.dylib"
echo 'Candidate only; not selected or packaged.'
