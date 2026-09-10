#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
test_dir="$(mktemp -d "${TMPDIR:-/tmp}/galaxypad-mobile-input.XXXXXX")"
trap 'rm -f "$test_dir/input"; rmdir "$test_dir"' EXIT
clang++ -std=c++17 -O1 -fsanitize=address,undefined -Wall -Wextra -Werror \
  "$root/tests/test-mobile-input.cpp" -o "$test_dir/input"
"$test_dir/input"
