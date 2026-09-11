# iPad controls and performance iteration — September 11, 2026

Private device build 0.1.0 (2). Hardware: 12.9-inch iPad Pro (M2), iPad14,5, iPadOS 26.6.1. The user supplied actual plaza gameplay feedback and a September 10 screenshot. These are physical observations, not simulator benchmarks.

## Reported problems and current disposition

| Report | This iteration | Still needs physical acceptance |
| --- | --- | --- |
| Touch pointer is inaccurate and off-center | Recorded as an unresolved defect. Checked viewport normalization and the virtual Wii IR projection. | Finger-to-star alignment across center/edges and game/menu states. No calibration fix is claimed. |
| Controls sit too far inward and low | Restored reviewed SunPad iPad stick/action/D-pad geometry; separated A/B rectangular hit areas. Existing custom positions still win. | Comfort during sustained gameplay and simultaneous move/aim/actions. |
| No discoverable Start or pause | Visible **Start +**; separate **Pause → Back to Game** uses the native modal pause lifecycle. The three-dot menu is host UI only and must not pause the runtime. | In-game Start, native Pause/Back to Game, and three-dot menu continuity on the device. |
| Severe audio underruns and lag | Enabled persistent five-second frame/audio/CPU/memory/thermal logs and collected a physical CPU profile. | Matched plaza measurements and audible comparison. No performance fix is claimed. |
| Higher than 1× is too slow; 1× looks poor | Retained 1× and labeled it as the recommended native setting. | Higher-resolution gameplay after CPU/GPU profiling; no overclock or speed hack applied. |
| Xbox aiming and actions unclear | Audited and regression-tested the existing right-stick pointer path; increased right-stick cursor response from 0.8× to 1.2×, clarified the controller guide, added ownership/raw-button/visibility logs, and wired Menu/Options rising edges to the native pause path. The exact physical hot-plug log now proves connect hides touch controls and disconnect restores them. | Right-stick aim comfort, simultaneous RB/RT, recenter, tilt and physical pause with a real controller. |

## Galaxy controls, including Start

Galaxy uses Wii **+ / − held** to open its game pause menu. Nintendo's [official manual, controls pages](https://m1.nintendo.net/docvc/RVL/USA/RMGE/RMGE_E.pdf) distinguishes this from HOME. The local Petari reference `PauseButtonCheckerInGame.cpp` counts 12 held update frames; it is a reference implementation, not a measured threshold from this installed executable. A quick tap can fail, especially during slowdown. Start's accessibility pulse now lasts 750 ms instead of 150 ms; native Pause remains an immediate alternative.

| Action | Touch | Xbox-style controller |
| --- | --- | --- |
| Move | Left stick | Left stick |
| Point / collect star bits | Touch the game viewport | Right stick; click to recenter |
| Jump / talk / select / activate Pull Star | A | A or RB |
| Shoot star bits | B | B or RT |
| Spin | X | X |
| Crouch / dive | Z | LT |
| Reset camera | Y | Y |
| Camera adjustment | D-pad | D-pad |
| Game pause | Hold Start + (or extra −) | Hold Menu (+) or Options (−) |
| Immediate app pause | Top-right Pause | Native UI access; game Menu remains + |
| Simulated tilt | Optional tilt stick | Hold LB and move right stick |

Face assignments can be remapped. RB/RT aliases allow the right thumb to keep aiming. This is the implemented mapping, not hardware-controller acceptance.

Before updating, QuickTime showed the game's Wii Remote communication interruption dialog. Its cause is not established; it should be correlated with controller ownership and app lifecycle during the next reproduction.

## Why the pointer remains open

The overlay correctly normalizes touches inside the current rendered viewport and ignores letterbox touches in isolated tests. The runtime then projects those inputs as a virtual Wii Remote: default yaw 25°, pitch 20°, vertical offset 10 cm. That angular/sensor-bar path is not inherently a pixel-to-pixel touchscreen mapping. The existing simulator calibration experiments are state-sensitive; they have not been promoted to physical defaults. Changing a constant without measuring the visible game cursor could improve one scene and break another. See [input and pointer notes](INPUT-AND-POINTER.md).

## Physical profile and logging

A 31.13-second Time Profiler recording was attached to the original build before replacement. Instruments reported 28.55 seconds of sampled CPU weight:

