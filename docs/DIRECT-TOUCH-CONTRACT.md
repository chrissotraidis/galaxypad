# Direct Touch: menu readiness investigation

## R586 stable file-detail mapping

Readiness now permits current nerve806a0128 (FileConfirm) as well as0114,
with pending0 and all existing profile/calibration/neutral/staleness guards.
Tests accept stable0128 and reject pending0128/back0110. This is coordinate
mapping permission only, never permission to synthesize A.

Actual UIKit drag on detail highlighted Play This File (ui-r586-play.png).
Explicit A then reached opening story (ui-r586-started.png), with0128→012c
transition observed in ios-runtime-r586.log. Touch coordinates are approximate
CUA window coordinates, not subpixel calibration measurements. Mode12 story
is outside this experiment. Default Classic and device configuration unchanged.
Clean runtime exit11:01:28.092 failed=0; performance and story obstruction remain
open. No general gameplay, automatic direct-tap, or save-integrity acceptance.

## R585 actual UIKit touch consumer and reset check

Installed R584 binary2a2314c091ba07845a63abf1de908eace83f9bf9b33ecfe736e2b03aa7e68b94
with22/context/calibrated-touch flags; same native module. Controller-channel
diagnostic file used only for title A+B, then remained neutral. CUA dragged
actual Simulator content from(345,430) to(375,465): main.mm's overlay callback
publishes this via InputSource::Touch, not the bypassing diagnostic channel.
File1 hovered visibly, native actor81144cc8 returned1 with processed
(321.355,298.066), valid past/current. Screenshot ui-r585-touch.png verified.
CUA window coordinates are not an exact normalized viewport measurement; do not
claim the earlier subpixel numerical error bounds for this gesture.

Important release semantics clarified from source and runtime: touchesEnded
retains the last aim in Classic Pointer mode so the user can reach A/B;
touchesCancelled and native-menu/lifecycle reset hide it. Prior mixer tests of
a hidden input state were not proof that ordinary UIKit release hides aim.
Real A selected file detail; B returned to file list, both visibly checked.
Native menu open10:47:31.120 and dismiss10:47:48.467 logged input cleared;
ui-r585-cleared.png shows no pointer/hover. Fresh UIKit drag(565,425)→(585,465)
then hovered file2, confirming reactivation after reset; retouch screenshot and
selector item81192d08 agree. No A on empty file2, no new save or automatic tap.

Evidence generated/ios-runtime-r585.log, ui-r585-touch.png, ui-r585-cleared.png,
ui-r585-retouch.png; file detail also observed through CUA after explicit A.
Runtime68048/session47340 clean stop10:49:57.000 failed=0. Single Simulator shell.
Observed25–38FPS remains performance failure. This accepts one experimental
file-list touch-mapping path plus explicit buttons/native-menu reset, not full
Direct Touch actions, all menus, background/controller handoff or device gates.

## R584 opt-in touch consumer implemented

InputMixer accepts an optional touch-pointer mapper, called during consumption
with raw touch state and merged buttons/axes. Its return type can change only
pointer coordinates/visibility. It cannot alter buttons/axes or make a released
pointer visible; invalid/missing output hides the touch pointer and leaves the
existing controller fallback intact. Calling on consumption rather than UIKit
events ensures a held touch is re-evaluated when its readiness expires.

Simulator flag GalaxyPadDevCalibratedTouch installs the mapper only with the22
profile and exact-DOL context-observer path enabled. It weakly references Session,
copies configuration under the independent mutex, rejects future/older-than250ms
timestamps, then runs the bounded inverse against actual CameraLogic projection.
Any merged Spin/tilt, including latched input without a visible touch, invalidates
this neutral-only experiment for the remainder of the session. No guessed
cooldown restores it. Normal/device behavior stays unchanged, flag defaultoff.
This is a file-menu-only diagnostic, not a general pointer replacement or A/B
action layer. Freshness is checked at consumption, not a full proof of game-side
revision/readiness or motion tracking.

Input regressions cover mapped coordinates, unchanged buttons/movement, expiry
without another input event, controller fallback, hidden-pointer Spin latch and
clear. Existing camera/readiness tests pass. Build79599 SHA
2a2314c091ba07845a63abf1de908eace83f9bf9b33ecfe736e2b03aa7e68b94 passes;
generated/mobile-input-r584.log, pointer-readiness-r584.log, build-app-r584.log.
Not installed/launched. Next must exercise the TOUCH channel: main.mm sends the
existing diagnostic JSON input through Controller, which deliberately bypasses
this mapper. Do not claim consumer validation from another controller-file run.

