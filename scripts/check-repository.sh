#!/usr/bin/env bash
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$root"

with_private_evidence=false
case "${1:-}" in
  "") ;;
  --with-private-evidence) with_private_evidence=true; shift ;;
  *) echo "usage: $0 [--with-private-evidence]" >&2; exit 2 ;;
esac
[[ $# == 0 ]] || { echo "usage: $0 [--with-private-evidence]" >&2; exit 2; }
echo "Running source and prepared-dependency checks (no game data required)."
if [[ "$with_private_evidence" == false ]]; then
  echo "Private game-derived evidence checks are separate: use --with-private-evidence to include them."
fi

git diff --check
bash scripts/check-public-content.sh
bash tests/test-repository-safety.sh
python3 tests/test-public-content.py
python3 tests/test-preview-archive-audit.py
python3 tests/test-ios-icons.py
python3 tests/test-ipad-install-assistant.py
python3 tests/test-preview-module-interface.py
python3 tests/test-dependency-lock.py
python3 scripts/dependency-lock.py

for script in scripts/*.sh tests/*.sh; do
  [[ -e "$script" ]] || continue
  bash -n "$script"
done

python3 -c 'import json,pathlib; [json.loads(p.read_text()) for p in pathlib.Path("config").glob("*.json")]'
python3 -m py_compile scripts/wii-pipe.py
./tests/test-wii-pipe.sh
./tests/test-macos-app-config.sh
python3 ./tests/test-runtime-directories.py
bash ./tests/test-mobile-input.sh
bash ./tests/test-thp-patch.sh
bash ./tests/test-movement-trace.sh
bash ./tests/test-simulator-input.sh
python3 ./tests/test-pointer-reacquisition.py
python3 ./tests/test-pointer-camera.py
bash ./tests/test-pointer-context.sh
bash ./tests/test-direct-tap.sh
bash ./tests/test-static-pointer-hooks.sh
bash ./tests/test-pointer-hook-probe.sh
bash ./tests/test-native-observer.sh
bash ./tests/test-native-observer-binding.sh
python3 ./tests/test-observer-cpu-layout.py
bash ./tests/test-mobile-control-size.sh
python3 ./tests/test-mobile-ui-result.py
bash ./tests/test-mobile-settings.sh
bash ./tests/test-mobile-stick-routing.sh
bash ./tests/test-mobile-controller.sh
bash ./tests/test-controller-pause-events.sh
bash ./tests/test-import-activation.sh
bash ./tests/test-import-transaction.sh
python3 ./tests/test-runner-background-input.py
python3 ./tests/test-psq-scale.py
python3 ./tests/test-psq-scale-patch.py
python3 ./tests/test-audio-phase-events.py
python3 ./tests/test-audio-interruption-recovery.py
bash ./tests/test-wiimote-idle-policy.sh
python3 ./tests/test-efb-read-context.py
python3 ./tests/test-efb-dispatch-timing.py
python3 ./tests/test-efb-peek-flush.py
python3 ./tests/test-metal-staging-flush.py
python3 ./tests/test-metal-staging-timing.py
bash ./tests/test-sys-platform.sh
bash ./tests/test-frontend-wait.sh
bash ./tests/test-cntlzw.sh
python3 ./tests/test-midblock-cycles.py
python3 ./tests/test-attack-trace.py
python3 ./tests/test-cpu-profile-summary.py
python3 ./tests/test-code-footprint.py
python3 ./tests/test-cpu-counters.py
python3 ./tests/test-process-work-snapshot.py
python3 ./tests/test-process-work-summary.py
python3 ./tests/test-capture-process-work.py
python3 ./tests/test-ios-sdk-selection.py
python3 ./tests/test-cpu-instruction-classifier.py
python3 ./tests/test-load-origin.py
python3 ./tests/test-platform-codegen-comparison.py
python3 ./tests/test-fp-guard-chains.py
python3 ./tests/test-memory-mapping-callback.py
python3 ./tests/test-scene-trace.py
python3 ./tests/test-trace-window.py
python3 ./tests/test-clock-bridge.py
python3 ./tests/test-scheduler-capture-guards.py
python3 ./tests/test-vi-timing-buffer.py
python3 ./tests/test-thread-work-recorder.py
python3 ./tests/test-thread-work-summary.py
python3 ./tests/test-vi-timing-wiring.py
python3 ./tests/test-vi-timing-summary.py
python3 ./tests/test-fixture-charge-reset.py
python3 ./tests/test-dvd-wait-boundary.py
python3 ./tests/test-gather-wait-boundary.py
python3 ./tests/test-gather-wait-wiring.py
python3 ./tests/test-wakeup-notification.py
python3 ./tests/test-wakeup-wiring.py
python3 ./tests/test-wakeup-installed-concurrency.py
python3 ./tests/test-thread-state-probe.py
python3 ./tests/test-checkpoint-undo-release.py
python3 ./tests/test-direct-call-sites.py
python3 ./tests/test-direct-call-binding.py
python3 ./tests/test-direct-call-boundary.py
python3 ./tests/test-direct-call-transfer.py
python3 ./tests/test-direct-call-chunk.py
python3 ./tests/test-direct-call-differential.py
python3 ./tests/test-fprf-gaps.py
python3 ./tests/test-fallback-pc-wiring.py
python3 ./tests/test-fallback-start.py
python3 ./tests/test-vector-dispatch.py
python3 ./tests/test-fallback-sample.py
python3 ./tests/test-run-cost.py
python3 ./tests/test-run-cost-summary.py
python3 ./tests/test-deferred-timebase.py
python3 ./tests/test-native-thp-configuration.py
python3 ./tests/test-fallback-pc-summary.py
python3 ./tests/test-fallback-image-ranges.py
python3 ./tests/test-xf-partial-command.py
python3 ./tests/test-fifo-compaction.py
python3 ./tests/test-gather-write-widths.py
python3 ./tests/test-xf-origin.py
python3 ./tests/test-thread-state-alignment.py
python3 ./tests/test-host-pressure-probe.py
python3 ./tests/test-host-pressure-alignment.py
python3 ./tests/test-live-slowdown.py
python3 ./tests/test-xf-context.py
python3 ./tests/test-development-checkpoint.py
python3 ./tests/test-madd-tie-outline.py
python3 ./tests/test-add-nan-outline.py
python3 ./tests/test-thermal-state-probe.py
python3 ./tests/test-two-range-policy-wiring.py
python3 ./tests/test-dc-build-graph.py
python3 ./tests/test-dvd-wait-wiring.py
python3 ./tests/test-completion-observer.py
python3 ./tests/test-completion-wiring.py
python3 ./tests/test-completion-summary.py
python3 ./tests/test-module-source-identity.py
python3 ./tests/test-ios-lc-default.py
python3 ./tests/test-thp-policy-wiring.py
python3 ./tests/test-dcbz-policy-wiring.py
python3 ./tests/test-fprf-regions.py
python3 ./tests/test-ps-fprf-chain.py
python3 ./tests/test-ps-vector-addsub.py
python3 ./tests/test-fp-single-facts.py
python3 ./tests/test-fp-island-ranking.py
python3 ./tests/test-cross-island-vector.py
python3 ./tests/test-cross-eligibility-summary.py
python3 ./tests/test-gpr-spans.py
python3 ./tests/test-typed-ps-multiply.py
python3 ./tests/test-normalization-square.py
python3 ./tests/test-checked-ps-multiply.py
python3 ./tests/test-audio-output-counters.py
python3 ./tests/test-audio-window-summary.py
python3 ./tests/test-fprf-emitted.py
python3 ./tests/test-module-output-path.py
python3 ./tests/test-unsafe-direct-call-guard.py
python3 ./tests/test-macos-reference-jit.py
python3 ./tests/test-smc-outside-bounds.py
python3 ./tests/test-pixel-store-trace.py
python3 ./tests/test-lc-byte-fast.py
python3 ./tests/test-psq-store-order.py
python3 ./tests/test-lc-pair-pointer.py
python3 ./tests/test-lc-pair-store.py
python3 ./tests/test-lc-pair-host.py
python3 ./tests/test-lc-pair-host.py --empty-rel
python3 ./tests/test-empty-rel-resolution.py
bash ./tests/test-lc-default.sh
bash ./tests/test-native-diagnostics.sh

if [[ "$with_private_evidence" == true ]]; then
  bash scripts/check-private-evidence.sh
fi
