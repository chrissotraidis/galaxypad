#!/usr/bin/env bash
set -euo pipefail

# Run a bounded, read-only physical-device performance loop. This script never
# installs, launches, terminates, suspends, or mutates GalaxyPad or its saves.
# Keep the same visible gameplay scene for each pass; change one source/build
# candidate between loop invocations, then compare the retained evidence.

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
DEVICE_ID="95937B69-2038-56A0-8069-0EB0484BC2F9"
TRACE_DEVICE_ID="00008112-001D485114DBC01E"
PROCESS_ID=""
LOG_PATH=""
SCENE=""
PASSES=1
CAPTURE_SECONDS=30
PROFILE_SECONDS=10
OUTPUT_DIR=""
SKIP_PROFILE=0
ACTIVE_CONFIRMED=0
WAIT_FOR_ACTIVE=0
WAIT_SECONDS=600

usage() {
  cat <<'EOF'
Usage: scripts/galaxypad-performance-loop.sh --pid PID --scene NAME [options]

Required:
  --pid PID                 Current GalaxyPad PID on the iPad.
  --scene NAME              Human-readable fixed-scene label.

Options:
  --device ID               CoreDevice ID (default: current iPad).
  --trace-device ID         Instruments device UDID (default: current iPad).
  --log PATH                Runtime console log. Omit when frame logging is off.
  --passes N                Number of bounded passes (default: 1).
  --seconds N               Unsampled host capture seconds, 10..45 (default: 30).
  --profile-seconds N       CPU Profiler seconds, 3..30 (default: 10).
  --output DIR              Evidence directory under generated/.
  --skip-profile            Only run unsampled host/process captures.
  --active-scene-confirmed  Confirm the mirror shows active fixed gameplay.
  --wait-for-active         Wait for a supplied lifecycle log to show active state.
  --wait-seconds N           Maximum active-state wait, 10..3600 (default: 600).
  -h, --help                Show this help.
EOF
}

while (($#)); do
  case "$1" in
    --pid) PROCESS_ID=${2:-}; shift 2 ;;
    --scene) SCENE=${2:-}; shift 2 ;;
    --device) DEVICE_ID=${2:-}; shift 2 ;;
    --trace-device) TRACE_DEVICE_ID=${2:-}; shift 2 ;;
    --log) LOG_PATH=${2:-}; shift 2 ;;
    --passes) PASSES=${2:-}; shift 2 ;;
    --seconds) CAPTURE_SECONDS=${2:-}; shift 2 ;;
    --profile-seconds) PROFILE_SECONDS=${2:-}; shift 2 ;;
    --output) OUTPUT_DIR=${2:-}; shift 2 ;;
    --skip-profile) SKIP_PROFILE=1; shift ;;
    --active-scene-confirmed) ACTIVE_CONFIRMED=1; shift ;;
    --wait-for-active) WAIT_FOR_ACTIVE=1; shift ;;
    --wait-seconds) WAIT_SECONDS=${2:-}; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ "$PROCESS_ID" =~ ^[1-9][0-9]*$ ]] || { echo "--pid must be a positive integer" >&2; exit 2; }
[[ -n "$SCENE" ]] || { echo "--scene is required" >&2; exit 2; }
[[ "$ACTIVE_CONFIRMED" -eq 1 ]] || {
  echo "Refusing to profile without --active-scene-confirmed" >&2
  exit 2
}
if ((WAIT_FOR_ACTIVE == 1)); then
  [[ -n "$LOG_PATH" ]] || {
    echo "--wait-for-active requires --log" >&2
    exit 2
  }
fi
[[ "$PASSES" =~ ^[1-9][0-9]*$ ]] || { echo "--passes must be a positive integer" >&2; exit 2; }
[[ "$CAPTURE_SECONDS" =~ ^[0-9]+$ && "$CAPTURE_SECONDS" -ge 10 && "$CAPTURE_SECONDS" -le 45 ]] || {
  echo "--seconds must be 10..45" >&2
  exit 2
}
[[ "$PROFILE_SECONDS" =~ ^[0-9]+$ && "$PROFILE_SECONDS" -ge 3 && "$PROFILE_SECONDS" -le 30 ]] || {
  echo "--profile-seconds must be 3..30" >&2
  exit 2
}
[[ "$WAIT_SECONDS" =~ ^[0-9]+$ && "$WAIT_SECONDS" -ge 10 && "$WAIT_SECONDS" -le 3600 ]] || {
  echo "--wait-seconds must be 10..3600" >&2
  exit 2
}

if [[ -z "$OUTPUT_DIR" ]]; then
  OUTPUT_DIR="$ROOT_DIR/generated/runtime/galaxypad-performance-loop/$(date +%Y%m%d-%H%M%S)"
