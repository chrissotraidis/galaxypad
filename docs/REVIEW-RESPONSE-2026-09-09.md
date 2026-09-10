# Performance review response and execution reset — R711

## Measured follow-through — R739

The review is recorded and the active goal loop was reoriented, not reduced.
R734–R736 guarded-call AB/BA trials failed to establish reproducible material
benefit; the first5.66% CPU/VI gain reversed and instructions/VI rose in both
pairs. This design is closed for promotion, with host/focus limitations retained
in DIRECT-CALL-EXPERIMENT.md. Production binding remains disabled.
R737–R739 shared-state screening found prior deferrals already implemented,
only one additional conservative integer-gap region, and no instruction-count
reduction from a conversion mode hint. Linked ps_add already inlines helpers.
These narrow variants are parked, not reported as frame-rate improvements.
Next require a materially broader shared-state reduction or advance to the
review's bounded mobile fallback-PC identification; do not resume tiny tweaks.

Chris requested that the independent review be recorded and the goal loop
reoriented if its conclusions track. The full submitted review is preserved in
INDEPENDENT-PERFORMANCE-REVIEW-2026-09-09.md. Original G0–G15, SunPad fidelity,
story completion, audio, no-JIT mobile and physical-device gates remain intact.

## Adopt

- **Architectural execution cost is the primary workstream.** R463 retained
  measurements show about3.81x process instructions/VI for AOT versus reference
  JIT. R425 accuracy-enabled reference still had substantial CPU headroom. These
  are historical, qualified comparisons, but justify a larger hypothesis than
  another sub-5-percent routine or hash-lookup change.
- **Guarded cross-chunk call/return is the first lever to evaluate.** The actual
  emitter already contains a direct-call prototype. Treat the old rejection as
  a correctness objection to that implementation, not proof that an appropriately
  guarded implementation cannot improve performance.
- **Flat chunk profiles do not imply no optimization opportunity.** Shared
  dispatch, entry and state-materialization work can be expensive without a
  single semantic routine dominating. Stop using that observation as a reason
  to default to small native-routine replacements.
- One architectural lever at a time. Primary comparison metrics: CPU-thread
  time/VI, process instructions/VI and native dispatches/VI from matched windows.
  Retain wall cadence, visual scene checks and host-pressure context; none of
  these metrics alone proves correct gameplay. Validate on the macOS diagnostic
  runner before another mobile module build, then revalidate on mobile.
- Stop repeated unchanged plaza stack sampling, mod-lookup microbenchmarks and
  opening-movie loops. Park further undo-buffer work after recording its current
  state; that memory change is not the explanation for pre-checkpoint slowdown.

## Corrections and unresolved claims

- Current selected generated directory has **1322 chunk C files**, not331.
  The review's150499/14721 branch counts have not been reproduced against its
  exact source identity and should not be treated as current-module counts.
- R700 shutdown326315957678 charged cycles/23268793341 native dispatches =
  **14.0237593 charged cycles/dispatch**. This supports frequent dispatch, but is
  a mixed whole-run ratio. It does not independently prove dispatches per frame
  or justify scaling by729MHz; use matched VI and dispatch-counter deltas.
- Recomputing exclusive weights in R705's CPU stack tree yields428 total,
  including49 wait samples. Named groups: Run42, chassis19, ModDispatch15,
  HandlesAddress5, IsHostCallAddress5, state-sync3 = **89 self samples**, not140.
  Hook wrappers add other costs; chunk-switch prologues remain unattributed.
  Do not double-count inclusive parents and children, call this exclusive CPU
  time, or claim an established one-third lower bound from this wall sample.
- The emitter's direct-call prototype checks recursion depth, calls func_target,
  then resumes if PC equals continuation. It does **not** itself supply mutable
  chunk validation, host hook/replacement interception, or a per-call cycle/
  interrupt check. Existing local-backedge budget logic and depth24 do not prove
  those contracts for all cross-chunk paths. Reject the review's assertion that
  the correctness risks cannot affect the measurement run. Keep the production
  unsafe-direct-call refusal in place; faster wrong execution is not a win.
- R464's~2753 instructions/call is a synthetic44-instruction fixture INCLUDING
  its driver/checks. R470's load-heavy sample is consistent with state traffic,
  but sampled loads alone do not prove provenance or prevent all register caching.
- JIT defaults are useful comparison policies, not blanket permission to remove
  observable FPSCR/FPRF/NaN behavior. R425 explicitly retained a large gap with
  accuracy options enabled. FP inlining/lazy state is second priority, with named
  observers, exception behavior and an explicit correctness contract.
- Fallback-vector attribution remains a hypothesis. Collect a bounded PC
  histogram before attempting any relocated-code registration. A new systematic
  trace of core residency could help, but repeated failing xctrace attempts are
  not a prerequisite or license for speculative QoS changes.

## First architectural experiment and decision gates

1. Pin the CURRENT generated source/runtime identities and inspect the old
   R424/R463 runner/checkpoint artifacts before reusing them. Reproduce static
   call/return counts over all1322 chunks; count actual dynamic dispatch/VI in
   a matched scene rather than extrapolating whole-run charged cycles.
2. Specify a minimal guarded direct-call boundary. Preserve invalidated/SMC and
   relocated targets, mod hooks and replacements, timebase/downcount and pending
   exceptions, stop/pause, depth exhaustion, early return and interior-entry
   behavior. Check concrete writers and callbacks; no cached mutable assumptions.
3. Implement the isolated diagnostic candidate and focused differential tests.
   Keep normal generated output and installed application selection unchanged.
   No wholesale module build until the guarded path is executable and its
   predicted saving is plausibly material (review suggests15% CPU time/VI).
4. Matched macOS baseline/candidate, same exact scene/settings with warm-up and
   repeated alternating windows. Inspect visual equivalence and all three work
   metrics. Target>=20% CPU/VI reduction; <8% reproducible benefit closes this
   specific design.8–20% requires evidence of useful scaling, not endless tweaks.
   Unexplained correctness failures stop promotion regardless of speed.
5. Only a useful, correctness-qualified result advances to mobile validation.
   If this lever fails, move to shared FP/state-materialization work, then named
   mobile fallback overhead. Do not revert to the previous tiny-target loop.

## Runtime checkpoint when this review arrived

R710 installed/test-booted dd96031a, found its INFO release message was not
forwarded by LogManager's warning/error-only embedder path, and clean-stopped
it at00:31:09 failed0. Changed only that diagnostic to one bounded stderr line;
128 flow cases passed, reverse patch check passed. Final patch0025 hash:
d35867c46664e050bd3184672e5811a544f36781020fe53ea68c8add0b6dcb9e.
Rebuild/provision/app89958 exited0. Installed d34fe13527221e697854c9d873831b14fcfe765d2461f03190bea2461dc661ca;
merged corec004e37e66f9fd0e483521d8669ad8b8d25f9afeca7201ce5e6ee358bd889212.
LivePID75679/session11407, generated/ios-runtime-r710b.log, soleSimulatorDE8E956F.
Bundle482CC8EC-BF78-4AA3-BAB8-75864998F117; dataCDE6EEC7-6C89-46BF-B9FF-0B2301E1E578.
No new candidate checkpoint created/restored yet, so memory-release verification
remains pending. R709 full suite passed before this diagnostic-only correction;
no full-suite rerun claimed afterward. Do not spend another long scene replay
on this small memory optimization. Original old-build/checkpoints retained.
