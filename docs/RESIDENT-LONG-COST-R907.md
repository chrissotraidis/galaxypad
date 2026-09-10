# R907 — long resident arithmetic tested, cost gate failed

Previous turn classification: progress. R906 added fused arithmetic semantics.
This turn reaches the promised longer-region cost gate instead of continuing
isolated opcode tests indefinitely. **No app promotion; this scalar lowering
variant is slower.**

## Implementation and correctness

Added lane-selected multiply/add, sum0/sum1 and scalar fmuls behavior to the
private static emitter. Sum1 retains original A0 across the passthrough low-lane
write. Scalar fmuls preserves both old destination lanes when invalid-operation
gating suppresses its write; successful writes duplicate the rounded result and
clear FI/FR. Existing paired rounding, fused halfway correction, guest status,
and observer boundaries remain.

`--resident-lanes` covers actual64E0–64F0 (five ops); fixed and randomized
whole-routine comparisons both pass629760 cases/172800 callback cases
(sessions81680/87281, generated/resident-lanes[-random]-r907).

`--resident-long` replaces the full13-op arithmetic span64E0–6510. The reciprocal
before it and store afterward remain original code. Every selected-routine
entry keeps original availability/cycle handling; dirty resident values flush
before original stores and their callbacks. No memory lookup policy changes.

- Fixed long-region test60687 exited0,629760 comparisons/172800 callback cases.
- Randomized long-region test67952 initially failed with equal guest state but
  FPSR0x17/0x1f. Exact control disassembly shows the sum passthrough lane branches
  around conversion when NI flushes it, unlike the arithmetic-result lane.
  Corrected that distinction, without masking status. Failure/disassembly:
  `generated/resident-long-random-r907/control-helpers.asm` and result.log.
- Corrected randomized operands/FPSCR plus explicit FMA halfway tests72056
  exited0:629760 comparisons/172800 callback cases, at
  `generated/resident-long-random-r907b`.

## Cost gate and one concrete boundary correction

The first whole-routine8-pair run2775 exited0, preserving correctness before
and after timing. Control192.501–194.502 ns/call; candidate208.719–215.466.
Instructions approximately3495.4–3496.1 versus3561.5–3565.1. All8 pairs slower.
Artifact: `generated/resident-long-cost-r907`.

Inspection found unnecessary per-operation X0–X7/NZCV preservation inside this
FP-only region. No guest integer cache owns those caller-saved registers here.
The final emitter therefore explicitly owns them as scratch, with a single
160-byte outer frame: original X29/X30 and full Q8–Q15 preservation plus16 scratch
bytes at SP+144. No broader ABI preservation is claimed, and a future integer
cache must not overlap this scratch set. This supersedes R905/R906's per-op
scratch preservation description.

Boundary-corrected random/halfway test63975 exited0 with the same629760/172800
counts (`generated/resident-long-scratch-r907`). Final fixed/cost run55294 also
exited0, at `generated/resident-long-boundary-cost-r907`:

| Pair | Control ns/call | Candidate ns/call |
|---|---:|---:|
|0|193.339|207.261|
|1|194.924|206.566|
|2|195.136|211.963|
|3|193.782|211.970|
|4|187.050|203.080|
|5|192.310|205.033|
|6|192.587|209.493|
|7|193.013|209.351|

Candidate now executes3431.3–3435.7 instructions/call versus control3493.7–3497.3,
but remains slower in every pair. Fewer instructions do not prove lower latency.
Timing uses complete routine calls through independently loaded whole chunks,
ordinary finite RAM, alternating order, original module flags and retained
full-state/memory/FPSR checks. Configuration is outside timing. Compiler PGO
warnings remain explicit; no exact training-context equivalence is asserted.

## Decision

Reject this scalar resident arithmetic variant for app/module integration.
Do not extend it with more scalar opcode coverage, tune its stack frame again,
or repeat unchanged simulator/profile captures. The next materially different
candidate should reduce arithmetic execution cost itself, using the pinned
reference paired-vector lowering as the starting point. Audit prior vector and
precision experiments before choosing that implementation; preserve its exact
guest semantics and screen cost before building a broader backend.

The verified entry/observer oracle and failed candidate remain private evidence,
not a faster app. Latest actual iPad heavy-plaza37.15 VI/s/movie59.88 VI/s remain
unchanged. No runtime, Simulator, install, source publication, disc/save, or
normal module selection changed. Full original PRD remains active.
