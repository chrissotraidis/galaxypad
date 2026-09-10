#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mkdir -p "$root/generated/tests"
xcrun clang++ -std=c++20 -fsanitize=address,undefined -Wall -Wextra -Werror \
  "$root/tests/test-mobile-stick-routing.cpp" -o "$root/generated/tests/mobile-stick-routing"
"$root/generated/tests/mobile-stick-routing"
echo "Mobile movement/tilt routing, sensitivity, inversion and mode-release tests pass"