## R583 CPU-to-host model readiness bridge

`GalaxyPadMenuPointerReadiness.h` recognizes only the current bounded experiment:
generated22-profile flag, pointer context5, FileSelect current Nerve806a0114,
nonzero actor spine, no pending transition, center(0,-.2)/scale2.272727,
radius.03/sensitivity.5/filter0, reference(1,0) and acceleration(0,-1).
Missing/mismatched observations reject. It authorizes modeling only, not A/B.

The existing exact-DOL VI observer publishes an optional configuration with a
steady-clock timestamp every sixth field, before its change-only logging early
return. Session uses a separate mutex, not its runtime lifecycle mutex. Input
reset clears the configuration and timestamp. No consumer yet: freshness/host
lifecycle/source/pose constraints must be applied before touch routing, and
the generated-profile flag is not a general runtime-settings introspection API.

ASan/UBSan tests cover missing inputs, wrong profile/menu, pending/other Nerve,
wrong center/scale/filter, nonneutral horizons and recovery; existing grid/live
fixtures remain passing. Build76830 passes, SHA
059d23c6f67f3c7d9574654705f487f63dc1fecc9a2be06c44ac237d7fc4701b.
Evidence generated/pointer-readiness-r583.log and build-app-r583.log.
Not installed/launched; R581 remains stopped. Next freshness-gated touch consumer
and live verification; snapshot publication alone is not Direct Touch acceptance.

## R582 reusable configuration-aware forward model

Extracted `apple/shared/GalaxyPadPointerModel.h` from the tested forward model.
It takes explicit yaw/pitch, signed sensor height, center/scale and a mandatory
neutralOrientationVerified flag (defaultfalse). The camera callback supplies
the actual projection with active FOV. No guest reads or action injection.
Unknown orientation, invalid/nonfinite configuration or host coordinates,
hidden/missing/degenerate sensor points and nonfinite results reject.

The camera test now exercises this shared implementation rather than a duplicate
formula. All prior inverse grid counts pass, plus four independent R580/R581
live position fixtures within.002 logical pixels. Unknown-orientation rejection
occurs before camera evaluation; invalid scale/pitch and hidden/degenerate LED
tests pass ASan/UBSan. Evidence generated/pointer-model-r582.log.

This is reusable app-side code, not enabled touch behavior. A caller must still
verify neutral motion, reference/acceleration horizons, current menu context,
calibration and FOV, and clear that readiness across transitions. Do not set the
verification flag unconditionally. Next integrate that runtime-to-host readiness
bridge and route only touch pointer coordinates through the inverse, retaining
Classic Pointer and ordinary button ownership. No runtime launched this turn.

## R581 live bottom/side coverage verified

Extended the existing read-only observer to log up to32 changed processed
positions/validity states, independently of target hits. Repeated unchanged
positions do not consume the budget. Tests cover missing/unchanged/changed
samples, validity transitions and the hard cap. This is not a revision ack.

Same22-degree experiment and native module; no A after title A+B. Three
nonoverlapping pointer-only leases produced valid past/current positions:

| Intended viewport point | Inverse host input | Live screen XY | Error vs832x456 |
|---|---|---|---|
| (.5,.999) | (.5,.985020) | (416,455.818) | (0,+.274) |
| (.02,.5) | (.142481,.568570) | (17.164,228.026) | (+.524,+.026) |
| (.98,.5) | (.857519,.568570) | (814.836,228.026) | (-.524,+.026) |

No target at these edges, as expected; raw return result0 does not mean invalid
pointer. The bottom screenshot shows the pointer tip clipped at the viewport
edge; left/right screenshots visibly place it at the appropriate side. All
captures occurred during their leases. Evidence generated/ui-r581-{bottom,left,
right}.png and ios-runtime-r581.log. FPS23.6/30.0/32.7 remains failed performance.

Build24370 installed app SHA
418d3477202e96ef1f229f86cb150ea1d11e1135c2c2ef675b8e217c6c11710c.
Hook sanitizer and inverse/camera regressions pass. Runtime66373/session31652
clean stop10:28:09.851 failed=0; sole Simulator shell. Normal/device default is
still20 degrees. Next configuration-aware touch mapping integration, preserving
Classic Pointer, explicit A/B and cancellation. Full motion/scene/device/tap
acceptance and performance remain open; three points are not every context.

## R580 first live inverse-coordinate verification

Simulator-only launch flag `GalaxyPadDevPointerPitch22` adds Total Pitch22 to
the existing generated mobile profile; normal/device template remains unchanged.
Built/installed app SHA
c90ab8764d798e99834d33113c400932e8e1fb6cb4925fc1e3cc350e76181e5c.
Both launch log and generated WiimoteNew.ini confirm22; same observer module.

