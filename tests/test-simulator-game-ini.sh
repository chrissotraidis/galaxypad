#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
source "$root/scripts/simulator-game-ini.sh"
fixture="$(mktemp -d)"
trap 'rm -rf "$fixture"' EXIT
support="$fixture/User"
target="$support/GameSettings/RMGE01r0.ini"
printf '[Video_Hacks]\nEFBAccessTileSize = 0\n' > "$fixture/candidate.ini"

galaxypad_stage_game_ini "$support" "$fixture/candidate.ini" "$fixture/run1"
cmp "$target" "$fixture/candidate.ini"
[[ ! -e "$support/Config/GameSettings" ]]
galaxypad_restore_game_ini
[[ ! -e "$target" ]]
galaxypad_restore_game_ini # cleanup is idempotent

printf '[Video_Hacks]\nEFBAccessTileSize = 64\n' > "$target"
cp "$target" "$fixture/original.ini"
printf 'unrelated game settings\n' > "$support/GameSettings/RMG.ini"
galaxypad_stage_game_ini "$support" "$fixture/candidate.ini" "$fixture/run2"
cmp "$target" "$fixture/candidate.ini"
galaxypad_restore_game_ini
cmp "$target" "$fixture/original.ini"
[[ "$(cat "$support/GameSettings/RMG.ini")" == 'unrelated game settings' ]]
if galaxypad_stage_game_ini "$support" "$fixture/missing.ini" "$fixture/missing-run"; then
  echo 'accepted missing input' >&2; exit 1
fi
cmp "$target" "$fixture/original.ini"

galaxypad_stage_game_ini "$support" "$fixture/candidate.ini" "$fixture/run3"
printf 'concurrent change\n' > "$target"
if galaxypad_restore_game_ini 2> "$fixture/conflict.log"; then
  echo 'unexpectedly overwrote a concurrent change' >&2; exit 1
fi
[[ "$(cat "$target")" == 'concurrent change' ]]
cmp "$fixture/run3/game-ini/before.ini" "$fixture/original.ini"
galaxypad_game_ini_target=""
echo 'Simulator INI staging uses the runtime path, restores controls and preserves conflicting writes'
