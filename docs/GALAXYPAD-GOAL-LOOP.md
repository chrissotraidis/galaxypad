# GalaxyPad goal-based loop

Operating loop for the autonomous build of GalaxyPad. The requirements live in `docs/GALAXYPAD-PRD.md`; this document is how you run. Written 4 Sep 2026.

## Active user priority — R838 complete app experience

R911: prioritize a useful physical-iPad baseline when hardware/signing becomes
available; Simulator-only results cannot establish device performance. See
PHYSICAL-IPAD-FIRST-TEST.md. No connected device or valid signing identity on
latest check. Full PRD remains unchanged; UI is exploratory-test quality only.
R910 private module built and ran; R911 confirms actual guarded-path use but
its timing capture is invalid because SIGTERM did not export VI/work CSVs.
Never repeat that termination method for measurement: native menu Stop, verify
exported files and coverage, then terminate/restore/shutdown. No gain claimed.

R909–R910 whole normalization vector candidate passes261120 full-routine cases
and expanded known-result/rejection fixtures. Complete-routine ordinary inputs
improve~40–44% in NI0/NI1; rejected large/zero inputs regress. Private Simulator
module build34260 exited0; R911 staged and restored the private test host.
See NORMALIZATION-VECTOR-R910.md. No current FPS gain or lasting app change;
avoid returning to another round of isolated scalar opcode work.

R908 audits prior vector work before another implementation. Add/sub helper
R432 and cross-product R813 already failed scene benefit; do not repeat them.
Next bounded candidate is whole9-op normalization with guarded resident paired
vectors and exact reciprocal/scalar semantics, not scratch-state inlining or
more scalar-emitter coverage. VECTOR-REORIENTATION-R908.md records8 live input
lanes, rounding/observer hazards and complete-routine cost requirements. No FPS
gain, app change, or new performance measurement in this audit.

R907 reaches the13-op resident arithmetic cost gate and rejects the scalar
variant. Fixed/random/halfway whole-routine correctness passes, but both8-pair
cost runs are slower. Removing per-op scratch saves lowers instructions below
control without fixing latency. See RESIDENT-LONG-COST-R907.md. No app build.
Next materially different arithmetic execution (reference paired-vector path),
after auditing existing vector/precision experiments; no further scalar opcode
coverage or frame tuning on this variant. Full PRD and iPad performance remain.

R906 adds resident paired fused arithmetic with reference halfway correction,
NaN/exception handling, and non-NaN result negation. Actual four-op arithmetic
region passes fixed/random/explicit-halfway whole-routine tests, each629760
comparisons. See RESIDENT-FMA-R906.md. Next lane-selected/scalar/sum forms for
the longer64E0–6510 span, then complete-routine cost. No app or FPS gain yet.

R905 adds direct resident paired multiplication with exact rounding/status
behavior. Fixed and randomized-operand/FPSCR whole-routine tests each pass629760
cases. A raw underflow-flag mismatch was traced to the actual helper's
unconditional conversion and fixed, not masked. See RESIDENT-MULTIPLY-R905.md.
Next fused arithmetic/scalar/sum lowering for the long arithmetic span, then
whole-routine cost. Five-op integration is not a performance win or app candidate.

R904 integrates four real DOL paired merges into an otherwise original whole
chunk via build-time ARM64 suffix functions. Original dispatch charges and
FP-unavailable entry behavior remain; complete selected-routine comparisons
pass629760 cases. See RESIDENT-REGION-ENTRY-R904.md. Next substantial resident
arithmetic region, then complete-routine cost and only then same-scene iPad
measurement. No tiny-fragment benchmark, app promotion, or new FPS claim.

R903 completes paired-merge record-bit value/CR1 lowering in the private cache
prototype; intermediate non-record full-state checkpoint prevents hidden CR
regressions. Combined/plain/conversion tests each100k pass. See
PAIRED-MERGE-CR1-R903.md. Next explicit guest entry/availability/PC/cycle handling,
then broader resident arithmetic and whole-routine cost. No app/backend promotion
or FPS improvement; all original PRD requirements remain required.

R902 extends the private offline FPR-cache path with exact non-record paired
merge decoding/value lowering; resident source capture handles aliases/spills.
100k full-state/status comparisons pass in combined/plain/regression modes.
See RESIDENT-PAIRED-MERGES-R902.md. Next guest entry/availability/cycle boundaries
and broader arithmetic with resident values, then complete-routine actual-policy
cost. No transport microbenchmark or product/backend promotion; no FPS gain.

R901 whole-chunk guard-relocation cost gate failed: selected wide routine still
passes629760 correctness cases, but candidate executes~3% more instructions and
is slower in all8pairs; smaller code and changed PGO applicability do not prove
game benefit. See FP-GUARD-COST-R901.md. Close this rollout, no module build or
per-helper follow-on tuning. Next materially different shared execution/data-
lifetime mechanism from existing R899 evidence, not another baseline capture.

R900 implements private FP guard-chain relocation with original external-entry
guards/cycle charges and unchanged arithmetic/status. Wide629760 full-state
comparisons pass including lazy mode both ways. See FP-GUARD-CHAINS-R900.md.
Next actual-policy WHOLE-CHUNK control/candidate correctness and cost, retaining
normal dispatch; no extracted-routine speedup claim or module build yet.
Platform comparison also finds identical opcode sequences/counts across577
sampled native/Simulator chunks. No new FPS gain; full product goal remains.

R899 heavy native instruction capture completed and mapped:577 chunks,27,445
CPU observations, loads52.44% of generated sampled weights. See
HEAVY-NATIVE-PROFILE-R899.md for identities, trace, timing contamination and
non-identical iPad scene limits. Runtime cleanly stopped/save unchanged.
Heavy-scene attribution is available: next shared-code implementation hypothesis
from this disassembly, not another baseline/profile or closed small-routine lane.
No new FPS gain or physical-device/gameplay acceptance.

R898 reconciles retained invaded-plaza wall sample with starting-plaza weighted
profile; see PERFORMANCE-SCOPE-R898.md. Cost is broad, and recent tiny-routine
screens cannot establish a material whole-game gain. Next one source-matched
native invaded-plaza instruction profile using the known working attach path:
identify which shared-code mechanism grows after the movie, then implement and
test it on iPad. No unchanged Simulator profiler retries, new sampler framework,
movie throughput replay, or another narrow guarded-memory variant.

R897 same-process iPad transition captured completely: movie59.88VI/s, invaded
plaza37.15VI/s with23.42ms CPU/VI and178.58M instructions/VI;74audio underruns in
interior21.5s gameplay interval. See POSTMOVIE-IPAD-R897.md. This is heavier than
R890 quiet plaza, not a cutscene-decoder failure or new FPS gain. Next material
whole-workload CPU reduction informed by retained profile coverage; no repeated
movie counters, tiny-routine tuning, or speculative depth-wait removal.

R896 readback audit reconciled with prior R595–604: no justified wait removal;
actual-method staging control-flow regression passes ASan/UBSan. Preserve depth.
Next actual heavier post-movie iPad gameplay: R890 neutral pre-invasion56VI/s is
not R791 invaded-plaza31.95VI/s. Reuse existing larger recorder/output telemetry
across that transition, separating workload growth from slower same-work execution.
No new recorder architecture, neutral-title loop or speculative wait rewrite.
Original full PRD and shippable iPad experience remain required.

