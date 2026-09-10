# Active execution plan — 2026-09-08

## Current user override — mobile development starts now

Chris explicitly authorized starting iPad/iPhone implementation before macOS
performance acceptance on 2026-09-08. This supersedes the macOS-first scheduling
restriction below, not any correctness or completion criterion. G6–G9 remain
open; no gate is declared passed. Preserve the installed macOS reference and
pause speculative performance experiments. Start iPad Simulator core/app and
SunPad-derived shell/control/menu integration, then iPhone, one Simulator only.
Track Simulator performance separately from physical-device evidence. Neither
is assumed faster, and desktop55–56Hz is not relabelled acceptable. Full PRD,
story/mechanics, audio/persistence/lifecycle, physical and release gates remain.

Immediate action: build the pinned core into generated/build/ios-simulator-core,
then matching AOT Simulator module and native Apple host. Reuse game-neutral
SunPad machinery; exclude Sunshine input, import assumptions and cadence patches.

This is the current execution queue, not a replacement PRD. The complete
`GALAXYPAD-PRD.md` and G0–G15 in `GALAXYPAD-GOAL-LOOP.md` remain the objective.
Chris reaffirmed macOS performance/stability before iPadOS/iOS promotion and the
complete expected SunPad-derived Apple product. No gate is waived by this plan.

## Evidence that changes the approach

- First Grand Star and genuine save/relaunch already work (R60/R61, R363).
  Do not restart feasibility or mistake the unfinished timing gate for lost progress.
- G6 remains the lowest unmet gate: current-artifact timing/audio/stability is
  incomplete. Current installed-product evidence is consolidated in
  `MACOS-ACCEPTANCE.md`.
- Matched late-scene AOT measured about 55 Hz and 16.7 ms CPU versus diagnostic
  JIT about 60 Hz and 6–7 ms CPU (R424–R427). This supports an AOT execution-cost
  problem; it does not explain every reported 20–40 FPS episode or permit JIT
  as the mobile solution.
- LLVM, vector, return-selector and prior dispatcher experiments are parked.
  Recent microbenchmarks did not deliver a repeatable installed-game FPS gain.
  Reopen only with materially new causal evidence, not another compiler setting.
- R462/R463's low-overhead matched-scene windows measured AOT 54.49 Hz and
  263.15 million process instructions/VI versus reference 59.95 Hz and 69.05
  million: about 3.81× work/VI. These are whole-process, single-order measurements
  with different execution contracts, not proof of one offending helper or every
  severe-lag episode. Prioritize attributable AOT work expansion; do not assume
  host weakness or cache stalls explain the deficit. JIT remains diagnostic only.
- R464/R465 identify repeated general floating-point handling as a candidate,
  not a proven dominant bottleneck. No recent diagnostic has improved product FPS.

## Ordered work and promotion gates

1. **Completed: startup-feedback fix (R457); side task closed.**
   R448 passed the packaged-entry path; R455/R456 tested visible elapsed startup,
   cancellation, failure reporting and real-game handoff in an isolated candidate.
   Integrate that frontend delta into reproducible patches, run focused monitoring
   regressions and audit frontend-only packaging with runner/module unchanged.
   This addresses the apparent freeze before the game window, not initialization
   speed or gameplay FPS. Do not repeat the completed entry audit or rebuild AOT
   for this UI change. Preserve separate disposable test profiles and logs.
2. **Resolve the actual macOS performance/audio blocker.** Use a fixed normal-app
   route with quiet-host context and existing timing instrumentation. Separate
   VI/game update, presentation, CPU/GPU/EFB waits and audio production. Compare
   ordinary gameplay, the known slow scene and transitions. A severe-lag capture
   must name the process/settings/artifact and host contention rather than assume
   the machine is responsible. Reuse prior profiles before adding instrumentation.
   Pick one source-supported cause and one semantics-preserving change at a time.
   Promote only a repeatable matched-route improvement with unchanged gameplay,
   pointer depth, timing, audio and save behavior; synthetic gains alone do not count.
3. **Finish macOS acceptance, not just a benchmark.** Close G6 with its complete
   required evidence; then G7 story/final credits and G8 completion/mechanics.
   Close G9 using the reference 60 Hz behavior at 1×, median/p95/p99/worst frame
   intervals, transitions, audio/speaker decision, save recovery, memory/lifecycle
   and the required 60-minute soak. No average-FPS-only pass. Preserve existing
   valid progress evidence and test changed boundaries against the exact candidate.
