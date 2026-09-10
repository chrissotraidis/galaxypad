#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
if [[ $# != 1 ]]; then
  echo "Usage: bash tests/run-mobile-ui.sh BOOTED_SIMULATOR_UUID" >&2
  exit 2
fi
device="$1"
# Never boot another device or terminate a product runtime for a UI test.
xcrun simctl list devices booted --json | python3 -c '
import json, sys
devices = [d["udid"] for group in json.load(sys.stdin)["devices"].values()
           for d in group if d["state"] == "Booted"]
if devices != [sys.argv[1]]:
    sys.exit("Exactly the requested Simulator must already be booted")
' "$device"
bash "$root/tests/build-mobile-ui.sh"
log="$(mktemp "$root/generated/tests/mobile-ui.XXXXXX")"
echo "UIKit test log: $log"
xcrun simctl install "$device" "$root/generated/tests/OverlayTests.app"
xcrun simctl launch --console "$device" org.galaxypad.overlay-tests > "$log" 2>&1
python3 "$root/tests/check-mobile-ui-result.py" "$log"