R895 transfer tests complete: normalization regresses and cross has negligible
CPU gain. Wide correctness still passes. Close broad direct-memory rollout;
no more guard tuning/module builds for it. See WIDE-FP-TRANSFER-R895.md.
Next source-audit CPU/GPU synchronization at EFB cache population/Metal staging
Flush for a concrete removable submission/wait cost, preserving current depth
semantics. No stale-depth workaround or repeated duplicate-peek experiment.
Full PRD and iPad gameplay/cutscene acceptance remain required; no new FPS gain.

R894 private guarded direct-memory routine passes314880 comparisons. Initial
whole-routine cost shows~15% fewer instructions but only5–7% CPU improvement;
not whole-game gain. See WIDE-FP-CANDIDATE-R894.md for final-guard timing caveat.
Next test transferability to different representative whole routines, preserving
callbacks/aliases/arithmetic and actual-policy cost. Do not tune this small
single-routine win or build a full module without material aggregate evidence.

R893 complete41-instruction original-chunk oracle passes314880 comparisons,
including aliases, quantization, callbacks and independent cycle/exception checks.
See WIDE-FP-ORACLE-R893.md. Next implement private guarded normal-RAM candidate
against this oracle, then inspect/measure whole-routine code under actual policy.
No candidate/FPS gain yet; no additional baseline/census/module build justified.

R892 memory-inclusive source query/tests complete; selected larger41-instruction
804B64A4–6544 routine for explicit observer-preserving oracle/fast-path contract.
See FP-MEMORY-SPANS-R892.md. Next implement that complete routine boundary, not
another census, compact-normalization variant or unchanged gameplay capture.
No module build before material actual-policy cost evidence; no FPS gain yet.

R891 correction after reading actual R791 evidence: native movie callback delivery
already passed; post-movie starvation coincided with sustained slow gameplay.
Do not invent a separate decoder audio bug, enlarge buffers or replay that movie
for the same throughput proof. Perceptual sync/device/promotion gates stay open.
R890 platform comparison is now complete enough to resume CPU implementation:
evaluate broader whole-routine register retention, not the rejected compact
normalization/state-copy, restrict, lookup snapshot or guarded direct-call designs.
Require a concrete observer/entry/cycle contract and material containing-routine
cost reduction before module integration. No speed gain claimed by this audit.

R890 actual iPad matching plaza baseline completes:56.114VI/s,15.660ms CPU/VI,
139.705M thread instructions/VI,98.38% P-core time, zero swap in full host bracket.
No historical6–22FPS reproduction or new code speedup. See
IPAD-PERFORMANCE-RESULT-R890.md. Stop unchanged baseline/recorder-build loops.
Next implementation lanes: material correctness-qualified CPU instruction
reduction (honor closed shared-state/FP designs), and existing native-THP movie
candidate's unresolved audio/transition gate. Accept changes on repeated iPad
gameplay/cutscene windows and sustained routes, not macOS-only or counters alone.
Full original PRD and product finish requirements remain unchanged.

R889 completes native CPU-thread comparison (THREAD-WORK-NATIVE-RESULT-R889.md).
Similar instruction work, slower Simulator CPU execution; native itself drops
60→32VI/s with stable work late in the capture. No optimization gain established.
User explicitly prioritizes iPad Simulator. Next capture synchronized iPad
thread/VI and host-pressure data during actual slowdown, select one material
intervention, then matched baseline/candidate gameplay AND cutscene verification.
No more control-only or unchanged title-check loops as performance progress.
Original full PRD, SunPad fidelity, audio/device/package gates remain intact.

R888 private paired recorder capacity65536 built/tested; product default intact.
Next run R889 native neutral-plaza measurement with working background-input
route and unchanged module. Require complete coverage; do not rebuild again or
claim instrumentation as an FPS improvement. Full original PRD remains active.

R887 corrected native runner reaches neutral plaza and completes snapshots, but
paired16384-row recorders filled before the requested window. Completeness check
rejects it; no result accepted. Next increase bounded private recorder capacity
or arm post-startup, with paired-buffer tests; never relax coverage validation.
Reuse working background-input route, not another unchanged-capacity attempt.

R886 isolated native counter candidate r886c now includes tested default-off
--background-input; control/source/object scope checks and signature pass.
Next launch this candidate with the option and fresh recorder outputs for the
pending R836 native thread-work comparison. No repeat build needed; no speed
gain established. Original PRD/product/physical/audio requirements unchanged.

R885 returns to unresolved native-versus-Simulator CPU-thread work comparison.
File-only BackgroundInput change is invalid: RuntimeConfig overwrites it; existing
counter runner lacks the isolated tested --background-input patch. Native attempt
stopped cleanly, no valid comparison. Next integrate that option into isolated
counter runner with control/scope proof, then capture once. No repeated unchanged
navigation or new module build. UI/full PRD/device/audio objectives remain intact.

R884 physical-iOS Release host rebuilt and privately staged with unchanged
device module. Current UI changes compile for IOS16+, not just Simulator.
No device connected, no signed hardware/runtime acceptance. Next Back/story
layout and bounded performance work; retain full PRD, not another unchanged build.

R883 packaged B activation returns existing file panel to planets with scripted
input released. Causal button response proven, not full accessibility/Plus proof.
Next current physical-iOS host compilation/integration (older device candidate
lacks recent changes), then remaining Back/story layout and performance work.
Do not repeat file/title checks without a new decision. Full PRD remains intact.

R881 adds explicit accessibility button pulses, isolated from physical-held
input, with reset/menu cancellation. Focused UIKit tests and host build pass;
not installed or causal proof of R880 Plus behavior. Next check actual activation
before claiming input acceptance; do not remap the valid Plus binding speculatively.

R880 actual phone confirmation/plaza visual check passes for new Plus placement;
save unchanged/clean stop. AX Plus activation produced no visible game pause,
so input behavior remains open: inspect activation vs mapping vs phase before
claiming a fix. Movement stick still overlaps Back/story; those remain next
layout targets. No repeat file-opening loop solely to re-prove Plus geometry.

R879 phone pause candidate moves inward beside actions (.72,.62), preserving
custom layouts/iPad. Lower-right proposal was rejected because it reintroduced
R848 save-Yes overlap. Focused exclusion/min-target tests and host build pass.
Next actual phone gameplay/confirmation visual verification, not position-only
acceptance; other Back/story/button/HUD overlaps remain open.

R878 verifies one actual same-process stop/restart pair: clean idle screen,
explicit Restart, fresh renderer/module initialization in same PID and two clean
stops, save unchanged. Not gameplay-input or audio acceptance. Return next to
known phone HUD/control overlaps and an actual gameplay action rather than
repeating this startup pair. Preserve performance and full original PRD gates.

R877 implements idle gameplay visibility and guarded Restart Game; Release build
and isolated overlay regressions pass. Next actual packaged same-process
stop/restart test is required: idle menu access, no idle game controls, clear
restart affordance, fresh rendering/input after restart, clean stop/save retention.
Do not treat isolated UI tests as runtime reuse proof. Full PRD remains open.

R876 actual packaged Audio menu/stop/relaunch pass completed: mute and50% persist,
unmute preserves50%, runtime config reflects both, clean exits/save unchanged.
Not audible gain or physical/audio acceptance. Next concrete UX defect is the
stopped screen: hide inapplicable gameplay controls and offer explicit Restart,
with startup guarding and continued menu/data access. Do not repeat the same
Audio startup solely to prove stored values again. Output gain remains open.