- CPU-GPU thread: 24.86 s (87.1% of sampled CPU weight).
- Audio RemoteIO thread: 2.26 s (7.9%).
- `StaticRecompCore::Run`: 13.10 s inclusive, 1.84 s self.
- `chassis_dispatch`: 10.96 s inclusive, 0.94 s self.
- `VertexLoader::RunVertices`: 4.84 s inclusive, 0.912 s self; normal/texture/position conversion functions also appear prominently.

Inclusive times overlap; do not add them together or treat sample percentages as FPS gains. This was not synchronized to a verified stationary plaza scene. Time Profiler also does not establish GPU utilization. The evidence points to guest execution and CPU vertex conversion as useful next targets, rather than proving that resolution or an audio-buffer change alone will solve slowdown. CLI sample export crashed twice; the trace was successfully read in Instruments and its tables captured locally.

Build 2 provides **Display → Performance Logging (Next Launch)** as an opt-in diagnostic switch. It is off by default so normal gameplay does not pay the persistence cost. When enabled, every roughly five seconds of active emulation it persists:

- Frame events and emulation-speed estimate, with observation duration. Frame events are not display-completion counts.
- Process CPU use (all threads; one core = 100%), resident memory, thermal state, low-power state, active render scale and display maximum refresh.
- Cumulative DMA enqueue/underrun/drop counters and RemoteIO requested/delivered/nonzero frames, short callbacks and peak, including instrumentation availability.
- Rate-limited runtime warning/error categories through the existing privacy filter, plus controller ownership changes. Raw runtime messages are intentionally absent from exported reports.

Logging resets frame windows around pause/background transitions. Audio counters are cumulative: compare deltas within one uninterrupted scene, using `scripts/summarize-audio-window.py`, not totals across startup, menus or restarts. RemoteIO counters measure callback delivery, not audible quality. Logging can be disabled for a later overhead comparison. Reports remain local under the app's Diagnostics flow; no automatic upload was added.

## Follow-up live evidence — save and controller/lifecycle build

The advanced private Wii save was injected only into the iPad's existing `GameData.bin` slot. The original 48,640-byte file was backed up before replacement (`717f7fb3…476e36c`); the candidate read-back matched immediately after injection (`f36bb076…88a3`). The first boot of the installed app rewrote 27 bytes in that same 48,640-byte slot: the save header/footer checksums and unsupported Mii metadata. That normalization changed the post-boot hash but did not replace the slot or restore the old save. The earlier wired QuickTime inspection visibly reached the candidate's 121-star late-game Observatory state. The pre-replacement backup and candidate/read-back files remain private under `generated/runtime/ipad-iteration-1/save-injection-2026-09-11/`.

The instrumented build was installed in place and relaunched at 08:39 JST. Its fresh console showed the iPad scene becoming active, the controller connected with one extended controller, the recomp module loading, and normal startup measurements. A clean QuickTime recording-start reproduction held the title screen at about 60 FPS with audio underruns flat at 4; it emitted no scene-deactivation or audio-interruption event. This does not reproduce the earlier slowdown by itself.

The prior heavy-scene window remains the strongest performance evidence: at render scale 1, frame rate fell from 60 to 32–49 FPS while process CPU reached 108–111%; audio underruns rose from 3 to 167, but requested and delivered RemoteIO frames stayed equal, short callbacks stayed at zero, and backlog drops stayed at 2. That points to CPU/emulation or upstream audio-production pressure rather than a starving RemoteIO callback. The device module used for this run is fresh/unprofiled; no performance fix is claimed yet.

The repeatable loop is now `scripts/galaxypad-performance-loop.sh`. Its first
logging-off pass retained before/after device process snapshots and attached the
CPU Profiler to PID 7869 for 10 seconds without restarting the app. The raw
private trace is under
`generated/runtime/ipad-iteration-1/performance-loop-20260911/loop-pass-logging-off-3/pass-1/cpu.trace`
and is about 11 MiB. The command-line TOC exporter crashed with status 139 and
left an empty XML file; the trace itself was saved successfully and remains the
authoritative Instruments artifact. This pass was not synchronized to a fixed
heavy scene, so it proves the loop/tool path, not a new FPS result. The quiet
native-burst actual-policy cost screen was subsequently rerun with the
available iPhoneOS device compile database: its private candidate object grew
to 7,216 bytes of text from 6,672 bytes for control (+8.3%), so it is rejected
before module integration. This is an offline cost result, not a gameplay
speedup.

