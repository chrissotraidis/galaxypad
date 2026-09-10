#!/usr/bin/env bash
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
temporary="$(mktemp -d "${TMPDIR:-/tmp}/galaxypad-wii-pipe.XXXXXX")"
trap 'rm -rf "$temporary"' EXIT

pipe_path="$($root/scripts/wii-pipe.py configure --user-dir "$temporary/user")"
[[ -p "$pipe_path" ]]
config="$temporary/user/Config/WiimoteNew.ini"
grep -Fq 'Device = Pipe/0/galaxypad' "$config"
grep -Fq 'Buttons/B = `Button X`' "$config"
grep -Fq 'Extension = Nunchuk' "$config"
grep -Fq 'Options/Sideways Wiimote = False' "$config"
grep -Fq 'Nunchuk/Stick/Up = `Axis MAIN Y -`' "$config"
grep -Fq 'IR/Right = `Axis C X +`' "$config"
grep -Fq 'Shake/Z = `Button L`' "$config"
! grep -Fq 'Extension = None' "$config"

if "$root/scripts/wii-pipe.py" configure --user-dir "$temporary/user" 2>/dev/null; then
  echo "configure unexpectedly replaced an existing controller profile" >&2
  exit 1
fi

actual="$temporary/commands.txt"
"$root/scripts/wii-pipe.py" run \
  --sequence "$root/tests/fixtures/wii-pipe-sequence.json" --dry-run >"$actual"
expected="$temporary/expected.txt"
printf '%s\n' \
  'SET C 0.625 0.750' \
  'SET MAIN 0.000 0.000' \
  'PRESS A' 'RELEASE A' \
  'PRESS X' 'RELEASE X' \
  'PRESS B' 'RELEASE B' \
  'PRESS Z' 'RELEASE Z' \
  'PRESS START' 'RELEASE START' \
  'PRESS L' 'RELEASE L' >"$expected"
cmp "$expected" "$actual"

g5_actual="$temporary/g5-commands.txt"
"$root/scripts/wii-pipe.py" run \
  --sequence "$root/tests/fixtures/g5-title-file-select.json" --dry-run >"$g5_actual"
printf '%s\n' \
  'PRESS A' 'RELEASE A' \
  'PRESS A' 'PRESS X' 'RELEASE X' 'RELEASE A' \
  'SET C 0.375 0.660' >"$expected"
cmp "$expected" "$g5_actual"

observatory_actual="$temporary/observatory-commands.txt"
"$root/scripts/wii-pipe.py" run \
  --sequence "$root/tests/fixtures/g6-observatory-save-load.json" --dry-run >"$observatory_actual"
printf '%s\n' \
  'PRESS A' 'PRESS X' 'RELEASE A' 'RELEASE X' \
  'SET C 0.410 0.660' 'PRESS A' 'RELEASE A' \
  'SET C 0.685 0.880' 'PRESS A' 'RELEASE A' \
  'SET C 0.500 0.500' 'SET MAIN 0.500 0.500' >"$expected"
cmp "$expected" "$observatory_actual"

"$root/scripts/wii-pipe.py" run \
  --sequence "$root/tests/fixtures/g6-observatory-control-smoke.json" --dry-run >"$observatory_actual"
printf '%s\n' \
  'SET MAIN 0.750 0.500' 'SET MAIN 0.500 0.500' \
  'PRESS A' 'RELEASE A' 'PRESS L' 'RELEASE L' \
  'SET MAIN 0.250 0.500' 'SET MAIN 0.500 0.500' >"$expected"
cmp "$expected" "$observatory_actual"

echo "GalaxyPad Wii Pipe controller tests passed"