R875 queue refresh: main-volume/mute settings and native Audio menu now compile
and pass isolated UIKit regressions. Next stage this host with the unchanged
accepted module and verify actual menu operation, mute/unmute, pause/resume and
stop/relaunch retention on one Simulator. Do not infer audible gain from the
R874 parameter probe or these UI tests. Separate Wii Remote speaker gain remains
open. Then return to phone layout overlap and gameplay/performance acceptance;
avoid repeating title navigation, tilt-consumer audits or counters without a
specific new decision. Icon/README assets exist, not full release acceptance.

R862 queue refresh: R861 verified packaged iPhone import/save recovery through
plaza movement; do not repeat the opening by default. Next close discoverability
and actual gameplay control gaps: concise in-menu touch guidance, followed by
unverified pointer/action or motion-alternative gameplay and lifecycle checks.
Keep the known phone HUD/control overlaps open. Icon assets and README exist,
but neither implies full branding, packaging, physical-device or release acceptance.
No measured performance improvement is claimed by the recent product passes.

R847 corrects the R846 detour: fallback counts are also present in R841/R844
iPad runs, and PERF R489/R553 plus JOURNAL R755/R758 already describe the counter
semantics and phase-specific vector census. They are not evidence of a new iPhone
regression or an interpreter time budget. Do not repeat that census by default.
Next extend the clean iPhone product run beyond startup into title/file creation
and gameplay, checking actual control/HUD placement and lifecycle. Keep its saves
separate. Native-only and performance acceptance remain unproven; preserve the
complete product queue below.

Chris explicitly requests continued app-experience optimization, refined controls
and a sensible shippable touch menu, an original GalaxyPad iPadOS/iOS app icon,
and README parity with SunPad. This supersedes earlier performance-only queue
ordering, not the original PRD/G0–G15 acceptance requirements or release gates.

1. Native thread-work navigation attempts are stopped; no valid comparison was
   captured. Park this lane while advancing the user-facing work below. Do not
   expand profiling tooling as the default queue.
2. Refine controls and the three-dot menu against the actual original SunPad
   implementation and Galaxy's actions. Keep primary controls ergonomic, avoid
   action-word text crammed into buttons and persistent rarely used controls.
   Verify mappings, simultaneous touches, pointer/Spin, safe areas, editing/reset,
   menu pause/resume and input clearing on one Simulator at a time. Inspect before
   changing; preserve working wiring and test each changed interaction.
3. Create original GalaxyPad icon artwork and complete iPhone/iPad AppIcon assets,
   with provenance and small-size/masked visual checks. No Nintendo artwork,
   characters, extracted textures or copied SunPad branding. Retain editable
   project-owned source and satisfy the PRD's macOS branding requirement too.
4. Bring README structure and usability to SunPad parity: accurate overview,
   screenshots when available, supported game/platform boundaries, prerequisites,
   reproducible setup/build/run, controls/menu documentation, troubleshooting,
   credits/notices and honest known limitations. Do not copy unsupported claims,
   declare releases available, or publish private/game-derived artifacts.
5. Continue performance changes with falsifiable, bounded comparisons and visible
   gameplay/audio evidence. Product/UI/icon/documentation work no longer waits
   for every performance uncertainty to be resolved. No benchmark-only completion.

Each continuation should advance a concrete user-facing deliverable or close a
specific runtime defect/evidence gap. Record what changed and what was actually
verified. All story/save/lifecycle/audio/stability/device/packaging requirements
remain; shippable is an acceptance standard, not authorization to publish.

## Active priority adjustment — R824 generated state lifetime

R836 completes the actual Simulator CPU-thread window:49.379VI/s,17.941ms CPU/VI,
140.437M thread instructions/VI,98.33% Performance-core CPU time. No dropped
samples or clock-unit mismatch. Do not blame E-core dominance for this run or
call its difference from R831 a speed fix. Next isolated native host-only recorder
counterpart, with verified control identity and unchanged guest module, to compare
same-thread work versus execution time. See THREAD-WORK-RESULT-R836.md. No repeat
Simulator capture, QoS tuning or original PRD scope reduction is warranted.

R832 standalone self-thread counter probe passes on native and Simulator with
verified Mach clock conversion. Next private opt-in VI-recorder integration and
injected-counter tests before a host-only diagnostic build, reusing unchanged
guest modules. Keep private SPI out of ordinary release targets. Measure actual
CPU-thread work/core-class time; standalone probe placement is not game evidence.
See THREAD-COUNTER-PROBE-R832.md. All original product requirements remain.

R831 completes the R830/R831 neutral-plaza platform comparison: Simulator CPU
time is2.07x native with only2.83% more whole-process instructions/VI. This is
not guest-thread or frequency attribution. Next qualify a bounded self-thread
counter probe and its clock units before another app build; preserve denied
profiling boundaries and do not repeat unchanged attaches or QoS tuning. See
PLAZA-PLATFORM-RESULT-R831.md. No speed fix or product gate is claimed; full
original PRD/SunPad/gameplay/audio/stability/device objective remains unchanged.

R828 supersedes the compact-normalization continuation: full audit retains96
host-flag failures; a separately qualified finite workload is~27% slower with
~7% more instructions. Park this design without further tuning or game build.
Next reconcile retained macOS/Simulator per-frame work, settings and host-version
differences before selecting another generated arithmetic target. See
NORMALIZATION-DISPOSITION-R828.md. Full original product requirements remain.

R827 compact FP closure passes isolated oracle and reduces scratch, but the
actual-policy whole-chunk routine fails host flags before timing. Investigate
the retained exact failing case; do not mask flags or promote from isolated
success. No game rebuild until correctness and cost gates pass. See
COMPACT-NORMALIZATION-R827.md. Full original requirements remain unchanged.

R826 establishes a real normalization-region oracle: all9suffixes and state/FP
flags pass in sanitized and ThinLTO modes. A local full-CPUState copy still has
a large stack frame; it is a correctness scaffold, not a speed candidate.
Evaluate compact FP-state/helper dataflow against this oracle before a cost
gate or game build. See NORMALIZATION-STATE-R826.md. Do not keep copying full
CPUState or tuning attributes; all original requirements remain unchanged.

R825 closes a simple CPUState restrict annotation: three whole-chunk private
ThinLTO pairs have identical instruction encodings. No timing run or app rebuild
is warranted for that design. Explicit state-lifetime changes remain distinct;
do not replace them with another alias/inline attribute. See
STATE-ALIAS-CODEGEN-R825.md for the verified compile-only boundary.

R822 supplied an actual macOS plaza per-PC profile; R823/R824 resolve opcode
weights and conservative local load origins. Next inspect whole-chunk optimized
state lifetimes and prototype only a substantive reduction that is not already
performed by LLVM or equivalent to rejected mapping-cache designs. Preserve
callback observations, aliases, exceptions, interior entries and cycle accounting.
Require full-state differential and actual-policy whole-chunk cost gates before
another app build, then matched gameplay A/B before promotion. Do not build a
general provenance analyzer or repeat unchanged profiles. See
PLAZA-LOAD-ORIGINS-R824.md. Original full PRD/SunPad/device requirements remain.

## Active priority adjustment — R815 shared native-loop cost gate

R817 supersedes the pending cost gate: separate-TU extracted-burst measurements
show no material repeatable savings with nontrivial callbacks. Park quiet-loop
specialization; no app rebuild or more tiny flag variants. Return to broad
source-correlated generated-code costs across chunks using retained R813 data,
not entry-frequency-only target selection. RUN-QUIET-COST-R817.md records results
and limitations. All original requirements remain unchanged.

