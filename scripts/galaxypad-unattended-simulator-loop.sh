#!/usr/bin/env bash
# Reproduce the fixed GalaxyPad scene without human input.
# This is a private Simulator diagnostic lane; it never installs to a physical
# device and never enables persistent frame logging.
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
simulator="${GALAXYPAD_SIMULATOR_UDID:-4E5EE60F-2887-4653-9508-F659BD433121}"
app="${1:-$root/generated/build/ios-simulator-app/GalaxyPad.app}"
output="${2:-${GALAXYPAD_SIMULATOR_OUTPUT:-$root/generated/runtime/simulator-loop-$(date +%Y%m%d-%H%M%S)}}"
input="${GALAXYPAD_SIMULATOR_INPUT:-$root/generated/ios-dev-input.json}"
game_root="${GALAXYPAD_SIMULATOR_GAME_ROOT:-$root/generated/extracted/run1}"
disc="${GALAXYPAD_SIMULATOR_DISC_IMAGE:-$root/generated/runtime/device-deploy/readback/RMGE01.wbfs}"
module="${GALAXYPAD_SIMULATOR_MODULE:-$root/generated/build/ios-simulator-fresh-module/gRMGE01_recomp.dylib}"
save_root="${GALAXYPAD_SIMULATOR_SAVE_ROOT:-$root/generated/runtime/ipad-iteration-1/advanced-seed/Wii}"
profile_seconds="${GALAXYPAD_SIMULATOR_PROFILE_SECONDS:-10}"
efb_trace="${GALAXYPAD_SIMULATOR_EFB_TRACE:-}"
phase_trace="${GALAXYPAD_SIMULATOR_PHASE_TRACE:-}"
local_game_ini="${GALAXYPAD_SIMULATOR_LOCAL_GAME_INI:-}"
frame_logging="${GALAXYPAD_SIMULATOR_FRAME_LOGGING:-NO}"
simulator_stderr="${GALAXYPAD_SIMULATOR_STDERR:-}"
terminate_after_profile="${GALAXYPAD_SIMULATOR_TERMINATE_AFTER_PROFILE:-NO}"
system_trace="${GALAXYPAD_SIMULATOR_SYSTEM_TRACE:-}"
system_trace_seconds="${GALAXYPAD_SIMULATOR_SYSTEM_TRACE_SECONDS:-20}"
llvm_profile_file="${GALAXYPAD_SIMULATOR_LLVM_PROFILE_FILE:-}"
stop_after_scene="${GALAXYPAD_SIMULATOR_STOP_AFTER_SCENE:-NO}"
log_stream_pid=""

