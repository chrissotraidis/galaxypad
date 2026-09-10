# R893 complete 41-instruction reference oracle

R892 changed authoritative tooling and selected a larger boundary. This turn
implements and executes that boundary instead of another selection census.

`tests/probe-wide-fp-routine.py` extracts exact original generated bodies for
804B64A4–804B6544, including return, and all41 original external switch charges.
Only the routine's final return-dispatch jump becomes a C return. The complete
original chunk is linked beside it as the reference; no scratch CPUState,
helper replacement, fast-math or discarded memory operation is introduced.
Source SHA38d5085e is required. Cached module O2/strict-FP/ThinLTO/PGO flags are
used for chunk and helper objects. The driver is compiled separately with
assertions enabled. Output manifest records commands and helper/header/driver
hashes. This is an oracle extraction, not the optimized implementation.

## Executed checks

Final command:

`python3 tests/probe-wide-fp-routine.py --output generated/wide-fp-routine-r893c`

Handle23196exit0; generated/wide-fp-r893c.log and output report/result retained.
314,880 CPUState, RAM, alternate RAM, ordered callback digest/count and raw
ARM FPSR comparisons pass.57,600 cases execute callbacks. Initial smaller run
31308 and expanded run95349 also exited0; final includes independent assertions.

Coverage: all41 external entries, four rounding modes, NI0/1, all8 GQR0 type
encodings, four scale encodings0/31/32/63 for both load/store fields, MSR.FP0/1
with lazy-FP enabled, VE on/off distributed by entry, three input/output overlaps,
normal RAM, external access, mutating store journals, boundary-crossing pointers,
and CPUState FPR/paired-bank self-aliasing. Callback changes GPRs, paired values,
RAM mapping and downcount. Store ordering remains original. Only equivalent
self-alias pointer addresses are normalized before CPUState comparison.

Independent assertions: unavailable-FPU SRR0 equals the actual suffix PC; a
completed no-callback/no-exception routine charges exactly41-entry cycles and
returns to aligned original LR. Comparisons include negative initial downcount.

## Limits and next implementation

This is native macOS oracle execution, not Simulator/device or game acceptance.
No optimized candidate or benchmark exists yet. Helpers are real but compiled
into a private harness; input coverage is finite, not exhaustive. No sanitizers
or full repository suite were run. Compiler warns one of51 profiled functions
mismatches and integer helper unit lacks profile data; do not claim exact final
game-module link/PGO identity or use this as a shipping performance result.

Next implement a default-off private routine candidate with explicit guarded
normal-RAM eligibility. Use original routine on aliases, callbacks/journals,
unsupported GQR/FP conditions or boundary cases. Guards must not themselves
change state or FP flags. Preserve original interleaved stores and suffix paths;
do not move output writes or cache mutable mapping through arbitrary callbacks.
Test against this oracle, inspect resulting code, then measure complete routine
under actual policy. Do not rebuild a game module without material savings.

No app/module/save mutation, game or Simulator launched. Full PRD and iPad
performance/gameplay/audio/device requirements remain active.
