# Guarded direct-call experiment — R712 implementation boundary

Purpose: test one architectural lever from REVIEW-RESPONSE-2026-09-09.md.
No unsafe-direct-call option enabled or product module changed yet.

## R736 disposition: no promotion; move to shared FP/state

Prepared fresh identical initial profiles from R462 for reverse order:
direct-enabled-r736 then direct-unbound-r736. Exact R730 runner/module/settings.
Enabled12581/PID87671 bound1, capture92913exit0; unbound21919/PID87870,
capture19586exit0. Native LoadState2 and pre/post screenshot checks show same
GoodEgg/hangingMario/life3/StarBits4 with animation. Both nativeQuit exit0,
fallback0/smc_failed0, GameData106e8248 unchanged. No running game afterward.

| Order | Binding | CPU ms/VI | VI/s | Process M instructions/VI |
| --- | --- | ---: | ---: | ---: |
| A1 | disabled | 26.247646 | 36.12235 | 289.964938 |
| B1 | enabled | 24.761164 | 38.19354 | 294.600105 |
| B2 | enabled | 28.988783 | 32.72282 | 298.073222 |
| A2 | disabled | 24.533556 | 38.49232 | 286.856603 |

All four windows have zero invalid CPU/reset intervals. First CPU improvement
5.6633% did NOT reproduce in reverse order. Instructions/VI are higher in both
enabled runs. Host scheduling/frequency/background/focus were not held constant;
the second enabled screenshots show inactive window chrome and no pointer, so
do not attribute all measured difference to the optimization. Two pairs do not
prove a universal regression or exact confidence bound. They do fail to establish
a reproducible material win, with no instruction-work reduction supporting one.
Enabled B2 whole-run1,015,149,729 transfers confirms path activity, not matched
dispatch/VI. No full mutable-code/input/audio/story correctness acceptance.

Decision: close THIS design for promotion and stop further tuning/rebuilds under
this hypothesis. Keep diagnostic sources/artifacts, do not replace the installed
module or enable its flag. No untransformed full same-flags control is warranted
to promote a variant that has not passed its initial binding-effect test.
This is a practical stop decision, not proof all guarded-call approaches fail.
Move to the planned shared FP/state-materialization lane, preserving accuracy.
Updated actual goal loop and active performance queue; full PRD scope unchanged.

## R735 first enabled pair result

Exact R730 signedrunner871f4f/module6871db, same R724 initial Config/save/state,
LC byte/pair1 and no-fallback-JIT1, only direct binding env enabled. Runtime65580
PID87354 reports bound1. Native LoadState2 restored expected hangingMario/life3/
StarBits4 GoodEgg; before/after screenshots show same scene with animation.
Capture42244exit0 then nativeQuit65580exit0. VI exported; fallback0/smc_failed0,
GameData106e8248 unchanged. No game/booted simulator remains.

30.005084417s,1146VI=38.193527Hz;1084VI/36.122336Hz unbound earlier.
CPUmean24.761163755ms/VI vs26.247645930ms:5.6633% lower.
Processinstructions294.600104517M/VI vs289.964938145M:1.5985% HIGHER.
Both windows have zero invalid/reset CPU intervals. This is a single fixed-order
pair with no runtime/per-core frequency control: not a reproduced gain and well
below20% target. No reason to claim large architectural savings from it.

Shutdownchecks1,204,746,800/transfers1,203,316,401 proves substantial guarded
execution, not matched-window dispatch/VI. Whole-run native366,388,583 versus
unbound1,385,526,356 covers unequal boot/gameplay duration; do not turn that ratio
into a measured reduction per VI. First correctness smoke passed, not full SMC,
input/audio/story acceptance. Next reverse-order repeat with identical initial
profiles. If reproducible gain remains<8%, close this guarded design and move
to shared FP/state-materialization lane; do not promote or restart tiny tuning.

## R734 first live unbound baseline

Module build37737 completed exit0. Output module/gRMGE01_recomp.dylib SHA
6871db5d16c9c6244e2b803fb5ecc3c2fc32941e56bdcae9a9395df4eef7fb24. nm -gU confirms
galaxypad_bind_direct_calls_v1 and staticrecomp_get_module exports. Loader reports
RMGE01/moduleABI3/CPUABI3/state3528/entry8000403c/2code/19SMC/1322chunk ranges.
Signature verify passes. Inspection90083exit0.