4. **Promote the accepted AOT core to iPad, then iPhone.** G10 then G11, exactly
   one Simulator at a time and no runtime JIT/code generation. Include controls,
   menu and lifecycle needed for each first-play loop; do not ship a bare viewport
   and postpone essential touch input. Simulator success is not device acceptance.
5. **Complete the expected Apple product and remaining gates.** Finish G12's
   SunPad-derived layout/editor, safe areas, controller handoff, Classic Pointer
   and context-safe Direct Touch, dedicated Spin and non-motion tilt. Implement
   the full three-dot hierarchy: Display, Controls, Audio, Unstable Experiments,
   Game Data & Saves, diagnostics, problem reporting and About/notices. Preserve
   import rollback/save separation, input clearing and lifecycle behavior. Verify
   actual iPad and compact iPhone appearance/interactions against the reference,
   not just compilation. Complete icons/provenance, G13 reproducibility/matrix,
   G14 Chris's exact physical-device acceptance and G15 explicit release approval.

## Anti-drift rules

- End each bounded step with: delivered user-visible change (or none), evidence,
  remaining blocker and one next action. Do not equate tests written with FPS gained.
- Before expensive work, state the causal question, expected decision and stop
  condition. Rejected hypotheses stay parked; unchanged third attempts are prohibited.
- Before building an optimization candidate, establish both semantic safety and
  plausible whole-game impact from retained profiles or a bounded attribution
  check. A large synthetic speedup in a rarely executed path is insufficient.
  Each investigation must end in a candidate decision or a parked hypothesis,
  not an open-ended chain of new diagnostic tools. If scope cannot plausibly
  address the measured frame-time deficit, stop that lane before a module build.
- Run focused checks for the changed layer. Reuse verified builds and evidence;
  full suites are for relevant regressions/session gates, not progress by repetition.
- If a blocker survives a working session, follow the goal loop's unblocking
  ladder and preserve a reproducible defect. Any independent preparation must
  remain within Chris's macOS-first restriction and cannot promote a blocked gate.
- Original input, normal saves, reference source and private artifacts remain
  protected. One game/one Simulator maximum. No publication without authorization.

**Immediate next action (user-directed refinement, 2026-09-08):** finish the
in-progress precision-provenance scope audit with a go/no-go decision. Check
external-entry, callback and conditional-write safety, then relate eligible work
to retained hot-path evidence. Do not add runtime provenance tracking or rebuild
the full module just because a local identity test passes. Proceed to one small
candidate only if correctness and plausible gameplay impact both justify it;
otherwise park this lane and identify the largest remaining attributable AOT
work expansion from existing evidence. The FP-guard, restore-range, data-page
table and other rejected probes remain parked.

**Next delivery milestone:** a reproducible normal macOS candidate with sustained
reference-cadence gameplay, improved tail frame times and stable audio on the
known slow route and ordinary play, with transitions, pointer depth and saves
unchanged. A single 60 FPS screenshot is not acceptance. Follow with the remaining
G6–G9 evidence, then iPad first and iPhone second. Do not substitute another
diagnostic milestone for this product outcome.

**R466 decision:** the precision scope audit is complete; the four-site candidate
is parked for insufficient demonstrated impact. Next audit execution-loop mode
and lookup metadata writers: retained exact-runner assembly attributes1218 CPU
leaves to dispatchability/lookup, shared across chunks. Preserve mutable SMC
verification and per-block timing/exception/stop behavior; no shortcut is approved
by sample counts alone. This supersedes the pending precision action above.

**Mobile appearance is an acceptance requirement:** use the read-only SunPad
reference's actual host, layout/editor and menu behavior, adapted for Galaxy.
Verify rendered iPad and compact iPhone layouts, safe areas, control placement,
editing, pointer interactions and every three-dot action. A compiling app or
bare game viewport does not satisfy the requested mobile product.

**Progress reporting:** report product changes, measured performance improvements,
and acceptance gates separately. The startup candidate improves feedback only;
recent rejected probes have not improved installed-game FPS. Mobile remains held
until the required macOS gates pass, while the full original mobile product scope
remains mandatory. Do not substitute more experiments for a delivery milestone.
