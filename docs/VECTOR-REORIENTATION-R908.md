# R908 — do not restart closed vector experiments

Previous turn: progress. R907 completed a substantial-region cost screen and
rejected the scalar resident implementation. This audit refines the next action
against actual source and prior experiments; it is not new performance evidence.

## Existing work constrains the next candidate

- R428–R432 paired add/sub helper vectorization already reached a matched game
  test: control55.0667 VI/s/16.6513 ms CPU versus candidate55.1/16.6606. No
  meaningful benefit. Do not expand or rebuild that helper candidate unchanged.
- R802–R813 whole cross-product vectorization passed isolated cost (~19.5%) and
  high scene eligibility (~99.2%), but scene order25.93A/26.63B/26.01B/27.06A did
  not show repeatable material gain. Keep that region parked too.
- R787 checked isolated multiplication, R769 blanket helper inlining, and R828
  compact scalar normalization are different failed designs, not unused ideas.
- Existing dead-FPRF work R164–R176 must not be rediscovered as a new general
  optimization. Instruction counts and source length are not scene CPU share.

The pinned reference `JitArm64_Paired.cpp` has actual paired arithmetic, precision
tracking, conditional C-operand rounding, fused-error handling, and fallback
when FP exceptions require it. Its single-precision path depends on register
facts, not instruction names. `test-fp-single-facts.py` explicitly demonstrates
that a gated scalar operation can preserve a non-single old destination.

## Next bounded implementation: whole normalization vector candidate

Use the existing C backend and whole-chunk oracle, not further scalar-emitter
opcode expansion. The new candidate is the complete nine-op normalization
arithmetic region804B6BE0–804B6C00, with the original memory operations before
and after it. This is not the earlier scratch-CPUState/mandatory-inline design.

R799's source-matched retained R792 coverage recorded22,608,668 attempts per
normalization site versus1,240,764 per longer-wide site. These are older entry
attempts, not current scene time or completed operations. They justify testing
the more frequently reached routine, not predicting a game FPS gain.

Actual source reads before writes:

- fpr0: scalar multiplier; fpr1: scalar fused-subtract addend.
- fpr2/ps1[2]: final paired scaling input.
- fpr3/ps1[3]: initial paired square/add and later scaling input.
- fpr5/ps1[5]: initial squared-component addends and sum input.

Eight incoming binary64 lanes therefore need a real value contract. Do not
assume preceding loads established their type: a callback before entry or a
direct suffix entry can change that. Final written pairs are0,2,3,4,5,6;
all other guest fields must remain unchanged except original PC/cycles/FPSCR.

Candidate implementation contract:

1. Enter only at6BE0 after its original availability check. Keep all interior
   suffix entries and their original instructions unchanged. Keep original
   precharge; resume6C04 only after successful commitment.
2. Capture inputs once and use guarded, bounded exact-single values for the
   paired-vector portion. Initial squared-component inputs must admit a
   positive normal norm; otherwise reject. Do not assume game constants when
   arbitrary valid inputs can reach this entry.
3. Retain original reciprocal-square-root estimate, not hardware sqrt/rsqrt.
   Its output is not automatically an exact single. Scalar multiplication must
   retain the original25-bit C rounding and single-result rounding.
4. Keep intermediate values local vectors/scalars, not a scratch CPUState.
   Preserve each guest operation's rounding. Scalar fnmsubs uses `ppc_fma`,
   whose single path differs from paired `ni_madd_msub`; audit both explicitly.
5. Reject unsupported modes, values, exceptional intermediates and halfway
   corrections to original code before any guest-state commitment. Restore
   raw FPSR after a speculative rejection. Do not change host FPCR or bypass NI.
6. The initial paired madd's upper value is overwritten by sum0, but its
   arithmetic/rounding can still set host flags: it cannot simply be omitted.
   Similarly, sum passthrough conversion is conditional in the actual helper.
7. Prove all guest fields, memory/observer behavior, raw status and unavailable
   entry behavior using the existing whole-chunk/17-op routine comparison.
   Require fast-path coverage, explicit halfway/zero/rejection fixtures, and
   real expected results in addition to control agreement.
8. Cost-screen the complete routine, including guard rejection and varied
   inputs, before any module build. Only repeatable material gain and measured
   scene applicability justify a clean same-scene iPad candidate.

## Unchanged product state

No source candidate, module, app, save, or Simulator changed during this audit.
No new throughput measurement. The last iPad heavy plaza remains37.15 VI/s and
movie59.88 VI/s. Full original PRD remains active, including gameplay, audio,
SunPad product experience and physical-device/package gates.
