# R766: narrower paired-FP helper interface

Current Simulator chunk804B60A0 contains calls to ppc_ps_* helpers. Internal
arithmetic inlining inside a helper is not the same as inlining that helper into
its caller. Existing LLVM, chunk-splitting, blanket-inline and finite-path
experiments have parked results; they were not restarted here.

## Isolated candidate

`tests/probe-value-fp-abi.py` extracts unchanged add/sub/mul arithmetic and its
status-only dependencies. It asserts that those dependencies access only FPSCR
and forward their CPU pointer only to the enumerated status helpers. Candidate
helpers receive four FP values and a FPSCR pointer, returning an ARM64-friendly
two-double pair. Small caller wrappers perform the original register writes.
No CPUState ABI, runtime, generated module, arithmetic or FPSCR policy is changed.

The first scratch-CPUState version left extra internal calls and a large scratch
object. The revised prototype uses a four-byte FPStatus object. Correctness
compares complete CPUState and host FP flags across192000 cases per build:
add/sub/mul, four rounding modes, both NI modes, destination/source aliases,
special/raw-bit inputs and varied initial FPSCR. UBSan and release pass.
This is not full generated-chunk, memory-callback, interior-entry or gameplay proof.

## Cost-screen correction and result

Initial sanitizer timings are not release evidence. A later apparent gain also
had unmatched internal inlining: the baseline still called ni_add/ni_sub while
the candidate inlined them. Neither justifies a speed claim.

Final comparison applies the same status-helper inlining requirement to BOTH
interfaces. Release ABBA three-op chain: original18.897/18.752ns, candidate
19.442/19.531ns. All checksums match. Original/candidate caller static instruction
counts20/25; helper counts207/199 for add/sub and213/207 for mul. Fewer helper
instructions do not imply less net chain cost. This is an isolated non-PGO C
screen, not the exact installed ThinLTO/PGO policy or a game-speed measurement.

Decision: park this value-ABI implementation; no module build or further small
attribute tuning. Retain the probe and logs under generated/value-fp-abi-r766*.

## Separate product-policy finding

Normal ios-simulator-app cache has nativeTHP OFF; the separate
ios-simulator-thp-app cache has it ON. This is a distinct private candidate lane,
not evidence that the normal build accidentally changed configuration. Previous
native movie completion exists (R680), but audio/device/full acceptance is open.
Normal host previously silently ignored NativeTHP YES when compiled without it.
Added an explicit unavailable/original-decoder warning and preprocessor tests.
Next review the native-candidate acceptance record before selecting that lane;
do not claim a launch argument enables code absent from the binary.
