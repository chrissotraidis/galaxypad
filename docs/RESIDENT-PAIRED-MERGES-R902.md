# R902: resident paired-lane value lowering

R901 rejected the guard-relocation candidate on measured cost. That candidate
stays closed. This turn extends the existing private offline reference-register-
cache path, not the app or a runtime JIT. No new game/profile/module build.

Added tests/aot-paired-merge.h: exact decoding of opcode4 XO528/560/592/624,
non-record ps_merge00/01/10/11 only, and register-cache value lowering. The
reference Interpreter_Paired.cpp73–120 confirms lane moves; record forms also
update CR1 and are deliberately rejected here.

Both source lanes are captured before acquiring the destination. Q30 is reserved
for staging; Q31 cannot be used because split-lane cache loads/spills overwrite
it. This handles destination/source aliases and source eviction under pressure.
Values stay in the actual reference FPR cache across successive operations;
there is no per-merge C helper call, CPUState scratch copy, FP arithmetic, rounding
change or runtime code allocation. Guest entry/availability/PC/cycle/CR handling
is explicitly outside this value-lowering component, not silently implemented.

Verification extends the existing static-export harness:

- All131072 register/selector encodings decode correctly, with corresponding
  record-form, wrong-primary-opcode and neighboring-XO rejections.
- Generated sequence performs128 merges across all destination registers, four
  selector modes, disjoint/d=a/d=b/a=b=d operands, cache pressure and a mid-sequence
  full flush. It follows the existing callback mutation/reload fixture.
- Paired merges plus exact conversion:98230 initial and74756 decoded-final exit0;
  100000 full CPUState/FPSR/FPCR comparisons each. Includes existing systematic
  exponent/sign/mantissa and16host-mode inputs plus random payloads.
- Paired merges without conversion and unchanged exact-conversion regression:
 53577exit0,100000 comparisons each. All final stderr files empty.
- C++ oracle/driver uses ASan/UBSan; generated static assembly is uninstrumented.
  Decoder-field coverage is not all possible runtime operands/guest entries.
  No independent NZCV/full-AAPCS/whole-guest-instruction acceptance is claimed.

Commands: python3 tests/probe-arm64-fpr-cache.py with --paired-merges,
--exact-conversion, or both. Artifacts generated/arm64-paired-merges-decoded-r902,
arm64-paired-merges-plain-r902 and arm64-fpr-regression-r902 (.json/.err).
JSON retains reference/adapted source hashes and emitted assembly. Temporary
compiler directories are cleaned by the existing harness. Vendor tree unchanged.

Next integrate guest instruction boundaries and broader FP arithmetic with
resident state before a complete-routine actual-policy comparison. Do not time
this transport fixture and call it a Galaxy speedup, or turn it into another
series of per-merge microbenchmarks. Reference arithmetic precision/status and
all suffix/callback/exception/cycle contracts remain required. Full original
PRD/SunPad/gameplay/audio/stability/device/package scope remains open; no FPS gain.
