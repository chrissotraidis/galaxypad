#!/usr/bin/env bash
# Build the exact RMGE01 two-range dispatcher candidate for Simulator only.
# The physical device remains on the current installed module until this
# candidate passes the unattended route and matched control comparison.
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
runtime="$root/ref/ModernGekko"
source_root="$root/generated/aot/device-fresh/RMGE01_generated"
candidate_root="${1:-$root/generated/aot/device-fresh-two-range-r916b/RMGE01_generated}"
build="${2:-$root/generated/build/ios-simulator-two-range-r916b}"

[[ -f "$source_root/RMGE01.h" && -d "$source_root/chunks" ]] || {
  echo "incomplete current AOT output: $source_root" >&2
  exit 1
}
[[ "$(shasum -a 256 "$source_root/RMGE01.h" | awk '{print $1}')" == \
   2cf2a7c3752cd6ab93f7c41140aaa2f3c1ae477cca6587925d6a5b51c3d683b9 ]] || {
  echo "unexpected generated-header identity; refuse two-range candidate" >&2
  exit 1
}
[[ ! -e "$candidate_root" ]] || {
  echo "candidate AOT directory already exists: $candidate_root" >&2
  exit 1
}

mkdir -p "$candidate_root/chunks"
for name in generated_smc.txt main.dol; do
  ln -s "$source_root/$name" "$candidate_root/$name"
done
for source in "$source_root"/chunks/*.c; do
  ln -s "$source" "$candidate_root/chunks/$(basename -- "$source")"
done

GALAXYPAD_ROOT="$root" python3 - "$source_root/RMGE01.h" "$candidate_root/RMGE01.h" "$candidate_root/generated.h" <<'PY'
import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, os.environ['GALAXYPAD_ROOT'] + '/scripts')
from two_range_lookup import transform

source_path, header_path, normalized_path = map(Path, sys.argv[1:])
transformed = transform(source_path.read_text(encoding='utf-8'))
assert hashlib.sha256(transformed.encode()).hexdigest() == (
    'da2def2ce566f57929afe0a8a2f7de5539b17624eb37452d6928790ac6999336'
)
header_path.write_text(transformed, encoding='utf-8')
normalized_path.write_text(transformed, encoding='utf-8')
PY

cmake -S "$runtime/vendor/dolphin/module-template" -B "$build" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$root/scripts/ios-simulator-toolchain.cmake" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DGAME_ID=RMGE01 -DGENERATED_DIR="$candidate_root" \
  -DGXRUNTIME_DIR="$runtime/vendor/dolphin/GXRuntime" \
  -DCHASSIS_ABI_DIR="$runtime/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp" \
  -DRECOMPCORE_MODULE_ENABLE_IPO=ON -DRECOMPCORE_MODULE_OPT_LEVEL=2
cmake --build "$build" --parallel "${GALAXYPAD_BUILD_JOBS:-4}"
xcrun vtool -show-build "$build/gRMGE01_recomp.dylib"
codesign --verify --verbose=2 "$build/gRMGE01_recomp.dylib"
shasum -a 256 "$candidate_root/RMGE01.h" "$build/gRMGE01_recomp.dylib"
