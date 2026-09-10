# R828: compact normalization rejected; host-flag mismatch characterized

Previous turn: progress, compact state isolation passed but actual-policy
whole-chunk flags differed. This turn preserves the failed comparison and
determines whether more engineering on this design is justified.

## FP environment findings

Removing only the oracle's FENV_ACCESS ON pragma reproduces an isolated failure:
RN0/NI0/lazy0/MSR-FP0/entry0/internal/i16, equal full CPUState and FPSCR79991768,
but raw FPSR0x1c/0x18. Artifacts: generated/normalization-fenv-detail-r828.
This demonstrates sensitivity to compilation context, not a proven individual
instruction cause.

Adding FENV_ACCESS ON only around the compact helper closure (then OFF before
unchanged generated code) passes the former whole-chunk failure but encounters
another: pattern4/RN0/NI0/entry1, flags0/1, CPUState equal, FPSCRf0d118a8 equal.
Log normalization-fenv-whole-r828.log and retained build
generated/normalization-compact-whole-r827-bnfm2dju. This is NOT a fix.

Audit mode continues past host-flag mismatches only to enumerate failures and
check every guest-state/memory comparison; it still returns failure before any
timing. Result:8,704 complete CPUState and memory comparisons pass,96host-flag
mismatches. Log generated/normalization-full-audit-r828.log; retained build
generated/normalization-compact-whole-r827-0oyoj2yp. No guest FPSCR bit is masked.

Read-only source searches found no FPSR/fetestexcept/fegetenv status reader in
GXRuntime or StaticRecomp. The inspected ARM64 mode update changes FPCR rounding
and flush bits, not FPSR. Broader Common/PowerPC hits include emitter support and
x64 MXCSR code. This is not exhaustive proof against callbacks, host traps,
external modules or linked libraries. Do not waive the host-status contract from
search results alone; raw status mismatches remain recorded.

## Bounded cost decision, not a weakened promotion gate

Rather than repair flags indefinitely without knowing if the design is useful,
`tests/benchmark-normalization-qualified.py` measures ONLY the existing ordinary
finite workload that passes all136suffix/RN/NI guest-state, memory, cycle and
host-flag checks. It uses unchanged R827 whole-chunk libraries and all original
comparison assertions; the broader failing corpus remains a failed gate.
This explicitly supersedes the earlier no-timing prerequisite only for deciding
whether further correctness work is worth doing, never for promotion.

Eight alternating ABBAABBA samples, one million complete routine calls each,
with per-sample warm-up and thread CPU timing:

| Variant | ns/routine samples | Instructions/routine |
| --- | --- | --- |
| Reference |83.539,82.904,83.356,84.019|1063.5–1064.5|
| Compact |104.307,104.552,108.666,107.141|1141.0–1142.0|

The candidate is roughly27% slower and performs roughly7% more instructions on
this qualified workload. Artifacts: generated/normalization-qualified-r828,
including exact library hashes and test command. This single-workload screen is
not a gameplay comparison, universal cost estimate or mobile performance result.

**Disposition: park compact normalization.** No further scratch-size, attribute,
guard, FP-environment or flag-preservation tuning for this design; no module or
app build. Preserve the state oracle and failed-corpus evidence. A smaller stack
frame was not a speed improvement.

## Next direction

Reconcile platform cost before another arithmetic target: current instruction
attribution comes from the older R730 macOS host, while the failed Simulator
plaza measurements use R791. Source-match alone does not make their thread CPU
cost, waiting and scheduling comparable. Audit retained settings, counters and
capture windows first, then define a matched per-frame work/timing comparison
only if evidence is missing. Neither the macOS60FPS screenshot nor Simulator
26FPS window by itself proves a platform multiplier. Do not repeat unchanged
stack profiles or a UI-control verification loop.

Full original PRD/SunPad/performance/audio/stability/gameplay/device requirements
remain unchanged. No normal app/module/save change or game-speed gain. All
experiment handles terminal; no game or Simulator launched this turn.
