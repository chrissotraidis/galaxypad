#!/usr/bin/env bash
# Generate GalaxyPad's exact-DOL portable-C AOT input with a fail-closed Wii guard.
set -euo pipefail

# The pinned generator's benchmark option skips mutable-code validation at
# dispatch boundaries and is not part of GalaxyPad's supported cache identity.
[[ "${DOLRECOMP_UNSAFE_DIRECT_CALLS:-}" != 1 ]] || {
  echo "unsafe cross-chunk direct calls are not supported by GalaxyPad" >&2
  exit 1
}

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mode=${1:-generate}
extraction=${GALAXYPAD_EXTRACTION:-$root/generated/extracted/run1}
output=${GALAXYPAD_AOT_OUTPUT:-$root/generated/aot/c}
titles=${GALAXYPAD_TITLES_DB:-$root/config/gametdb-titles.txt}
dolrecomp=${GALAXYPAD_DOLRECOMP_BIN:-$root/generated/build/dolrecomp/dolrecomp}
expected_dol_sha=2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09

[[ -x "$dolrecomp" ]] || { echo "missing built DolRecomp: $dolrecomp" >&2; exit 1; }
[[ -f "$extraction/sys/main.dol" ]] || { echo "missing extracted main.dol" >&2; exit 1; }
[[ -f "$titles" ]] || { echo "missing pinned title database; refusing Wii generation" >&2; exit 1; }
rg -q '^RMGE01[[:space:]]*=' "$titles" || {
  echo "title database does not contain exact RMGE01; refusing Wii generation" >&2
  exit 1
}

actual_dol_sha="$(shasum -a 256 "$extraction/sys/main.dol" | awk '{print $1}')"
[[ "$actual_dol_sha" == "$expected_dol_sha" ]] || {
  echo "main.dol identity mismatch: $actual_dol_sha" >&2
  exit 1
}

if [[ "$mode" == --preflight ]]; then
  echo "Wii AOT preflight passed: RMGE01, Broadway, MEM2=0x04000000"
  exit 0
fi
[[ "$mode" == generate ]] || { echo "usage: $0 [generate|--preflight]" >&2; exit 2; }

state="$root/generated/dolrecomp-state"
mkdir -p "$state/database" "$output"
cp "$titles" "$state/database/titles.txt"
log="$root/generated/aot/dolrecomp-rmge01.log"

(
  cd "$state"
  "$dolrecomp" -j"${GALAXYPAD_JOBS:-8}" --backend=c --cpu broadway \
    "$extraction/sys/main.dol" RMGE01 "$output"
) 2>&1 | tee "$log"

header="$output/RMGE01_generated/RMGE01.h"
[[ -f "$header" ]] || { echo "missing expected Wii-named generated header" >&2; exit 1; }
rg -q '^#define DOLRECOMP_CPU_BROADWAY 1$' "$header" || {
  echo "generated header does not declare Broadway" >&2
  exit 1
}
if rg -q 'using GameCube mode|cpu:[[:space:]]+Gekko' "$log"; then
  echo "DolRecomp silently entered GameCube mode" >&2
  exit 1
fi

echo "Generated exact RMGE01 portable-C AOT input with Broadway guard."