R813 closed the cross-product candidate without repeatable game-speed benefit.
R814 separates thread costs and identifies shared Run self work. R815 audits
optional configuration and passes an extracted native-burst differential with
stub services. Next measure actual-policy whole-burst specialization cost, with
opaque representative callbacks and entry/code-size overhead, before a private
host rebuild. Preserve live SMC, hooks, timing, exceptions and CPU state; no
stale eligibility caches. Park this lane if savings are negligible. See
RUN-QUIET-AUDIT-R815.md. Full original PRD/SunPad/gameplay/audio/stability/device
objective remains unchanged; tests alone do not establish performance.

## Active priority adjustment — R806 actual mode prerequisite

R813 disposition supersedes the R808 next step: sequential plaza measurements
25.93 baseline,26.63/26.01 candidate,27.06 reverse baseline show no repeatable
material gain. Park the cross-product region; no further guard tuning or
expansion from its local benchmark. Fresh post-measurement plaza CPU sample is
retained; classify CPU/GPU stacks separately and map host dispatch/vertex-decode
cost to source before another build. See CROSS-DISPOSITION-R813.md. All original
product requirements remain unchanged.

R808 update: NI-capable diagnostic now passes actual Star Festival plaza
eligibility:99.21695% of999424 calls fast, zero mode rejection. Simulator stopped,
save unchanged. Next distinct uninstrumented candidate and matched sequential
plaza speed comparison, not more eligibility-only runs. Diagnostic FPS remains
poor and is not a performance A/B. See CROSS-SCENE-R808.md. All original goals
below remain in force.

Live title/file-select counters all rejected the old NI guard; observed FPSCR
86004004 has NI1/RN0. Bounded NI-capable source passes local/full-context gates
with retained ordinary-input benefit. Build a distinct diagnostic using verified
unchanged control/objects, then remeasure applicability before uninstrumented
scene A/B. Do not reuse the NI-rejecting R804 binary or infer gameplay gains from
the menu observation. CROSS-LIVE-MODE-R806.md records evidence and save safety.
Full original PRD/SunPad/performance/audio/stability/device goals remain intact.

## Active priority adjustment — R803 measure applicability before promotion

Expanded callback/journal/alias/suffix gates pass. Varied eligible inputs retain
~20% local gain, but large-value rejection and midpoint ties cost~19%/~29% more.
The fallthrough rewrite preserves rejection state but does not remove the cost.
Next use a private bounded diagnostic candidate to measure actual scene
eligibility/rejection mix; retained entry counts have no operand distribution.
Keep instrumentation measurements separate from uninstrumented scene CPU/FPS
A/B. Do not promote or keep tuning guards based only on ideal inputs.
CROSS-CONTEXT-R803.md records evidence. Original PRD and all product gates remain.

## Active priority adjustment — R802 whole FP island benefit

Whole cross-product vector region in the existing C backend passes focused and
actual-routine state gates and reduces local CPU time~19.52%, instructions~10%
under original strict-FP/ThinLTO flags. Candidate profile is unmatched and the
workload is fixed-input: this is not game-wide benefit. CROSS-ISLAND-R802.md
records evidence. Prioritize this simpler existing-backend path over additional
offline compiler expansion. Extend callback/alias/tie/varied-input and rejection
cost coverage before a private module, then bounded scene A/B. Preserve full
original PRD/SunPad/audio/stability/gameplay/device requirements and exact source
identity. No default promotion or completion claim from an isolated routine.

## Active priority adjustment — R798 offline exporter cost screen

The bounded offline integer exporter now links and passes full-state, callback,
RAM and CPU-alias differentials for two real blocks. Direct RAM load emission
does not beat generated C in the isolated mixed-block cost screen. Do not
promote it or tune the same tiny fixture repeatedly. Qualify a larger observed
hot region and its state-observation boundaries; account for helper crossings,
register lifetime and save/restore work before further backend expansion.
Require actual-policy material cost improvement before a broader module build.
ARM64-DIRECT-LOAD-R798.md records results and limitations. Full original PRD,
SunPad, gameplay, movie/audio, stability and physical-device gates remain.

## Active priority adjustment — R793 broader native lowering

Mapping lifetime audit does not justify blanket cache removal across mutable
module/callback boundaries. Current C memory variants retain their prior cost
dispositions. Evaluate a private offline ARM64 complete-block exporter using
reference register allocation/precision dataflow, with static helper relocations
and an explicit state adapter. NATIVE-EXECUTION-R793.md records live-pointer,
GQR-specialization and code-cache dependencies. Prove relocatable linking,
full block state/memory/exception/cycle equivalence, then material actual-policy
cost reduction before broader build. No runtime code generation on mobile.
At R793 this exporter was not implemented; R794–R798 provide a bounded integer
prototype, not a complete backend. Preserve all original PRD/SunPad/device,
movie/audio and stability requirements; no completion claim from an isolated block.

## Active priority adjustment — R791 movie delivery evidence

Private native movie now has matched59.946frame-events/sec and approximately48kHz
nonzero callback delivery with zero new underruns in36.9seconds; complete5591
native frames/0fallback, clean return/stop. Post-movie gameplay31.953events/sec,
104underruns in21.5seconds despite full output callbacks. See MOVIE-AUDIO-R791.md.
This is callback evidence, not perceptual pitch/AV-sync/device acceptance. Keep
native decoder default OFF pending remaining gates; no more unchanged movie
throughput/output-counter replays. Return to material native guest execution
cost with retained instruction-level coverage/exact-policy disassembly before
another candidate build. No tiny helper variants or larger audio buffers to mask
the sustained producer deficit. Full original PRD, SunPad UI, stability and device
requirements are unchanged.

## Active priority adjustment — R788 local arithmetic lane disposition

Instruction-level retained coverage corrected cold target selection. Hot square
has a bounded~7%routine gain; general multiply and shared-load/type variants only
~1.1%/~3.4% with higher instruction work. None proves material game-level gain.
Do not extend those variants with more predicate/attribute tuning or a full build.
Next close a missing timing/audio delivery gate on the substantially faster
private native movie path, first auditing retained logs for the exact evidence
gap. No unchanged opening replay, throughput or pixel checks just to restate
known completion. Gameplay CPU deficit and all original PRD gates remain open;
no default decoder promotion without the required evidence.

## Active priority adjustment — 9 September, R780 precision cost gate

Guarded precision propagation passes full-transform correctness but yields only
about2.8% local CPU benefit with more instructions. This is insufficient for a
full module build or game-speed claim. Close this batch implementation for
promotion; no further attribute/representation variants. Before implementing
broader typed lowering, establish reachable coverage and attributable native
cost using retained profiles/source, then choose a materially larger target.
Run regressions including precision-fact/typed-arithmetic tests. Preserve the
original performance, cutscene/audio, stability, SunPad and device requirements.

## Active priority adjustment — 9 September, R769 actual-policy FP result

Mandatory float-helper inlining fails the whole-chunk ThinLTO/PGO cost screen:
~1.4% fewer instructions, slightly slower CPU time, versus the misleading~16%
standalone result.22,528 fixture comparisons pass but do not justify deployment.
Close blanket inlining and attribute tuning. No full module build is warranted.
This is not proof all FP/state-lifetime changes fail; new work must change the
underlying generated dataflow and demonstrate a material benefit in real build
context, not isolated helper code. Keep the malformed XF stability fault open
and inspect retained origin evidence before any renewed long gameplay run.
Original PRD, SunPad UI, audio, progression and physical-device gates remain.

## Active priority adjustment — 9 September, R764 CPU-time split

