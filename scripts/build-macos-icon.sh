#!/usr/bin/env bash
# Derive standard macOS icon slots from GalaxyPad's original raster source.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
iconset="$root/generated/branding/GalaxyPad.iconset"
mkdir -p "$iconset"
for size in 16 32 128 256 512; do
  sips -z "$size" "$size" "$root/apple/branding/galaxypad-icon-source.png" \
    --out "$iconset/icon_${size}x${size}.png" >/dev/null
  double=$((size * 2))
  sips -z "$double" "$double" "$root/apple/branding/galaxypad-icon-source.png" \
    --out "$iconset/icon_${size}x${size}@2x.png" >/dev/null
done
iconutil -c icns "$iconset" -o "$root/generated/branding/GalaxyPad.icns"