Launched exact signed R730 runner, explicit game generated/extracted/run1,
diagnostic module, direct-unbound-r724 profile. Direct-call env unset; lockstep,
trace and dispatch-sample env unset; NO_FALLBACK_JIT=1, LC_BYTE_FAST=1,
LC_PAIR_FAST=1, VI_TIMING points to that profile/vi.csv. Runtime84704/PID86966.
Initial no-window delay sampled in InspectGame->HashDirectorySha256, not direct
dispatch; startup sample retained generated/direct-unbound-startup-r734.sample.txt.
Then actual module loaded. Native States->Load State2 restored Good Egg hanging
Mario/life3/StarBits4; same scene visible after capture, with animation advancing.

Capture95366exit0 (existing process probe,10s warmup/30s capture). Native Quit
cleanly ended84704exit0 and flushedVI. work-summary.json:30.0091335835seconds,
1084VI=36.122336Hz,289.964938M whole-process instructions/VI. vi-summary.json uses
first.after_ns..last.before_ns,1083complete intervals, CPUmean26.247645930ms/VI,
wallmean27.669658319ms, zero invalid/reset intervals. These are baseline values,
not a speedup or comparison with old differently-built/profiled runners.
Whole-run shutdown fallback0/smc_failed0; GameData106e8248 unchanged.

Next enable binding in fresh direct-enabled-r724 with identical runner/module
and settings, confirm bound=1 and visible checkpoint scene, repeat measurement
and clean close. Additional alternating windows and untransformed same-flags
control remain required before net-product improvement claims.

## R731 simulator shutdown ahead of desktop diagnostics

While module37737 progressed past1105/1333, clean-stopped the already-paused
simulator game through native Stop Game confirmation. R710b runtime log records
01:41:15.881 exit failed0, smc_failed0. GameData hash remains
99d432d517b92b19da0c403819b91288b10c7063c3ce61f5000347ef823ab64f.
Terminated idle app and shut down device DE8E956F; command8698exit0 confirms
PID75679 absent and no booted devices. Installed app/saves/checkpoints remain.
No desktop game launched. Continue module37737, then verify link/exports before
launching the sole diagnostic game with an explicit R724 profile.

## R730 isolated diagnostic bundle

FileUtil's Apple system-resource lookup uses bundle Contents/Resources/Sys.
Prepared generated/macos/direct-calls-r730/GalaxyPad.app with only the R729 runner,
desktop Sys resources and new experimental Info.plist. CFBundleExecutable is
GalaxyPadRunner; distinct ID org.galaxypad.directcalls.diagnostic. No normal
launcher/frontend/default-profile bootstrap or game data/module copied.
plutil lint and ad-hoc codesign --verify --deep --strict pass37936exit0.
Signing changes executable identity: packaged runnerSHA
871f4f8726cf1e12c56022a61dfbd013cbfa6614ce68ee6873982e869a9f4faf.

Not launched. Invoke its exact Contents/MacOS/GalaxyPadRunner with explicit
--game generated/extracted/run1, --module finished diagnostic dylib and
--user-dir matching R724 disposable profile; never launch bare against normal
user data. Build37737 remains live (910/1333 last read). Simulator remains
paused; clean-stop it before any desktop game launch after compiler completion.

## R729 desktop runner links

Runner build87774 completed exit0. New moderngekko-run SHA
b5151c2f38f6b76638e93f9c57e0a5fb156f165068828fa0e83cad953ef5c2c5.
nm -C confirms StaticRecompCore::HookDirectCallBoundary in the linked executable.
strings confirms GALAXYPAD_GUARDED_DIRECT_CALLS, galaxypad_bind_direct_calls_v1
and bound/checks/transfers diagnostic messages. Duplicate-library linker warnings
were nonfatal. This verifies linked plumbing, not a loaded-module binding or
working game. Prior runner backup remains at R723 path/hash.

Module37737 is still compiling (819/1333 at last log read); poll same handle.
No runner/game launch under ongoing compiler load. Simulator remains paused.
Next finish module, inspect exported setter/identity, package isolated diagnostic
runner/resources if needed, then clean-stop simulator and test matched profiles.