Fresh phase-selected Simulator plaza capture gives non-native routing an
estimated2.08% of CPU-thread time (includes fallback AND host-call routing).
Native bursts dominate.14,145 native and3,426 non-native samples, no clock
errors. Raw native estimate101.35% illustrates sampling/clock overhead, not
impossible physical utilization; do not normalize it or claim precise shares.
See RUN-COST-EXPERIMENT.md. This is enough to park the vector acceleration lane,
not a speed improvement or instruction-level native attribution.

Return to material native execution overhead: inspect repeated state/timing
materialization and shared FP work under the original observer/cycle/exception
contracts. Use source/disassembly and retained profile evidence to qualify a
substantial change before a full module build. Do not restart the rejected
dispatch-only vector, direct-call ABBA failure, or tiny lookup variants.
Full original PRD, performance/stability, SunPad UI and physical-device gates
remain unchanged. Default diagnostic clocks remain OFF.

## Active priority adjustment — 9 September, R761 vector cost screen

R762 fresh current-build plaza sample:9 interpreter-ancestry samples out of1695,
but236 Run self samples. This is wall sampling, NOT an exhaustive CPU-cost bound.
Two displayed Run offsets map to AOT dispatch/bookkeeping; collapsed offsets
cannot be apportioned. Deprioritize vector execution; next distinguish AOT
state/timing work from fallback chassis cost, retaining material-benefit gates.

R755/R758 established low-vector fallback-step dominance and exact installed
RAM templates, not CPU-time dominance. R760 recognition and R761 reuse of the
actual interpreter dispatch tables now pass focused tests. The dispatch-only
guarded candidate loses its isolated ABBA cost screen (6.73–7.08ns versus
4.35–4.37ns baseline); do not integrate, rebuild or polish this variant.

Next qualify the WHOLE fallback path's CPU cost in the verified plaza before
designing broader batching/chassis changes. Use a bounded diagnostic with
explicit overhead/phase limits; step counts alone do not establish this cost.
If cost is minor, close this lane and return to measured AOT/shared-state work.
If material, preserve the R759 exception/fetch/budget/observer contracts before
reducing repeated chassis work. No general cached-backend swap or mobile JIT.
The prior Simulator ownership note is superseded by the user's authorization
to switch: shut down the existing Simulator before booting another, no repeated
permission request. Full original PRD and G0–G15 remain unchanged.

## Active priority adjustment — 9 September, R736 measured direct-call disposition

R745 stability interruption: R742 runtime ended after malformed XF command
00611600, with no clean shutdown/census. Analyze the captured FIFO command
boundary before another performance run; do not suppress the assertion. UI
access recovered, but another project's Simulator is booted: preserve it and
the one-Simulator limit. Full performance and original PRD scope remain intact.

R740 next executable diagnostic: identify actual mobile interpreter PCs with a
bounded opt-in census (FALLBACK-PC-EXPERIMENT.md). R737–R739 narrow shared-FP
variants failed scope/code-shape screening; do not keep extending them. Broader
shared-state work remains eligible with a material-benefit case. The census is
attribution, not performance acceptance or authorization to bypass verification.

The first guarded cross-chunk design is closed for promotion after R734–R736
matched-binary AB/BA trials. CPU/VI improvement did not reproduce; process
instructions/VI increased in both pairs. Preserve experimental code/artifacts
but keep binding off in product paths. This is not proof every possible direct
call architecture fails, nor permission to enable the unsafe prototype.

Next major lever: shared floating-point helper/state-materialization overhead.
Use current source and retained profiles to identify repeated work across
instructions, then implement one semantics-preserving shared-path change with
an explicit observer/exception contract and material-benefit gate. Do not reopen
tiny routine/lookup experiments or loosen FPRF/NaN behavior without proof.
Full PRD/G0–G15, SunPad UI, mobile/device, story/audio/stability gates remain.
See DIRECT-CALL-EXPERIMENT.md R736 for measurements and limitations.

## Earlier priority adjustment — 9 September, R711 independent review

Chris supplied an independent performance review and requested reassessment.
Follow `docs/REVIEW-RESPONSE-2026-09-09.md` for its source-checked disposition
and experiment gates. This supersedes the narrow profiling/memory work queue,
not the original PRD or G0–G15 acceptance criteria. The actual PRD filename is
`docs/GALAXYPAD-PRD.md`.

1. Make architectural AOT execution overhead the main performance workstream.
   First evaluate guarded cross-chunk call/return on an isolated macOS diagnostic
   path; do not simply enable the existing unsafe direct-call flag.
2. Use matched CPU time/VI, process instructions/VI and dispatches/VI, retaining
   visual correctness, frame-time and host-pressure checks. Do not infer dynamic
   call rates from static branch counts or whole-run charged-cycle ratios.
3. One major lever at a time, a material predicted benefit before a full module
   build, and explicit success/failure thresholds. Preserve SMC, hook, exception,
   timebase, stop, depth and callback contracts before promotion.
4. Second priority is shared FP/state-materialization work with explicit observed
   semantics; third is identified mobile fallback overhead. JIT comparisons do
   not by themselves authorize silent accuracy reductions.
5. Stop unchanged plaza wall-stack recaptures, small mod lookup tuning, repeated
   movie navigation and further checkpoint-memory iteration as the default loop.
   Current memory candidate is recorded but its live release check is unfinished.

Full SunPad UI/menu/touch fidelity, story completion, stability, audio, packaging
and physical iOS/iPadOS proof remain required. No performance gate is closed by
accepting this review or by passing a synthetic experiment.

## Active priority adjustment — 8 September, R653

Chris explicitly reprioritized frame rate and prerecorded-cutscene performance.
The full G0–G15/PRD scope and acceptance criteria below are unchanged. Performance
now gates resuming the long mobile first-play route; UI polish, touch verification,
and repeated title-to-movie navigation are not the main work queue.

Follow `docs/CUTSCENE-PERFORMANCE-PLAN.md` in this order:

1. Establish exact video cadence and isolate decoder throughput from host stalls.
   Use direct movie frames and a bounded harness rather than navigating the game
   for every experiment. Distinguish source frames, VI, presents and wall time.
2. Investigate a native ARM64 THP decoder at the existing THPVideoDecode boundary,
   preserving the exact supported game's outputs, side effects and player contract.
   Existing generated-code kernel extraction is not a whole native decoder.
3. Fix measured buffering, synchronization and audio-clock bottlenecks, preserving
   guest timing, completion, cancellation and return-to-gameplay semantics.
4. Quantify memory compression/swap and process contention with timed deltas.
   No killing unrelated apps, clearing caches or changing their settings without
   permission. Device/signing access remains a separate physical-proof boundary.
5. Optimize upload/presentation or gameplay EFB only when stage timings identify
   them. No speculative resolution/QoS changes or returning fake/stale depth.

An experiment must change the decision: standalone throughput plus output parity,
then a complete in-game movie with normal duration/audio and correct return.
No more unchanged byte-cache A/B runs; its mobile default is already implemented.
Do not equate that incremental improvement with cutscene/performance acceptance.
Resume broader progression and SunPad UI completion after this blocker is reduced.

## The goal stack

Work the lowest unmet goal. A goal is met only when its required evidence exists in `docs/` under PRD Section 11. Never work a higher goal while a lower goal is broken; a regression reopens the lowest affected goal.

