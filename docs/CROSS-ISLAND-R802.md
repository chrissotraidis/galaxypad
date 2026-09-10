# R802: whole cross-product island clears the local material-cost screen

R801 completed exact cache widening. Inspection of actual paired FMA rules then
identified a simpler way to test sustained register reuse: one guarded native
vector region in the existing C backend, rather than finishing a new backend
before measuring benefit. This is distinct from the rejected single-multiply
R787 and load-prefix R788 variants.

## Candidate

patches/experiments/cross-island-vector.inc computes all six instructions
804B6CCC–804B6CE0 together: two paired multiplies, two paired multiply-subtracts,
and two lane merges. Input values are captured and intermediate pairs remain
local vectors until the complete result is accepted. Only final FPRF is needed
inside this observer-free region; all other status bits are preserved.

One eligibility guard requires nearest rounding, NI off, and exact binary32
inputs that are zero or bounded normal magnitudes [2^-30,2^31). This excludes
NaNs, infinities and inputs whose intermediate products/differences need the
original overflow/subnormal/25-bit operand handling. Rejected inputs execute
the unchanged four arithmetic helpers and two merges.

Fast arithmetic uses paired double multiplication/FMA with original single
rounding after each guest operation, not freely reassociated float math. The
reference corrects double-rounding midpoint cases in ni_madd_msub. Detection
of any such result restores the pre-attempt FPSR and runs the original island
before committing any guest output. Function-scoped FENV_ACCESS and compiler
memory barriers preserve status-sensitive ordering. No approximate sqrt or
fast-math policy is introduced.

## Correctness

tests/test-cross-island-vector.py:262,144 complete CPUState/FPSR comparisons
across rounding/NI, arbitrary status/registers, special/raw/exact-single inputs,
signed zeros and deliberate halfway results.24,129 fast cases and128 tie
fallbacks execute; both counts asserted. ASan/UBSan pass, stderr empty. Test is
registered in check-repository; full suite not rerun.

tests/probe-transform-inline.py --cross-island builds both complete chunks with
the actual Ninja strict-FP/ThinLTO/profile flags. Only entry6CCC calls the fused
island after its original FPU check and resumes at6CE4. Interior entries retain
their original instructions, and original suffix cycle charges remain intact.
7,680 actual15-instruction routine CPU/RAM/host-flag comparisons pass across all
entries, RN/NI, random/special state and FPU unavailable cases. This is release
integration testing; the standalone candidate test is the sanitized one.

The actual-source/DOL fixture remains authoritative. Candidate source is not
yet a production generation policy, and no normal module was changed.

## Measured cost, with limitations

Final72291exit0 includes the strict-status regression and full-context run.
Eight alternating reference/candidate windows, one million routine calls each:

| Actual containing routine | Mean CPU ns/call | Instructions/call |
| --- | ---: | ---: |
|Reference|43.608|about865|
|Candidate|35.095|about778|

This is a19.52% local CPU-time reduction and about10% less instruction work.
Initial83504 also showed a similar benefit before status-order tightening.
Unlike R798, this passes the bounded material-cost screen. It is still one
fixed ordinary input pair, not a representative scene or game-wide FPS result.
The candidate's changed source has no matching profile; compiler explicitly
reports unprofiled candidate data. Existing runtime-unit profile/comment warnings
also remain. Actual flags are preserved, not falsely claimed identical PGO
application. Save these diagnostics rather than suppressing them.

Final evidence:
- generated/cross-island-r802-strict.log/.err
- generated/cross-island-context-r802-strict.log/.err
- helper SHA6ab99fb2a7229f0684261072ac0add543aa7d49e7b72582104a141dd4ae58253

## Next decision

Prioritize this smaller existing-backend change over further offline-backend
expansion for now. Extend full-context tests to deliberately exercised tie,
callback/journal, memory alias and varied input workloads; measure guard rejection
cost and applicability before a private module candidate. Preserve exact source
identity and all suffix paths. Then use a bounded scene A/B to determine actual
CPU/FPS benefit. Do not multiply19.52% by the whole game's runtime or assume
retained19.3M entry attempts equal current CPU share.

No app/module/save/Simulator changes or FPS gain claimed. Full original PRD,
SunPad controls/menu, movie/audio, stability and device gates remain active.
