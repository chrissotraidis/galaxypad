#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mkdir -p "$root/generated/tests"
xcrun clang++ -std=c++23 -fsanitize=address,undefined -Wall -Wextra \
  -I "$root/ref/ModernGekko/include" \
  "$root/tests/test-static-pointer-hooks.cpp" "$root/ref/ModernGekko/src/runtime/mod_loader.cpp" \
  -o "$root/generated/tests/static-pointer-hooks"
"$root/generated/tests/static-pointer-hooks"
