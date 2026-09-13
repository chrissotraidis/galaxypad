#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
include="${GALAXYPAD_MODERNGEKKO_INCLUDE:-$root/ref/ModernGekko/include}"
test_dir="$(mktemp -d "${TMPDIR:-/tmp}/galaxypad-thp-patch.XXXXXX")"
trap 'rm -rf "$test_dir"' EXIT
clang -std=c11 -Wall -Wextra -Werror -fsanitize=address,undefined \
  -I "$include" -I "$root/apple/shared" "$root/tests/test-thp-patch.c" \
  "$root/apple/shared/GalaxyPadTHPPatch.c" -o "$test_dir/thp-patch"
"$test_dir/thp-patch"
