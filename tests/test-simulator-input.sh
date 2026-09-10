#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mkdir -p "$root/generated/tests"
xcrun clang++ -std=c++23 -fobjc-arc -framework Foundation \
  -fsanitize=address,undefined -Wall -Wextra -Werror \
  "$root/tests/test-simulator-input.mm" -o "$root/generated/tests/simulator-input"
"$root/generated/tests/simulator-input"