die() { echo "galaxypad-unattended-simulator-loop: $*" >&2; exit 1; }
cleanup() {
  if [[ -n "$log_stream_pid" ]]; then
    kill "$log_stream_pid" 2>/dev/null || true
  fi
  if [[ -n "$efb_trace" ]]; then
    xcrun simctl spawn "$simulator" launchctl unsetenv GALAXYPAD_EFB_TRACE >/dev/null 2>&1 || true
  fi
  if [[ -n "$phase_trace" ]]; then
    xcrun simctl spawn "$simulator" launchctl unsetenv GALAXYPAD_PHASE_TRACE >/dev/null 2>&1 || true
  fi
  if [[ -n "$llvm_profile_file" ]]; then
    xcrun simctl spawn "$simulator" launchctl unsetenv LLVM_PROFILE_FILE >/dev/null 2>&1 || true
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
# This loop is the verified 121-star file, not the old zero-star backup.
seed_file="$save_root/title/00010000/524d4745/data/GameData.bin"
[[ -f "$seed_file" ]] || die "missing advanced GameData seed: $seed_file"
seed_hash="$(shasum -a 256 "$seed_file" | awk '{print $1}')"
[[ "$seed_hash" == cd8d1fa98c266aa321dbb018247e5df7a084e5330ffa55f2012df4971b1bc473 ]] || \
  die "save seed does not match the verified 121-star file"
[[ "$stop_after_scene" == YES || "$stop_after_scene" == NO ]] || die "stop after scene must be YES or NO"
[[ "$profile_seconds" =~ ^[1-9][0-9]*$ ]] || die "profile seconds must be a positive integer"
# The instrumented builder uses continuous counters, but an explicit LLVM
# filename without %c disables runtime continuous mode and leaves a stale file.
if [[ -n "$llvm_profile_file" && "$llvm_profile_file" != *%c* ]]; then
  die "continuous LLVM profile filename must contain %c (for example observatory-%p%c.profraw)"
fi
[[ "$frame_logging" == YES || "$frame_logging" == NO ]] || die "frame logging must be YES or NO"
[[ "$terminate_after_profile" == YES || "$terminate_after_profile" == NO ]] || \
  die "terminate after profile must be YES or NO"
[[ "$system_trace_seconds" =~ ^[1-9][0-9]*$ ]] || \
  die "system trace seconds must be a positive integer"
if [[ -n "$local_game_ini" && ! -f "$local_game_ini" ]]; then
  die "missing local game INI: $local_game_ini"
fi
if [[ -n "$efb_trace" ]]; then
  mkdir -p "$(dirname -- "$efb_trace")"
fi
if [[ -n "$phase_trace" ]]; then
  mkdir -p "$(dirname -- "$phase_trace")"
fi
if [[ -n "$simulator_stderr" ]]; then
  mkdir -p "$(dirname -- "$simulator_stderr")"
fi
if [[ -n "$system_trace" ]]; then
  mkdir -p "$(dirname -- "$system_trace")"
fi

mkdir -p "$output"
mkdir -p "$(dirname -- "$input")"
ps -axo pid,pcpu,rss,stat,command | sort -k2 -nr | head -20 > "$output/host-top-before.log" || true
# Start from a neutral lease. The unattended lane owns this generated file;
# callers do not need to create it manually before the first launch.
if [[ ! -f "$input" ]]; then
  python3 "$root/scripts/simulator-input.py" "$input" '{}' --seconds 0.1
fi

booted="$(xcrun simctl list devices booted)"
# Multiple Simulators are allowed by the user. Retain their inventory so
# matched comparisons can account for concurrent host work.
unrelated="$(printf '%s\n' "$booted" | rg '\(Booted\)' | rg -v -F "$simulator" || true)"
if [[ -n "$unrelated" ]]; then
  printf '%s\n' "$unrelated" > "$output/other-booted-simulators.log"
  echo "Concurrent Simulators recorded; compare host conditions across candidates."
fi
if ! printf '%s\n' "$booted" | rg -F "$simulator" | rg -q '\(Booted\)'; then
  xcrun simctl boot "$simulator" 2>&1 | tee "$output/boot.log"
fi
xcrun simctl bootstatus "$simulator" -b 2>&1 | tee "$output/bootstatus.log"

xcrun simctl install "$simulator" "$app" 2>&1 | tee "$output/install.log"
data_container="$(xcrun simctl get_app_container "$simulator" org.galaxypad.GalaxyPad data)"
if [[ -n "${GALAXYPAD_SIMULATOR_PCM_FILENAME:-}" ]]; then
  [[ "$GALAXYPAD_SIMULATOR_PCM_FILENAME" =~ ^[A-Za-z0-9._-]+\.wav$ ]] || die "PCM capture requires a plain WAV filename"
  [[ "$frame_logging" == YES ]] || die "PCM capture is a diagnostic run, not FPS acceptance"
  pcm_path="$data_container/Library/Caches/$GALAXYPAD_SIMULATOR_PCM_FILENAME"
  [[ ! -e "$pcm_path" ]] || die "PCM capture already exists; use a new filename"
  mkdir -p "$data_container/Library/Caches"
  export SIMCTL_CHILD_GALAXYPAD_AUDIO_PCM_PATH="$pcm_path"
  printf '%s\n' "$pcm_path" > "$output/pcm-path.txt"
fi
support="$data_container/Library/Application Support/GalaxyPad"
# Stop only GalaxyPad before backing up and reseeding its private test save.
xcrun simctl terminate "$simulator" org.galaxypad.GalaxyPad >/dev/null 2>&1 || true
if [[ -d "$support/Wii" ]]; then
  mkdir -p "$output/Wii-before-seed"
  rsync -a "$support/Wii/" "$output/Wii-before-seed/"
fi
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

if [[ -n "$efb_trace" ]]; then
  xcrun simctl spawn "$simulator" launchctl setenv GALAXYPAD_EFB_TRACE "$efb_trace"
fi
if [[ -n "$phase_trace" ]]; then
  xcrun simctl spawn "$simulator" launchctl setenv GALAXYPAD_PHASE_TRACE "$phase_trace"
fi
if [[ -n "$llvm_profile_file" ]]; then
  xcrun simctl spawn "$simulator" launchctl setenv LLVM_PROFILE_FILE "$llvm_profile_file"
fi
xcrun simctl spawn "$simulator" log stream --style compact --level debug \
  --predicate 'process == "GalaxyPad"' > "$output/console.log" 2>&1 &
log_stream_pid=$!
sleep 3

launch_args=(xcrun simctl launch)
if [[ -n "$simulator_stderr" ]]; then
  launch_args+=("--stderr=$simulator_stderr")
fi
launch_args+=("$simulator")
launch_args+=(org.galaxypad.GalaxyPad)
launch_output="$("${launch_args[@]}" \
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
xcrun simctl io "$simulator" screenshot "$output/file-select.png"
python3 "$root/scripts/simulator-input.py" "$input" \
  '{"buttons":1,"pointerVisible":1,"pointerX":0.375,"pointerY":0.66}' \
  --aim-first 1 --seconds 0.8
sleep 3
xcrun simctl io "$simulator" screenshot "$output/slot1-details.png"
python3 "$root/scripts/simulator-input.py" "$input" \
  '{"buttons":1,"pointerVisible":1,"pointerX":0.73,"pointerY":0.88}' \
  --aim-first 1 --seconds 0.8
# The advanced file enters the Observatory directly; opening-story pulses
# belonged to the rejected zero-star route and must not move this checkpoint.
sleep 10

xcrun simctl io "$simulator" screenshot "$output/scene.png"
if [[ "$stop_after_scene" == YES ]]; then
  echo "Route ended without sampling; verify scene.png before an observation window: $output"
  exit 0
fi
# `sample` preserves native/SDL/generated stack names, but its aggregate report
# cannot tell running from runnable-but-unscheduled or blocked time. When the
# opt-in system-trace path is requested, use Xcode's unprivileged System Trace
# attach instead: it records chronological stacks and scheduler state around
# the stationary scene. Keep the ordinary sample path unchanged for callers.
if [[ -n "$system_trace" ]]; then
  xctrace record --template 'System Trace' --attach "$pid" \
    --time-limit "${system_trace_seconds}s" --output "$system_trace" \
    --no-prompt --quiet > "$output/system-trace.log" 2>&1
else
  # xctrace can leave a Simulator attach open indefinitely on this host even
  # after its advertised time limit. `sample` uses the same host PID, has a
  # bounded duration, and preserves the native/SDL/generated stack names
  # needed for hotspot attribution without holding the loop open.
  sample "$pid" "$profile_seconds" 1 -mayDie -fullPaths \
    -file "$output/cpu-sample.txt" > "$output/cpu-profile.log" 2>&1
fi
ps -axo pid,pcpu,rss,stat,command | sort -k2 -nr | head -20 > "$output/host-top-after.log" || true

if [[ "$terminate_after_profile" == YES ]]; then
  xcrun simctl terminate "$simulator" org.galaxypad.GalaxyPad \
    > "$output/terminate.log" 2>&1 || true
  # Give the core and diagnostics stream a bounded opportunity to flush
  # shutdown counters before the EXIT trap closes the stream.
  sleep 2
fi

rg 'simulator input accepted|\[GalaxyPad input device\]|\[GalaxyPad wiimote\]' \
  "$output/console.log" > "$output/input-route.log" || true
rg '\[GalaxyPad\]' "$output/console.log" > "$output/runtime.log" || true

echo "unattended Simulator scene/profile complete: $output"
