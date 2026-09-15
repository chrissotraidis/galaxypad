#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mkdir -p "$root/generated/tests"
xcrun clang++ -std=c++23 -fsanitize=address,undefined -Wall -Wextra -Werror \
  "$root/tests/test-import-image-policy.cpp" -o "$root/generated/tests/import-image-policy"
"$root/generated/tests/import-image-policy"
echo "WBFS container bounds and storage sizing passed"
