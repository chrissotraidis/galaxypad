#!/usr/bin/env bash
# These regression fixtures are derived from locally supplied game data.
# Keep them out of the public source-only check suite; never download them.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$root"
echo "Running private game-derived evidence checks; all fixtures are required."

required=(
  generated/thp-kernels-r198-exits/candidate.c
  generated/extracted/run1/sys/main.dol
  generated/modules-thp-r205/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-daa33a86eff05b70/dolrecomp-output/RMGE01_generated/RMGE01.h
  generated/two-range-r358/candidate/RMGE01.h
  generated/modules/RMGE01/active-module.txt
)
missing=false
for fixture in "${required[@]}"; do
  if [[ ! -f "$fixture" ]]; then
    echo "Missing private evidence fixture: $fixture" >&2
    missing=true
  fi
done
if [[ "$missing" == true ]]; then
  echo "Prepare the recorded local experiment artifacts before running this suite. No checks were skipped or passed." >&2
  exit 1
fi

python3 ./tests/test-thp-dead-pc.py
python3 ./tests/test-thp-dead-pc-entries.py
python3 ./tests/test-vector-snapshot.py
python3 ./tests/test-vector-plan.py
python3 ./tests/test-thp-first-pass.py
python3 ./tests/test-s16-psq-load.py
python3 ./tests/test-s16-pair-psq-load.py
python3 ./tests/test-two-range-lookup.py
python3 ./tests/test-two-range-dispatch.py
python3 ./tests/test-two-range-policy.py
python3 ./tests/test-two-range-module-audit.py
python3 ./tests/test-kernel-read-cache.py
python3 ./tests/test-dc-store-run.py
python3 ./tests/test-zero-column.py
python3 ./tests/test-zero-column.py --nonzero-dc
python3 ./tests/test-zero-column.py --nonzero-dc --second-kernel
python3 ./tests/test-huffman-tail.py
python3 ./tests/test-normal-kernel-entry.py