For intended normalized target(.38,.64), sent the R579 inverse input
(.411593,.685748). Native file1 actor81144cc8 hit reports past/current
(315.896,291.972), both valid; filtered(-.240635,.280579), unchanged calibration.
Expected screen position at832x456 is(316.160,291.840): errors(-.264,+.132)
logical pixels. This confirms one settled live inverse target, not a full-screen
grid, touch gesture, timing bound or tap permission.

Evidence generated/ios-runtime-r580.log and ui-r580-hover.png (verified pointer
over Mario/file1,27.3FPS). Initial ui-r580.png captured after lease expiry and is
NOT hover proof; repeated pointer-only lease captured the corrected image.
No A after title A+B, no save creation. Mobile input regression passes.
Runtime65791/session57265 clean stop10:21:15.821 failed=0; sole Simulator shell.
Next verify bottom/edge live positions and integrate configuration-aware pointer
mapping before context-gated tap work. Do not promote22 or claim performance.

## R579 bounded inverse and full-viewport coverage candidate

Added shared `GalaxyPadPointerInverse.h`: normalized target to host input through
a caller-supplied forward model, capped at75 evaluations, finite/domain checks,
singular/unavailable model rejection and no unverified last-iterate return.
It does not inject input, alter guest state or establish target readiness.

`tests/test-pointer-camera.py` now tests this solver against the actual camera
projection plus the R578 neutral-orientation WPAD/KPAD model. Integer camera
pixels required a fixed small-neighborhood check after Newton iterations; the
same error threshold is retained, not expanded until every case passes.
Tolerance0.0015 normalized corresponds to1.248 logical pixels at width832.
The initial0.001 threshold was below half a typical camera quantization step
(~0.00222), and rejected otherwise useful solutions; tight trial log retained.

- Pitch20:420/441 viewport-grid points pass; all21 bottom-row targets reject,
  with best sampled residual0.03724–0.04250 (not negligible numerical noise).
- Pitch22 and24:441/441 pass the same accuracy bound, including corners.
- File1/file2/Play targets, invalid/nonfinite/out-of-range targets, missing model,
  singular model, bounded evaluations and accepted-result residual checks pass
  ASan/UBSan. The R578 live sensor fixture still passes unchanged.

Evidence `generated/pointer-inverse-r579.log` and initial
`generated/pointer-inverse-r579-tight.log`. Pitch22 is the smallest tested
full-viewport candidate, not a proven minimum. No app/configuration/module change,
no runtime launch, and no Direct Touch acceptance. The forward test assumes the
observed neutral horizons, sensor offset0.1m and scale2.272727; it is not a general
motion/tracking model. Next live-verify the22-degree configuration and inverse
coordinates, then wire only behind configuration/context/processed-position
checks. Classic Pointer and explicit A/B remain intact.

## R578 live orientation closes the sensor-Y discrepancy

Read-only conversion-input snapshot added at the existing query entry. Exact USA
loads identify direction, reference/acceleration horizons, regular points and
filtered position. Missing/nonfinite data rejects the snapshot; sanitizer tests
cover malformed input and entry-time retention. No target-validity assumption.

At host (.38,.64), live file1 hit reports:

- direction (.999973,-.007299), reference (1,0), acceleration (0,-1);
- regular points (.006836,-.262695) and (.274414,-.264648);
- filtered position (-.323968,.142360), processed screen (281.229,260.458).

The R576 formula reproduces filtered XY within 1.1e-6 using six-decimal log
values. Applying the reference screen formula at 832x456 yields
(281.229497,260.457848), consistent with logged screen coordinates. Dimensions
here are a consistency check, not a new live render-mode field measurement.

An apparent mismatch with R573 camera rows was a missing WPAD parsing step,
not evidence that host Y should be inverted. Retail `__parse_dpd_data` performs
767 minus decoded Y at 804DF030 (extended), 804DF1B4/804DF1F4 (basic). Raw DOL
instruction checks now cover these operations. Applying that transform and KPAD
normalization to the actual camera projection's (652,519)/(515,518) matches both
live regular points within 1e-6, in reversed object order. The updated camera
test captures this fixture under sanitizers. Full tracking/order logic remains
outside the probe; do not make an input-axis patch from the old discrepancy.