- **G0. Environment, state, and private boundary ready.** Toolchain and free space verified; current git state recorded; `ref/sunpad` and selected upstreams pinned/read with push disabled; `RIGHTS-STATUS.md` says `private-only` or a stronger explicitly approved state; repository safety checks reject game/generated/save/private data; no stray Simulator or game process exists.
- **G1. Exact Galaxy input identified.** Original image preserved; title ID, region, revision, partitions, full-image hashes, `main.dol` hashes, deterministic extracted manifest, and every executable-looking DOL/REL/RSO/blob are recorded. `config/galaxypad-disc.json` represents the exact supported input.
- **G2. Wii/Broadway substrate proven.** DolRecomp setup/title data and `wit` are pinned; the build guard proves Wii/Broadway mode and 64 MiB MEM2; the selected coherent ModernGekko/RecompCore graph initializes the Wii address model; a missing database can no longer silently create a GameCube build.
- **G3. Executable model and AOT module proven.** Exact-DOL C-backend generation completes; SMC and warnings are interpreted; executable inventory and coverage telemetry exist; the ARM64 module compiles/links; every fallback/unknown PC is named; the HOME-menu RSO has a bounded native replacement plan.
- **G4. macOS Wii runtime boots.** GalaxyPad creates a Metal surface; exact disc/module identity matches; IOS/ES/NAND/SYSCONF, MEM1/MEM2, disc, DSP, GX, and WPAD/KPAD initialize; the AOT entry point executes; no unresolved native link or fatal runtime-init failure remains.
- **G5. macOS title and file select work.** Stable video/audio reach the title; mouse/controller pointer works in file select; a new file can be created; pointer/EFB and input breadcrumbs are credible. A title screenshot alone does not satisfy this goal.
- **G6. macOS first Grand Star loop works.** New file → Star Festival/opening → Gateway Galaxy → movement/jump/camera → pointer/Star Bits/Pull or Launch interaction → dedicated Spin when unlocked → first Grand Star → Comet Observatory → save → clean exit/relaunch/load. This is the first hard technical feasibility gate. (PRD D3)
- **G7. Complete macOS story works.** A fresh GalaxyPad save progresses through all required story gates, final Bowser, credits, post-game return, save, and relaunch with no progression, timing, render, input, audio, memory, or save blocker. (PRD D4)
- **G8. Completion mechanics and controls are covered.** Pointer menus and world depth, cannon/sling/bubble, transformations, bosses, comet/Hungry Luma/Green/Trial paths, stick-backed ball/ray/tilt controls, all mandatory shake consumers, Luigi/post-game content, and completion sequence have evidence. Direct Touch and Classic Pointer are both usable. (PRD D5, D7)
- **G9. Correctness, performance, audio, and persistence are stable.** Reference 60 Hz behavior, 1× 640×456-class baseline, EFB/Z readback correctness/cost, MEM2 high-water behavior, DSP/main audio, Wii Remote speaker decision, NAND saves, repeated transitions, and 60-minute soak pass. (PRD D6, D8, D11)
- **G10. iPadOS Simulator first-play loop works.** With every other Simulator shut down, one iPad Simulator runs the same exact AOT identity through G6 with no runtime PowerPC JIT or executable-code generation. Touch, pointer, Spin, save/reload, lifecycle, menu, and diagnostics pass.
- **G11. iPhone Simulator first-play loop works.** The iPad Simulator is shut down first; one iPhone Simulator runs the same exact AOT identity through G6; compact controls, pointer precision, safe areas, menu, lifecycle, and diagnostics pass.
- **G12. SunPad-derived GalaxyPad shell is complete.** Game-neutral Apple host, editable Galaxy controls, controller handoff, three-dot menu, game-data import/reimport/remove, module matching, settings, Direct Touch, diagnostics/privacy, original macOS/iOS/iPadOS icons, and provenance are complete. (PRD D10)
- **G13. Technical matrix and clean clone are green.** PRD matrix rows 1–35 pass against exact artifacts; the regression suite and full macOS/iPad Simulator/iPhone Simulator pipeline reproduce from scripts and pins; no undocumented manual build step remains.
- **G14. Physical candidate accepted.** Chris tests the exact candidate on Apple Silicon Mac, physical iPad, and physical iPhone; artifact hashes, hardware/OS, hands-on pointer/touch/control/audio/performance/save evidence, and open defects are recorded. Simulator results cannot satisfy this goal.
- **G15. Public release explicitly authorized.** Source/package rights, GPL/corresponding-source obligations, generated-module boundary, notices, game-data/privacy audits, icon provenance, candidate hashes, and Chris’s explicit release authorization are recorded. Only then may the authorized source, macOS binary, or IPA action occur.

G6 is the first hard feasibility gate. G7 and G13 are the technical release bar. G14 and G15 are mandatory for any public binary. There is no fallback to a title-screen demo, file-select-only release, Gateway-only release, pointer-with-fake-depth release, macOS-JIT-only release, motion-required mobile release, or “ROM-free therefore cleared” release.

`RIGHTS-STATUS.md = private-only` does not block G1–G13. It blocks publication and G15.

## The loop

Repeat until the current authorized terminal goal is met:

1. **Pick** the lowest unmet goal. Choose the smallest concrete step that can advance it.
2. **Check state before acting.** Read `docs/STATUS.md`, the last `JOURNAL.md` entry, the relevant technical inventory, `git status`, running processes, booted Simulators, disc/DOL/module hashes, dependency pins, selected save/NAND, runtime settings, and verified build caches. Do not rebuild or regenerate what a matching verified cache already holds.
3. **State the hypothesis.** Name what this step is testing and what evidence would support or refute it. “Try things” is not a hypothesis.
4. **Execute** one bounded step. Install public tooling, clone public source, or download official setup data only when required; record source/version/hash/license. Never download game data.
5. **Test immediately.** Run the smallest relevant check when the step completes. Compilation is not launch; launch is not title; title is not file select; file select is not Gateway; Gateway is not a saved/reloaded Grand Star; story credits are not completion-content coverage.
6. **Capture evidence.** Put the screenshot, log excerpt, manifest, profile, hash, or capture under the local dated artifacts path. Append one dated journal entry: goal, hypothesis, step, command, result, evidence path, interpretation, and next step.
7. **Update** `docs/STATUS.md` and the relevant inventory (`DISC-IDENTITY.md`, `EXECUTABLE-COVERAGE.md`, `WII-SUBSYSTEMS.md`, `INPUT-AND-POINTER.md`, `MOTION-AUDIT.md`, `EFB-READBACK.md`, `AUDIO.md`, `SAVE-AND-NAND.md`, `PERF.md`, or `RIGHTS-STATUS.md`) if state changed.
8. **Continue.** If the step failed, enter the unblocking ladder before retrying. A changed hypothesis or variable is required for another attempt.

## Process hygiene — hard rules

