#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
out="$root/generated/tests/native-diagnostics"
mkdir -p "$out"
clang -std=c11 -O1 -fsanitize=address,undefined \
  -I"$root/ref/ModernGekko/include" "$root/tests/test-thp-timing.c" \
  -o "$out/thp-timing"
"$out/thp-timing" > "$out/thp-timing.log" 2>&1
# Verify rendered diagnostic fields as well as the fixture's state assertions.
rg -q 'seconds=0.074 idle_since_last_call=60.000 calls=3 fallback=1' "$out/thp-timing.log"
rg -q 'dispatch_max_ms=63.000 cpu_calls=2 cpu_mean_ms=6.000 cpu_at_max_wall_ms=3.000' "$out/thp-timing.log"
clang++ -std=c++20 -O1 -fsanitize=address,undefined \
  -I"$root/ref/ModernGekko/include" "$root/tests/test-mod-address-lookup.cpp" \
  "$root/ref/ModernGekko/src/runtime/mod_loader.cpp" -o "$out/mod-lookup"
"$out/mod-lookup"
echo "Native diagnostic and hook-lookup regressions passed"
