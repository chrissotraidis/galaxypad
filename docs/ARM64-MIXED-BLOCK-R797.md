# R797: arithmetic, loads and journaled stores in an exported block

Extended the private exporter to decoded addi/li, non-record/non-overflow add,
lwz and stw followed by blr. Unsupported instruction forms reject before output.
The reference GPR cache handles arithmetic values; it flushes before memory
helpers and return. ABI argument registers are reserved from allocation.

The selected real DOL sequence80319AB8–80319ADC contains ten instructions:
lwz,add,addi,stw,lwz,stw,add,stw,li,blr. Its generated source SHA is
34534c0a4f7fa9105f1a41c7f01a053dbf9fc9dc38d40ac79d0007ab8e7b766b.
The existing exact DOL hash check remains. Each suffix charge10through1 is
verified against the current generated switch. This is a static integration
fixture, not an asserted gameplay hotspot.

The driver now compares all three RAM buffers as well as full CPUState and
ordered callback traces. Store helpers use existing mem_write32, preserving
reservation and journal semantics. Journaling can change all GPRs, RAM mapping,
LR, flags and cycle counter while the store retains its already acquired pointer.
Buffers reset before each reference/candidate half; no comparison uses memory
modified by the other half. Missing callbacks, MEM1/MEM2 mirrors, boundaries,
wrap and all ten legal suffix entries are included. Five invalid PCs reject
without side effects; an unsupported opcode rejects export before writing text.

Direct-layout mixed run94353exit0:152,320 comparisons. Earlier restore block
regressions67065direct/60862frame both exit0,60,928 comparisons each with the
expanded journal-mode matrix. All stderr files empty; git diff check passed.
ASan/UBSan cover driver/helpers; generated assembly is not instrumented.

Reproduce with `python3 tests/probe-arm64-restore-block.py --direct-cpu --mixed`.
Evidence generated/arm64-mixed-r797.json, arm64-restore-regression-r797.json,
arm64-frame-regression-r797.json and their.err files.

No FPS gain or usable new game backend yet. Ordinary memory accesses still
cross C helper boundaries, so these tests establish semantics rather than the
intended speed improvement. Actual CPUState/RAM overlap, broad opcode coverage,
FP/CR, interrupts/SMC integration and mobile execution remain unproven.

Next emit normal-RAM memory accesses directly while preserving canonical-state
flushes and the original callback/journal path. Validate this same complete block
and CPUState-alias cases before measuring whole-block work under actual build
policy. Continue into reference FP register/precision handling if the architecture
remains viable. Do not treat this narrow fixture as the final performance target.
Original PRD/SunPad/stability/device requirements remain unchanged.