- **One Simulator at a time.** Before booting a Simulator, run `xcrun simctl list devices booted`; shut down every booted device, then boot only the intended iPad or iPhone. This is not optional.
- **One game instance at a time.** Before launching on any target, kill every previous GalaxyPad, ModernGekko, Simulator app, runtime, launcher, profiler-attached copy, and stray test harness. Multiple instances corrupt save/NAND/config evidence and create false input/audio/renderer defects.
- **Kill before relaunch, always.** Never layer a new run on a hung, crashed, or half-terminated process.
- **One variable at a time.** During runtime, AOT, fallback, EFB, input, timing, audio, MEM2, and optimization work, change one variable, rerun the same evidence-producing test, and journal the result.
- **Clean up after crashes.** Check for booted Simulators, orphan processes, locked save/NAND/config files, stale Metal/Instruments captures, incomplete imports, staging directories, and partial logs before the next run.
- **Never touch the original input.** The image in `ref/rom/original/` and `ref/sunpad` are read-only. Work from ignored staged paths. Re-hash whenever state is uncertain.
- **Never leak game data.** Images, partitions, `main.dol`, REL/RSO files, extracted assets, generated AOT/objects/modules, saves/NAND, screenshots/audio, crash memory, and private logs never enter a commit, issue, upload, public artifact, or paste.
- **No destructive cleanup.** Never run `git clean -fdx`, blanket `rm -rf` against the project root, destructive reset, or a command that can erase ignored inputs/evidence. Inspect exact paths first.
- **Respect unknown work.** Do not overwrite or reset modifications you did not create. Isolate changes or leave a handoff.
- **Pin before patching.** Verify exact root and recursive revisions before applying a SunPad or GalaxyPad patch. A patch applying with fuzz is not proof of correctness.
- **No silent Sunshine carryover.** GMSE01 hashes, GameCube pad mappings, FLUDD analog trigger behavior, Sunshine audio/timing/widescreen patches, save paths, or UI labels are hypotheses until Galaxy reproduces the need.
- **No silent upstream mixing.** ModernGekko, its RecompCore/Dolphin vendor tree, DolRecomp, template, and patch set form one graph. Record and test a coherent update; never cherry-pick random binaries or commits into an unrecorded combination.
- **No title-database footgun.** Every Galaxy build must prove Broadway and 64 MiB MEM2. A build that silently fell back to GameCube mode is invalid regardless of what it renders.
- **No silent stubs.** A stub is allowed only for an optional external device or a named bounded system path whose original contract is understood. Never stub progression, disc reads, pointer depth, save, audio timing, input state, MEM2, or scene behavior merely to reach another screen.
- **No fallback fiction.** macOS JitArm64 or interpreter fallback may expose a missing AOT range; it does not prove that iPad/iPhone can execute the path. Log every mode and keep mobile acceptance separate.
- **No fake EFB optimization.** Never disable CPU EFB access, return a constant/stale depth, force every target to the foreground, or skip draw-sync semantics to make a benchmark green.
- **No motion-only baseline.** Device tilt, device shake, and controller gyro are optional. The lowest accepted path always includes dedicated Spin and stick-backed tilt controls.
- **No runtime-downloaded code.** The Apple apps may import user game data; they may not download a generated module, mod, executable patch, or guest code.
- **Timebox repetition.** The same command failing the same way twice is a blocker. Stop repeating it and enter the unblocking ladder. Never run an unchanged third attempt.
- **No publication by momentum.** A technically green build remains private until G15. Do not push releases, tags, packages, screenshots, or generated files without explicit authorization.

## Wii substrate discipline — hard rules

- Treat disc identity, title ID, DOL identity, Broadway selection, MEM2 state, IOS, NAND, SYSCONF, and module identity as one boot contract. Log them before game code.
- Verify the exact extracted image. “Galaxy usually has no RELs” is not an executable inventory.
- Any required file loaded as executable is an AOT/dynamic-code incident until classified. Record source path, hash, guest range, loader, and route.
- Use a clean local virtual NAND by default. Never borrow or download a personal NAND/system-file bundle to make a failure disappear.
- MEM2 faults are layout incidents before capacity assumptions. Record arenas, paired heaps, allocation, address, and high-water marks before changing sizes.
- The optional homebrew/control DOL may isolate the Wii substrate. A commercial control title is never a hidden prerequisite and may not be downloaded.

## Recompilation and dynamic-code discipline — hard rules

- Capture DolRecomp’s SMC report and every warning for the exact DOL. Suppressing output is not resolving it.
- Log AOT hit, interpreter fallback, macOS JIT fallback, unknown PC, and executable-write events from the first native boot.
- Every fallback incident records guest address, current function/scene, frequency, expected section, and mobile consequence.
- macOS JIT may be a diagnostic safety net only. A required path that works solely under JIT keeps the lowest affected goal unmet.
- The HOME Button Menu RSO and its seven entry points are an explicit subsystem. Replace it narrowly with the native menu; never globally disable dynamic-code checks.
- A Petari symbol is exact only when the DOL hash and range match. Wrong-region names are clues, not patch addresses.
- A function replacement preserves original semantics, carries provenance, and has a focused regression. Never patch a symptom without naming the underlying behavior.

## Pointer and EFB discipline — hard rules

- Keep Dolphin’s required `RMG` baseline: CPU EFB access enabled, deferred invalidation enabled, and arbitrary mipmap detection enabled until measured evidence justifies a compatible change.
- Instrument the first pointer frame. Record `GXPeekZ` count, coordinates, active channel, stall, returned depth, selected target, and frame interval.
- Prove correctness at 1× before increasing internal resolution.
- Classic Pointer is the bring-up baseline. Direct Touch is a separate product layer and receives its own context matrix.
- Pointer visibility is deliberate host/guest state. Clear or restore it explicitly across cutscenes, transitions, native menus, controller handoff, background/foreground, and runtime restart.
- A readback optimization stays default-off until it reproduces target/depth outcomes and improves recorded frame time.
- P2/Co-Star pointer work is disabled in the P1 baseline unless explicitly being tested; do not pay or claim its cost accidentally.

## Input and motion discipline — hard rules

- Generate a Wii Remote **with Nunchuk** profile. `Extension = None` or sideways-only output is invalid for Galaxy.
- Keep one normalized host state for touch, keyboard/mouse, and GameController input; merge by explicit rules and clear on ownership/lifecycle transitions.
- Spin is a dedicated host action. Prefer a virtual Wii Remote/Nunchuk shake pulse; otherwise patch one named query. Never globally steal A or B.
- Audit every swing, acceleration, gyro, IR, distance, roll, rumble, and speaker consumer. Do not assume Mario’s spin is the entire motion surface.
- Each mandatory tilt mechanic gets a tested stick-backed path before optional motion work begins.
- Optional `GCMotion` is capability-detected, manually activated only while needed, stopped on pause/background/disconnect, and never required.
- No touch, pointer, Spin, tilt, or controller value may remain logically held after native UI, interruption, or lifecycle transition.

## Audio, save, and lifecycle discipline — hard rules

- Main DSP audio and the Wii Remote speaker stream are separate evidence paths. Hearing music is not proof of speaker-cue routing.
- Verify guest timebase, producer cadence, Apple callback, queue depth, underruns, and pitch before changing buffers.
- Use disposable ignored saves/NAND. Hash and back up before/after a test that can write.
- A save write passes only after game-visible relaunch/load. A file timestamp or nonzero size is insufficient.
- Keep saves separate from imported game data; removing/reimporting the image must not silently remove or rewrite saves.
- Lifecycle tests include native menu, picker/share sheet, resign-active, background grace, audio interruption, renderer recreation, memory warning, controller disconnect, and clean shutdown.

## Unblocking ladder

When blocked, escalate through these in order. Journal each rung used.