## R724 matched profile preparation during builds

Prepared fresh generated/runtime/direct-unbound-r724 and direct-enabled-r724.
Copied only R462 Config, Wii, config.ini and StateSaves/RMGE01.s02; created own
Pipes/galaxypad FIFOs. No old logs, shader caches or output measurements copied.
Config trees match. Both state filesSHA74e453b5fd20b6a603a9811dfb363c9b66903662bda83971c558f57493adfe01;
both GameDataSHA106e8248bd8081404e8258a7ca33c54e0d476d651f139fde5ee2e4aad7302c90.
Checkpoint compatibility with the newly linked core is unverified; never bypass
version/identity rejection. Confirm restored Good Egg scene visually before and
after each window, and preserve source profile/save. Same candidate and runtime,
only GALAXYPAD_GUARDED_DIRECT_CALLS absent versus1 for initial comparison.

Existing VI recorder is configured by GALAXYPAD_VI_TIMING in dolphin_runtime.cpp.
Existing capture-process-work.py checks PID/executable identity, waits10s warmup,
takes30s bracketed snapshots and writes a new measurement only. Whole-process
counters are not CPU-thread counters. Thread CPU/VI and eligible transfers still
need appropriate matched evidence; startup/shutdown totals cannot substitute.
No measurements or game launch during builds. Module37737 and runner87774 remain
live (221/1333 and40/232 at last poll). Simulator remains paused, not stopped;
cleanly stop it before launching the single desktop game after builds complete.

## R723 runner build and preserved baseline

The module build37737 continues normally. Desktop moderngekko-run needs a real
relink, not merely the earlier guarded-core object compile. Preserved its prior
binary under generated/candidates/r723-runner-baseline/moderngekko-run and verified
both hashes13354ea966aeca76f893c769ee81c0b85ce260dcefa14c80debf8f3459c8f53a.
Started runner build87774 with parallel1, log direct-call-runner-build-r723.log;
dependency graph reports232 steps. Combined compiler concurrency is at most3
ordinary compile workers (module2/runner1); simulator remains paused, no profile
or benchmark overlap. Both builds still live at checkpoint. Poll same handles.
The SCM '^master' diagnostic is the known nonfatal revision-generation warning,
not proof of build failure; require final exit status. No installed app update.

## R722 full diagnostic build started

Verified compile_commands:1321 transformed chunk files,1 unchanged chunk and
1binding.c, no duplicated source entries; actual flags include arm64 ThinLTO/O2
and strict floating point.36GiB free at launch. Same simulator game75679 paused
through native menu. Full gRMGE01_recomp build in generated/build/direct-call-r721
started session37737 with parallel2, log generated/direct-call-build-r722.log.
It is still compiling; poll this handle, do not restart based on a quiet log.
Resume simulator after completion unless transitioning cleanly to the Mac run.

Build decision: broad150753-site coverage, historical3.81x process-instruction
gap, and retained billions of dispatch entries make this architecture experiment
plausibly material enough to test. This is a hypothesis, not a quantified15%
forecast; no such forecast has been proven. Building the candidate is explicitly
the next empirical test, not performance promotion. Preserve the existing
>=20% target and <8% stop criterion once matched measurements exist.

Guard changes are only object-compiled in desktop core so far; its diagnostic
runner must still be linked. Retained R462/R463 runners/modules/PGO results are
not a matched control for this unprofiled candidate. First enabled/unbound runs
of the same candidate can isolate binding effects; an untransformed same-flags
control is required before claiming net product improvement. No benchmark may
overlap this compiler load or another running game. Original PRD gates remain.

## R721 broad caller overlay

prepare-direct-call-overlay.py reuses the tested single-chunk transformation,
indexes actual target entries, verifies source hashes between indexing/rewrite,
and writes only changed chunks into a new out-of-tree directory. Manifest is
written last and records every original hash, replacement hash and static count.
Actual generated/direct-call-r721 contains1321 changed chunks/150,753 guarded
sites of1322 total chunks,361MiB. Preparation86148exit0. Relative to current
150,916 original cross-chunk return sites,163 remain untransformed. No dynamic
coverage or material speedup follows from these static counts alone.

