# Shared FP/state experiment — R737 source boundary

## R739 linked-helper check and conversion hint: parked

The linked R721 diagnostic ps_add already inlines arithmetic, force_single and
FPRF work. The review's blanket out-of-line characterization is not sufficient
for this artifact. NI-off conversion still computes flush candidates, motivating
an isolated unlikely-NI branch hint in the exact force_single source.
tests/test-single-mode-hint.py passes800000 conversion cases, comparing bits,
host flags and unchanged FPSCR across all RN and NI combinations under UBSan.
Original and hinted ps_add each have84 static assembly instructions. Static
counts are not dynamic work or a proof of identical assembly; no material
benefit is established. Log: generated/single-mode-r739.log.
Park this hint without a module build. No production source/module mutation.
Do not replace the architectural workstream with more conversion micro-tweaks.

## R738 coverage result: integer-gap deferral parked

New audit-fprf-gaps.py reuses the established paired-writer body recognizer and
admits only selected non-record integer mnemonics whose entire emitted body is
a GPR assignment over register/immediate expressions (or an empty NOP). Calls,
other state, extra statements, unexpected entries and unknown shapes stop the
region. This is a read-only census, not a correctness proof or transformation.
Focused positive/barrier tests pass; registered in repository suite.

Actual1322chunk scan97973exit0:165regions, only ONE nonadjacent region (two gap
instructions: addi and li). Artifact generated/fprf-gaps-r738.json includes source
hashes and exact producer/overwrite addresses. Existing164 adjacent regions are
not newly discovered savings. No material scope established by this conservative
extension; park it without code generation, timing harness or module build.
This does not prove every integer opcode or broader state optimization lacks
opportunity. Next investigate shared helper lowering/state traffic rather than
adding another opcode to rescue a one-region experiment. Keep original accuracy.

Follows the R736 closure of the first guarded direct-call design. Full original
PRD and accuracy requirements remain unchanged; no new product optimization yet.

## Avoid repeating completed or rejected work

- R164–R177 already implemented and promoted119 decoder FPRF deferrals with
  actual emitted-code, all-entry, rounding/exception and lifecycle evidence.
- Re-ran existing strict adjacent-writer audit against CURRENT R387 generated
  chunks:164 remaining sites across68chunks. Largest804220A0=37,
  804B60A0=23,804B50A0=16.123 textual deferred-helper mentions include declarations,
  so that is not a count of distinct optimized call sites. These are static
  counts, not execution frequency or expected CPU saving.
- R465–R466 already tested canonical-single conversion provenance and parked a
  small local specialization. FPSCR NI changes invalidate its identity property;
  conditional destination suppression prevents unconditional producer facts.
- R181–R187 already tested one-chunk normal/interior entry splitting; its live
  gain was only1.376% versus fresh control. Do not restart that unchanged design.

## Next bounded coverage question

Can status liveness across callback-free straight-line regions remove materially
more classification/state writes than the existing adjacent paired-op whitelist?
Investigate paired writers separated by proven non-observing integer instructions,
not an extra handful of identical adjacent sites. Read actual emitted bodies:
PC labels/entry joins, downcount charging, FP availability checks and early-return
paths must remain explicit. Unknown operations are barriers, not assumed safe.

Required barriers include memory/helper callbacks, branches/returns/traps,
exception/control changes, FPSCR reads/writes/record observers, and any operation
whose later FPRF write is conditional. A producer may be suppressed only if an
overwrite is guaranteed before every possible observation/exit from that path.
Preserve every external instruction entry; a suffix entry cannot assume an
earlier producer ran. No CPUState ABI or runtime lazy-state machinery is needed
merely to establish coverage. First count safe regions and their actual bodies;
if scope remains tiny, do not build another module on static counts alone.

No game, simulator or compiler is running at this checkpoint. No source/emitter
or installed module has been changed by this read-only audit.
