# R782: qualify broad register-state scope before another batch

Previous turn: progress. R780 rejected a small typed transform for promotion;
R781 full regression passed. No current game-speed improvement is claimed.

Recomputed retained R762 CPU-thread exclusive wall-stack categories from
fallback-sample-r762.json:1695 total,1070 generated-chunk leaves,305 Run/chassis
leaves,320 other/unattributed. Chosen transform chunk804B60A0 has44. These are
wall samples, not CPU-time shares; no whole-game Amdahl estimate is justified.
Retained Run assembly's two displayed offsets identify module dispatch-pointer
load and idle-PC load. Collapsed samples cannot be apportioned between them.

R764's selected phase has3615590 native spans and80601706708 CPU nanoseconds.
An optimization applied once per native span would need to save about1783ns
per span to remove8% of that measured CPU time. This is a required savings
budget, NOT measured SyncIn/SyncOut cost. Those functions copy full registers
once per burst, not once per generated dispatch. Do not confuse these rates or
start a synchronization rewrite merely because the source contains memcpy.

New scripts/audit-gpr-spans.py reuses the existing exact integer-body recognizer
to count contiguous callback-free GPR-only spans. Cycle charges, callbacks,
other state, control exits, unknown bodies and address gaps break spans.
Original external labels are not removed. The scan is not a liveness proof.
tests/test-gpr-spans.py passes positive and barrier checks and is registered;
full suite has not been rerun after this addition.

40039exit0, generated/gpr-spans-r782.json:1322chunks,169835 recognized integer
instructions, only671 in spans of at least8. Conservative whitelist coverage,
not all integer code or dynamic execution. Result does not justify another pure
local GPR batch implementation. Do not add one opcode at a time to rescue it.

Next substantive dataflow proposal must handle memory/helper boundaries and
demonstrate actual redundant state traffic there, including callback mutation,
aliasing, external entry and exception/timing observers. Source census alone
cannot establish a speedup. Preserve the rejected mapping-cache, direct-call,
FP-batch and conversion-hint dispositions; do not rename them as new work.
No module/app rebuild, runtime launch, settings or saves changed. Original PRD
and cutscene/audio, SunPad, progression and physical-device gates remain open.
