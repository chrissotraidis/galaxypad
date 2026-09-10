# R768: whole-transform strict FP inlining screen

## R769 disposition: reject blanket inlining

The `--full-chunk` mode now compiles the complete original1024-instruction
chunk twice, retaining its function name, entry switch and return dispatcher.
It reads compile flags from the actual macOS scale-r387 build graph, including
ThinLTO, PGO, final-O2, NDEBUG, ARM64, hidden visibility and strict arithmetic.
Both libraries link freshly compiled current CPU runtime units. Candidate alone
contains renamed mandatory-inline float clones. The separate assertion-enabled
driver loads both libraries; neither product-code variant gets-UNDEBUG.

Session70051exit0, generated/transform-inline-r769b.log:22,528 CPU/RAM/host-flag
comparisons pass through the actual chunk entry switch. Warmed ABBA x2:
reference191.197–193.905ns and2744–2749instructions/call; candidate
194.011–197.010ns and2708–2711instructions/call. The prior~16% standalone
instruction reduction contracts to about1.4%, with no CPU-time benefit.

These are same-policy single-chunk libraries, not the installed full module:
link context, driver and runtime ownership differ. Build warnings retained:
unprofiled integer unit, one stale CPU profile function, existing comment warning.
They do not invalidate the matched comparison, but neither full PGO coverage nor
an exact installed binary was demonstrated. The first attempt failed because
clone declarations preceded FPRes's private header; fixed include order and
reran. No behavior stubs or relaxed flags were introduced.

**Close this implementation.** Do not rebuild the full module, force-inline
globally, add more attribute variants, or cite the earlier standalone percentage
as a projected game gain. This fails the material-benefit gate before needing
wider callback/fault qualification. It does not rule out a different emitter
that changes state lifetime/dataflow, or every future FP optimization.

The R767 turn completed bounded decoder coverage, not a gameplay improvement.
Return to the independent review's shared FP/state-materialization hypothesis.
This experiment differs from R766's three-operation value ABI: it executes the
complete emitted44-instruction transform804B6278–804B6324, including loads,
stores, reciprocal-square-root estimate, fused-operation helpers and returns.

`tests/probe-transform-inline.py` reads the current scale-r387 source and clones
the actual float implementation with mandatory inlining. Arithmetic, NaN/FPRF/
FPSCR behavior and CPUState ABI remain unchanged. No fast-math or fused host
contraction is enabled. Reference and candidate use the same extracted body,
44-way entry switch, strict compilation, actual RAM/exception runtime and driver.
Only candidate float calls are renamed to the inlined clones. Generated product
sources, core, app selection and saves are untouched. Temporary sources/binaries
are removed by the probe; retained logs contain hashes and results, not media.

## Executed evidence

- Source chunk SHA256:38d5085e7e8eceece0521f5566c012a5c15fa5a7be7c2c1fe915985d28c376ac.
- Float SHA256:554149a2e7d08783402af38e5a2b898aff476370b0e3a6af0ed4bd411aab934f.
-22,528 full CPU-state, RAM and host-FP-flag comparisons pass in ASan/UBSan
  and release:44 entry points,4 rounding modes,2 NI modes,64 FP patterns with
  finite, special/raw-bit operands and varied initial status. PC, charged cycles
  and absence of unexpected exceptions also checked. RAM inputs are a fixed
  valid synthetic fixture; callbacks/faulting accesses are NOT covered.
- Final session2788exit0, generated/transform-inline-r768d.log. Two warmed
  release ABBA sequences,1million calls/window: reference170.750–178.007ns,
  candidate145.364–153.593ns. Dynamic process instructions/call including driver
  ~3291–3294 versus2766–2769 (about16% fewer). Earlier c-log timing was noisy;
  do not use its236ns first-reference sample as the claimed saving.
- Static extracted-function size1570 versus5519 instructions; direct call sites
  82 versus51. This is a substantial code-size tradeoff, not a free optimization.
  Counts include all interior entries and cold paths, not runtime frequencies.

## Boundary and next decision

This is an isolated compiler screen, NOT the installed ThinLTO/PGO module or
measured gameplay benefit. The extracted reference's instruction count is higher
than historical R464 installed-fixture counts; different drivers/build policy
prevent subtracting these as a speedup. Do not promote or rebuild the full module
from the isolated percentage. The review's proposed2x instruction-work reduction
is not met here. Blanket inlining is therefore not qualified for deployment.

Next use the actual build flags and a bounded single-chunk comparison to check
whether any reduction survives installed-code optimization, plus callback/fault
and representative-kernel coverage before any wider emitter policy. If the
installed-code cost screen removes the benefit, stop this implementation rather
than retuning attributes indefinitely. Full gameplay performance, stability,
SunPad touch/menu and physical-device PRD gates remain open.
