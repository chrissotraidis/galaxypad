#!/usr/bin/env bash
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$root"

git diff --check
python3 tests/test-ios-icons.py
python3 tests/test-ipad-install-assistant.py

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
python3 ./tests/test-thp-dead-pc.py
python3 ./tests/test-thp-dead-pc-entries.py
python3 ./tests/test-psq-scale.py
python3 ./tests/test-psq-scale-patch.py
python3 ./tests/test-audio-phase-events.py
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
python3 ./tests/test-vector-snapshot.py
python3 ./tests/test-vector-plan.py
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
python3 ./tests/test-xf-patch-order.py
python3 ./tests/test-thread-state-alignment.py
python3 ./tests/test-host-pressure-probe.py
python3 ./tests/test-host-pressure-alignment.py
python3 ./tests/test-live-slowdown.py
python3 ./tests/test-xf-context.py
python3 ./tests/test-development-checkpoint.py
python3 ./tests/test-madd-tie-outline.py
python3 ./tests/test-add-nan-outline.py
python3 ./tests/test-thermal-state-probe.py
python3 ./tests/test-thp-first-pass.py
python3 ./tests/test-s16-psq-load.py
python3 ./tests/test-s16-pair-psq-load.py
python3 ./tests/test-two-range-lookup.py
python3 ./tests/test-two-range-dispatch.py
python3 ./tests/test-two-range-policy.py
python3 ./tests/test-two-range-policy-wiring.py
python3 ./tests/test-two-range-module-audit.py
python3 ./tests/test-kernel-read-cache.py
python3 ./tests/test-dc-store-run.py
python3 ./tests/test-zero-column.py
python3 ./tests/test-zero-column.py --nonzero-dc
python3 ./tests/test-zero-column.py --nonzero-dc --second-kernel
python3 ./tests/test-dc-build-graph.py
python3 ./tests/test-huffman-tail.py
python3 ./tests/test-normal-kernel-entry.py
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

prohibited="$(git ls-files | rg '(^|/)(ref|generated|extracted|game-data|runtime-data|modules|saves|save|nand|docs/artifacts|artifacts)/|\.(iso|gcm|rvz|wia|wbfs|gcz|dol|rel|rso|dylib|ipa|xcarchive|mobileprovision|provisionprofile|p12|pem|key|gci|sav|raw|crash|ips|trace|log|profraw|profdata)$' || true)"
if [[ -n "$prohibited" ]]; then
  echo "prohibited tracked material:" >&2
  echo "$prohibited" >&2
  exit 1
fi

if git grep -n -I -E 'BEGIN [A-Z ]*PRIVATE KEY|github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}' -- .; then
  echo "possible credential material found" >&2
  exit 1
fi

if git grep -n -I -E '(^|[^[:alnum:]_])/Users/[^ ]+' -- . ':!scripts/check-repository.sh' ':!tests/test-mobile-diagnostics.mm'; then
  echo "personal absolute path found" >&2
  exit 1
fi

if git ls-files --error-unmatch ref >/dev/null 2>&1; then
  echo "ref must never be tracked" >&2
  exit 1
fi

echo "Repository safety checks passed"