Evidence: generated/ios-runtime-r578.log, ui-r578.png, pointer-camera-r578.log,
pointer-contract-r578.log, pointer-hook-r578.log. Screenshot shows file1 hover
and26FPS; performance remains failed. Runtime64595/session98723 stopped cleanly
10:08:42.213 failed=0. Next bounded inverse mapping against this verified forward
path, with regular-point validity/context checks; Direct Touch remains unwired.

## R577 emitted position-filter execution

`tests/probe-kpad-filter.py` executes accepted generated labels 8044FB60 through
8044FC9C with bounded memory and finite FP/sqrt doubles. All 84 cases pass
ASan/UBSan: both modes, zero/nonzero radius, below/on/above radius, and three
sensitivities. The R576 conversion test still passes after sharing its harness.
Evidence: `generated/kpad-filter-r577.log`; generated source identity unchanged.

For distance d, radius r, sensitivity s, the movement multiplier is:

- Mode 0: s when d >= r; otherwise s * (d/r)^4.
- Mode 1: s * (d-r)/d when d > r; otherwise zero.

Thus mode 1 has a true dead zone; mode 0 slows sharply near the destination.
This does not prove repeated floating-point convergence, tracking or FPSCR
equivalence. No filter is bypassed or guest input state rewritten.

The read-only calibration snapshot now includes mode at KPAD +0x1be8, verified
by exact retail instruction 8044FB88. Missing/unknown mode fails closed; tests
cover both modes, malformed values and entry-time snapshot retention.

R577 live capture reports mode 0 at title and file1 hover, with the same center,
scale, radius and sensitivity as R575. File1 actor81144cc8 returns a hit with
past/current (281.229,260.458), both valid. `generated/ui-r577.png` visibly confirms
the hover during the pointer lease and reads 34.5 FPS. Title's earlier ~57 FPS
does not establish performance improvement. No A was injected after entering
file select, no save was created, and no Direct Touch behavior was enabled.
Runtime PID63970 stopped cleanly at10:02:16.246 (failed=0). Next capture active
orientation inputs and validate inverse mapping; full goal/performance remain open.

## R576 emitted conversion block execution

tests/probe-kpad-conversion.py extracts accepted generated labels8044FA6C through
8044FB2C without editing them. It compiles the block under ASan/UBSan with bounded
test memory and explicitly limited finite float arithmetic doubles, comparing
1000 varied normalized orientations/offsets/scales to the midpoint/rotation/scale
formula. Result agrees within2e-6; PC reaches expected last instruction.
Evidence generated/kpad-conversion-r576.log; source SHA
38bbbb86262d98f6c015062e83c8edbd47bfbca11c7dc0967c8156fec9e3ce6a.

For regular-point midpoint m, sec direction s and reference horizon h,
d=dot(s,h), c=s.x*h.y-s.y*h.x. Rotate m by [[d,-c],[c,d]], subtract from
center and multiply by scale, then apply [[-a.y,a.x],[-a.x,-a.y]] using the
accXY horizon a. The probe varies all these components, rather than assuming
neutral orientation. It does not execute object tracking, position filtering,
or the real floating-point exception/status helpers; no full SDK/CPU equivalence
or inverse touch calibration is claimed. This private-artifact probe is explicit,
not silently added as a clean-checkout test requiring a generated module.

Next establish filter behavior and active orientation inputs before applying a
bounded inverse. No product input/runtime settings changed; no game active.

## R575 live KPAD calibration and logical width

Installed R574 app with same native module; PID62707/session91906, log
ios-runtime-r575.log. Title misses and file1/file2 hover hits consistently report
center(0,-0.2), scale2.272727, playRadius0.03, sensitivity0.5. Pointer-only sequence
(.38,.64)0.5s then(.61,.64)15s reproduces actor81192d08 and processed
(539.691,260.502); verified ui-r575-right.png visibly highlights file2.
No generic mod-fallback or pairing-invalid messages. Native Stop09:48:20.013
failed=0. No selection/new save or automatic input action was performed.

Raw getScreenWidth803F6B44 selects608(0x260) or832(0x340) via aspect predicate;
added exact checks to pointer-contract-r575.json. Do not normalize guest XY using
640 EFB width. This still does not prove a complete camera/KPAD inverse: horizon
orientation and filtering also participate. Located retail conversion region
8044FAD0–8044FB2C with center/scale loads and multiplications, and filter branches
8044FB98/8044FC18. These are next raw execution-proof candidates; not yet a full
equivalence test. KPAD reference source contains an explicit unresolved filter
comment, so it cannot be adopted as authoritative without the retail check.

## R574 active KPAD calibration reader

