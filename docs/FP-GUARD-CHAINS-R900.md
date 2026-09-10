# R900: platform code comparison and private FP guard-chain candidate

R899 completed actual heavy-scene attribution. This turn checks platform code
generation and implements a distinct shared lowering candidate. No product module,
app, default setting, save, Simulator or game runtime is changed.

## Platform code-generation result

`python3 scripts/compare-platform-codegen.py --profile generated/runtime/heavy-native-r899/summary.json --output generated/platform-codegen-r900.json`

Run17455 exits0. Both exact module SHA identities are checked (native c0021b9f,
Simulator3acdcddc). All577 sampled generated chunks have identical opcode
sequences and instruction counts:13,240,666 instructions each.13,237,199 words
match exactly at the same instruction index;3,467 differ. No complete chunk is
byte-identical. The comparator does NOT normalize relocations or claim all
differences are addresses. Initial inspected805170A0 entry shows the same
prologue/dispatch with shifted code/data addresses.

This rules out extra static instructions in these Simulator chunks, not a
platform runtime penalty, different dynamic paths, alias/cache effects, callee
differences or semantic equivalence of complete modules. It is not a timing
measurement. Missing/empty/duplicate symbols and differing sequences are tested;
raw encoding equality remains separate from opcode equality. No new profile or
build was needed for this comparison.

## Implemented candidate, private only

scripts/fp_guard_chains.py relocates a redundant FP-availability guard from a
strictly adjacent pure-arithmetic fall-through to its external switch case.
The external case retains original suffix downcount charge, materializes the
original PC, performs the original guard/exception return, then enters the body.
The chain's first instruction retains its original guard. Internal arithmetic,
FPR/FPSCR/paired values and every non-guard statement are unchanged.

Only literal register operands0–31 and a closed helper allowlist are accepted.
The pinned float helper source SHA554149a2e7d08783402af38e5a2b898aff476370b0e3a6af0ed4bd411aab934f
was inspected: selected add/sub/multiply/madd/sum helpers and their status-update
paths do not change MSR or lazy-FP availability or invoke external memory/hooks.
The builder-side probe verifies that source hash before compiling. No assumption
of availability is carried across loads/stores, extra statements, unknown calls,
record forms, extra incoming gotos, cycle-leader statements or function boundaries.
Multiple/outlined functions are conservatively skipped. This is a private
closed-grammar transform, not an arbitrary-C optimizer or an integrated emitter.

This is different from dead-FPRF elimination, compact-state arithmetic, guarded
memory mapping, or blanket inlining: all FP arithmetic/status writes remain.
Its possible gain is unmeasured and may be modest; R899 lazy-global sampled loads
are not a bound on all check costs or a promise of removable time.

## Executed verification

Extended tests/probe-wide-fp-routine.py with mutually isolated correctness-only
--fp-guard-chains. It reuses the actual original chunk, headers/helper objects,
strict-FP/O2/ThinLTO/PGO compilation policy and full-state driver. It refuses
--benchmark for this mode: extracted-function timing would confound dispatch
changes and cannot replace a whole-chunk comparison.

- Wide41-instruction routine:14 guards relocated. Initial80219exit0,
  314880 full CPUState/memory/callback/raw-FPSR comparisons,57600 callback cases.
- Normalization17-instruction routine:64195exit0,130560 comparisons,
  23040 callback cases. This run precedes the next lazy-mode expansion.
- Expanded driver adds lazy-FP disabled as well as enabled, keeping independent
  unavailable-exception assertion conditional on lazy mode. Wide35339exit0:
  629760 comparisons,172800 callback cases. All41 suffix entries, MSR-FP on/off,
  RN/NI, quantization/scales, overlaps, external callbacks, journaling and
  CPUState-as-RAM cases are retained. No comparison masks were weakened.

Artifacts: generated/fp-guard-chains-r900, fp-guard-normalize-r900,
fp-guard-chains-lazy-r900 plus corresponding logs. These compare the extracted
transformed routine against the unchanged whole-chunk reference; this is NOT
whole-module/interruption/SMC/mobile acceptance. No sanitizer claim is made for
this actual-policy harness. Existing nested-comment, one-of51 mismatched-PGO and
unprofiled integer-helper warnings remain visible. No complete PGO parity claim.
The printed memory-candidate fast-path count0 is expected in this mutually
exclusive mode; relocated-site list separately proves guard transformation.

Pure-transform tests pass positive relocation/idempotence and negative
observer/branch/operand/record/multiple-function cases. Platform-comparison tests
and py_compile pass. Both lightweight tests registered in check-repository.sh;
the full repository suite was not run this turn.

## Next gate

Compile the transformed **whole original chunk**, retaining normal entry dispatch
and all original surrounding code. Compare whole-chunk behavior across entries
and callbacks and measure actual-policy CPU work/code size. Include an unchanged
control, record PGO mismatches, and check whether relocation merely shifts cost
into dispatch or expands hot code. Reject on absent material repeatable benefit;
do not start another series of tiny per-helper guard tweaks.

Only then quantify eligible coverage in other chunks and consider a private
module for matched iPad gameplay A/B. No guest precision/status/exception/clock
relaxation and no real-depth removal. Current nativeTHP/movie, touch/menu/icon,
audio/story/stability/device/packaging/rights gates remain part of the full PRD.
No game-speed improvement or shipping selection is claimed.
