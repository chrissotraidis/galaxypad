#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mkdir -p "$root/generated/tests"
xcrun clang++ -std=c++23 -fsanitize=address,undefined -Wall -Wextra -Werror \
  "$root/tests/test-native-observer-binding.cpp" -o "$root/generated/tests/native-observer-binding"
"$root/generated/tests/native-observer-binding"