Traced WPadPointer reset BL803ABD7C to retail setter8044E33C. Its instructions
identify inside_kpads8061D340, channel stride0x1bf8, play radius+0x84 and
sensitivity+0x88. Sensor-height setter8044E580 writes center+0xb8/+0xbc and scale
+0xc0. These narrow raw-DOL contracts are now checked; no blanket SDK equivalence
or Japanese-address relocation assumption used.

ReadPointerCalibration reads only P1 exact-address fields and rejects missing,
nonfinite, nonpositive scale and negative radius/sensitivity values. Query-entry
frames snapshot optional calibration alongside past/current coordinates; bounded
return logging reports the active values. Sanitizer context/probe tests and app
build76531 pass. Candidate app SHA
f6a3caacdc1719b6d735d11958c9b4dc2dba754f862a0bdc211b88ee965a8d33.
Not installed yet; installed R571 shell remains stopped. No module rebuild.

Petari KPAD source suggests midpoint/horizon rotation, center subtraction, scaling
and position filtering, but its complete retail correspondence is unproven.
Next collect active calibration with the already verified two-target sample;
then verify the relevant retail conversion instructions before deriving inverse.

## R573 executable camera-stage isolation

tests/test-pointer-camera.py extracts the actual GetCameraPoints body and point
type/constants, compiling with the checkout's real Matrix.cpp under ASan/UBSan.
Neutral swing/tilt/IMU, settled pointing, yaw25/pitch20 and top sensor offset10cm
are explicit assumptions; this is not the whole running configuration or KPAD.
It verifies centered LEDs, offset response, hidden-camera rejection and unused
points, then reports the two R572 host positions. Output pointer-camera-r573.log:
(.38,.64) -> LEDs(652,519),(515,518); (.61,.64) -> (514,518),(377,519).
(.5,.5) with offset -> (580,452),(443,452), versus zero-offset y383.

Initial ideal-center assertion384 failed: actual quarter-turn float projection
and integer truncation produce383. Test now allows383/384 and requires both LEDs
agree. This is sensor quantization, not the larger touch calibration correction.
The camera stage can now be tested without runtime startup or module compilation.
Added to check-repository.sh; focused test passes, full suite not rerun here.

Next trace retail KPAD's LED-to-position conversion and its calibration parameters
against these values. Do not substitute sensor coordinates for guest-screen pixels
or assume the two live target samples define a general inverse.

## R572 live processed positions and calibration boundary

Installed appc0c1236f312cbfbad789dfcd63f1f712cfb9c0ec7d25829f396c5a1c50c7c160
with unchanged R562 native observer module. ios-runtime-r572.log attaches
09:32:07.103, reads controller809ebe90 and invalid zero samples at title. A+B
reaches file select. Sequential host pointer(.38,.64) for0.5s then(.61,.64) for20s
produces actor81144cc8 past(281.229,260.458), then actor81192d08
past(539.691,260.502). Verified screenshot ui-r572-right.png highlights file2.
No file-selection A was sent and no new save created.

At09:33:35.335 a hit still uses pastValid1 while currentValid0. This directly
demonstrates stale validity, not just a theoretical buffer offset. The two
coordinate pairs are correlations, not a calibration model or revision proof.
They do not equal simple normalized host coordinates times framebuffer size.

Source path explains why direct scaling is not a contract: Mobile input maps
normalized coordinates to Cursor axes; Cursor default total yaw25deg/pitch20deg
and vertical offset10cm feed EmulatePoint's virtual remote at2m. That path changes
angles (with acceleration when already visible), then camera/KPAD process the IR
data. It is not an absolute guest-screen coordinate setter. Need trace/calibrate
the actual camera/KPAD projection, not fit two points and declare touch accurate.

Clean stop09:35:29.363 failed=0. Next audit this coordinate path and establish a
validated mapping plus guest processed-sample acknowledgement. Native diagnostics
remain optional; no automatic taps or claimed FPS improvement.

## R571 bounded query-entry sample

ReadProcessedPointer resolves the exact P1 chain r13-14968 -> +0x20 -> +0x30 -> +4,
validated against retail director getter/controller indexing and query channel0.
It captures past/current XY and independent validity bytes, requiring mapped
aligned words, P1 channel, finite coordinates and boolean validity. Unknown chains
fail closed. Positions remain guest screen units; no host normalization assumed.

Native query frames now snapshot these values at entry and report them alongside
bounded return results. They do not reread the buffer at return. ASan/UBSan tests
cover malformed chains, missing words, NaN/infinity, channels and validity, plus
actual CPUState big-endian RAM decoding and snapshot retention after RAM changes.
App Release build65401 passes, build-app-r571.log. Not installed/live-tested yet.
No module rebuild or change to callback ABI, input masks, or automatic taps.

