#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mkdir -p "$root/generated/tests"
xcrun clang++ -std=c++20 -fsanitize=address,undefined -Wall -Wextra -Werror \
  "$root/tests/test-mobile-control-size.cpp" -o "$root/generated/tests/mobile-control-size"
"$root/generated/tests/mobile-control-size"
echo "Mobile control sizing: finite values, touch minimums and viewport bounds pass"
