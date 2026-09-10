#!/usr/bin/env bash
# Validate the selected RMGE01 desktop module without exposing generated code.
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
marker="$root/generated/modules/RMGE01/active-module.txt"
info="$root/generated/build/moderngekko-desktop/moderngekko-module-info"

[[ $# -le 1 ]] || { echo "usage: $0 [absolute-candidate-module]" >&2; exit 2; }
if [[ $# -eq 1 ]]; then
  module="$1"
else
  [[ -f "$marker" ]] || { echo "missing active RMGE01 module marker" >&2; exit 1; }
  module="$(<"$marker")"
fi
[[ "$module" == /* ]] || { echo "active module path is not absolute" >&2; exit 1; }
[[ -f "$module" ]] || { echo "active module is missing: $module" >&2; exit 1; }
[[ -x "$info" ]] || { echo "missing moderngekko-module-info" >&2; exit 1; }
artifact="$(dirname "$module")"
manifest="$artifact/manifest.txt"
[[ -f "$manifest" ]] || { echo "module manifest is missing" >&2; exit 1; }
chunk_instructions="$(awk -F= '$1 == "c_chunk_instructions" {print $2}' "$manifest")"
dispatch_lookup="$(awk -F= '$1 == "dispatch_lookup" {print $2}' "$manifest")"
[[ "$chunk_instructions" =~ ^[0-9]+$ ]] || {
  echo "module manifest has no valid C chunk size" >&2
  exit 1
}
[[ "$dispatch_lookup" == linear || "$dispatch_lookup" == indexed ]] || {
  echo "module manifest has no valid dispatch lookup mode" >&2
  exit 1
}
chunks_dir="$(find -H "$artifact/dolrecomp-output" -type d -name chunks -print -quit)"
[[ -d "$chunks_dir" ]] || { echo "module generated chunks are missing" >&2; exit 1; }
expected_chunks="$(find "$chunks_dir" -maxdepth 1 -type f -name 'chunk_*.c' | wc -l | tr -d ' ')"
[[ "$expected_chunks" -gt 0 ]] || { echo "module generated chunk count is zero" >&2; exit 1; }

# Older accepted manifests predate this policy. New declarations must match
# the exact generated header whose semantics and runtime were verified.
two_range_policy="$(awk -F= '$1 == "two_range_policy" {print $2}' "$manifest")"
case "$two_range_policy" in
  ''|none) ;;
  rmge01-two-range-v1)
    [[ "$chunk_instructions" == 1024 && "$dispatch_lookup" == indexed ]] || {
      echo "two-range policy has incompatible generation settings" >&2; exit 1;
    }
    generated_header="$(dirname "$chunks_dir")/RMGE01.h"
    [[ -f "$generated_header" ]] || { echo "two-range header is missing" >&2; exit 1; }
    [[ "$(shasum -a 256 "$generated_header" | awk '{print $1}')" == \
      da2def2ce566f57929afe0a8a2f7de5539b17624eb37452d6928790ac6999336 ]] || {
      echo "two-range header identity mismatch" >&2; exit 1;
    }
    cmp "$generated_header" "$(dirname "$chunks_dir")/generated.h"
    ;;
  *) echo "unknown two-range policy: $two_range_policy" >&2; exit 1 ;;
esac

file "$module" | rg -q 'Mach-O 64-bit dynamically linked shared library arm64$' || {
  echo "module is not an arm64 Mach-O dylib" >&2
  exit 1
}
vtool -show-build "$module" | rg -q 'platform +MACOS$' || {
  echo "module does not target macOS" >&2
  exit 1
}
vtool -show-build "$module" | rg -q 'minos +14\.0$' || {
  echo "module minimum macOS is not 14.0" >&2
  exit 1
}

details="$($info "$module")"
rg -q '^game_id=RMGE01$' <<<"$details" || { echo "module game ID mismatch" >&2; exit 1; }
rg -q '^entry_point=0x8000403c$' <<<"$details" || { echo "module entry mismatch" >&2; exit 1; }
rg -q '^smc_ranges=19$' <<<"$details" || { echo "module SMC table mismatch" >&2; exit 1; }
rg -q "^chunk_ranges=$expected_chunks$" <<<"$details" || {
  echo "module chunk table mismatch" >&2
  exit 1
}

echo "Module audit passed: RMGE01, arm64 macOS 14.0, $expected_chunks chunks ($chunk_instructions instructions, $dispatch_lookup dispatch), 19 SMC ranges."