Next install this host with the already verified observer module and compare
past/current samples while moving between separated screen targets. Coordinate
agreement still cannot by itself establish revision identity for repeated taps.

## R570 retail pointer-buffer handoff

Exact-DOL instruction audit now verifies the query's target predicate receives
StarPointerController+4 (past XY), +0x14 past view distance and +0x64 world position.
The retail query checks byte+0x0c (past in-screen) directly. Petari's current
isInScreen helper instead uses an out-of-screen counter; do not transplant that
predicate into USA validation.

movement80384FF8 calls storeDataFromCallback80385034, storePastPointingData8038513C,
then updateDpdInfo803852BC. The first copies current XY+0x18/+0x1c and validity+0x20
to past+4/+8/+0x0c. The last loads new-position array+0x40 into current+0x18.
The called two-float copy body is audited too. Screen-position getter803FB5BC
independently returns controller+4. Evidence generated/pointer-contract-r570.json.

Consequence: observing newly updated current XY is insufficient to authorize a
tap against a past-position hit. This identifies a buffering boundary, not a
fixed wall-time delay or complete host-to-KPAD correspondence. Next correlate
actual past XY/validity at query with host input revisions; keep automatic input
disabled until scene readiness and identity also hold. No module rebuild needed
for this source-contract check; current app shell is stopped.

## R569 native observer runtime validation

Candidate c1c06e0a03ab0822120f855291abf195139299b924e9363eb71408a15d521421
with app522b0dd47cd0f1cefb83ce74b76cb0f0fd6c872fa15d037df4a140ed5818b0be
attaches successfully at09:18:21.149. Native entry/return callbacks report misses
at title and actor81144cc8/result1 at09:19:42.117 for file1 pointer-only hover.
CUA visibly shows the highlight; saved verified repeat is ui-r569-hover.png.
ui-r569-hit.png was captured after the first input lease expired and is not hit
evidence. Ordinary pre-aim+A selection and B return visibly work.

ios-runtime-r569.log has no mod fallback or pairing-invalid messages in this test.
Generic ModManager hooks remain disabled. This is native delivery evidence, not
zero observer overhead, whole-game coverage, performance acceptance, or proof that
the query consumed the latest host pointer revision. No automatic A/B injection.

Next: trace publication through input sampling/WPAD into the guest pointer update
before wiring queued taps. A host Device::UpdateInput snapshot is not proof of
guest consumption. Preserve the unknown-context rejection in DirectTap policy.

## R561 observer-only module extension

GalaxyPadNativeObserver.h/.c defines an optional export separate from ModManager.
No CPUState/module ABI change. Metadata contains exact DOL hash, CPU ABI/size and
intended sites803FB0EC/80178EC8. Host must verify this and emission coverage before
attach. Attach/detach occurs only with CPU stopped; callback is trusted/read-only,
user context must outlive execution. Rejection clears old registration. Sanitizer
tests cover the bridge; it is not linked into current modules or the app yet.

Do not treat hardcoded site metadata as proof that generated native paths invoke
it. Candidate build must add/audit the actual selected labels and preserve all
instructions/cycle accounting. Generic mod hooks/fallback guard stay untouched.

## R560 native label experiment

Isolated tests/probe-native-observer.py compiles the actual emitter after temporary
selected-label instrumentation. Synthesized code executes entries, fallthrough,
loop back-edges and local-return paths under ASan/UBSan with expected callback
counts, guest results and cycle charges. Null callback preserves results. Selected
functions use ordinary loops instead of outlined counted-loop helpers so sites
inside a loop are not skipped. Production codegen/guard/module remain untouched.

Before integration: observer-only capability (not arbitrary replacement patches),
coverage of exact named sites, no double dispatch callback, cache/module identity,
and real runtime proof. This does not establish host-pointer revision freshness.

## R558 live observer delivery and cost boundary

Opt-in Simulator DevPointerHooks, exact DOL gated, observes query803FB0EC entry
and return without changing guest state. Return80178EC8 matches raw BL80178EC4.
File1 hover visually agrees with actor81144cc8/result1; no-pointer misses observed.
Bounded pairing/output and actual-header sanitizer tests pass. This proves callback
delivery, not that the hit test processed a particular host input revision.

Runtime reports whole chunk803FB0A0–803FC0A0 forced to fallback by host-call range
guard. This is not acceptable as an unexamined normal-path cost. Keep diagnostic
flag off for performance comparison; investigate native named-site delivery,
preserving the guard until emitted code is proven to honor those sites. No A/B
injection or Direct Touch mode enabled. Evidence ios-runtime-r558.log.