Experimental CMake accepts GALAXYPAD_DIRECT_OVERLAY, validates tree identity,
original/replacement hashes and original membership before substituting sources.
Configuration generated/build/direct-call-r721 completed63234exit0 after123.1s.
It reported validated overlay and generated the diagnostic graph. Full
candidate compilation has NOT started. Reduced repeated JSON parsing in the
wrapper after starting configure; the completed invocation retained the prior
loop body, so next build may regenerate configuration with that parsing edit.
Source-shape and executable differential tests pass again. Next verify the
complete graph then proceed to justified macOS diagnostic link and measurement.

## R720 coverage decision from retained PGO

Read retained rmge01.profdata with llvm-profdata show --function=func_. Its
1322 chunk function-entry counts sum to2,895,966,494; top20 account for45.9042%.
The first diagnostic chunk800AA0A0 accounts for247,493 entries (about0.00855%).
It is appropriate for compilation verification, not a meaningful speed trial.
Largest destination805170A0 has238,389,378 entries, followed by804A20A0 with
120,399,808 and800180A0 with105,216,101. These are historical training counts,
not current matched scene measurements, CPU cost or eligible direct-BL counts.

Decision: do not benchmark the single-chunk wrapper as the architectural test,
and do not select only hot destination chunks. Direct calls are rewritten at
caller sites; a hot destination's many incoming calls can remain unchanged if
only its own source is transformed. Prepare broad eligible caller coverage in
an isolated overlay, retaining unrecognized/unsupported paths and original source
identities. Reuse the focused build path for verification, then decide the full
diagnostic build on that coverage plus the existing architectural hypothesis.
No numeric speedup prediction is established by these counts. Existing >=20%
target and <8% stop threshold remain; no new runtime/profile capture is needed
to re-establish that the single test chunk is unrepresentative.

## R719 diagnostic target integration

apple/experiments/guarded-direct-calls/CMakeLists.txt wraps the vendor module
target using its existing options/runtime/ABI tables. Required original and
override paths must exist and differ, and the original must belong to the
selected target. Only that source is replaced in the diagnostic graph; binding.c
is added. No vendor build or generated source mutation occurs.

Configured generated/build/direct-call-r719 (89506exit0) with GAME_ID RMGE01,
the selected R387 generated directory, original chunk0166_text1_800AA0A0.c and
isolated R716 chunk_0166.c override. Targeted object build65636exit0 compiled the
transformed chunk and binding under actual arm64 Release ThinLTO/O2 strict-FP
flags. Module tables generated1322 hashed ranges. No complete module link yet.
This proves build integration for the isolated object, not full module execution
or a performance result. One chunk is not representative dynamic coverage.

Sole booted Simulator DE8E956F and existing PID75679 verified before build;
native menu paused it, then dismissed after successful compile. Installed module
selection and app unchanged. Next choose justified diagnostic coverage and
materiality evidence before committing to a full1322-chunk candidate build.

## R718 transformed fixture differential execution

test-direct-call-differential.py now runs the actual transformation on two
generated-shaped callers, including continuation-entry suffix charges7 and13.
Original and transformed executables use actual binding.c/transfer.h. Each runs
36 combinations of binding enabled/disabled, depth0/1/24, and boundary rejection
index0–5. Five boundary records (PC, LR, value, cumulative charge), final saved
LR, total53 cycles and balanced depth match the unbound dispatcher baseline.
ASan/UBSan passes. Registered in full suite, which was not rerun this turn.

This closes executable transformation coverage for this small nested fixture;
the guest bodies and runtime accounting are explicit test implementations.
R717 separately exercises the actual core accounting/guard. Neither substitutes
for full module/runtime integration, real mutable-code callbacks or gameplay.
Proceed to diagnostic integration and bounded materiality evidence; do not treat
these correctness fixtures as performance measurements.

## R717 nested boundary/helper execution

The existing boundary test now links actual binding.c and includes transfer.h
alongside the extracted actual core guard/outer accounting bodies. Five nested
scenarios pass ASan/UBSan: successful return (53 charged cycles); forced fallback,
pause and synchronous exception (23 cycles); depth exhaustion before leaf entry
(12 cycles). Checks include PPC budget, timebase quotient/remainder, balanced
depth and no caller continuation executing after rejection. In the forced case,
the inner rejected continuation equals the outer continuation: the latch prevents
outer resumption and a fourth boundary commitment.

