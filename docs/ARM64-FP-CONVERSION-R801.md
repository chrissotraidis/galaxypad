# R801: exact single-to-double widening in the offline FP cache

R800 made progress by fixing split-lane state transport. This turn replaces the
private host's conversion aborts only when AOT_EXACT_FP is explicitly enabled.
No vendor source or normal build include path changes.

tests/aot-exact-fp-conversion.h emits integer-only binary32-to-binary64 widening.
It maps sign/exponent/fraction, normalizes subnormals with CLZ/variable shift and
preserves special-value payload bits. The output is compared with the selected
GXRuntime core/types.h convert_to_double oracle, not a host-language float cast.
Both packed source lanes are captured before an aliased destination is written.
Scratch X0–X7 and NZCV are saved/restored. No host FP arithmetic/conversion,
runtime helper address, far-code area, executable allocation or runtime JIT.

The static code is longer than a precision-proven FCVT/FCVTL. IsFPRStoreSafe
returns false: no unproved offline single-precision facts are asserted. This is
an exact general path, not a performance optimization or permission to narrow
arbitrary doubles. Single, LowerPairSingle and DuplicatedSingle cache states now
have a usable widening path; double-to-single precision/rounding remains separate.

## Verification

`python3 tests/probe-arm64-fpr-cache.py --exact-conversion` builds private static
emission and tests conversion through the actual cache, including:

- Single pair conversion in place and copying to another destination;
- lower-single conversion followed by upper-lane reload;
- duplicated-single conversion and duplication;
- dirty single-pair upper-lane preservation when overwriting only the lower;
- prior spill/callback-entry/full-state transport checks;
- 65,536 systematic cases covering every binary32 exponent/sign, eight mantissa
  edges and16 combinations of host rounding/FZ/DN, plus34,464 random cases;
- complete CPUState and unchanged host FPSR/FPCR checks.

Final46372exit0:100,000 cases pass; initial80729 also passed before explicit
edge/mode coverage. GPR34938 and non-converting FP1516 regressions each pass
100,000 cases. All stderr files empty. C++ driver uses ASan/UBSan; emitted assembly
is uninstrumented. NZCV preservation is emitted but not independently measured
by this driver; this is not exhaustive AAPCS preservation proof.

Evidence: generated/arm64-convert-r801-final.json, arm64-gpr-regression-r801.json,
arm64-fpr-regression-r801.json and corresponding .err files.

## Next

Use this exact cache conversion path while implementing the qualified complete
FP region, with explicit facts for any faster path. Preserve per-instruction
rounding, status and conditional writes, legal suffixes and original cycle
charges. Compare actual containing-routine state and original ThinLTO/PGO cost
before integration. Do not equate successful widening with correct guest
arithmetic, narrowed intermediates, or a faster module.

No app/module/save/Simulator change, no FPS gain. Full original PRD, SunPad,
gameplay, audio, stability and physical-device gates remain active.
