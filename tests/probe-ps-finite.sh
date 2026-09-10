#!/usr/bin/env bash
# Isolated experiment: not linked into GalaxyPad and not a speed acceptance gate.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
output="$root/generated/tests/ps-finite-probe"
mkdir -p "$root/generated/tests"
clang -O2 -std=c11 -ffp-contract=off -fno-fast-math \
  -ffunction-sections -fdata-sections \
  -I "$root/ref/ModernGekko/vendor/dolphin/GXRuntime/src/core" \
  -I "$root/ref/ModernGekko/vendor/dolphin/GXRuntime/include" \
  "$root/tests/probe-ps-finite.c" -Wl,-dead_strip -o "$output"
"$output"
