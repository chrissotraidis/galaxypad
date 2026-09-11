#!/usr/bin/env bash
# Build a private Simulator module with the guarded normalization candidate.
# Unchanged generated chunks remain symlinks to the pinned current AOT tree.
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
runtime="$root/ref/ModernGekko"
source_root="$root/generated/aot/device-fresh/RMGE01_generated"
private_header="$runtime/vendor/dolphin/GXRuntime/src/core/cpu_interpreter_private.h"
candidate_root="${1:-$root/generated/aot/device-fresh-normalization-r911/RMGE01_generated}"
build="${2:-$root/generated/build/ios-simulator-normalization-r911}"
target_name="chunk_1202_text1_804B60A0.c"
target="$source_root/chunks/$target_name"
helper="$root/patches/experiments/normalization-vector.inc"

die() { echo "build-ios-simulator-normalization-candidate: $*" >&2; exit 1; }
[[ -f "$source_root/generated.h" && -f "$source_root/generated_smc.txt" &&
   -f "$source_root/main.dol" && -f "$target" && -f "$helper" &&
   -f "$private_header" ]] ||
  die "current AOT or candidate helper is incomplete"
[[ "$(shasum -a 256 "$target" | awk '{print $1}')" == \
   38d5085e7e8eceece0521f5566c012a5c15fa5a7be7c2c1fe915985d28c376ac ]] ||
  die "normalization chunk identity changed; refuse to patch"
[[ ! -e "$candidate_root" ]] || die "candidate AOT directory already exists: $candidate_root"

mkdir -p "$candidate_root/chunks"
for name in generated.h generated_smc.txt main.dol RMGE01.h RMGE01.c; do
  [[ -e "$source_root/$name" ]] && ln -s "$source_root/$name" "$candidate_root/$name"
done
for source in "$source_root"/chunks/*.c; do
  name="$(basename -- "$source")"
  destination="$candidate_root/chunks/$name"
  if [[ "$name" == "$target_name" ]]; then
    python3 - "$source" "$destination" "$helper" "$private_header" <<'PY'
import hashlib
import sys

source_path, destination_path, helper_path = sys.argv[1:]
source = open(source_path, encoding='utf-8').read()
helper = open(helper_path, encoding='utf-8').read()
entry = '    if (!ppc_fp_available_inline(ctx, 0x804B6BE0u)) return;'
assert source.count(entry) == 1
assert source.count('void func_804B60A0(CPUState* ctx) {') == 1
candidate = source.replace(entry, entry + '\n    if (norm_vector_try(ctx)) goto label_804B6C04;', 1)
candidate = candidate.replace(
    'void func_804B60A0(CPUState* ctx) {',
    '#include "' + sys.argv[4] + '"\n' + helper +
    '\nvoid func_804B60A0(CPUState* ctx) {', 1)
open(destination_path, 'w', encoding='utf-8').write(candidate)
print('patched normalization entry:', destination_path)
PY
  else
    ln -s "$source" "$destination"
  fi
done

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
shasum -a 256 "$build/gRMGE01_recomp.dylib"
