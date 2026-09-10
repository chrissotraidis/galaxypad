# R817: quiet-loop cost screen does not justify an app rebuild

Previous turn was progress: full private Run objects compiled and the exact
candidate source was tied to the differential. This turn executes a bounded
cost screen and parks the specialization for promotion.

## What ran

tests/benchmark-quiet-burst.py extracts the checked fixture using the exact R816
candidate-source identity gate. It builds three separate translation units:
loop wrappers, callback/configuration implementation, and driver. No LTO permits
cross-unit constant propagation; disassembly retains indirect callback calls.
The entry selection is inside the timed candidate wrapper. Configuration and
callback work are opaque to the loop compiler.

O3, NDEBUG, C++23, ARM64 armv8-a+crc, no-strict-aliasing, no-exceptions and host
visibility/frame-pointer policy match the checked host entry. The target is
intentionally macOS rather than Simulator so the executable runs without a
Simulator. This remains a synthetic extracted-burst/stub-layout screen, not the
actual Dolphin object, generated Galaxy instructions or actual gameplay.

27 combinations: burst lengths 1/16/128, callback recurrence workloads 0/16/128,
and downcount/hook/synchronous-exception exits. Every combination uses ABBAABBA
order, 100,000 target dispatches per sample (integer-rounded burst count), thread
CPU time, runtime-enforced dispatch-count and checksum equivalence. Timings include
the common per-burst reset/driver overhead. Tiny samples and host scheduling are
limitations; do not derive stable nanosecond instruction latencies from them.

generated/quiet-burst-r817 retains source, objects, binary, disassembly,
timings.csv and report.json with all samples/commands and candidate-source hash.
An additional unchanged-binary invocation completed with the same output checks;
its summary is retained in this turn's tool output, not the initial CSV.

## Result and decision

For callback workload 16, initial median savings across configurations ranged
from -1.25% to +2.90%; repeat ranged -1.35% to +1.75%. For workload 128, initial
range was -1.11% to +0.41%; repeat was -2.64% to +0.75%. There is no material,
repeatable benefit with nontrivial callback work in this screen.

Nearly empty multi-dispatch bursts improved roughly 15–25% initially and 14–23%
in the repeat. That does not establish Galaxy applicability or game-speed benefit.
Single-dispatch empty cases varied sharply between invocations. No averaging of
these arbitrarily chosen workloads into a claimed game-wide percentage is valid.

Park quiet-loop specialization for promotion; no private app rebuild or additional
tiny optional-flag variants are justified. This is an investment decision based
on insufficient benefit, not proof of zero possible gain in actual Dolphin.
Keep R816 objects as experimental evidence; normal host/module remain unchanged.
The exact-source 5,376-case sanitized/optimized differential was rerun and passes.
No Simulator or game was launched; no saves or disc data changed.

## Next direction

Return to the native module work that dominates the measured CPU thread, using
the retained R813 profile to aggregate source-correlated generated-code costs
across chunks rather than optimizing one small routine from entry counts.
Before another candidate, identify a repeated emitted-code mechanism with broad
sampled coverage and distinguish helper/state traffic from generated call/branch
work. Read existing lane dispositions first: dead FPRF, cross-chunk direct calls,
lookup caches, inline helpers, cross-product and bounded offline exporter all
have prior evidence and must not be rediscovered as new fixes. No FPS improvement
or PRD acceptance is claimed. All original product requirements remain active.