These are executable integration tests of those actual components, but runtime
membership/services and generated callee bodies remain stubs. They do not prove
real SMC callbacks, generated nested instruction semantics, gameplay or speed.
Next apply the transformation in a differential executable fixture, then link
the macOS diagnostic path for a bounded baseline/candidate experiment.

## R716 isolated generated call-site wiring

scripts/prepare-direct-call-chunk.py transforms an explicitly selected generated
chunk into a new file outside the selected tree. It verifies canonical target
entry membership in the target chunk, an existing caller continuation entry,
and exact BL/LR/PC shape. Missing/unknown targets and absent continuations stay
on the original path. Unexpected accounting or inconsistent LR/PC fails closed.
Both existing-output and in-tree writes are refused.

The continuation entry may charge a block suffix before its goto. Resuming
directly at the label must retain that charge; the tool copies that exact
validated subtraction inside the successful-transfer branch. This is separate
from the runtime boundary's flush of the completed callee segment.

Actual chunk_0166_text1_800AA0A0.c transformed into
generated/direct-call-r716/chunk_0166.c:76 guarded sites. clang -std=c11
-fsyntax-only with GXRuntime/include succeeds using the actual generated header
and CPUState. No linked or executed module yet. Focused transformation tests
pass and are registered; full suite not rerun. Next execute differential
generated fixtures with actual boundary accounting, including nested denial,
then determine whether to build a measured macOS diagnostic candidate.

## R715 replacement-aware transfer glue

Added experimental transfer.h, included after the generated game header. It
balances depth entry/leave, asks the host boundary before entering the callee,
runs module replacements before original code, and requires matching return PC
plus a fresh continuation boundary before resuming the caller. A continuation
replacement executes and returns to the chassis without overwriting its PC.
Missing binding, depth exhaustion, denied boundaries and early returns all yield.

This preserves a distinct obligation found in RMGE01.h:dolrecomp_call:
module replacements precede host hooks and original dispatch. The runtime guard
excludes host interception, but does not itself implement module replacements.
Only canonical, known generated targets are intended for this first experiment;
physical aliases and unknown targets must retain the original dispatch path.

Actual transfer.h plus binding.c compile and pass eight focused ASan/UBSan cases
via tests/test-direct-call-transfer.py, now registered in the repository suite.
Coverage includes exact event ordering, target/continuation replacements, both
boundary denials, mismatched returns, missing binding and depth exhaustion.
These are stub-runtime tests, not nested accounting/SMC or gameplay proof.
No generated call site is wired yet; no module or installed app changed.
Next wire isolated generated sites, verify continuation labels and cycle charges,
then test nested unwind against the actual runtime guard before benchmarking.

## R714 host runtime integration

Core Init now optionally resolves/binds galaxypad_bind_direct_calls_v1 when
GALAXYPAD_GUARDED_DIRECT_CALLS=1, the module is dynamically loaded, and REL,
lockstep, dispatch tracing/sampling modes are absent. Default/attached paths
do not bind. Shutdown detaches before unloading/destroying the core.

HookDirectCallBoundary commits completed segment charges/timebase, checks CPU
ownership/context, PC, current chunk verification/forced fallback, host hooks,
run state, budget, idle and pending guest/host exceptions. Denial latches unwind
until the outer dispatch returns; no outer caller can accidentally resume.
Outer Run skips its empty-dispatch minimum only when that segment was already
committed by a denied boundary. Accepted transfer starts a fresh segment, so
an actually empty callee still gets its existing minimum charge.

Canonical0026-guarded-direct-call-boundary.patch f9c905b4 registered/reverse-check
passes. Actual macOS Core.cpp and Run.cpp objects compile (44167exit0). Actual
guard and outer accounting bodies pass ASan/UBSan in runtime stubs:13 denial
conditions, disabled/outside/wrong-state contexts, latched unwind,257 chained
charge/timebase cases including zero and EE-disabled interrupt behavior.
Not yet a linked runtime or generated-module integration test. Emitter/module
replacement routing, depth/return behavior and real callback/SMC interactions
remain required; no direct-call performance experiment has run yet.

