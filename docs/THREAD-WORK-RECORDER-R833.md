# R833: private VI/thread-work recorder integration tested

Previous turn was progress: native/Simulator standalone counter feasibility.
This turn prepares an isolated host-header overlay, not a game build or new
performance result. Canonical/vendor VI recorder and normal app remain unchanged.

## Implementation

`patches/experiments/thread-work-recorder.h` is compile-guarded by
GALAXYPAD_PRIVATE_THREAD_WORK. It resolves the normal thread_selfcounts wrapper
before writer start. Runtime opt-in is a separate GALAXYPAD_THREAD_WORK_TIMING
output path, only honored when the VI recorder is enabled. Disabled collection
does not resolve symbols/query counters/allocate its sample buffer. The private
header is not included at all in ordinary builds.

One CPU-thread writer records the exact VI sample timestamp, query begin/end
timestamps, error and raw per-core-class instructions/cycles/user/system Mach
ticks into a fixed16384-entry array. No writer file I/O or allocation. Filled
buffer drops subsequent samples without querying; drop count saturates. Metadata
preserves level count, timebase and configuration error. Failed queries discard
partial payloads and retain the error. Counter decreases remain raw evidence,
not silently clamped. Caller must exclude invalid/reset intervals during analysis.
The sidecar is created exclusively only after writer join, with reported result;
existing VI format and clock are unchanged. Level names must be captured in the
run manifest; numeric levels alone are not universal Performance/Efficiency labels.

`scripts/prepare-thread-work-recorder.py --output NEW_DIRECTORY` checks canonical/
vendor equality and unique source anchors, then creates new isolated headers.
It refuses existing output and does not edit vendor or bootstrap sources. Only
five private guarded insertions wire configure, per-VI sampling, post-join
export, include and member storage. Guest modules are not changed.

## Tests run

`python3 tests/test-thread-work-recorder.py` passes:

- ASan/UBSan fake-reader tests: disabled clock/query bypass, single joined writer,
  raw counter resets, failed partial output, bounded prefix/drop behavior,
  missing wrapper/bad topology, deferred/idempotent export and no overwrite.
- Overlay rejects existing destination and missing source anchor.
- Existing VI lifecycle/file-error tests pass with and without private define.
- Ordinary compiled fixture has no thread_selfcounts string and ignores the
  runtime opt-in. Private fixture contains the wrapper name.
- Native worker-thread integration exports two VI samples and matching sidecar
  timestamps, successful real queries and nonzero instruction counts. This is
  native test-process evidence, not Simulator/game integration acceptance.

`python3 tests/test-vi-timing-wiring.py` passes canonical/vendor provenance and
existing post-join/disabled wiring. New suite is registered in check-repository.sh;
the full repository suite was not run this turn. Test handles48203/35978 terminal0.

Recorder SHA693554937b2941ac03aad73872c92bf077d4b665a810063f6892e0fb6d9a4240.
Overlay script SHA65f809469edce18759455b18d5614e4e3473f0d9b58b5b9a20e5fd571b95fefa.

## Next

Prepare a private host-only build using this isolated overlay and explicit
private define, retaining the existing guest module and normal app. First inspect
build-cache/source identity and include precedence: quoted runtime includes must
actually select the overlay, not the original sibling header. Verify resulting
binary and run scope before launching the sole Simulator. Add sidecar interval
validation for query-boundary uncertainty, reset/error/drop coverage and Mach
conversion before making per-VI claims. Measure actual neutral-plaza CPU-thread
work/core-class time to answer R831's unresolved gap; do not repeat an unchanged
aggregate-only run or reopen QoS tuning from the standalone probe.

No game/Simulator started, no save/module/app edit, no performance improvement
claimed. Full original PRD/SunPad/audio/stability/device goal remains active.
