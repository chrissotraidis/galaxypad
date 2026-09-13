# iPhone performance second pass

## Observed result and evidence limits

The user reports build 6 holding approximately 60 FPS on iPad, with occasional
dips, but approximately 32 FPS on iPhone 14. This is hardware feedback, not a
matched workload comparison: scene, camera, thermal state and aspect ratio differ.
The user reports switching the phone to 16:9. It would be incorrect to extrapolate
a precise CPU or GPU speed ratio from those observations.

The fresh phone logs under the private `generated/runtime/hardware-pass2-20260913/`
directory confirm that detailed frame logging was disabled. They contain lifecycle
and startup records but no timed frame/CPU/thermal/EFB/audio windows. The copied
GFX configuration confirms internal resolution 1, hybrid asynchronous shaders,
shader cache, and software vertex loading. The absence of performance records is
an observability defect; it is not evidence of zero audio underruns or low CPU use.

The phone already renders at 1× internally, and `GalaxyPadMetalView.mm` uses one
output pixel per UIKit point. Blindly reducing a Retina scale is therefore not an
available improvement. Build 6 already carries the audited PGO game module. The
current host explicitly enables CPU/render dual-core operation and preserves real
EFB depth access, which Pull Stars require.

## Research and ranked experiments

| Priority | Hypothesis | Evidence and experiment | Acceptance boundary |
| --- | --- | --- | --- |
| 1 | Serial guest execution or portable vertex conversion dominates the phone | Capture the current slow physical scene with Time Profiler; distinguish CPU-thread execution, rendering-thread conversion, and blocked waits. Prior iPad profiles implicate generated game code plus `Pos_ReadIndex` and indexed normals, but do not establish today's iPhone attribution. | A sampled hotspot selects work; only a matched hardware comparison establishes gain. |
| 2 | A few fixed vertex formats dominate portable conversion | Count processed vertices by existing VAT/VCD format key in an isolated diagnostic core, then AOT-compile direct converter combinations for a measured high-coverage format, preserving the generic loader fallback. | Byte-identical output, consumed input and skip/cache state across indexed/direct/boundary fixtures, then actual-policy object inspection and gameplay A/B. No executable-memory generation. |
| 3 | EFB depth dependency stalls remain costly on A15 | Compare delta EFB service time with frame windows; if large, use Metal System Trace to distinguish queue backlog, CPU scheduling and GPU execution. | Preserve same-frame depth correctness. No fake depth, stale readback or blind cache-deferral hack. |
| 4 | The generated game has excessive state/memory traffic | Use physical sampled stacks and existing heavy-scene instruction mapping to select a meaningful data-lifetime boundary. Existing native mapping assigns much weight to loads, but cannot classify most origins or equate weights with removable latency. | Strict floating-point, interrupt/observer/exception and entry semantics must survive differential tests before costly module rebuild. |
| 5 | Sustained thermal pressure or GPU work causes later dips | Retain thermal/low-power and frame windows through the same scene over time; use GPU trace if CPU samples do not account for the delay. | A thermal enum alone is not CPU frequency. Lower resolution only after a GPU-throughput bottleneck is demonstrated. |

The strongest structural difference from an ordinary Dolphin ARM64 configuration
is the portable vertex loader. `ref/ModernGekko/src/runtime/dolphin_runtime.cpp`
selects it for iOS because the alternative generates host executable code at
runtime. Ahead-of-time specialization can remove per-stage indirect calls for
known formats without introducing JIT. It is a larger but testable improvement;
reordering the same function-pointer loop is a different, already rejected idea.
The separate controls/vertex research agent owns the detailed feasibility audit.

