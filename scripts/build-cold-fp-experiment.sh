#!/usr/bin/env bash
# Candidate only; never changes normal module selection or the app.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
experiment="$root/generated/cold-fp-r160"
profile="$root/generated/pgo/rmge01.profdata"
[[ "$(shasum -a 256 "$profile" | awk '{print $1}')" == f39a3cedeb6c49f35c411356893c619dc347eb1b0bb5986687f25cf81e7d460d ]] || exit 1
python3 "$root/scripts/cold_fp_transform.py"
python3 "$root/tests/test-cold-fp.py"
CMAKE_NINJA_FORCE_RESPONSE_FILE=1 cmake \
  -S "$root/ref/ModernGekko/vendor/dolphin/module-template" \
  -B "$experiment/module-build" -G Ninja -DGAME_ID=RMGE01 \
  -DGENERATED_DIR="$experiment/module-build/dolrecomp-output/RMGE01_generated" \
  -DGXRUNTIME_DIR="$experiment/GXRuntime" \
  -DCHASSIS_ABI_DIR="$root/ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp" \
  -DCMAKE_OSX_DEPLOYMENT_TARGET=14.0 -DCMAKE_BUILD_TYPE=Release \
  -DRECOMPCORE_MODULE_ENABLE_IPO=ON -DRECOMPCORE_MODULE_OPT_LEVEL=2 \
  -DCMAKE_C_FLAGS="-fprofile-instr-use=$profile" \
  -DCMAKE_SHARED_LINKER_FLAGS="-fprofile-instr-use=$profile"
cmake --build "$experiment/module-build" --parallel 8
"$root/scripts/audit-module.sh" "$experiment/module-build/gRMGE01_recomp.dylib"
echo "Candidate only: $experiment/module-build/gRMGE01_recomp.dylib"
