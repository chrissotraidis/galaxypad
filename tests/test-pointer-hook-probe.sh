#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mkdir -p "$root/generated/tests"
xcrun clang++ -std=c++23 -fobjc-arc -fsanitize=address,undefined -Wall -Wextra \
  -I "$root/ref/ModernGekko/include" "$root/tests/test-pointer-hook-probe.mm" \
  "$root/ref/ModernGekko/src/runtime/mod_loader.cpp" -framework Foundation \
  -o "$root/generated/tests/pointer-hook-probe"
"$root/generated/tests/pointer-hook-probe"
