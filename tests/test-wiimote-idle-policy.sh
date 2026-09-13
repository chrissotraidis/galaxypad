#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
testdir="$(mktemp -d "${TMPDIR:-/tmp}/galaxypad-wiimote-idle.XXXXXX")"
trap 'rm -rf "$testdir"' EXIT
xcrun clang++ -std=c++23 -Wall -Wextra \
  "$root/tests/test-wiimote-idle-policy.cpp" -o "$testdir/idle-policy"
"$testdir/idle-policy"
