# R787: general checked multiply is correct but fails useful cost gate

Previous turn progress: square guard sanitizer coverage and hot-site selection.
Private checked-ps-multiply.inc generalizes the integer precision check to four
source lanes, retains original helper for nonfinite/non-single/NI, and captures
both vector operands before output writes. No runtime helper is replaced.

tests/test-checked-ps-multiply.py,29700exit0, ASan/UBSan:
655360 fullCPU/hostflag comparisons;106571 vector calls; five alias patterns
(distinct, destination=A, destination=C, same operands, all equal), all RN/NI,
varied FPSCR, raw64/widenedraw32/exponent-neighbor/special inputs and retained
hostflags. Test registered; no full suite rerun. Logchecked-multiply-r787.log.

Full-context probe --cross-checked replaces only804B6CCC in the complete chunk,
and executes actual fifteen-instruction routine804B6CB8–804B6CF0. Input vectors
use separate RAM ranges, outputr5 uses its own range.15interior entries, random
input/register/status, four RN/two NI and FPU-unavailable cases.75110exit0:
7680full CPU/RAM/hostflag comparisons pass under original Ninja ThinLTO/PGO flags.
Integration run is release, not sanitized; original compiler warnings retained.

Eight alternating cost windows: reference43.286–43.949ns, candidate42.878–43.180ns.
Mean local benefit only about1.1%, while instructions rise865→934 (about8%).
Loggenerated/cross-checked-r787.log. This does not meet a material cost gate;
do not deploy this general helper, rebuild a module, or extrapolate square's7%
result to arbitrary multiply. Standalone correctness does not override cost.

Square candidate remains separately bounded evidence. Broader dataflow would
need to eliminate precision-check overhead using proven facts across real
memory/observer paths; this runtime four-lane guard is not that transformation.
No further predicate/attribute micro-tuning to rescue this implementation.
Full original PRD/performance/movie/audio/stability/SunPad/device goal remains.
