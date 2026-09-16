# Native-function feasibility on slower iPhones

No additional iPhone speedup is established by this pass. Build 7161 remains
installed. The new work is an executable structural audit of function-sized
regions, not a runtime optimization or a new test build.

## Size of the problem

The retained 7161 Observatory capture has 43.59 seconds of game-thread CPU time
in 45.90 seconds. Run self time is 6.77 seconds and dispatcher self time is 3.19
seconds: together about 22.8% of that thread. Inclusive times must not be added
to these self times. Starting at 40 FPS, a simplified fixed-work, CPU-limited
model needs a one-third reduction in critical-path time for 60 FPS. Eliminating
all of those two overheads would only give about 52 FPS in that model. This is
a sizing calculation, not a performance prediction; overlap, thermals and GPU
dependencies also matter. Slower hardware needs still more headroom.

The translated bodies therefore deserve architectural work alongside dispatch.
The earlier 4096/1024/256 chunk experiment, entry-suffix splitting, local state
cleanup and direct-call experiments are already documented in PERF.md. This
pass does not rebrand them as new ideas.

## What other recompilers actually change

[XenonRecomp's implementation notes](https://github.com/hedge-dev/XenonRecomp/blob/main/README.md#optimizations)
describe localizing registers using function/ABI assumptions, removing guest
save/restore work, and reducing Unleashed's executable size and frame time.
Those assumptions are the essential difference from splitting a large switch:
our exact interior entries, timing yields and exception paths expose guest state
at boundaries that a native function normally hides. Its Xbox-specific exception
and ABI assumptions cannot simply become Wii defaults.

[QEMU's helper contracts](https://www.qemu.org/docs/master/devel/tcg-ops.html#helpers)
explicitly distinguish helpers that read CPU globals, write them, or have side
effects. That is relevant to retaining values across calls. Our existing LLVM
backend already synchronizes particular FP slots for exact FP helpers and
materializes state for external memory callbacks; merely adding another local
dead-store pass does not establish a new opportunity.

## Executed audit

`scripts/audit-native-leaf-regions.py` reads real DolRecomp annotations across
chunk boundaries and validates corresponding entry labels. It starts at direct
call targets, walks ordinary operations and conditional/direct branches, and
rejects cycles, unresolved/indirect/system operations, other function entries,
external interior branches/fallthrough and excessive region size. A second
pass permits direct calls and computes a least fixed point of fully resolved,
nonrecursive call regions. It does not rely on Galaxy names or regional symbol
addresses, so the tool can run on another game's emitted chunks.

Results on 1,322 source files, whose hashes match the earlier region census:

| Structural result | Count |
| --- | ---: |
| Distinct direct-call targets | 23,687 |
| Acyclic leaf candidates | 6,049 |
| Leaf candidates with at least 32 instructions | 42 |
| Unique instruction addresses in leaf candidates | 31,387 |
| Closed direct-call candidates, including leaves | 6,881 |
| Additional nonleaf candidates | 832 |
| Unique instruction addresses in closed candidates | 48,234 |
| Structurally traversable candidates with unresolved/recursive callees | 3,899 |

Private PC inventories and per-input hashes are in
`generated/native-leaf-20260916/audit.json`. Generated game text is not committed.
The denominator of 1,352,112 annotated addresses includes unrecognized/embedded
data; these counts are not dynamic CPU coverage. A tiny frequently executed
region can matter, and a large cold region may not. The opcode whitelist and
512-instruction per-region limit are deliberately conservative, not a complete
function recovery algorithm.

Most importantly, a candidate is **not** proven ABI-safe. The audit does not prove
return-link preservation, pointer aliasing, stack escape, exceptions, indirect
entry absence, helper effects or timing equivalence. The normal arbitrary-entry
path remains necessary. No candidate is selected automatically for emission.

## Implementation decision

Do not mass-convert the 6,049 leaves or run another module rebuild merely from
these counts. The audit establishes concrete candidate inventories, but no
dynamic-cost evidence that leaf-only conversion closes the gap.

The larger experiment worth pursuing is native execution of a hot call region
with explicit resumable state: native locals across known calls, exact state
materialization at observable memory/helper boundaries and timing exits, and
the existing path for arbitrary/interrupted entry. Removing guest stack writes
also requires proving their memory observability or reconstructing them at
exits; local register variables alone do not make that safe. This is a compiler
and runtime contract change, not a compiler flag.

Before a phone build, the first such region must demonstrate different and
cheaper ARM64 code and exact CPU/memory/callback behavior on every exit. Reuse
the captured hot regions to choose it; do not require the owner to replay another
comparison route just to select an experiment. Broader support for loops and
indirect calls is a subsequent step, not something this audit claims to solve.

## Validation

Eleven regression tests cover branch joins, cycles, missing code, nested calls,
recursion, unresolved callees, cross-chunk traversal, external entry hazards and
annotation integrity. The check is included in the default repository suite.
These are analyzer correctness checks, not native-region execution tests.
The focused tests and full default `bash scripts/check-repository.sh` passed;
the latter's private log is `generated/native-leaf-20260916/repository-checks.log`.
