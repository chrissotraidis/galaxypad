# R901: whole-chunk guard relocation fails its cost gate

R900 implemented and correctness-tested a private candidate. This turn builds
independent complete control/candidate chunks and executes the cost gate. No
game, Simulator, product module, save or default setting changed.

## What ran

`python3 tests/probe-wide-fp-routine.py --whole-fp-guards --benchmark --output generated/fp-guards-whole-r901`

Session76821 exits0. Existing harness now supports isolated whole-chunk libraries.
Both compile the original1024-entry chunk structure under retained O2/strict-FP/
ThinLTO/PGO flags, with all actual cpu helper objects. Candidate relocates95guards
across the whole chunk; control keeps original source. Identical test-only changes
make the entry visible and add a configuration shim. Separate RTLD_LOCAL libraries
keep each variant's globals and helpers together. Driver synchronizes lazy-FP and
journal settings outside timing, then calls original entry addresses indirectly.
These are private test libraries, not final full-module linkage.

629760 complete CPUState/memory/callback/raw-FPSR comparisons pass, including
172800 callback cases, all41 entries of the selected wide routine, RN/NI,
lazy-FP/MSR states, quantization, overlaps and CPUState-as-RAM. This does NOT
exercise every one of the full chunk's1024 entries or every relocated guard;
the loaded compilation unit is whole, but execution coverage remains the selected
routine. Independent unavailable-PC/cycle checks remain. No sanitizer claim.

Eight alternating-order pairs execute1M complete wide-routine calls per half.
PC/downcount reset and indirect-call overhead are included; library configuration
and initial memory/CPU setup are outside timing. Final state/memory/FPSR agree
after each pair. Thread CPU time and process instruction counters are retained.

| Pair | Control ns/call | Candidate ns/call |
| --- | ---: | ---: |
|0|194.893|202.337|
|1|194.383|202.430|
|2|194.876|195.205|
|3|186.879|193.742|
|4|193.913|200.235|
|5|192.782|200.292|
|6|192.336|200.657|
|7|192.770|200.310|

Control3493.9–3497.3 instructions/call; candidate3600.7–3604.4, about3% more.
Candidate is slower in all eight pairs. Code __text shrinks288144→160860bytes;
smaller code alone is not a speed win. Counts are for this workload and include
driver/indirect-call overhead, not a per-game-frame estimate.

Warnings remain explicit: shared cpu helper build has one-of51 PGO mismatch and
unprofiled integer helpers, plus existing nested comment warning; candidate chunk
build warns one-of28 functions has mismatched PGO. Changing CFG changes profile
applicability, so this is not complete PGO equivalence or an isolated causal
measurement of guard cost. Neither candidate retraining nor a game-wide benefit
is established by this result.

Source/binary hashes, full commands, relocated addresses, actual libraries,
size reports and execution output are in generated/fp-guards-whole-r901 and
generated/fp-guards-whole-r901.log. Lightweight guard-chain and platform-comparison
regressions pass. Full repository suite not run.

## Decision

Do not promote or build a game module from this candidate. Close this particular
guard-relocation design for rollout: it changes dispatch/code generation and
loses its local cost gate. No follow-on per-helper guard tweaks or unchanged
timing repetition. Keep private oracle/candidate artifacts and failed performance
evidence; do not silently remove the original external-entry guarantees.

The broader availability/state-retention idea is not proven impossible, but
reopening it needs a materially different mechanism and evidence, not renaming
this transform. Next select a broader execution/data-lifetime change using the
retained R899 disassembly and known callback contracts; no further baseline
capture is needed. Full original PRD/SunPad/performance/audio/story/device/
packaging requirements remain active. No app-level performance gain claimed.
