#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
for variable in GALAXYPAD_LC_BYTE_FAST GALAXYPAD_LC_PAIR_FAST; do
setting="$(sed -n "/^export $variable=/p" "$root/apple/macos/GalaxyPad")"
[[ -n "$setting" ]]
for value in unset 0 1; do
  actual="$(
    if [[ "$value" == unset ]]; then
      unset "$variable"
    else
      export "$variable=$value"
    fi
    eval "$setting"
    bash -c 'echo "${!1}"' -- "$variable"
  )"
  expected="$value"
  [[ "$value" != unset ]] || expected=1
  [[ "$actual" == "$expected" ]]
done
done
echo 'LC package default and inherited opt-out tests passed'
