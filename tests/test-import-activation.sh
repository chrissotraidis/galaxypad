#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mkdir -p "$root/generated/tests"
xcrun clang++ -std=c++23 -fsanitize=address,undefined -Wall -Wextra -Werror \
  "$root/tests/test-import-activation.cpp" -o "$root/generated/tests/import-activation"
"$root/generated/tests/import-activation"
