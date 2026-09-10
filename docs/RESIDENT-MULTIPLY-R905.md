# R905 — first exact resident arithmetic operation

Previous turn classification: progress. R904 integrated actual guest entry and
cycle boundaries, but its four merge operations were not a performance solution.
This turn adds paired multiplication to the same offline register-cache path.
No app or module selection changed; no measured FPS improvement is claimed.

## Implementation

`tests/aot-paired-multiply.h` emits ARM64 for `ps_mul` directly, without a C
helper call or temporary CPUState. It captures both old operands before cache
allocation, implements the original 25-bit C-operand rounding (including
subnormals), both multiplies, NaN precedence/quieting, guest exceptions and
VX/FEX recomputation, NI result selection, binary32 rounding/widening, and
low-lane FPRF classification. Scratch Q28–Q31 are reserved; X0–X7 and NZCV
are preserved by the operation. This is not exhaustive ABI or opcode coverage.

The private staging option now selects the actual five-op region
804B6518–804B6528: one multiply followed by four merges. Original whole-chunk
dispatch, entry charges/availability and subsequent stores/callbacks remain.
Recorded multiplication forms and other arithmetic are rejected by the exporter.
The existing recorded merge support remains. Source helper hash is pinned.

## A falsified assumption and its fix

Initial fixed-pattern run passed629760 cases. Randomized operands then exposed:
entry18, mode0, RN1, NI1, type3, FP enabled, overlap0; full guest state identical,
but raw ARM FPSR was0x1e in control versus0x16 in candidate (underflow bit).
Failure retained in `generated/resident-multiply-random-r905`.

Disassembly of the exact control helper shows unconditional `fcvt s1,d3`
before `fcsel` chooses the NI flushed-zero result (44c60–44c74; upper lane
44cd0–44ce4). Its conversion raises status even when its value is discarded.
The first emitter incorrectly skipped that conversion on the flushed path.
The emitter now preserves this behavior and the helper's result `fcmp`.
This is an actual compiled-helper compatibility choice, not proof that every
toolchain emits this sequence. Disassembly retained at
`generated/resident-multiply-random-r905/control-multiply.asm`.

## Final tests

- `generated/resident-multiply-final-r905`: session16928 exited0;
  629760 fixed-pattern complete-routine state/memory/callback/FPSR comparisons,
  including172800 callback cases.
- `generated/resident-multiply-status-r905`: session8240 exited0;
  another629760 comparisons with deterministic arbitrary binary64 operands and
  randomized guest FPSCR bits, retaining all RN/NI and entry/observer axes;
  172800 callback cases.
- Earlier corrected random-operand run40414 also exited0, before the randomized
  FPSCR expansion. Initial build32666 failed on enum spelling;56807 passed.
- Reports retain commands and hashes. Compiler still warns about helper profile
  mismatch/unprofiled inputs; no exact-PGO equivalence or cost assertion.
- No Simulator was booted at verification;19GiB disk available during work.

These cover the actual routine's multiply destination/source alias, not every
possible multiplication register combination, longer arithmetic residency,
physical device execution, audible playback, or performance. Host floating
exception traps are not enabled by this test. Assembly is not sanitizer-
instrumented. No benchmarking was performed on the five-op fragment.

## Next

Extend resident arithmetic to fused multiply-add/subtract and scalar/sum forms
needed by the long 804B64D8–804B6510 span. Preserve reciprocal, double-rounding
correction, exceptions and callback boundaries; do not merely substitute host
FMA. Once that substantially larger region is implemented, use full-routine
cost to decide whether an app candidate is justified. Avoid unrelated control
tests and already-rejected compact-state/value-call/guard tuning.

The last actual iPad heavy-plaza measurement remains37.15 VI/s; movie59.88 VI/s.
The entire original PRD, including gameplay, audio, product UI, device, and
private packaging requirements, remains active and incomplete.
