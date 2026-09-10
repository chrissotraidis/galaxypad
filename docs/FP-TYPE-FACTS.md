# R778: precision facts require the actual execution contract

## R780 full-chunk typed-span cost screen: insufficient benefit

`tests/probe-transform-inline.py --typed-span`, session23621 exit0;
`generated/typed-fp-span-r780.log`. Facts start unknown at span entry and
are derived only within the nineteen-instruction span. Entry requires FP on,
VE off and NI off. Four qualified paired multiplies use binary32 vectors,
with original nonfinite fallback. Original interior labels remain available.
No module, installed app, accuracy setting or save was changed.

22,528 complete-transform CPU/RAM/host-flag comparisons pass under the actual
whole-chunk ThinLTO/PGO compile policy. This integration run is release, not
sanitized; the separate R779 arithmetic oracle was sanitized. Missing candidate
profile and existing stale-profile warnings remain, so this is not a newly
trained candidate-PGO comparison or whole-module measurement.

Eight alternating windows: reference191-ish ns/transform (190.836–191.501),
candidate185.167–187.579. Mean improvement about2.8%, while instructions rise
from about2747 to2873–2874 (about4.6%). This narrowly reverses the scalar batch's
timing loss but does not establish a material game-level benefit. Do not promote,
train a full module, or claim FPS improvement from this result. Broader type
lowering needs independent coverage and native-cost evidence; further batch
representation/attribute variants remain closed.

## R779 arithmetic prerequisite: precision-qualified paired multiply

`tests/test-typed-ps-multiply.py` compares actual ppc_ps_mul_op with paired
binary32 multiplication only when both input lanes are already exact widened
binary32 values, finite, and NI is clear. Source precision is a PRECONDITION,
not a runtime check or inference from an opcode. Nonfinite/NI inputs execute
the original helper. Output writes and FPRF classification remain original.
The PS helper writes unconditionally; this does not waive R778's success/VE
guard requirement when deriving facts from preceding scalar instructions.

40165exit0 under ASan/UBSan:640000 complete CPU-state/host-flag comparisons,
four RN modes, both NI values, varied status, four destination/source alias
patterns, boundary/special and random binary32 inputs.292605 vector calls;
remaining cases take original fallback. Input conversion is performed with host
flush disabled before setting the tested mode, so preceding NI tests cannot
silently remove subnormal fixtures. Widening may quiet signaling NaNs; the
test does not claim an exhaustive raw signaling-NaN binary64 corpus.

No timing benchmark or speed claim: the operation is not installed in the
module and no general precision propagation exists yet. Next source-validated,
guarded facts inside the complete chunk, original interior-entry/fallback paths,
full-transform differential check and actual-policy cost screen. Do not replace
unqualified calls or change NI/exception settings to increase eligibility.

Rechecked actual JitArm64_Paired.cpp: paired arithmetic chooses32/64-bit host
registers based on input precision facts, and omits C-operand rounding only when
the source is known single. PPCAnalyst.cpp forward propagation classifies scalar
single results, frsp, loads and paired outputs. This is not merely inlining.

Do not copy those facts unconditionally into the C backend. The JIT paired path
explicitly falls back for `jo.fp_exceptions`. Current scalar C helpers can keep
the old destination when invalid-result gating applies. Neither the precision
fact nor the chosen execution contract can be inferred from the opcode name.

`tests/test-fp-single-facts.py` executes actual ppc_fmuls/ppc_frsp under ASan/UBSan:
12 invalid-operation/VE/source-destination-alias cases plus finite VE-enabled
success.65217exit0. With VE enabled, invalid multiplication and signaling-NaN
rounding preserve both old destination lanes. A retained non-single destination
is demonstrably changed by force_25bit_c, so deleting that later rounding from
an unconditional type tag would be incorrect. Successful finite writes still
establish a single with VE enabled: treating VE as unconditional failure is also
too coarse. Test registered; no emitter/runtime change.

Any future precision-dataflow prototype needs success-conditioned facts or an
explicit guarded region with original fallback, invalidation at observers and
callbacks, and unknown facts for external/interior entry. A named scalar local
does not establish single precision. R776/R777's batching cost failures remain
closed; do not relabel them as a type-aware emitter.

Also reverified retained reference-fp-r425/Config/Dolphin.ini: CPUCore4,
FPRF/AccurateNaNsTrue and FloatExceptions/DivByZeroExceptionsFalse. R425's retained
measurement is6.257ms CPU/VI versus R424 AOT16.683ms, historical same-scene data,
not a new run. Accuracy defaults alone are not an established explanation.
No relaxed FP policy, mobile machine-code JIT, full build or performance claim.
