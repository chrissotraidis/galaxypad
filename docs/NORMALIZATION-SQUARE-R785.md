# R785: checked paired square in executed normalization routine

## R786 guard stress and adjacent executed-site qualification

tests/test-normalization-square.py extracts the exact helper string from the
R785 probe AST rather than copying its implementation. Actual ppc_ps_mul_op
oracle, full CPU state and host flags compared.53008exit0 under ASan/UBSan:
262144 cases,43133 vector-path calls. All RN/NI modes, varied status, raw64
values, widened raw32, exponent sweep with neighboring mantissas, signed zero,
subnormals, maxima, infinities and raw signaling/quiet NaNs. Some cases begin
with FE_DIVBYZERO already set; retained flags must agree. Exact fixed r2→r5
square only, not a general variable-register multiply or exhaustive input proof.
Registered in repository suite; no full-suite rerun this turn. Log retained at
generated/normalization-square-r786.log. Prior~7%local timing is unchanged evidence,
not a new speed benchmark or game result.

Joined R784 resolved instruction counts to actual source annotations. Other
executed ps_mul sites include804B6CCC(f4=f1*f2):19279400 and
804B6CA0(f2=f2*f3):7130427; another square804B6C5C(f0=f0*f0):4276210.
These counts are retained training frequency, not current CPU share, and the
non-square operations require four-lane input qualification plus alias tests.
Next generalize the guarded arithmetic only in an isolated candidate and measure
these complete routines under actual build policy; do not infer the square's
benefit transfers automatically or mutate all ps_mul calls without evidence.
No runtime/app/module/save change. Full original objective remains incomplete.

Previous turn: progress, instruction-level retained profile corrected target.
Current exact source804B6BCC–804B6C0C is seventeen instructions, including input
loads, arithmetic, output stores and return. No prior exact804B6BCC candidate
found in scoped tests/scripts/experiment search. Earlier cold FP batch/inlining
results are not evidence of improvement for this routine.

tests/probe-transform-inline.py --normalization-square changes only the paired
square at804B6BD4 in the complete1024-instruction chunk. Integer conversion
round-trip checks require finite exact widened-binary32 inputs and NI clear.
This check does not itself change host FP flags. Original helper handles other
inputs. Output/FPRF logic is original. Unlike opcode-derived facts, the guard
works for interior entry and prior callbacks that may have changed registers.
No memory operation, FP-availability check, label, cycle or return is removed.

Actual Ninja ThinLTO/PGO flags retained; temporary separate full-chunk dylibs,
no installed module change. First28029exit0:8704CPU/RAM/hostflag cases, then
ABBA timing with initial reference108.871ns outlier; do not summarize it as a
large speedup. Added randomized binary32 input-memory payloads to the existing
arbitrary register/status/interior-entry corpus. Benchmark resets1,2,3input.

Final15227exit0, generated/normalization-square-r785b.log:

-8704complete routine comparisons pass over17entries, four RN modes, both NI,
  random registers/status/input data and FP-unavailable cases. Release build;
  not a new sanitizer result, callback/mapping or game stability acceptance.
- Reference81.810–83.876ns; candidate76.845–77.379ns in eight alternating windows.
  Mean about7.0% lower CPU time for this normalization fixture.
- Instructions increase from1062–1064 to1074–1075 per call. Retained existing
  CPU profile mismatch/unprofiled integer warnings remain visible.

This is a local routine gain, not7%game FPS, fresh scene coverage or fullmodule
candidate-trainedPGO proof. R784 establishes historical execution frequency,
not CPU share. No full build/promotion yet. Next independently stress the integer
precision guard (raw64/subnormal/NaN/hostflags), then qualify applicability/cost
across genuinely executed paired arithmetic before broader integration.
Full original PRD, native movie/audio, stability, SunPad and device gates remain.
