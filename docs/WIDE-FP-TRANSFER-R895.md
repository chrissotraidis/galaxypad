# R895 transfer test closes broad direct-memory rollout

R894 implemented one guarded routine and measured a limited local gain. This
turn extends the same memory-only transformation to two complete containing
routines, without changing their arithmetic or using the previously rejected
compact-state/FP helper replacements.

The private generator derives three checked MEM1 spans from the literal memory
accesses and preserves interleaved loads/stores. It accepts only the three named
routine boundaries; no arbitrary code transformation is claimed. Every suffix
retains original fallback. The probe accepts --routine wide|normalize|cross,
extracts exact original suffix charges and parameterizes independent checks.

## Executed

All builds use source-pinned original chunk and strict-FP/O2/ThinLTO/PGO policy,
with previously documented profile warnings. Each cost pair executes one million
calls per half, eight alternating-order pairs, after correctness checks. No game
or Simulator, normal module/app/save mutation, or full repository suite.

| Routine | Complete comparisons | Callback cases | Fast correctness entries | Cost result |
| --- | ---: | ---: | ---: | --- |
|Normalization17 instructions|130560|23040|96|Candidate slower in every pair|
|Cross-product15 instructions|115200|23040|96|No material CPU gain|
|Original wide41 regression|314880|57600|96|Correctness only this turn|

Normalization reference roughly80.5–85.4ns/call versus candidate91.9–98.2ns;
instructions roughly1060–1062 versus1124–1127. Cross reference43.3–44.2ns
versus candidate43.4–43.6ns, with approximately863 versus797 instructions.
All pairs compare complete final CPUState, memory and raw FPSR. Cost is a
single finite workload and extracted-entry context, not full-module/game evidence.

Handles85445,85308,64239 exit0. Artifacts:
generated/wide-fp-{normalize,cross,regression}-r895 plus corresponding logs.
The normalization/cross changes test memory prevalidation, not a renewed proposal
to approximate their arithmetic or resurrect rejected scalar/compact designs.

## Decision and next action

Close broad rollout of this design. Its modest wide-routine improvement does
not transfer reliably to these more frequently reached routines. Do not perform
another guard tweak, module build or iPad A/B for it. Retain private code and
oracles for regression evidence; no shipping selection changed.

Next inspect measured CPU/GPU synchronization waits at the actual source boundary:
FramebufferManager::PeekEFBDepth/PopulateEFBCache and Metal::StagingTexture::Flush.
R890 EFB elapsed mean1.727ms contributes to the frame budget, but is not all of
the gameplay deficit. Require a concrete unnecessary synchronization or submission
cost before editing; do not disable EFB access, accept stale depth, or repeat
already closed duplicate-peek suppression. If no such cost exists, record that
source result rather than blindly changing renderer policy. Full PRD remains.