## R557 built-in runtime API

Canonical ModernGekko0028 exposes RuntimeConfig::builtin_mods. Descriptors and
callbacks are linked into the app and must outlive Runtime. Empty preserves
directory loading; nonempty rejects mixed mod directories and returns a runtime
error on any descriptor validation failure. Core and app rebuild together pass.
No descriptor enabled yet. Exact DOL verification belongs to the Galaxy caller
before supplying hooks; title ID validation alone is not sufficient. Runtime
delivery, rejection integration and processed-pointer freshness remain unproven.

## R556 static hook route tested

ModernGekko ModManager already supports AttachedDescriptor entry/return observers.
New test compiles the actual mod_loader.cpp with dynamic loading disabled under
ASan/UBSan. Confirms wrong title/CPU ABI rejection, register-state preservation,
return-address plus stack-pointer matching, one-shot return observation and unload
clearing pending hooks. Observer mutation of r3 is restored: this route can read
the hit-test result, not replace it with an automatic A response.

RuntimeConfig currently exposes only mod_directories and Runtime::Create calls
LoadDirectories. Next expose explicitly attached built-in descriptors through
that existing manager, then validate exact-DOL query entry/return at runtime.
The test does NOT prove the installed AOT module yields at internal calls or
guest hit-test input freshness. Do not add a dynamic mod directory as a device
workaround or assume the query's input position belongs to the latest host touch.

## R552 live state evidence

Installed R551 candidate. Visible file-select→confirmation→B Back matches
current Nerves806a0114→0118→0128→0110→0114, consistent with pinned symbol names.
All remain pointer mode5. At field3744, pending0118 is already set while current
0114 and old item81144cc8 still report pointing. Confirmation retains that item
with invalid-select set (flags2). Thus mode/identity/pointing alone can authorize
a stale target during transition. Current+pending checks are required; sampling
still cannot supply complete epoch or pointer-input freshness. No automated
Direct Touch action enabled. Evidence: generated/ios-runtime-r552.log and live
CUA screen observations; no copy/erase/save mutation performed in this check.

## R551 selector substates

Petari's ordinary file-select and copy-select both update cached file hover.
Pointer mode5 alone cannot distinguish them. Added bounded actor Spine reader
(actor+0x50, current+4, pending+8); exact DOL LiveActor/getCurrentNerve instructions
verify that a pending Nerve overrides current during transition. Probe logs both
on change. Tests and Release build pass; not installed/live-validated yet.
Sampling these fields still cannot certify that no transition occurred between
samples or that a pointer revision has reached the guest hit-test.

## R550 queued-tap policy (not wired to runtime)

`apple/shared/GalaxyPadDirectTap.h` provides a CPU-thread-owned, one-shot queue.
Requests bind gesture ID, scene/lifecycle epoch, pointer revision, intended target
and monotonic deadline. Unknown context, epoch change, newer pointer revision,
confirmed different target, cancellation and expiry discard the request. Older
observations cannot authorize it. Readiness requires the expected target and A
released; consumption cannot repeat. Invalid/replayed replacements clear old work.
ASan/UBSan tests cover these cases; existing input mixer tests still pass.

This policy does not read memory or inject buttons and is deliberately not
connected to the app. The R549 VI probe cannot certify that a cached hover has
processed a particular input revision. Integration must establish that at the
guest input/hit-test boundary and provide a real scene epoch, not equate a VI
counter, host publication or unchanged mode5 with freshness. Intended-target
resolution and ordinary menu/submenu readiness remain required. Full Direct
Touch includes all PRD contexts, not merely file-select planets.

## R549 file-item observation

Mode5 request owner provides a bounded route to FileSelector. Read16 request
pointers at controller+0x0c, records owner+0/mode+4; require one unambiguous owner.
Then selector+0xbc is its cached hover item. Item bytes+0x144/+0x145 report
pointing/invalid-select. The exact-DOL audit verifies request-array bounds,
record stores, mode5 argument and cached-item load. Sanitizer tests cover hover,
invalid-select, no hovered item, wrong mode and ambiguous owners.

Extended opt-in probe logs selector/item/flags changes. Flags bit0=pointing,
bit1=invalid-select, −1=unknown. Cached hover is not permission to tap: it can lag
new coordinates and belong to a previous interaction. No A/B injection added.

## R548 opt-in live probe

