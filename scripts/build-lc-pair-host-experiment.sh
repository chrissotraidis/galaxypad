#!/usr/bin/env bash
# Temporarily layer only this experiment, preserve runner, then undo its source delta.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
vendor="$root/ref/ModernGekko/vendor/dolphin"
patch_file="$root/patches/experiments/lc-pair-host.patch"
output="$root/generated/lc-pair-r116"
[[ "$(shasum -a 256 "$patch_file" | awk '{print $1}')" == 87d3d595ff69f2619ce0a7dc90b290e6882b36e7dba5eb16f4946db9b4b950a1 ]] || exit 1
[[ ! -e "$output/GalaxyPadRunner" ]] || { echo 'Candidate exists; audit it instead of overwriting.' >&2; exit 1; }
git -C "$vendor" apply --check "$patch_file"
mkdir -p "$output"
git -C "$vendor" apply "$patch_file"
restore() {
  git -C "$vendor" apply --reverse --check "$patch_file" &&
    git -C "$vendor" apply --reverse "$patch_file"
}
trap restore EXIT
cmake --build "$root/generated/build/moderngekko-desktop" --target moderngekko-run --parallel 4
cp "$root/generated/build/moderngekko-desktop/moderngekko-run" "$output/GalaxyPadRunner"
shasum -a 256 "$output/GalaxyPadRunner"
echo 'Candidate saved; experiment source delta will be reversed. Normal app was not touched.'
