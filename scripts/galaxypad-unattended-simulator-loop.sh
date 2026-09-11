#!/usr/bin/env bash
# Reproduce the fixed GalaxyPad scene without human input.
# This is a private Simulator diagnostic lane; it never installs to a physical
# device and never enables persistent frame logging.
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
simulator="${GALAXYPAD_SIMULATOR_UDID:-4E5EE60F-2887-4653-9508-F659BD433121}"
app="${1:-$root/generated/build/ios-simulator-app/GalaxyPad.app}"
output="${2:-$root/generated/runtime/simulator-loop-$(date +%Y%m%d-%H%M%S)}"
input="${GALAXYPAD_SIMULATOR_INPUT:-$root/generated/ios-dev-input.json}"
game_root="${GALAXYPAD_SIMULATOR_GAME_ROOT:-$root/generated/extracted/run1}"
disc="${GALAXYPAD_SIMULATOR_DISC_IMAGE:-$root/generated/runtime/device-deploy/readback/RMGE01.wbfs}"
module="${GALAXYPAD_SIMULATOR_MODULE:-$root/generated/build/ios-simulator-fresh-module/gRMGE01_recomp.dylib}"
save_root="${GALAXYPAD_SIMULATOR_SAVE_ROOT:-$root/generated/runtime/ipad-iteration-1/preinstall/Wii}"
profile_seconds="${GALAXYPAD_SIMULATOR_PROFILE_SECONDS:-10}"
efb_trace="${GALAXYPAD_SIMULATOR_EFB_TRACE:-}"
local_game_ini="${GALAXYPAD_SIMULATOR_LOCAL_GAME_INI:-}"
frame_logging="${GALAXYPAD_SIMULATOR_FRAME_LOGGING:-NO}"
log_stream_pid=""

die() { echo "galaxypad-unattended-simulator-loop: $*" >&2; exit 1; }
cleanup() {
  if [[ -n "$log_stream_pid" ]]; then
    kill "$log_stream_pid" 2>/dev/null || true
  fi
  if [[ -n "$efb_trace" ]]; then
    xcrun simctl spawn "$simulator" launchctl unsetenv GALAXYPAD_EFB_TRACE >/dev/null 2>&1 || true
  fi
}
on_exit() {
  local status=$?
  set +e
  if (( status != 0 )) && [[ -d "$output" ]]; then
    {
      printf 'exit_status=%s\n' "$status"
      date
      printf '%s\n' '--- booted devices ---'
      xcrun simctl list devices booted
      printf '%s\n' '--- GalaxyPad launchd state ---'
      xcrun simctl spawn "$simulator" launchctl list | rg 'GalaxyPad|org.galaxypad' || true
      printf '%s\n' '--- host pid state ---'
      if [[ -f "$output/pid.txt" ]]; then
        ps -p "$(<"$output/pid.txt")" -o pid,lstart,stat,command
      else
        printf '%s\n' 'no pid.txt'
      fi
      printf '%s\n' '--- console tail ---'
      if [[ -f "$output/console.log" ]]; then
        tail -100 "$output/console.log"
      else
        printf '%s\n' 'no console.log'
      fi
    } > "$output/failure-state.log" 2>&1
  fi
  cleanup
  exit "$status"
}
trap on_exit EXIT

[[ -d "$app" ]] || die "missing Simulator app: $app"
[[ -d "$game_root" ]] || die "missing extracted game root: $game_root"
[[ -f "$disc" ]] || die "missing private disc image: $disc"
[[ -f "$module" ]] || die "missing Simulator module: $module"
[[ -d "$save_root" ]] || die "missing private save seed: $save_root"
[[ "$profile_seconds" =~ ^[1-9][0-9]*$ ]] || die "profile seconds must be a positive integer"
[[ "$frame_logging" == YES || "$frame_logging" == NO ]] || die "frame logging must be YES or NO"
if [[ -n "$local_game_ini" && ! -f "$local_game_ini" ]]; then
  die "missing local game INI: $local_game_ini"
fi
if [[ -n "$efb_trace" ]]; then
  mkdir -p "$(dirname -- "$efb_trace")"
fi

mkdir -p "$output"
mkdir -p "$(dirname -- "$input")"
# Start from a neutral lease. The unattended lane owns this generated file;
# callers do not need to create it manually before the first launch.
if [[ ! -f "$input" ]]; then
  python3 "$root/scripts/simulator-input.py" "$input" '{}' --seconds 0.1
fi

booted="$(xcrun simctl list devices booted)"
if [[ -n "$(printf '%s\n' "$booted" | rg -v '^--|^$' | rg '\(Booted\)' || true)" ]]; then
  if printf '%s\n' "$booted" | rg -q "$simulator"; then
    printf '%s\n' "$booted" | rg '\(Booted\)' > "$output/other-booted-simulators.log"
  elif [[ "${GALAXYPAD_ALLOW_OTHER_SIMULATORS:-0}" == 1 ]]; then
    printf '%s\n' "$booted" | rg '\(Booted\)' > "$output/other-booted-simulators.log"
    echo "allowing unrelated booted Simulators; host-pressure comparison is qualified" \
      | tee "$output/simulator-isolation-warning.log"
    xcrun simctl boot "$simulator" 2>&1 | tee "$output/boot.log"
  else
    die "another Simulator is booted; stop it explicitly or set GALAXYPAD_ALLOW_OTHER_SIMULATORS=1"
  fi
else
  xcrun simctl boot "$simulator" 2>&1 | tee "$output/boot.log"