Apple recommends identifying the actual CPU/GPU dependency and thread state with
Instruments and Metal traces before selecting an optimization. GPU completion,
CPU execution and presentation are different events; our existing frame event
counter does not measure display completion.
[Apple Metal performance analysis](https://developer.apple.com/documentation/xcode/analyzing-the-performance-of-your-metal-app)

More threads are not automatically helpful. Apple's game scheduling guidance
shows that tiny jobs repeatedly signaling and waiting can lose their parallelism
to wake-up and synchronization overhead. Useful work must be coarse enough to
amortize those costs. The existing guest CPU and rendering split is an appropriate
starting point; introducing per-vertex worker jobs into shared loader state is not.
[Apple CPU job scheduling](https://developer.apple.com/videos/play/tech-talks/110147/)

Dolphin documents why GPU readbacks force coordination and why caching neighboring
EFB pixels reduces repeated synchronization. That supports inspecting actual
readback dependencies, rather than treating a different blocking API as a cure.
Our earlier standalone wait experiments failed to reproduce the game's expensive
wait. [Dolphin VideoCommon and EFB caching](https://dolphin-emu.org/blog/2019/04/01/the-new-era-of-video-backends/)

Hybrid ubershaders already address compilation interruptions while specialized
shaders become ready. Substituting synchronous compilation can exchange one form
of slowdown for visible stalls; it is not a blanket performance fix.
[Dolphin ubershader design](https://dolphin-emu.org/blog/2017/07/30/ubershaders/)

## Implemented diagnostic correction

Normal sessions now collect a summary approximately every 15 seconds of active
emulation. The existing switch is labeled **Detailed Performance Logging (Next
Launch)** and retains five-second windows plus opt-in RemoteIO PCM inspection.
The default does not scan audio samples: it reads existing cumulative mixer and
runtime counters, and records that output counters are unavailable.

Summary collection uses the existing one-second UI observation, with the same
pause/background reset and original monotonic timestamps. At most four formatted
lines are handed to a serial utility queue. Redaction, timestamp formatting and
file persistence happen there. A single nonblocking slot bounds all pending and
writing summary work; if the writer is busy, a new window is discarded and a
later accepted batch reports the skipped count. The ordinary one-megabyte log
rotation and reviewed-report privacy filter remain in force. Nothing is uploaded.
Log line timestamps reflect persistence; `mono` fields identify the observation.
The newest batch may not yet be present if the app is killed or a report is
exported immediately; this is not a lossless profiler.

This supplies evidence for the next iteration. It is not an FPS optimization
claim. At normal cadence there are at most 16 summary lines per minute, rather
than enabling the PCM scan or per-frame disk writes on the lower-power phone.
The sampling/formatting cost remains nonzero and a physical on/off overhead check
is still required before describing it as imperceptible.

Validation: main and diagnostic translation units compiled against both the frozen
Simulator and iPhoneOS build-6 inputs. The native diagnostics integration test passes
redaction, issue/report bounds, rotation, and a new deliberately blocked-writer
check: submission returns, the second batch is dropped, the first is sanitized,
and the drop count is retained. Artifacts are under
`generated/tests/performance-pass2/`. No shared core artifact, hardware process or
saved game/configuration was changed by this subtask.

## Closed experiments and next decision

Do not repeat unchanged O3, heavy-route PGO, dispatcher LUT/preserve-none,
paired-single rounding, MEM1-first helper, blind QoS, simple vertex-stage unroll,
Metal completion primitive, or prefetch-history experiments. Their rejected
results are retained in `docs/RESUME-2026-09-11-GALAXYPAD-IPAD.md`,
`docs/HEAVY-NATIVE-PROFILE-R899.md` and the first-pass research document.

The physical profiler attach attempted during this pass did not yield usable
attribution: the parent task reports that Instruments listed the devices offline
while CoreDevice saw them available, and the Time Profiler attach timed out.
No CPU/GPU bottleneck is inferred from that tooling failure.

The next performance patch must follow the actual slow-phone profile. If vertex
conversion dominates, obtain format coverage and implement one AOT specialization.
If guest work dominates, select a state-lifetime mechanism from the physical
profile. If blocked GPU service dominates, inspect Metal dependencies. Keep the
currently successful iPad build as control, retain exact source/module identity,
and compare fixed scenes with audio and frame-gap deltas before promotion.

## Build 7 integration and hardware deployment

Build 7 includes the quick-tap Pause/+ correction, clearer ball/ray tilt
instructions, controller handler/profile recovery, sparse performance summaries
and the bounded read-only pointer observer. The complete iPhoneOS and Simulator
host source hashes match. Both were rebuilt against their accepted frozen
audio-v8 cores; the hardware package retains the device PGO module used by build 6.

Both physical devices report installed version 0.1.0 build 7 and running app
processes. In-place installation preserved all 33 protected iPad save/settings
files and all 54 iPhone files byte-for-byte before launch. Private receipts:
`generated/runtime/hardware-build7-20260913/`. This is a control/diagnostic update,
not a measured performance improvement.

The interim Simulator integration completed the 121-star Observatory route.
Normal, non-detailed operation produced frame/CPU/thermal/EFB/audio summaries
and live gameplay pointer records; output PCM counters correctly remain unavailable.
The captured source predates only the later controller-recovery integration.
Two concurrent Simulator workloads were active during part of this validation,
so its frame rates are not used as benchmark evidence.

Physical Time Profiler capture remains unavailable: xctrace lists both devices
offline and timed out waiting for the phone, while CoreDevice and xcdevice
report connected/available, unlocked, wired devices with usable developer services.
No physical CPU hotspot is claimed from that failed capture.

## Controller recovery incident

The latest iPad build-6 log records disconnection at 07:49:04 UTC and reconnection
at 07:49:14, followed by no raw button transitions before the app restart at
07:50:57. Button transitions then resume. Because raw-button logging occurs
before neutral-input gating, this does not by itself implicate the neutral gate.

Reconciliation previously returned immediately when the GCController object
identity was unchanged. It now also checks the extended profile and handlers,
rebinds a replaced profile or missing callbacks, and rejects stale callbacks by
generation. Intact handlers retain queued Menu/View edge state. New readiness
and axis records help distinguish neutral gating from absent delivery.
Production adapter tests cover same-owner repair, profile replacement, ordinary A
input, stale callbacks, held-button suppression and existing pause behavior.
The physical incident cause and recovery after a long idle still require testing.

## First hardware diagnostic records

The first build-7 log pull verifies that default summaries work on both devices.
The iPhone reports thermal state 2 (serious) throughout the captured startup/menu
intervals, with approximately 59.8–60.0 frame events/s after startup. Those
intervals are not the reported slow gameplay scene. The iPad also reports state 2.
Apple documents that serious thermal state can reduce performance; it does not
reveal CPU frequency or establish the cause of the earlier 32 FPS report.
[Apple thermal state documentation](https://developer.apple.com/documentation/foundation/processinfo/thermalstate-swift.enum/serious)

After startup, the phone's observed DMA underrun/full-drop totals remain fixed
in the captured window, while the iPad shows additional full-queue drops across
its later activity. Neither finding establishes audible quality. Startup maxima,
pause/scene transitions and cumulative values must be separated before attributing
a hitch to active gameplay. Private immutable records are under
`generated/runtime/hardware-build7-20260913/live-logs/`.

A later iPad capture records active intervals around 46–56 frame events/s,
with serious thermal state and approximately 134–151% process CPU (one core
is 100%). In those contiguous windows, EFB service deltas consume roughly
27–79 ms per elapsed second. This bounded counter does not account for the
whole slowdown. One interval adds 59 DMA underruns alongside full-queue drops;
other slow intervals add no underruns. These are scene-unlabeled user activity
records, not a build-6/build-7 comparison or proof of diagnostic overhead.
Receipts: `later-logs/ipad-slow-windows.json` and the full runtime log.

The host's Instruments diagnostic identifies `kAMDNotConnectedError`
(`0xe800000b`) on its MobileDevice session path before attach. Xcode and
Instruments versions match. Reconnecting the device cable is the next
non-destructive remedy; on-device Performance Trace with Power Profiler is
an alternative that can include lower-rate CPU samples. No device settings
were changed for that alternative.
[Apple Power Profiler workflow](https://developer.apple.com/videos/play/wwdc2025/226/)

## Twenty-minute iPad session and current Beach Bowl checkpoint

The later build-7 iPad14,5 log contains 68 summaries from the approximately
19-minute session beginning 07:59 UTC. Counter analysis uses each frame window's
monotonic endpoint and duration, not the asynchronous disk timestamp. Sixty-four
windows have contiguous counter predecessors and no app-native menu, UI block,
or app-pause flag. Every such record reports thermal state 2 and **active render
scale 2**. The earlier phone observation of 1× does not describe this iPad run.

The longest contiguous run below 55 frame events/s spans 94.60 seconds at
50.30 events/s; its worst 15.80-second window is 46.01. Process CPU averages
142.86% of one core over that run. It adds 463 gaps of at least 33 ms and no
additional gaps of at least 100 ms. EFB service deltas are 42–56 ms per elapsed
second, averaging 51 ms/s. One of those windows adds 59 DMA underruns; the three
slowest windows in the entire capture add none. Audio production failures do
not consistently accompany the measured slowdown.

A later 47.40-second run averages 53.02 events/s, CPU 164.71%, and EFB service
59–136 ms/s, without new DMA underruns. Across this scene-unlabeled capture,
windows at least 58 events/s have more measured EFB service on average
(76.63 ms/s) than windows below 50 events/s (42.55 ms/s). This is not a controlled
correlation experiment, but it directly argues against treating the EFB counter
alone as an explanation for every slow interval. Serious thermal state stays
constant across fast and slow activity; it cannot identify clock changes.

The live mirror shows Beach Bowl Galaxy / Sunken Treasure at the original
game's pause screen. These logs do not label historical scenes, and app-pause
flags cannot distinguish that in-game pause screen. Consequently neither the
final approximately 60-events/s records nor an aggregate startup-to-end mean
establish performance during the reported Beach Bowl gameplay.

The next reversible resolution experiment is justified by the newly verified
**2× iPad setting**, but has not been run: after preserving progress and ending
the current session deliberately, compare 2× / 1× / 2× at the same Beach Bowl
position, camera and active gameplay, with equal warmup and similar thermal
conditions. Resolution is selected when the runtime starts; a settings toggle
without restart is not an active-resolution comparison. A clear repeatable
improvement would establish resolution sensitivity, not by itself isolate GPU
execution from CPU/backend/EFB costs. Keep real depth reads and the unchanged
core. A successful CPU/GPU profiler attach to the current slow scene remains
preferable for selecting a code optimization; the failed Instruments connection
is not a bottleneck measurement.

Private reproducible interval analysis and complete per-window deltas are in
`generated/runtime/hardware-build7-20260913/ipad-20min/{analyze.py,analysis.json}`.
No physical session, save, settings, or core was changed for this analysis.

### Audio interruption recovery candidate (build 8)

The temporary QuickTime mirror introduced an audio interruption at 08:20:06 UTC.
The subsequent log retained `interrupted=1` without an interruption-ended record,
even after closing the preview and quitting QuickTime. Raw controller button
changes still arrived at 08:25:02. This is a separate lifecycle failure from the
build-6 idle disconnect/reconnect report, which had no audio interruption.

Build 8 adds guarded audio reacquisition when returning to the foreground,
dismissing native pause, or requesting controller View/Resume while interrupted.
It clears the interruption latch only after audio activation succeeds. Failed
activation preserves the pause; explicit native pause and background state block
recovery. The production-method test covers those cases, including a missing
ended notification. Both device and Simulator hosts compile against the unchanged
accepted audio core. The device candidate is staged with the existing PGO module
and development signed for both devices. It has **not been installed**: build 7
and the current iPad session remain in place.

This is not verified recovery from the reported idle-controller bug. Existing
raw log `ready` means the pause buttons are released, not that gameplay is allowed.
After a reset the input adapter also requires all controls to become neutral;
a stuck button or drifting stick can therefore block gameplay. The latest
pre-mirror build-7 record did rearm, so this mechanism is a hypothesis rather than
a diagnosis of the user's failure. Further changes need a reproduced idle window
with controller state and lifecycle gates captured together.

The isolated pointer candidate now maintains its neutral calibration through
Spin. Sparse Simulator samples observed up to 2.90 logical pixels of error,
versus 79.81 in the first candidate; this does not establish continuous-motion
accuracy or physical-device behavior. See `experiments/pointer/README.md` for
coverage and remaining reachability/context limits. Neither that prototype nor
the vertex experiment has been promoted into the hardware core.

### Reconnected preinstall capture

The fresh build-7 capture through approximately 08:46 UTC preserves the earlier
slow intervals but does not reproduce their sustained severity near the latest
reported input incident. Between approximately 08:43 and 08:46, contiguous
windows are approximately 59.93–60 events/s except one 15.60-second window at
57.31, with CPU 173.32% and EFB service 80.5 ms/s. That interval adds no DMA
underruns or gaps of at least 33 ms. A preceding 58-events/s window crosses an
app lifecycle discontinuity, so its cumulative-counter deltas are excluded.
Subsequent approximately 60-events/s windows report CPU around 89%; historical
scene identity remains unknown and may include the original game's pause menu.
The thermal transition from 0 to 2 near 08:42:43 also occurs while approximately
60 events/s continues, rather than establishing a thermal slowdown at that point.

After the user reconnected the cable, `xctrace list devices` still listed both
physical devices offline. No profiler attach was attempted during installation.
The late data provides no new measured basis for a speculative core change;
retain the fixed active-scene resolution comparison and successful profiler
attribution as the next performance gates. Private records are under
`generated/runtime/hardware-build8-20260913/preinstall-reconnect/`, including
`late-window-summary.json` and full monotonic-window analysis.

### Controller reconnect candidate (build 9)

The user's next report was stronger than a missing controller: after reconnect,
Mario kept moving in one direction. The captured 08:44 disconnect/reconnect
sequence does clear ownership and rearm from neutral, so the available log cannot
attribute that runaway to stale enumeration alone. Its button records lack axis
values; absence of a button change does not establish zero movement.

A production-adapter regression reproduced another concrete unsafe boundary:
explicit disconnect was previously ignored when framework enumeration retained
the same controller and profile. The new handler immediately excludes the
explicitly disconnected owner, clears movement and invalidates queued callbacks.
A connect event rebinds even an unchanged owner, suppressing cached held axes until
neutral before accepting fresh movement. Tests cover lagging enumeration, old
callbacks, neutral release, fresh movement, and unchanged-owner connect. Both
controller suites pass; device and Simulator hosts build against the unchanged
accepted core. Existing button-change records now include stick axes and actual
input/lifecycle gates without periodic per-frame logging.

Build 8 was installed in place on iPad with all 33 protected files byte-identical
and its logs preserved before preparing build 9. The user explicitly authorized
the hardware update and restart. These controller changes do not establish a
performance improvement or verified resolution of the observed runaway; those
remain physical gameplay checks.

### Build-9 startup controller failure

After installation the user reports Xbox A/B cannot start the game. Captured
logs in `generated/runtime/hardware-build9-20260913/controller-start-failure/`
show one GCXboxGamepad acquired at 08:51:10, neutral readiness becoming true,
and no raw-button changes through the follow-up capture. Runtime frame events
continue near 60 with no native UI/pause flags. Thus the captured failure is
upstream of a demonstrated guest-button mapping failure; the log has not recorded
the requested physical presses. This does not by itself identify the failed
framework/transport boundary. The app was deliberately left running.

A bounded system-log capture adds only GameController analytics messages, not
proof of delivery to the selected profile. SDK review confirms background-event
monitoring is ignored on iOS; wireless discovery is for discovering controllers,
not repairing an already listed profile. The implementation already uses the main
handler queue and polls at 60 Hz. No further speculative build was installed.
The pending diagnostic is Home Screen then foreground return without restarting,
followed by A/B, to test whether event delivery recovers with focus/lifecycle.

### Guest Wiimote interruption and controller event routing (build 10)

The user clarified that the guest displays the Wii Remote communication warning
and asks for A with the Nunchuk stick released after idle. Source inspection
finds that Bluetooth input polling continues while the emulated Wiimote is
inactive (`BTEmu.cpp`). After a one-second cooldown, `WiimoteDevice::PrepareInput`
reads currently pressed mapped buttons and `UpdateInput` reconnects on a button.
Missing physical A delivery therefore also explains an unwakeable guest warning;
no independent missing-wake implementation was found in that path.

The root game view used plain UIViewController. Apple's shipped
`GCEventViewController.h` recommends its specialized root controller for clients
of GCController and describes the controller-to-UIKit versus controller-profile
routing choice. Build 10 changes the root superclass to GCEventViewController and
explicitly sets controllerUserInteractionEnabled to NO. Touch interaction stays
available; the existing adapter owns Menu/View. This is a focused correction to
event routing, not proof that it resolves every idle failure.

Both device and Simulator builds succeed with the unchanged core and PGO module.
The necessary hardware check is raw A delivery followed by guest recovery with
sticks neutral, then another idle/reconnect reproduction. We did not inject
synthetic buttons or disable guest timeout behavior.

Reference: [Apple GCEventViewController documentation](https://developer.apple.com/documentation/gamecontroller/gceventviewcontroller).

Hardware result: the user reports build 10 still does not accept Xbox A/B after
startup. Its postinstall logs again show ownership and neutral readiness, without
raw button events. The routing correction is **not a sufficient fix**. A controlled
physical controller reconnect without restarting the game has been requested;
the comparative result is pending. Keep this negative result distinct from
compile/sign/install success.

### Controlled reconnect versus full relaunch result

User feedback and the captured pair in
`generated/runtime/hardware-build10-20260913/user-relaunch-recovery/Logs/`
agree: Xbox disconnected at 09:06:46 and reconnected at 09:06:55; ownership cleared
and neutral readiness rearmed, but no button events followed before app shutdown.
The next app session starts at 09:07:10 and records A/B presses at 09:07:13 with
both sticks neutral and gameplay/input readiness true. The user confirms play
works again. This is a recovered session, not proof of long-idle persistence.

The failure survives hardware reconnect within the app process but clears after
full app relaunch. A stale per-session input-delivery state is therefore a stronger
lead than A/B mapping. The initial failing launch was tool-driven and the working
relaunch was user-driven; launch method, connection timing, and process reset are
confounded, so do not attribute the cause to devicectl without a matched comparison.

Build 11 is compiled for device and Simulator, not installed. It adds a read-only
controller diagnostic string to the existing bounded performance batch: timer
and callback counts, input gates, controller snapshot/profile/handler state,
legacy values/timestamp, and the iOS17 live-input values/timestamp with explicit
availability. It does not drain queues or replace callbacks. Controller regression
checks and iOS compilation pass. The currently working hardware build10 is retained.

### Verified guest auto-sleep policy correction (build 12)

After the successful manual relaunch, the user again reports the guest Wii Remote
communication warning after a few minutes idle. The local SDK implementation
contains an explicit default five-minute auto-sleep policy; Galaxy's scene setup
sets five or fifteen minutes. Zero disables this disconnect policy.

The exact RMGE01 DOL hash identifies the shipped revision. Its unique setter at
0x804D8A98 contains a byte store at r13-6966; boot initializes r13=0x806A4CA0,
locating the sleep byte at 0x806A316A. The caller selects 5/15 exactly as the
matching decompilation's WPadHolder wrapper does. These are verified RMGE01
instructions, not the different RMGK01 symbol addresses.

Build 12 applies the native port's persistent virtual-remote policy on the CPU's
VI callback: only a known 5/15 value becomes 0, after exact DOL hash, SDA register,
MEM1 bounds and all 13 setter instruction words match. A normal zero value returns
immediately. It reapplies when scene setup changes the policy. No guest code or
PGO module is rewritten; physical Xbox ownership remains independent. Logging
is limited to the first 8 actual policy changes.

The production-helper tests verify known values, scene resets, a synthetic hour
of the SDK idle predicate, every preimage byte mismatch, incorrect register,
short/null memory, unknown values, and unchanged surrounding bytes. Both device
and Simulator hosts build. Synthetic tests are not physical idle acceptance;
the remaining test is an actual idle interval longer than five minutes with the
controller still responsive afterward. The separate startup event-delivery
failure is not claimed fixed by disabling guest auto-sleep.

Live build 12 Simulator verification completed: 399.94 seconds after launch and
22,678 recorded frame events (more than six minutes of emulated frame time)
with neutral input. No Wii Remote communication warning was visible afterward;
a two-second A+B input advanced from the title screen to file selection. The
runtime recorded three verified changes from five minutes to zero. This checks a live idle
interval and subsequent guest input, not physical Xbox Bluetooth persistence.
Evidence and screenshots: `generated/runtime/wiimote-idle12-simulator/`.
Build 12 is installed on the iPad with 33 protected files byte-identical; it awaits
a Home Screen launch and physical idle test. No tool-driven launch was performed
for this installation because the user's previous successful recovery used a
manual relaunch.

Negative control reproduced: build 10, without the policy change, displayed the
exact Wii Remote communication warning after more than six minutes idle
(379.13 wall seconds; 20,791 recorded frame events in the final receipt).
Screenshot and logs are in `generated/runtime/wiimote-idle-negative10/`.
Both runs used the same extracted game and Simulator module; they used separate
Simulator device profiles, so this is a behavioral reproduction and correction
check, not a performance A/B benchmark. Build 12's live verified zero setting,
absence of the warning, and successful subsequent A+B response support the
sleep-policy correction. Physical Xbox startup delivery and long-idle acceptance
remain separate from these Simulator results.

### Build 12 physical dead-cursor recurrence

The user reports a dead cursor after pausing and leaving the controller idle,
despite its continued connection. Hardware logs confirm the guest sleep policy
was applied repeatedly. The deeper input probe isolates another failure:
controller ownership/list membership, main-thread timer, profile identity and
all handlers remain intact; gameplay and pause gates remain allowed. Timer ticks
continue increasing, but callback count remains at 1,076 and both legacy and live
input timestamps/values stop changing after the 09:31:50 Menu release. This is not
evidence that changing the virtual Wiimote sleep policy restores physical input.
Capture: `generated/runtime/hardware-build12-20260913/dead-cursor/`.

A bounded Bluetooth/system capture did not establish a specific transport error.
The implementation lacked explicit game-view first-responder acquisition and
screen idle suppression. Apple documents responder ownership for profile input
routing and [screen idle suppression for controller-driven iOS games](https://developer.apple.com/library/archive/documentation/ServicesDiscovery/Conceptual/GameControllerPG/Appendix/Appendix.html).
The next correction restores game focus at lifecycle/UI boundaries while
preserving modal text input, and disables screen idle while an active game is
running or paused. Actual responder/window/idle flags are included in the existing
low-rate diagnostic batch. These omissions are verified; their causal role in
this particular physical input freeze still requires the hardware comparison.

Build 13 implements that lifecycle correction. The Metal view explicitly supports
first-responder ownership; gameplay start, appearance, foreground return and UI
unblock restore it when no editor/import/modal owns input. Native pause is allowed
to reacquire it after a background/foreground cycle so View can resume. Active
running or paused gameplay disables screen idle; stop, exit and background restore
it. The existing performance line now records surface responder status, key-window
status and screen-idle state alongside the controller probe.

The actual UIKit Simulator regression passed focus acquisition, modal text-field
preservation/restoration, paused background/foreground followed by a production
controller View resume event, and idle restoration on background/stop. Reproduce
with `python3 tests/test-controller-focus.py BOOTED_SIM_UUID`; no argument builds
only. Receipt: `generated/tests/controller-focus-results.log`. Both full hosts
compile with the unchanged accepted core and PGO module. These tests validate the
implemented lifecycle behavior, not recovery of the physical dead-cursor report.

### Build 13 recurrence and system input routing

Physical build 13 still lost Xbox input after a short guest pause. Callbacks and
both profile timestamps stopped after the 10:31:15 UTC Menu release while the
poll timer continued. Controller ownership, handlers and input gates remained
valid, and the actual first-responder, key-window and screen-idle flags were all
one. The lifecycle correction therefore did not resolve this hardware failure.

The historical device system log supplies a separate, concrete routing finding.
At 10:31:53.692 UTC on September 13, SpringBoard acquired a strong focus lock with
reason `universalControl`; at 10:31:53.696 the controller daemon redirected its
active HID target from GalaxyPad to SpringBoard. It briefly restored GalaxyPad at
10:31:53.783. A second Universal Control focus lock at 10:31:54.791 redirected the
target to SpringBoard again at 10:31:54.796. No restoration was found through
10:38 UTC, despite the app returning active and retaining local responder status.
Private captures are under
`generated/runtime/hardware-build13-20260913/pause-monitor/`.

This establishes a system routing diversion during the failed session; it does
not yet establish the onset or cause of every earlier controller freeze. Direct
touch and Universal Control disconnection tests were the next check; their
confirmed recovery result is recorded below. The unbuilt GCEventInteraction
experiment was removed, and no new app build was installed for that check.

### Same-session recovery confirmed; Universal Control isolated

The user confirmed that a direct tap on the iPad game restored Xbox input without restarting GalaxyPad or reconnecting the controller. The runtime capture `generated/runtime/hardware-build13-20260913/pause-monitor/recovered-after-direct-touch.log` corroborates recovery at 10:42:08 UTC: callback count rose from 589 to 627 and both legacy and physical-input timestamps resumed, with nonzero right-stick values. This establishes a recoverable system-focus failure in this session, rather than requiring an app or Bluetooth restart. It does not prove every earlier controller failure had the same cause.

For a clean repeat, Mac System Settings > Displays > Advanced pointer/keyboard sharing was switched off. The UI confirmed the switch off and removed the iPad link, leaving only the built-in display. The previous setting was on; it can be restored there, but restoration may reintroduce Universal Control focus takeover. No new build was installed, no app restarted, and no game data changed. The user subsequently confirmed that the repeated physical pause/resume test remained responsive. The idle duration was not recorded, so this is successful repeat pause/resume acceptance with Universal Control disabled, not a measured long-idle endurance result. The untested GCEventInteraction candidate was withdrawn from source rather than bundled into this comparison.
