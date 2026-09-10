# R818: conserved CPU-symbol attribution exposes the next evidence gap

Previous turn made progress by rejecting quiet-loop promotion with executed cost
evidence. This turn reuses the retained R813 plaza sample rather than launching
another unchanged game merely to repeat the FPS observation.

Extended the existing sample parser to report exclusive symbol buckets while
retaining its established ancestry-based groups. Synthetic regressions verify
parent/child subtraction, count conservation and exclusion of the video thread.
generated/plaza-symbol-cost-r818.json contains the full report.

Of 6,004 CPU-thread observations:

| Exclusive symbol bucket | Observations |
| --- | ---: |
| Generated chunks, including their inlined work | 3,496 |
| Run | 698 |
| Hook-routing symbols | 557 |
| Module dispatcher | 242 |
| Out-of-line ppc_ helpers | 231 |
| Remaining symbols, including waits | 780 |

There are 420 sampled generated-chunk symbols. Their top ten account for 844
observations, not most of the CPU thread. The largest chunk has 139 exclusive
observations across the whole CPU tree; R814's 138 was a single dispatch branch,
so these numbers are different scopes rather than contradictory results.

The separate ancestry grouping recognizes 283 wait observations and 41 with
interpreter ancestry. Do not add those groups to the symbol table: they classify
the same observations on another axis. Counts are wall-stack observations, not
running CPU-time percentages, and incomplete/tail-call unwinds remain possible.

## What this does and does not establish

Generated chunks contain most sampled CPU observations, spread across hundreds
of chunks. The 231 out-of-line helper observations cannot measure total helper
cost because inlined helper work is inside the chunk bucket. The collapsed sample
lists offsets such as `112,113132,...` without individual weights. Assigning the
whole chunk count to either displayed instruction would be invalid. Therefore
this artifact cannot establish arithmetic versus state traffic versus branching
as the next dominant emitted-code mechanism.

Rechecked ModManager::Dispatch source: runtime-start callbacks and dynamic pending
returns precede its existing static-range guard. IsHostCallAddress/HandlesAddress
also retain dynamic behavior. The hook bucket does not authorize bypassing these
semantics or resurrecting prior stale-cache/direct-call work.

## Concrete next experiment

One fresh CPU Profiler capture of the unchanged baseline at the visually verified
neutral starting plaza, using the same sole Simulator and saved route. CPU Profiler
is present in the current xctrace template listing; capture permission/counter
availability is not yet demonstrated by that listing. No rebuild is needed.
Capture should retain per-PC cycle weights and exact binary identity/load bases,
not another collapsed sample or entry-count census. Separate profiling from
profiler-free frame-rate measurements; this run answers attribution, not speed.

The existing xctrace summary previously retained per-PC sample counts but dropped
their cycle weights. It now preserves both, with reference/zero-weight/range/
thread-filter tests passing. This prepares a source/disassembly join without
equating sample hits to cycles or guessing omitted PCs. If CPU Profiler cannot
capture this target, record the specific limitation and use an available uncollapsed
profiling source rather than claiming that the collapsed data answers the question.

No runtime, Simulator, app, module, save or disc changed. Full original PRD,
SunPad UI, performance/audio, stability, progression and physical-device gates
remain active. No game-speed improvement is claimed.