fi
xcrun simctl bootstatus "$simulator" -b 2>&1 | tee "$output/bootstatus.log"

xcrun simctl install "$simulator" "$app" 2>&1 | tee "$output/install.log"
data_container="$(xcrun simctl get_app_container "$simulator" org.galaxypad.GalaxyPad data)"
support="$data_container/Library/Application Support/GalaxyPad"
mkdir -p "$support" "$data_container/Library/Preferences"
# Seed only the private Wii/NAND state. Do not copy the disc image into the
# app container: the Simulator launch uses the explicit read-only host paths.
rsync -a "$save_root/" "$support/Wii/"
if [[ -n "$local_game_ini" ]]; then
  mkdir -p "$support/Config/GameSettings"
  cp "$local_game_ini" "$support/Config/GameSettings/RMG.ini"
fi
if [[ -f "$root/generated/runtime/ipad-iteration-1/preinstall/Preferences/org.galaxypad.GalaxyPad.plist" ]]; then
  cp "$root/generated/runtime/ipad-iteration-1/preinstall/Preferences/org.galaxypad.GalaxyPad.plist" \
    "$data_container/Library/Preferences/org.galaxypad.GalaxyPad.plist"
fi
shasum -a 256 "$support/Wii/title/00010000/524d4745/data/GameData.bin" \
  | tee "$output/save-seed.sha256"

xcrun simctl terminate "$simulator" org.galaxypad.GalaxyPad >/dev/null 2>&1 || true
if [[ -n "$efb_trace" ]]; then
  xcrun simctl spawn "$simulator" launchctl setenv GALAXYPAD_EFB_TRACE "$efb_trace"
fi
xcrun simctl spawn "$simulator" log stream --style compact --level debug \
  --predicate 'process == "GalaxyPad"' > "$output/console.log" 2>&1 &
log_stream_pid=$!
sleep 3

launch_output="$(xcrun simctl launch "$simulator" org.galaxypad.GalaxyPad \
  -GalaxyPadDevGameRoot "$game_root" \
  -GalaxyPadDevDiscImage "$disc" \
  -GalaxyPadDevModule "$module" \
  -GalaxyPadDevInputFile "$input" \
  -GalaxyPadLogFrameRateWindows "$frame_logging" \
  -GalaxyPadShowFPSCounter YES)"
printf '%s\n' "$launch_output" | tee "$output/launch.txt"
pid="$(printf '%s\n' "$launch_output" | awk -F': ' '/org\.galaxypad\.GalaxyPad/{print $2; exit}')"
[[ "$pid" =~ ^[0-9]+$ ]] || die "could not resolve Simulator GalaxyPad PID"
printf '%s\n' "$pid" > "$output/pid.txt"

# Runtime creation includes loading the large private module and first Metal
# pipelines. Do not inject input on a fixed short timer: that races the core's
# controller initialization and can turn a valid launch into a false crash.
# The first nonzero viewport is the app's existing "renderer is presenting"
# readiness signal.
ready=0
ready_deadline=$((SECONDS + 180))
while (( SECONDS < ready_deadline )); do
  if rg -q 'Overlay viewport changed' "$output/console.log"; then
    ready=1
    break
  fi
  if ! xcrun simctl spawn "$simulator" launchctl list 2>/dev/null |
      rg -q 'org\.galaxypad\.GalaxyPad'; then
    die "GalaxyPad exited before the Simulator renderer became ready"
  fi
  sleep 1
done
(( ready == 1 )) || die "Simulator renderer did not become ready within 180 seconds"

# Observed unattended navigation from the title screen to the seeded file,
# Play, and the late-game plaza. The title screen needs a sustained A+B hold;
# a short edge is accepted by the guest but does not transition, and this host
# required 30 seconds before the title moved. Settle the pointer before each A
# edge, as required by the file-select path.
python3 "$root/scripts/simulator-input.py" "$input" '{"buttons":3}' --seconds 30
sleep 3
python3 "$root/scripts/simulator-input.py" "$input" \
  '{"buttons":1,"pointerVisible":1,"pointerX":0.375,"pointerY":0.66}' \
  --aim-first 1 --seconds 0.8
sleep 3
python3 "$root/scripts/simulator-input.py" "$input" \
  '{"buttons":1,"pointerVisible":1,"pointerX":0.73,"pointerY":0.88}' \
  --aim-first 1 --seconds 0.8
sleep 5
# The seeded file opens on the first story page. Advance its A-gated pages
# without a human operator; the final pulses are intentionally bounded so the
# loop reaches a repeatable late-game plaza without wandering indefinitely.
for _ in $(seq 1 30); do
  python3 "$root/scripts/simulator-input.py" "$input" \
    '{"buttons":1}' --seconds 0.5
  sleep 0.8
done
sleep 5

xcrun simctl io "$simulator" screenshot "$output/scene.png"
# xctrace can leave a Simulator attach open indefinitely on this host even
# after its advertised time limit. `sample` uses the same host PID, has a
# bounded duration, and preserves the native/SDL/generated stack names needed
# for hotspot attribution without holding the loop open.
sample "$pid" "$profile_seconds" 1 -mayDie -fullPaths \
  -file "$output/cpu-sample.txt" > "$output/cpu-profile.log" 2>&1

rg 'simulator input accepted|\[GalaxyPad input device\]|\[GalaxyPad wiimote\]' \
  "$output/console.log" > "$output/input-route.log" || true

echo "unattended Simulator scene/profile complete: $output"