Simulator launch flag `-GalaxyPadDevPointerContext YES` registers a scoped
vi_end_field_event listener around Runtime::Run. The event runs on the CPU thread;
callback checks that and samples every sixth field, reading words from bounded
MEM1/MEM2. Exact main.dol size/SHA256 is checked on worker before registration.
Logs only changed controller identity/raw mode; invalid chains log mode−1.
No guest writes, instruction-level trace, UI-thread guest access, or A/B injection.
Listener is destroyed when runtime returns. Normal launches and device builds
do not register it. Mode alone still does not mean an actionable target exists.

Live R548: title screenshot corresponds mode4/object8091f3d8 at field1398;
field1530 unknown then1536 mode4 again. A+B→file select visibly corresponds
mode5 atfield2946 with same object. Thus controller identity alone is not a
scene epoch; mode and host lifecycle changes must invalidate queued actions.
Brief unknown observations must fail closed. Target readiness still separate.

## R547 context reader (not yet connected)

Exact-DOL audit now also verifies getter803FA3E4: load singleton at r13−14968,
then offsets12→4→8; mode load+0xd0 verified at803FCC74. Added read-only
GalaxyPadPointerContext.h with injectable big-endian reader, cached MEM1/MEM2
bounds/alignment checks and invalid/missing/mode-range rejection. Return includes
controller identity and raw mode, NOT permission to tap. Caller must establish
exact DOL identity and read on CPU thread. No UI-thread guest memory access.
Sanitizer regression test-pointer-context.sh passes mixed-region chain, absent
objects, invalid/alignment/overflow addresses and invalid mode cases.

Not integrated into host/core yet. Next connect to a bounded CPU-thread context
observation point (not every-instruction instrumentation), then compare scene
transitions visibly. Even a verified mode does not establish a specific target
is pointing or that an old tap belongs to the current scene.

R546, 2026-09-08. Classic Pointer remains the only implemented product mode.

## Evidence

R545 immediate pointer+A failed;0.2s pointer lead-in then A selected file1 and
Play. This alone does not establish a minimum latency or justify a timer-based
product shortcut.

Petari source explains an edge/readiness dependency:

- FileSelectItem::updatePointing requires !mIsInvalidateSelect and _144 before
  calling MR::testDPDMenuPadDecideTrigger. onPointing/offPointing set/clear _144.
- ButtonPaneController::trySelect requires its Pointing Nerve and an enabled
  decide animation before that same predicate.
- GamePadUtil maps this predicate to P1 trigger A, not held A.

The [community symbol finder](https://mariogalaxy.org/symbols) warns that
non-Korean maps may contain errors. Candidate USA names came from
[Bussun USA symbols](https://github.com/SMGCommunity/Bussun/blob/78f4a04ce85964440442101c606ba49fcf1c634e/symbols/USA.txt),
commit78f4a04ce85964440442101c606ba49fcf1c634e. Download kept ignored at
generated/bussun-usa-symbols-r546.txt, SHA256
4efed2da6a3cd9bd10f998f5499fa827141c1e1a0706e5fff4194753de26eaf9.
No injector, executable patch, or replacement game data was downloaded.

`python3 scripts/audit-menu-pointer-contract.py` verifies raw instructions from
the hash-gated supported DOL, not merely names or AOT comments:

| Check | Exact USA evidence |
|---|---|
| File item invalid/pointing | lbz at80178EF4/80178F00, offsets145/144 |
| File item A predicate | bl80178F0C→803D2B6C |
| Menu button pointing Nerve | bl8034BF8C→803A29B8 |
| Menu button A predicate | bl8034BF98→803D2B6C |
| Predicate P1 channel | li r3,0 at803D2B74 |
| Predicate WPad/trigger | bl803D2B7C→803AB568; bl803D2B84→803AB094 |

These are narrow verified instruction contracts, not whole-function equivalence.
Public symbols identify the latter callees as getWPad/testTriggerA; the exact
call operands and P1 argument are independently verified. Runtime object
identity, scene lifetime, and target readiness still need observation.

## Next implementation boundary

Probe target readiness and stable target identity at these named sites first.
Do not turn the shared menu A predicate into an unconditional queued tap: it is
used by multiple screens, and stale taps must not cross scene/menu transitions.
Any eventual queued tap must match its current pointer target/context, consume
once, expire/cancel on finger cancellation or host lifecycle changes, and preserve
ordinary A/B behavior. Keep shooting, Pull Stars, cannons, sling pods and bubbles
as separate audited contexts; no blanket A/B and no forged pointer depth.

No Direct Touch UI switch or runtime hook was added in R546. Current running
candidate is R545/PID47040, unchanged, at opening story.