The controller candidate now logs Menu/Options raw-button transitions and sends a one-shot native pause request on a rising edge after the controller has first returned to neutral. Touch **Start +** remains the guest's held Wii pause input. The source build and device launch are verified; physical Xbox pause acceptance still requires pressing Menu/Options on the connected controller and observing the new log entry and panel.

The secondary-account Astra Medium input-route audit found no supported,
non-destructive way to inject a tap into the physical iPad from this desktop:
QuickTime is display-only and `devicectl` has no touch command. The paused
performance gate consequently remains a direct physical-iPad interaction.

The accepted logging-off active-scene profile then captured 34,090 CPU/GPU
thread samples on the 121-star Observatory platform. The dominant stacks were
`StaticRecompCore::Run` (3,372), `chassis_dispatch` (1,377),
`Pos_ReadIndex` (1,158), and `Normal_ReadIndex<unsigned short, short, 1u>`
(907); the RemoteIO mixer had 515 samples and the main thread 28. This is
stronger evidence for CPU/emulation and vertex conversion than for a callback
starvation problem. The full CPU profile export passed; the thermal export
crashed in Instruments with status 139 and is retained as a tooling limit.

The first bounded source candidate was the normal indexed reader. Its isolated
parity probe passes 500,000 conversions and the staged object is 55 ARM64
instructions versus 63 in the isolated probe. Before accepting it, the linked
archive member was compared with the baseline and found byte-identical, so no
normal-reader change reached the app; this lane is rejected and supplies no
performance result. A private package did install at 10:17:56 JST after
correcting a missing `application-identifier` entitlement in the first
rejected package, but it is not evidence for the reader change.

The iteration loop is now reoriented to the unattended Simulator route. The
new `scripts/galaxypad-unattended-simulator-loop.sh` drives a 30-second title
A+B hold, file selection, Play, 30 A-gated story advances, the private saved
scene, screenshot capture, and a bounded host `sample` run without operator
input. The full route was manually verified to reach the late-game plaza with
logging off at
`generated/runtime/ipad-iteration-1/simulator-reorientation-unattended-plaza-manual.png`.
The physical iPad remains the final acceptance target; its mirror cannot
provide unattended taps.

The unattended loop's next diagnostic rung is an opt-in EFB dispatch trace,
which records read coordinates, guest PC/LR, and elapsed time while preserving
the default logging-off route. This is intended to explain the measured depth
waits before attempting a performance change; it is not itself a performance
fix or a physical-device acceptance result.

The trace-enabled unattended pass recorded 10,365 depth reads before the
private Simulator app was terminated. Mean read duration was 1.242 ms and
maximum was 11.391 ms, with 648 reads over 5 ms; reads were concentrated at
two main coordinates and two previously verified guest callers. This confirms
that the next performance investigation should measure EFB service/wait cost
against caller and scene, while keeping the default route unchanged.

## Pause behavior follow-up

Nintendo's [Super Mario Galaxy manual](https://m1.nintendo.net/docvc/RVL/USA/RMGE/RMGE_E.pdf) says to hold Wii **+ / −** for the pause screen; that screen provides **Back** to resume the action and **Return to the Observatory**. The three-dot app menu is separate host UI: it blocks gameplay input while open, but it must not pause the emulated CPU or audio clock. The app-level top Pause button and Xbox Menu/Options path use a lightweight **Pause Menu → Back to Game** panel instead of a generic “Game Paused / Resume” alert; the panel explains how to reach Galaxy's original in-game pause options. Performance logging is now off by default and remains available as an opt-in next-launch diagnostic.

## Validation and device update

