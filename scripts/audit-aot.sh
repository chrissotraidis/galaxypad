#!/usr/bin/env bash
# Audit exact-DOL generated coverage and name every interpreter fallback site.
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
generated="${GALAXYPAD_GENERATED_AOT:-$root/generated/aot/c/RMGE01_generated}"
log="${GALAXYPAD_AOT_LOG:-$root/generated/aot/dolrecomp-rmge01.log}"
report="${GALAXYPAD_FALLBACK_REPORT:-$root/generated/aot/rmge01-fallbacks.txt}"

[[ -f "$generated/RMGE01.h" ]] || { echo "missing generated RMGE01 header" >&2; exit 1; }
[[ -f "$log" ]] || { echo "missing DolRecomp generation log" >&2; exit 1; }
rg -q '^#define DOLRECOMP_CPU_BROADWAY 1$' "$generated/RMGE01.h" || {
  echo "generated output is not marked Broadway" >&2
  exit 1
}
[[ "$(rg -o '[0-9]+ unknown$' "$log" | awk '{sum += $1} END {print sum + 0}')" == 0 ]] || {
  echo "generation did not prove zero unknown instructions" >&2
  exit 1
}
rg -q 'chunks: .* \(331 files\)$' "$log" || {
  echo "unexpected RMGE01 chunk count" >&2
  exit 1
}

mkdir -p "$(dirname "$report")"
rg --no-filename -B 1 'ppc_fallback_instruction' "$generated/chunks" --glob '*.c' |
  rg '^    // [0-9A-F]{8}:' |
  sed -E 's/^    \/\/ //' |
  LC_ALL=C sort -u > "$report"

fallback_calls="$(rg -o 'ppc_fallback_instruction' "$generated/chunks" --glob '*.c' | wc -l | tr -d ' ')"
named_sites="$(wc -l < "$report" | tr -d ' ')"
[[ "$named_sites" == "$fallback_calls" ]] || {
  echo "fallback inventory incomplete: $named_sites names for $fallback_calls calls" >&2
  exit 1
}
[[ "$named_sites" == 419 ]] || {
  echo "unexpected exact-RMGE01 fallback count: $named_sites" >&2
  exit 1
}

echo "AOT audit passed: Broadway, 331 chunks, 0 unknowns, 419 named fallback PCs."