1. **Read the first causal error and full context.** Use persistent runtime log, unified log, crash report, full build output, AOT/fallback trace, Wii boot trace, MEM2 allocation log, EFB profile, input trace, audio counters, and save log. Do not diagnose from the final cascade line.
2. **Check current project state.** Confirm disc/DOL/module hashes, title ID, Broadway/MEM2 guard, root revision, dependency graph, patch manifest, generated cache identity, active save/NAND, settings, running processes, and Simulator state.
3. **Reproduce the last known-good boundary.** Run the exact recorded command/artifact/settings. If it no longer passes, reopen the lowest regressed goal before experimenting farther ahead.
4. **Check SunPad.** Read the exact reference script, Apple host, input mixer, import flow, diagnostics, test, relevant patch, `KNOWN_ISSUES.md`, `TECH-DEBT.md`, `TESTING.md`, and `HANDOFF.md`. Reuse only the game-neutral mechanism.
5. **Check the exact Galaxy input and Petari.** Use the extracted manifest, DOL sections/disassembly, exact-region map, and named source paths to turn addresses into behavior. Do not apply a Korean address to another revision.
6. **Check the toolchain source.** Read DolRecomp analysis/backend/module code, ModernGekko runtime/module loader, RecompCore/Dolphin Wii boot, memory, DiscIO, DSP, GX/EFB, WPAD/KPAD, save, and Metal paths at the pinned revisions.
7. **Research one named question.** Search primary source, issue history, commits, and official Apple documentation. Research must answer a precise blocker and return to a bounded experiment.
8. **Reduce the problem.** Examples: toolchain check before disc; Wii mode before game code; homebrew DOL before Galaxy only when lawful; C backend before LLVM; AOT entry before title; title before pointer; Classic Pointer before Direct Touch; one EFB read before full UI; main audio before speaker mix; one save write before repeated termination; macOS before Simulator; iPad before iPhone; 1× before 2×–4×.
9. **Route around narrowly.** Replace one named SMC function, HOME-menu entry, input query, tilt consumer, speaker sink, or runtime defect. Preserve original semantics, add a regression, and keep the stable route explicit. Do not replace a subsystem with no-ops.
10. **Park and pivot.** If a blocker survives a working session, write a complete reproducible defect and take the largest step on the same or later workstream that does not falsify the lowest goal—for example, shell extraction while an EFB profile is blocked. Do not mark the blocked goal met.
11. **Stop and hand off only for a real decision/blocker.** Valid conditions: unusable/wrong/corrupt image; exact identity cannot be established; required source/tool is unavailable; an unavoidable executable path cannot run without prohibited dynamic code; continuing would destroy/leak protected input; physical-device action is required; a public rights/release decision is required; or a measured hardware limit leaves no semantics-preserving route. Ordinary compile errors, crashes, black screens, missing audio, bad pointer state, save defects, MEM2 faults, and performance regressions have an unblocking path.

## Testing rhythm

- **Per change:** run the smallest build/boot/gameplay/regression check relevant to the changed layer.
- **Per dependency change:** verify recursive pins and patch provenance; rerun Wii-mode guard, module generation, macOS boot, and the highest known-good gameplay smoke.
- **Per AOT/replacement change:** inspect SMC/coverage output; run the exact scene; compare dispatch counts and unknown PCs; verify mobile compatibility.
- **Per Wii-subsystem change:** run a narrow boot/service test plus the highest known-good gameplay boundary.
- **Per EFB change:** rerun the same pointer coordinate/scene at 1×; compare depth, target, read count, stall, and frame-time distribution.
- **Per input change:** run deterministic press/hold/release, simultaneous inputs, pointer, Spin, tilt, menu/lifecycle clear, controller connect/disconnect, and stuck-state tests.
- **Per audio change:** run music, voice, effects, Star Bit/speaker cue, transition, interruption, and pitch/underrun checks.
- **Per save change:** back up disposable state; write in game; exit/terminate as specified; relaunch and verify visible progress; compare hashes; never commit the fixture.
- **Per goal claim:** complete the exact evidence required by PRD Section 11 before changing `STATUS.md` to met.
- **Per session:** run the host regression suite and a boot/end-to-end smoke on the highest known-good target. End with the exact known-good command, revision, artifact/module/disc/save identity, settings, and next lowest step.
- **Per Simulator target:** verify all others are shut down; capture `xcrun simctl io <device> screenshot`; kill the app and shut the device down at session end.
- **Per candidate:** run the entire applicable matrix against the exact artifact. Do not combine evidence from earlier packages.
- **Input automation:** extend SunPad’s pipe/test-input machinery for Wii controls, IR coordinates, Spin pulses, and tilt axes. Use repeatable file-select/Gateway/Observatory routes. Rows marked hands-on remain hands-on.
- **Honesty rule:** configured, source-inspected, or unit-tested behavior is not a gameplay acceptance claim. Performance numbers come only from recorded measurements.

## Using the SunPad machinery — not just its appearance

- **Dependency control:** port exact locks, dirty-check refusal, recursive setup, revision verification, disabled push URLs, and coherent patch application. Produce a GalaxyPad lock and upstream-delta ledger.
- **Scripts:** port the shape of SunPad’s bootstrap, preparation, core/module builds, device deployment, macOS packaging, crash capture, repository checks, IPA/package audits, and deterministic input helpers; add Wii-mode, disc-identity, executable-inventory, and EFB-profile scripts.
- **AOT boundary:** preserve local image → exact DOL → ignored DolRecomp output → locally generated module → game-data-free source tree. No on-device compiler and no runtime-downloaded executable code.
- **Apple shell:** extract CAMetalLayer host, loading/error presentation, settings, normalized input, controller ownership, paths, lifecycle, import staging, diagnostics, and privacy before renaming.
- **Input mixer:** extend the state model to Wii Remote/Nunchuk/IR/Spin/tilt; do not force Wii input through the old GameCube layout.
- **Three-dot menu:** retain the accepted Display, Controls, Unstable Experiments, Game Data & Saves, Report a Problem, and diagnostics hierarchy; adapt labels/actions to Galaxy and replace the guest HOME overlay.
- **Game-data safety:** preserve security-scoped picker handling, validation, unique staging, atomic activation, rollback, real removal, and save separation. Add large-Wii-image storage preflight and exact DOL/module matching.
- **Logging:** wire boot, Wii mode, MEM2, dispatch, EFB, pointer, Spin/tilt, audio/speaker, save, and lifecycle breadcrumbs before the port becomes unstable.
- **Experimental framework:** every risky EFB optimization, renderer change, timing change, Direct Touch heuristic, motion mode, aspect fill, or performance mode is default-off, has a logged identity, and never silently replaces the stable baseline.
- **Release safety:** keep source/package audits executable throughout development. Passing them once at the end is insufficient if the build graph or module packaging changes.
- **Branding:** create original GalaxyPad icons with provenance; never derive them from game art or extracted assets.

## Session start checklist

1. Read `docs/STATUS.md`, the last `JOURNAL.md` entry, and the relevant inventory for the lowest unmet goal.
2. Run `git status`; preserve unknown work. Record the root revision.
3. Run `xcrun simctl list devices booted`; shut down strays. Kill GalaxyPad, ModernGekko, launcher, runtime, and test processes.
4. Confirm the original image and active staged copy hashes when relevant. Confirm exact DOL/module identity.
5. Verify `ref/sunpad`, selected ModernGekko/RecompCore/DolRecomp/template, and Petari revisions against the GalaxyPad lock; check patches target the intended commits.
6. Run or verify the Broadway/MEM2 guard before a Wii build.
7. Confirm the active save/NAND/test fixture and back it up if the session can write it.
8. Confirm stable settings: target, backend, EFB scale, aspect, pointer mode, Spin route, tilt route, audio/speaker mode, and fallback policy.
9. State the session goal, hypothesis, and smallest next step in `JOURNAL.md`.
10. Enter the loop.

## Session end checklist

1. Kill the game/runtime and shut down every Simulator.
2. Run the regression suite and highest known-good smoke test, or state exactly why one cannot run.
3. Record root/dependency revisions, disc/DOL/module/build identity, evidence paths, settings/mode identity, active save/NAND hashes, open processes (none expected), and remaining defect.
4. Update `STATUS.md` and every changed technical inventory.
5. Remove incomplete import staging directories only after verifying they are not the original input or required evidence.
6. Run repository safety checks before any commit.
7. Leave one unambiguous next step for the lowest unmet goal.
