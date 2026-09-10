# R803: callback/alias coverage passes; fallback cost limits promotion

R802 was progress: a whole arithmetic island beat the original fixed-input
routine. This turn expands correctness and measures both accepted and rejected
workloads before any product integration.

## Context verification

Added tests/cross-island-context-checks.inc to the private full-chunk driver.
Each independently linked library exposes a test-only journal setter, ensuring
the callback is installed in that library, not merely in the driver executable.

12,000 cases cover all15 entry offsets, four rounding modes, output/input RAM
overlap, CPUState's FPR array as RAM, external read/write callbacks, and store
journals. Callbacks mutate FP/GPR state, FPSCR, cycles and RAM mapping. Both halves
reuse the same CPUState address, avoiding pointer normalization. Complete final
CPUState, both RAM buffers, host exception flags, callback counts and an ordered
observation digest match.26,800 callbacks are observed. The digest is not an
exhaustive byte-for-byte callback-state trace.

The earlier7,680 all-suffix/RN/NI/unavailable-FPU comparisons also pass. Additional
four workloads each verify64 complete-routine CPU/output/host-flag results before
timing: varied ordinary inputs, smaller finite inputs, large rejected inputs,
and deliberately constructed midpoint ties. No live game or Simulator required.

Initial86634 failed because new driver code preceded needed C headers; fixed
the include placement.3269 and84678 then passed. No product defect inferred
from that private harness compile failure.

## Rejection contract and final results

The first expanded cost screen showed significant rejection/tie overhead. The
candidate now returns bool from cross_island_try: rejected attempts preserve
CPUState/FPSR and fall through to the original generated instructions. Successful
attempts alone skip the original region. This avoids depending on a duplicate
fallback helper body in the integration, but did NOT eliminate the measured
fallback penalty. Do not describe that rewrite as a speed fix.

Standalone tests now explicitly compare CPUState/FPSR before and after every
false return, before executing the original fallback.262,144 cases pass, with
24,129 successful fast paths and128 tie rejections. ASan/UBSan apply here.

Final66614exit0: full-chunk context/suffix/workload tests pass. ABBA timing means,
including identical input copying and state resets in both variants:

| Workload | Reference ns/call | Candidate ns/call | Result |
| --- | ---: | ---: | --- |
|Varied ordinary inputs|42.969|34.356|about20% less CPU time|
|Small finite inputs|43.140|34.310|about20% less CPU time|
|Rejected large inputs|44.603|52.902|about19% more CPU time|
|Forced midpoint ties|43.439|56.169|about29% more CPU time|

Ordinary instructions decline about879→799; rejected/forced-tie paths increase
about899→1149 and891→1284. The changed chunk still has no matching PGO data;
original compilation policy is retained, not identical profile application.
These are workload-specific routine measurements, not game-wide effects.

Evidence: generated/cross-fallthrough-r803.log/.err,
generated/cross-island-rejection-r803.log/.err. Earlier expanded candidate
results remain in cross-context-r803-final.log/.err for comparison.

## Next gate

Do not promote based on the accepted-input benchmark alone, and do not keep
tuning the same guard speculatively. Measure actual scene eligibility/rejection
mix with a private diagnostic candidate and bounded counters before judging
expected net benefit. Existing retained entry counts do not contain operand
values, so cannot answer that question. Then compare uninstrumented baseline
and candidate scene CPU/FPS under the same conditions. Preserve normal selection,
save data, one-Simulator limit and full PRD/SunPad/audio/stability/device scope.

No app/module selected or modified, no Simulator launched, no FPS gain claimed.
