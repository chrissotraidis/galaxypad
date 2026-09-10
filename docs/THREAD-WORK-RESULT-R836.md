# R836: complete Simulator CPU-thread work measurement

Previous turn progressed analysis/live collection but rejected incomplete window.
Retry reuses the exact private24002e50 host and3acdcddd guest module; no rebuild.
Prompt navigation removes earlier stale-menu delay. One iPad Simulator only.

## Executed run

Artifacts: generated/runtime/thread-work-r836/{runtime.log,vi.csv,work.csv,
process-work.json,GameData.before.bin,input-sequence.py,input.json}.
Boot87907 completes; console37616, PID68587. Installed private binary hash verified.
Same LC0/nativeTHPoff/CPUQoSexperimentoff/no fallback JIT as R831/R835. Exact
launch command is in process-work.json. No movement input. Bounded title82716,
selection44748, story43696, finish97302 all complete. CUA verifies landscape
starting plaza before/after capture: life3/lives4/coins0/StarBits0. Pointer lease
45175 surrounds warmup/capture; process capture7485 finishes. Screenshots are
retained in conversation tool output, not new image files. Starting camera settles
in10s warmup; this is stationary plaza, not first-play or touch acceptance.

## Complete measurement

Requested outer bounds577932903973416–577962916761625; process snapshot midpoint
duration30.012771271s. Both recorders dropped0, exact VI pairing and topology pass.
Retained tail margin48.856979s. CPU-clock invalid/reset intervals0. Numeric level
names captured from this host:0 Performance,1 Efficiency. Mach timebase125/3.

| Metric | Result |
| --- | ---: |
| VI events/rate |1482 /49.378979 per second|
| CPU-thread instructions per VI interval |140,436,806.290|
| CPU-thread cycles per VI interval |41,619,280.387|
| CPU-thread mean/p95/p99 ms |17.941337 /20.771000 /24.107958|
| Performance-core CPU-time share |98.333311%|
| Efficiency-core CPU-time share |1.666689%|
| Whole-process instructions/VI |226,120,090.366|
| Whole-process cycles/VI |64,352,783.513|
| Wall mean/p99 ms |20.253372 /27.277375|
| EFB elapsed mean ms |1.838622|
| Throttle elapsed mean ms |0.001000|

Thread summary uses1482sample snapshots spanning1481guaranteed VI intervals;
first/last query brackets577932906642166–577932906643083 and
577962901885750–577962901886625. Requested-boundary omissions2.668750ms and
14.875000ms are explicit. Thread counts total207986910115instructions,
61638154253cycles. Performance CPU26.128261833s, Efficiency0.442857833s. Converted
total26.571119667s agrees with existing CPU clock26.571119625s on same intervals.
This independently validates units; no raw Mach ticks treated as nanoseconds.

Reproduce with scripts/summarize-thread-work.py work.csv vi.csv and
scripts/summarize-vi-timing.py vi.csv using --start-ns577932903973416
--end-ns577962916761625 (separate option/value arguments). Process summary takes
process-work.json and vi.csv. No prefix override needed; no CSV edits.

## Interpretation and next gate

This rules out predominantly efficiency-core execution **in this run**, not in
unmeasured historical slowdowns. CPU thread includes host/runtime code as well as
generated guest code; it is not a guest-only instruction count. VI is not scanout.
1264/1481CPU intervals still exceed16.667ms. Stage elapsed counters overlap and
must not be summed as exclusive costs. Low Power Mode0 and pmset reports no
recorded warning before capture; neither measures actual frequency/thermal state.

R831 uninstrumented30.689VI/s versus this49.379 shows large run/context variability.
There was no optimization; do not attribute the increase to instrumentation or
claim a new accepted baseline. R830 native59.949/14.226ms lacks same-thread work
counts. We still cannot tell whether native executes materially less CPU-thread
work or executes similar work faster. Task totals cannot fill that gap.

Next reuse the private recorder in an isolated native host-only build, verify
unchanged-source/control identity and run a corresponding neutral-plaza thread
window. No guest-module rebuild or repeat Simulator capture is needed. Compare
thread instructions/cycles/core-class time before another lowering/QoS change.
If native build cache cannot reproduce, report the exact drift rather than
silently changing baseline. This is the remaining platform-attribution question,
not a reason to restart closed arithmetic/QoS/profile lanes.

## Cleanup

Menu Stop Game exports both recorders successfully and runtime failed=0. Original
85ffc100 app restored; Simulator shutdown87371 exit0. New restored bundle UUID
3CB4B98E-F893-4496-B033-0DBCAA257463, data461E9EEB-5871-45F4-A2F8-8095CBF87E2C.
GameData rehashed99d432d517b92b19da0c403819b91288b10c7063c3ce61f5000347ef823ab64f,
unchanged. No normal module/save change. Full original PRD/SunPad/gameplay/audio/
stability/device requirements remain active, with no speed/acceptance gate closed.