## R713 implementation checkpoint

apple/experiments/guarded-direct-calls/binding.h and binding.c now implement
the optional versioned extension. The module has one shared callback binding,
not per-chunk static copies. Missing binding/null state yields to the chassis;
unsupported version clears stale binding; explicit null detaches before teardown.
CPUState stays opaque and unchanged. Binding/rebinding is only legal outside
guest CPU execution; no concurrent-rebind guarantee or atomic hot-path cost.

tests/test-direct-call-binding.py compiles the actual implementation into a
hidden-symbol dylib with the setter explicitly exported. A host fixture uses
dlopen/dlsym to exercise forwarding, rejection, detach and three load cycles
under ASan/UBSan. PASS. This proves extension plumbing, NOT the actual runtime
guard, accounting, replacement or generated-call behavior. It is not linked
into the installed application. Next wire the core callback and emitter against
this interface; do not mistake the fixture CPUState for production state proof.

## Current source census

scripts/audit-direct-call-sites.py reads actual direct-BL instruction comments
and emitted bodies, rejects unknown shapes, and fingerprints all chunk contents.
1322 files; manifest1a0cc0094e8abb55a4addea5e1cdaecf53e0dc7813ea6fc4abed5bf408142789.
165220 direct-BL sites:150916 return-to-chassis,14304 local goto,0 direct calls.
Artifact generated/direct-call-census-r712.json. This corrects the supplied
review's different chunk partition/counts; static coverage is NOT dynamic cost.
Indirect calls/returns and guard eligibility are not classified by this census.

## Concrete boundary found in existing source

- emitter.c:emit_cross_chunk_call writes target PC, depth-checks, calls the target
  chunk, and resumes the caller only when PC equals continuation. It does not
  check runtime mutable-code state or host interception at either transition.
- StaticRecompCore_SMC.cpp:FastDispatchableAt respects forced fallback and the
  current CHUNK_VERIFIED state. DispatchableAt can additionally verify an
  unverified chunk. A failed fast check should yield to that existing slow path,
  not silently mark a chunk verified. Target AND caller continuation need checks.
- IsHostCallAddress uses mutable host membership including physical-address
  alias handling. HookHostCall has actual dispatch side effects. Do not call it
  merely as a membership test or skip pending return hooks/replacements.
- Run.cpp flushes accumulated downcount and updates guest timebase after each
  module return; it also delivers pending exceptions and checks CPU run state.
  A direct transfer must not expose stale timebase to guest mftb/busy waits.
  If a guard commits charges early, the outer Run flush must not double-charge
  or add its minimum1 cycle again for a glue-only unwind. Pure empty/zero-charge
  dispatches still require their existing forward-progress behavior. Explicitly
  test rejected entry, early callee return and nested unwind accounting.
- Existing local-return256-cycle guard is not proof of per-cross-chunk interrupt
  or stop checks. Depth24 bounds stack, not all mutable/timing contracts.

## Smallest integration shape to implement next

For the isolated macOS dynamic-module experiment, prefer an optional versioned
module setter resolved through the core's existing DynamicLibrary GetSymbolAddress
path. Bind a CPU-thread-owned direct-transfer callback without changing CPUState
ABI or silently repurposing a memory/host callback. Absent/incompatible binding
must take the original dispatcher path. Clear binding before core/module unload.
Attached/mobile modules need no support for this diagnostic-only first experiment.

Callback guards entry and continuation, commits each original dispatch segment's
charges exactly once, and returns control to the chassis for slow/unverified/
relocated/forced-fallback/hooked/exception/stop cases. Begin with unsupported modes
such as lockstep rejected to the original path; do not weaken their behavior.
Do not add a full bitmap/cache redesign to this first experiment. Use current
membership/validation initially so any measured gain is from reduced round trips.

Required differential cases before the module comparison: ordinary and nested
calls, depth limit, early/tail return, interior entries, target/caller invalidation,
hook/replacement entry and return, forced fallback, missing binding, guest/host
exceptions, pending interrupt with EE changes, stop, and exact cycle/timebase
accounting including zero-charge unwind. This is a bounded integration oracle,
not a new general emulation framework. Preserve the review's matched-metric
and material-benefit stop conditions; no new tiny-helper workstream.
