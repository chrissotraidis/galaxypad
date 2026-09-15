#!/usr/bin/env bash
# Sourced by the private Simulator runner; never targets a physical device.
galaxypad_game_ini_target=""

galaxypad_stage_game_ini() {
  local support="$1" source="$2" evidence="$3"
  # Dolphin loads revision-specific files last, under User/GameSettings.
  local target="$support/GameSettings/RMGE01r0.ini"
  [[ -f "$source" && ! -L "$target" && ! -d "$target" ]] || return 1
  [[ ! -e "$evidence/game-ini" ]] || return 1
  mkdir -p "$evidence/game-ini" "$support/GameSettings" || return 1
  galaxypad_game_ini_evidence="$evidence/game-ini"
  cp "$source" "$galaxypad_game_ini_evidence/requested.ini" || return 1
  if [[ -f "$target" ]]; then
    cp -p "$target" "$galaxypad_game_ini_evidence/before.ini" || return 1
  fi
  local temporary
  temporary="$(mktemp "$support/GameSettings/.galaxypad-ini.XXXXXX")" || return 1
  if ! cp "$galaxypad_game_ini_evidence/requested.ini" "$temporary" || ! mv "$temporary" "$target"; then
    rm -f -- "$temporary"
    return 1
  fi
  galaxypad_game_ini_target="$target"
}

galaxypad_restore_game_ini() {
  [[ -n "$galaxypad_game_ini_target" ]] || return 0
  # Preserve unexpected writes rather than silently overwriting another owner.
  if ! cmp -s "$galaxypad_game_ini_target" "$galaxypad_game_ini_evidence/requested.ini"; then
    echo "Simulator game INI changed during the run; retained it and the backup in $galaxypad_game_ini_evidence" >&2
    return 1
  fi
  if [[ -f "$galaxypad_game_ini_evidence/before.ini" ]]; then
    cp -p "$galaxypad_game_ini_evidence/before.ini" "$galaxypad_game_ini_target" || return 1
  else
    rm -- "$galaxypad_game_ini_target" || return 1
  fi
  galaxypad_game_ini_target=""
}
