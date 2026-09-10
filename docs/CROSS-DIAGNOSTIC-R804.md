# R804: private Simulator diagnostic build in progress

R803 progressed by validating callback/alias behavior and exposing rejection
cost. Actual gameplay eligibility is the next missing fact; retained coverage
has instruction counts but no operand distribution.

Added scripts/build-cross-diagnostic.py. It verifies baseline Simulator module
SHA3acdcddcd47812c2e2a67b8cec0cf06c17009cf1ad7f2e9dc9abd83158a1bac0,
the selected chunk source hash,1329 existing object identities and timestamps,
and original Ninja compiler/linker settings. It first relinks unchanged objects
into a private control and requires exact binary equality. Only then may it
compile the one diagnostic chunk and link a private candidate. It never runs
Ninja or changes normal module selection. Existing experiment paths are not
overwritten.

Diagnostic counters distinguish accepted, mode-rejected, range-rejected and
rounding-tie cases. A summary prints every4096 attempted islands, preserving
FPSR around integer-formatted logging. Counters are private to this single-CPU
execution diagnostic and are not a thread-safe general runtime API. Their
instrumentation means this candidate must not supply an FPS A/B result.

Added scripts/summarize-cross-eligibility.py and a registered focused test.
It checks outcome totals, nondecreasing counters, two complete observations and
nonzero window deltas. Missing/reset/inconsistent windows reject. Tests pass.
No scene, CPU share, elapsed-time or FPS inference is made from the counters.

## Exact continuation

Build exec session5301 is still live. Last inspected linker PID44968, parent
clang44967, elapsed about2m29s and approximately704% CPU. Output currently says
`Link control.dylib`; no control hash result, candidate build or runtime evidence
yet. Poll the SAME5301 handle; do not restart or rerun the builder based on an
observation timeout. Log paths are generated/cross-build-r804.log/.err.

Private directory: generated/candidates/cross-diagnostic-r804, containing
provenance.json and control response file so far. If control hash validation
fails, inspect the discrepancy before proceeding; no candidate should be built.
If it succeeds, wait for the same script's compile/link/Simulator platform/signature
checks. Then inspect the final provenance and plan one bounded Simulator scene
with existing save protection before interpreting the counter log.

At turn inspection32Gi available; no Simulator booted. Normal module is unchanged,
app/save data untouched. Full PRD/SunPad/gameplay/audio/stability/device objective
remains active. No gameplay eligibility percentage or FPS gain is known yet.
