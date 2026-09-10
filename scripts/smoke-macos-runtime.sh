#!/usr/bin/env bash
# Bounded macOS smoke test for the exact RMGE01 DOL/module pair.
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mode="${1:-headless}"
duration="${2:-75}"

case "$mode" in
  headless|metal) ;;
  *) echo "usage: $0 [headless|metal] [duration-seconds]" >&2; exit 2 ;;
esac
[[ "$duration" =~ ^[1-9][0-9]*$ ]] || {
  echo "duration must be a positive integer" >&2
  exit 2
}

game="$root/generated/extracted/run1"
module_marker="$root/generated/modules/RMGE01/active-module.txt"
[[ -f "$module_marker" ]] || { echo "missing active module marker: $module_marker" >&2; exit 1; }
module="$(<"$module_marker")"
[[ "$module" == /* ]] || { echo "active module path is not absolute" >&2; exit 1; }
runner="$root/generated/build/moderngekko-desktop/moderngekko-run"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
user_dir="$root/generated/runtime/smoke-$mode-$stamp"
log="$root/generated/runtime/smoke-$mode-$stamp.log"

for required in "$game/sys/main.dol" "$module" "$runner"; do
  [[ -e "$required" ]] || { echo "missing prerequisite: $required" >&2; exit 1; }
done
mkdir -p "$user_dir"

args=(
  "$runner"
  --game "$game"
  --module "$module"
  --user-dir "$user_dir"
  --allow-interpreter
  --no-mods
)
if [[ "$mode" == headless ]]; then
  args+=(--headless)
else
  args+=(--graphics Metal)
fi

pid=""
cleanup() {
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    kill -INT "$pid" 2>/dev/null || true
    for _ in 1 2 3 4 5; do
      kill -0 "$pid" 2>/dev/null || return
      sleep 1
    done
    kill -TERM "$pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

"${args[@]}" >"$log" 2>&1 &
pid=$!
deadline=$((SECONDS + duration))
while kill -0 "$pid" 2>/dev/null && (( SECONDS < deadline )); do
  sleep 1
done
if kill -0 "$pid" 2>/dev/null; then
  kill -INT "$pid"
fi
set +e
wait "$pid"
status=$?
set -e
pid=""

cat "$log"
[[ "$status" -eq 0 ]] || { echo "runtime exited with status $status" >&2; exit 1; }
grep -Fq '[staticrecomp] module loaded:' "$log"
grep -Eq 'shutdown: native=[1-9][0-9]* fallback=0 .*smc_failed=0' "$log"
echo "PASS: $mode runtime smoke; evidence: $log"
