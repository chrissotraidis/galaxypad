# R824: load origins and callback contract

The R822 actual macOS plaza capture remains the input; no repeated boot or
profile was needed. R823's load-heavy distribution is not a cache-miss or
removable-cost measurement. Most load origins remain unresolved.

Fixed a diagnostic attribution error: the local global-load recognizer now
requires the numeric ADRP page plus load offset to equal the exact symbol
address from the verified module. A nearby symbol annotation is insufficient.
Regression tests cover absent symbols, misleading labels and wrong offsets.
The mapper now checks conservation independently for origins, bases and opcodes.

Artifacts: `generated/plaza-load-origins-r824/{context.asm,report.json}`.
Re-run with all three conservation assertions passes in
`generated/plaza-load-origins-r824-verified`, reproducing the same weights.
Exact globals are lazy-FP flag `0x6c24000` and write journal `0x6c24008`.

| Local load origin | Sampled cycle-weight units |
| --- | ---: |
| Unresolved | 6,490,744,191 |
| Adjacent exact lazy-FP global | 523,564,892 |
| Stack | 433,612,551 |
| Adjacent exact write-journal global | 304,572,509 |
| Compact PC-relative branch table | 274,183,132 |
| Total | 8,026,677,275 |

These numbers describe sampled instruction sites, not dynamic instruction
counts, load latency, cache misses or a predicted FPS improvement. The macOS
host/platform differences recorded in R821/R822 still apply to Simulator use.

## Actual ABI and observation boundaries

`tests/probe-cpu-field-offsets.c` confirms CPUState size 3528, downcount at
0xd98, RAM pointer/size at 0xd80/0xd88 and EXRAM pointer/size at 0xda0/0xda8.
Matching these offsets to x0/x19 operands alone does not establish register
provenance throughout an entire function.

`tests/test-memory-mapping-callback.py` passes with ASan/UBSan: external reads
can change RAM/MSR, and a journal callback can remap RAM after a store acquired
its pointer. That store must retain its original pointer; the next access must
see the new mapping. Reservation clearing remains checked. This confirms the
existing R793 contract; it is not a newly discovered product defect.

The entry dispatch and first case in exact `_func_804AB0A0` visibly contain
downcount, mapping metadata and actual guest-data loads. This provides a bounded
source/assembly example, not a whole-function register-origin proof. Existing
R311 and R452/453 mapping-cache failures remain binding. The compiler already
targets apple-m1: there is no newly discovered generic-A7 tuning defect.

## Next bounded implementation gate

Investigate whether a whole generated chunk can retain architectural CPU state
across a callback-free region, with explicit flush/reload at actual observers.
First inspect the existing optimized chunk: if LLVM already retains the fields
or the proposed change merely repeats the rejected mapping cache, stop that
design before rebuilding. Do not implement a general register-provenance engine
or repeat unchanged profiles as a prerequisite.

Any candidate must compare full CPUState, memory, callback observations, exception
exits and charged cycles at every supported entry. Measure whole-chunk cost with
the real strict-FP/ThinLTO policy; a local win does not justify promotion without
a matched gameplay A/B. The original PRD, SunPad, audio, stability, gameplay,
physical-device and packaging requirements remain active.

Focused load-origin, instruction-classifier and callback-mapping tests pass.
No app/module/save change, game-speed improvement or acceptance claim. No game,
profiler, build or booted Simulator remains at this checkpoint.
