#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mkdir -p "$root/generated/tests"
clang++ -std=c++17 -Wall -Wextra -Werror -fsanitize=address,undefined \
  "$root/tests/test-gyro-aim.cpp" -o "$root/generated/tests/gyro-aim"
"$root/generated/tests/gyro-aim"