- Device host build passed; exact staged app signature passed deep/strict verification.
- iPad and iPhone UIKit regression hosts passed, including simultaneous buttons, pointer viewport mapping, non-overlap, settings persistence, native Pause wiring/input reset and accessible Start cancellation.
- Mobile input/controller/settings and audio-counter regression checks passed.
- In-place device installation succeeded; build 2 relaunched and its title screen, new controls and Pause button were observed through wired QuickTime.
- Refreshed Wii save/preferences backup before installation. The injected candidate matched immediately; first boot then normalized only 27 checksum/Mii bytes in the same `GameData.bin` slot. Existing WBFS/game data remained in place.
- New frame/audio/performance/lifecycle entries were observed on the physical device. A clean launch now reports `frame_logging=0`; title/startup observations do not resolve the user's plaza lag report.
- The latest exact private install uses the rebuilt host with `aspect_ratio_mode=0` (4:3), and the physical launch log reports a normalized viewport of `{{0, 0.013671875}, {1, 0.97265625}}`, confirming the iPad 4:3 letterbox. Malformed saved aspect values now also fall back to 4:3. The three-dot pause exemption is unconditional in the host gate, and the menu/pause controls are lowered by 8 points.
- The full repository gate remains limited by the previously missing private experiment fixture `generated/thp-kernels-r198-exits/candidate.c`; it is not claimed green.

Private evidence is under `generated/runtime/ipad-iteration-1/`: save backups, signed bundle, install result, launch console, profiler trace and Instruments table capture. It is ignored and must not be published with game data, saves, paths or device identifiers.

## Latest iPad build — menu and aspect correction

The fresh device build was installed in place at 16:13 JST using the exact
staged app path and the unchanged app database UUID. Its startup log reports
`aspect_ratio_mode=0`, `frame_logging=0`, and a 4:3 normalized viewport. The
private pre-install `GameData.bin` backup remains byte-identical to the prior
backup (`cd8d1fa9…`); no save, WBFS, or app-data erase was performed.

The source change makes the native three-dot menu input-only: it clears held
input and sets `pause_runtime=0` even if UIKit exposes the menu through a
presentation controller. Dismissal clears the menu gate synchronously. The
top Pause button still pauses intentionally and resumes through **Back to
Game**. Physical confirmation of menu motion/controller/touch behavior still
requires observing and interacting with the iPad; no unattended hardware tap
or Xbox injection path is available from this Mac.

## Controller visibility and menu pause correction — 16:24 JST

The follow-up build fixes the two concrete lifecycle paths exposed by the
physical log. The generic view-controller override no longer forces a pause
while UIKit is presenting the three-dot UIMenu; it marks input blocked first
and reconciles the real presentation afterward. The three-dot sequence can
therefore remain `pause_runtime=0` throughout. The top Pause panel and actual
modal dialogs still pause intentionally.

The default `Hide touch controls when controller connected` preference is now
on when no prior choice exists, while an explicit off choice remains honored.
The fresh device launch logged `connected=1 auto_hide=1 hidden=1`; the
disconnect notification uses the same reconciliation path to show the touch
controls again. The right-stick pointer response is now 1.2× instead of 0.8×.
Physical disconnect/reconnect and pointer-comfort acceptance are still the
next direct checks.

## Final private label build — 16:30 JST

The newest host rebuild was strict-signed and installed in place at 16:30 JST
as PID 8142. Its startup log reports `aspect_ratio_mode=0`,
`frame_logging=0`, `connected=1 auto_hide=1 hidden=1`, and the 1.2× pointer
mapping. The HUD now labels its counter `emu FPS` to make clear that it is a
frame-event rate, not a display-completion measurement. The app database UUID
remains unchanged and the pre-install save backup is byte-identical
(`cd8d1fa9…`). No performance improvement is claimed by this label-only host
pass; the measured CPU/emulation and audio-production investigation remains
open.

## Physical controller hot-plug evidence — 16:42 JST

The exact installed build produced a complete physical connect/disconnect
sequence in
`generated/runtime/ipad-iteration-1/controller-hotplug-console-20260911.log`.
With `auto_hide=1`, the connected state logged `hidden=1`; after disconnect it
logged `hidden=0`. Ownership also changed from zero extended controllers to
one and back, and each ownership transition cleared stale input. This closes
the previously open visibility-logic defect for the tested Xbox controller.

The console attachment was released for another private device task. The app
was relaunched without changing its installed bundle or save; the current
process is PID 8160 and the post-release save backup has the same SHA-256 as
the pre-release backup (`cd8d1fa9…`). Three-dot continuity, pointer comfort,
and the large moving-scene performance result still require direct physical
acceptance or a matching automated route.
