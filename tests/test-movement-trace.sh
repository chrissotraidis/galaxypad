#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mkdir -p "$root/generated/tests"
xcrun clang++ -std=c++20 -Wall -Wextra -Werror -fsanitize=address,undefined \
  "$root/tests/test-movement-trace.cpp" -o "$root/generated/tests/movement-trace"
for setting in 0 true 01; do
  result="$(GALAXYPAD_MOVEMENT_TRACE="$setting" "$root/generated/tests/movement-trace" 2>&1)"
  test -z "$result"
done
GALAXYPAD_MOVEMENT_TRACE=1 "$root/generated/tests/movement-trace" 2> "$root/generated/tests/movement-trace.log"
test "$(wc -l < "$root/generated/tests/movement-trace.log" | tr -d ' ')" = 128
sed -n '1p' "$root/generated/tests/movement-trace.log" | rg -q 'poll=2 x=1.000000 y=-0.500000'
sed -n '2p' "$root/generated/tests/movement-trace.log" | rg -q 'poll=4 x=0.000000 y=0.000000'
echo 'Movement trace exact opt-in, change-only records and cap pass'
