#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
testdir="$(mktemp -d "${TMPDIR:-/tmp}/galaxypad-pause-events.XXXXXX")"
trap 'rm -rf "$testdir"' EXIT
# Optional overlay supports exact old-source differential testing without edits.
extra=(-fno-exceptions)
if [[ $# -gt 0 ]]; then extra+=(-ivfsoverlay "$1"); fi
xcrun clang++ -std=c++23 -fobjc-arc -fblocks -Wall -Wextra \
  "${extra[@]}" "$root/tests/test-controller-pause-events.mm" \
  "$root/apple/ios/GalaxyPadControllers.mm" \
  "$root/apple/shared/GalaxyPadControllerMappingStore.mm" \
  -framework Foundation -framework GameController -framework QuartzCore \
  -o "$testdir/pause-events"
"$testdir/pause-events"
