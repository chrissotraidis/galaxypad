# R906 — resident fused arithmetic and halfway correction

Previous turn: progress. R905 added actual paired multiplication but no app
performance gain. This turn extends that static emitter to paired fused
multiply-add/subtract and optional result negation. Nothing is promoted.

## Source and scope

`tests/aot-paired-multiply.h` now retains three source pairs, rounds the C
operand, emits fused arithmetic and the reference `ni_madd_msub` error correction
for binary32 halfway results, preserves original A/B/C NaN precedence, updates
guest exception state, clears FI/FR for infinite operands, and negates only
non-NaN rounded results. It does not substitute a single host FMA for all guest
semantics. The multiply-only path remains available.

The common emitter reserves Q24–Q31, stages sources before cache acquisition
can evict them, and retains its scratch/NZCV preservation. No runtime compiler,
helper call, or temporary CPUState is introduced. Guest availability/PC/cycle
handling still belongs to the original whole chunk and entry wrappers.

The private `--resident-fma` candidate replaces the actual four arithmetic ops
at804B6504–804B6510 (multiply, multiply, negative multiply-subtract, multiply).
The whole surrounding 41-op routine remains the comparison scope, including
each direct suffix entry and original memory/callback operations afterward.
This is not the longer final arithmetic span yet. The exporter can encode the
four non-record FMA variants; actual-DOL integration here exercises nmsub.
Recorded FMA and unrelated opcode forms remain rejected.

## Tests and evidence

- Initial fixed-pattern `generated/resident-fma-r906`, session12071 exited0:
  629760 full-routine CPUState/memory/callback/FPSR comparisons pass, including
  172800 callback cases.
- Arbitrary binary64 inputs and randomized FPSCR:
  `generated/resident-fma-random-r906`, session15770 exited0, same counts.
- Explicit halfway tests: `generated/resident-fma-ties-r906`, session75603
  exited0, same counts. At650C the fixtures include exact mathematical FMA
  results just above/below a binary32 halfway point by2^-75, a negative case,
  and an exact tie. Nearest-mode results have independent expected-value
  assertions in addition to full control/candidate state comparison. Both lanes
  are exercised, across the existing RN/NI/entry/memory matrix.
- Multiply/merge regression: `generated/resident-multiply-regression-r906`.
  Session67663 exited0 with the same629760 comparisons/172800 callback cases.
- Reports retain source, emitter, assembly/object/library hashes and commands.
  Existing helper PGO warnings and changed-chunk profile mismatch remain
  explicit; these are not exactly equivalent PGO training contexts.

No host-flag differences are masked. This is not exhaustive operand/opcode/
register-alias/ABI coverage, hardware proof, a sanitized assembly execution,
or a throughput measurement. No tiny-fragment benchmark was run.

## Next performance gate

Add lane-selected multiply/add and scalar/sum forms needed to cover the longer
804B64E0–804B6510 region, leaving the preceding reciprocal and following memory
observer boundaries explicit. Compare that substantial region in the complete
routine before deciding whether a same-scene iPad app candidate is worthwhile.
The full-routine cost must justify app work; component test counts do not.

Installed app and last measured iPad results are unchanged: heavy plaza37.15
VI/s, movie59.88 VI/s. No game/Simulator was launched. Disk19GiB available during
the final check. The full original PRD remains active and unfulfilled.