elif [[ "$OUTPUT_DIR" != /* ]]; then
  OUTPUT_DIR="$ROOT_DIR/$OUTPUT_DIR"
fi
case "$OUTPUT_DIR" in
  "$ROOT_DIR/generated"/*) ;;
  *) echo "--output must remain under generated/" >&2; exit 2 ;;
esac
[[ ! -e "$OUTPUT_DIR" ]] || { echo "Refusing to overwrite $OUTPUT_DIR" >&2; exit 2; }
mkdir -p "$OUTPUT_DIR"

if [[ -n "$LOG_PATH" && ! -f "$LOG_PATH" ]]; then
  echo "Runtime log does not exist: $LOG_PATH" >&2
  exit 2
fi

command -v xcrun >/dev/null || { echo "xcrun is required" >&2; exit 2; }
cat > "$OUTPUT_DIR/README.txt" <<EOF
GalaxyPad physical performance loop
scene=$SCENE
device=$DEVICE_ID
trace_device=$TRACE_DEVICE_ID
pid=$PROCESS_ID
passes=$PASSES
capture_seconds=$CAPTURE_SECONDS
profile_seconds=$PROFILE_SECONDS
runtime_log=$([[ -n "$LOG_PATH" ]] && echo supplied || echo omitted)
frame_logging=not-inferred-from-log-option
active_scene_confirmed=$ACTIVE_CONFIRMED
wait_for_active=$WAIT_FOR_ACTIVE
wait_seconds=$WAIT_SECONDS

Keep this scene fixed. Host captures are unsampled. CPU Profiler traces are
diagnostic and may perturb timing; they are never used as FPS acceptance.
No app, save, or device-data mutation is performed by this loop.
EOF

is_live_galaxypad() {
  local process_json=$1
  rg -q "GalaxyPad" "$process_json" && rg -q "\"$PROCESS_ID\"|$PROCESS_ID" "$process_json"
}

if ((WAIT_FOR_ACTIVE == 1)); then
  wait_started=$(date +%s)
  while :; do
    latest_lifecycle=$(rg 'host lifecycle (runtime_paused|menu_presented)=' "$LOG_PATH" | tail -n 2 || true)
    if [[ "$latest_lifecycle" == *"runtime_paused=0"* && "$latest_lifecycle" == *"menu_presented=0"* && "$latest_lifecycle" != *"runtime_paused=1"* && "$latest_lifecycle" != *"menu_presented=1"* ]]; then
      echo "active lifecycle observed; entering performance passes"
      break
    fi
    elapsed=$(( $(date +%s) - wait_started ))
    if ((elapsed >= WAIT_SECONDS)); then
      echo "Timed out waiting for runtime_paused=0 menu_presented=0" >&2
      exit 1
    fi
    echo "waiting for active scene: ${elapsed}s/${WAIT_SECONDS}s"
    sleep 5
  done
fi

for pass in $(seq 1 "$PASSES"); do
  pass_dir="$OUTPUT_DIR/pass-$pass"
  mkdir -p "$pass_dir"

  set +e
  xcrun devicectl device info processes --device "$DEVICE_ID" \
    --json-output "$pass_dir/device-processes-before.json" \
    >"$pass_dir/device-processes-before.log" 2>&1
  device_status=$?
  set -e
  [[ "$device_status" -eq 0 ]] || {
    echo "Device process snapshot failed on pass $pass" >&2
    exit "$device_status"
  }
  is_live_galaxypad "$pass_dir/device-processes-before.json" || {
    echo "Requested GalaxyPad PID is not present before pass $pass" >&2
    exit 1
  }

  if [[ -n "$LOG_PATH" ]]; then
    latest_lifecycle=$(rg 'host lifecycle (runtime_paused|menu_presented)=' "$LOG_PATH" | tail -n 2 || true)
    if [[ "$latest_lifecycle" == *"runtime_paused=1"* || "$latest_lifecycle" == *"menu_presented=1"* || "$latest_lifecycle" == *"menu=1"* ]]; then
      echo "Refusing pass $pass: lifecycle log still reports the native menu paused" >&2
      exit 1
    fi
  fi

  if [[ -n "$LOG_PATH" ]]; then
    cat >"$pass_dir/runtime-log-window.txt" <<EOF
A runtime log was supplied for lifecycle gating. This is an unsampled wait
window; device process presence is checked before and after it. The log option
does not imply that frame logging is enabled. Remote PIDs are not sampled with
host ps, and log-derived frame windows are diagnostic counters only.
EOF
    sleep "$CAPTURE_SECONDS"
    cp "$LOG_PATH" "$pass_dir/runtime.log"
    rg '\[GalaxyPad frame window\]' "$pass_dir/runtime.log" \
      >"$pass_dir/frame-windows.log" || true
  else
    cat >"$pass_dir/logging-off-window.txt" <<EOF
Frame logging is off. This is an unsampled wait window; device process presence
is checked before and after it. No host ps value is substituted for device CPU.
EOF
    sleep "$CAPTURE_SECONDS"
  fi

  if ((SKIP_PROFILE == 0)); then
    set +e
    xcrun xctrace record \
      --template 'CPU Profiler' \
      --device "$TRACE_DEVICE_ID" \
      --attach "$PROCESS_ID" \
      --time-limit "${PROFILE_SECONDS}s" \
      --output "$pass_dir/cpu.trace" \
      --no-prompt \
      >"$pass_dir/cpu-profile.log" 2>&1
    profile_status=$?
    set -e
    printf '%s\n' "$profile_status" >"$pass_dir/cpu-profile.exit"
    if [[ -s "$pass_dir/cpu.trace" ]]; then
      set +e
      xcrun xctrace export --input "$pass_dir/cpu.trace" --toc \
        --output "$pass_dir/toc.xml" >"$pass_dir/toc-export.log" 2>&1
      toc_status=$?
      set -e
      printf '%s\n' "$toc_status" >"$pass_dir/toc-export.exit"
    fi
  fi

  set +e
  xcrun devicectl device info processes --device "$DEVICE_ID" \
    --json-output "$pass_dir/device-processes-after.json" \
    >"$pass_dir/device-processes-after.log" 2>&1
  device_status=$?
  set -e
  [[ "$device_status" -eq 0 ]] || {
    echo "Device process snapshot failed after pass $pass" >&2
    exit "$device_status"
  }
  is_live_galaxypad "$pass_dir/device-processes-after.json" || {
    echo "Requested GalaxyPad PID disappeared after pass $pass" >&2
    exit 1
  }

  printf 'completed pass %s/%s: %s\n' "$pass" "$PASSES" "$pass_dir"
done

echo "Loop complete: $OUTPUT_DIR"
