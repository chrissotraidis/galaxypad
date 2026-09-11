# Physical iPad performance loop — 2026-09-11

The current signed GalaxyPad build is running on the iPad with frame logging
off by default. The previous device run already showed the heavy scene falling
to about 32–49 FPS while process CPU reached about 108–111%; turning the optional
frame windows off therefore does not address the main slowdown. The retained
evidence points to guest execution/upstream production pressure, not a starving
RemoteIO callback: requested and delivered audio frames matched, short callbacks
were zero, and backlog drops stayed low while underruns rose.

## Valid active-scene profile — 2026-09-11

After the physical tap on “Back to Game”, the lifecycle log recorded
`runtime_paused=0`, `menu_presented=0`, and `active=1` at 09:59:35. The live
mirror showed the fixed 121-star Observatory central galaxy-map platform.
With frame logging still off, the retained 10-second CPU Profiler capture
(`generated/runtime/…/resumed-active-20260911/pass-1/cpu.trace`) contained
34,090 CPU/GPU-thread samples. The largest attributed stacks were
`StaticRecompCore::Run()` (3,372 samples), `chassis_dispatch` (1,377),
`Pos_ReadIndex` (1,158), `Normal_ReadIndex<unsigned short, short, 1u>` (907),
`VertexLoader::RunVertices` (724), and `TexCoord_ReadIndex` (685). The
RemoteIO mixer thread accounted for 515 samples, while the main thread had
28, so this capture points first at the CPU/GPU emulation and vertex-loader
path rather than an audio callback stall. The full CPU profile export
completed successfully; the separate thermal-state export exited 139 and is
treated as an Instruments exporter limitation. This is attribution evidence,
not an FPS measurement.

## Loop

1. Reach one fixed heavy scene and leave the visible view unchanged.
2. Visually confirm the scene is active, not the three-dot or app pause panel,
   and pass `--active-scene-confirmed`.
3. Run an unsampled 30-second device-presence window with logging still off.
4. Attach the CPU Profiler for a bounded 10-second attribution sample. Treat
   this as diagnostic only because profiling can perturb timing.
5. Keep the raw `.trace`, process snapshots, and exit statuses even if the
   command-line XML exporter crashes. A successful capture is still useful;
   exporter failure is a tooling limitation, not a game conclusion.
6. Make one source/build change only, install the new private candidate, and
   repeat the same scene. Reject the candidate unless CPU/emulation evidence
   improves without a correctness, audio, or lifecycle regression.

The first offline candidate screen used the available iPhoneOS device compile
database after the Simulator compile database was found missing. The quiet
native-burst differential still passes 5,376 cases, but its full `Run` object
grew from 6,672 to 7,216 bytes of text (+8.3%) under the device policy. That
candidate is rejected before module integration; this is not a gameplay FPS
claim.

The runnable loop is:

```sh
scripts/galaxypad-performance-loop.sh \
  --pid 7869 \
  --scene "current fixed heavy scene" \
  --passes 1 \
  --active-scene-confirmed \
  --wait-for-active \
  --log generated/runtime/ipad-iteration-1/launch-console-pause-panel-logging-off-default.log
```

The `--wait-for-active` mode watches the supplied lifecycle log and begins only
after a new active transition is present. Passing `--log PATH` does not enable
frame logging; the current log still records `frame_logging=0`. The loop retains
before/after device process snapshots and never substitutes a host `ps` reading
for remote iPad CPU data. Use a new output directory for every candidate. The
script never installs, launches, terminates, suspends, or changes GalaxyPad or
its saves.

The earlier paused mirror state (`runtime_paused=1 menu=1`) was deliberately
rejected as a performance sample. It was the explicit Pause panel state, not
the intended three-dot behavior. The three-dot menu is now required to report
`pause_runtime=0` while it blocks gameplay input; the active-scene pass above
is the accepted performance baseline.
The secondary-account Astra Medium audit also confirmed that the current
desktop environment has no supported non-destructive touch-injection route:
QuickTime mirroring is display-only and `devicectl` exposes no physical touch
command. The active-scene gate therefore requires one direct tap on the iPad.
The earlier bounded watcher reached its 600-second limit while waiting for
that physical tap; it is historical diagnostic output only.

## Latest unattended recheck and physical input evidence — 16:42 JST

The logging-off unattended Simulator replay reached the seeded late-game
Observatory plaza without operator input. Its screenshot is
`generated/runtime/ipad-iteration-1/simulator-r915-recheck-20260911-163729/scene.png`;
the on-screen `emu FPS` counter read 47.3. The bounded 8-second sample
attributed 4,263 samples to `StaticRecompCore::Run()` and 3,990 to
`chassis_dispatch`, with the remaining work spread across generated code and
vertex readers. The Simulator result is a candidate-attribution and route
check only, not a physical-iPad FPS measurement.

The physical console excerpt at
`generated/runtime/ipad-iteration-1/controller-hotplug-console-20260911.log`
now proves the hot-plug contract: controller connect logged
`connected=1 ... hidden=1`, and disconnect logged `connected=0 ... hidden=0`.
The app was relaunched without the console attachment as PID 8160 after the
device service was released; the save backup hash remained
`cd8d1fa98c266aa321dbb018247e5df7a084e5330ffa55f2012df4971b1bc473`.

## Candidate under test — normal indexed reader

The active profile identified `Normal_ReadIndex<unsigned short, short, 1u>` as
a measured hot path. A device-policy differential retained the existing
500,000-case parity test and reduced that isolated symbol from 63 to 55
instructions (object text 12,236 to 12,036 bytes). The private candidate
archive and signed app are staged under
`generated/runtime/ipad-iteration-1/performance-loop-20260911/normal-reader-candidate-20260911b/`.
The candidate is not considered effective until it is installed in place and
the same active scene is profiled with no lifecycle, audio, visual, or save
regression.

That first device package was subsequently audited before accepting its result:
the `VertexLoader_Normal.cpp.o` member in the staged archive was byte-identical
to the baseline member, so the 63-to-55 isolated probe did not reach the app.
It is rejected as a performance candidate and supplies no device comparison.
The loop has been reoriented to the unattended Simulator route documented in
`docs/GALAXYPAD-GOAL-LOOP.md`; the physical iPad remains reserved for the final
candidate install/acceptance pass. The first complete manual verification of
that route used a 30-second title A+B hold, pointer-based file selection and
Play, then 30 A pulses through the opening story. It reached the late-game
plaza at
`generated/runtime/ipad-iteration-1/simulator-reorientation-unattended-plaza-manual.png`
with logging off and showed 48.2 FPS in the on-screen counter. This is a
Simulator reachability and diagnostic baseline, not a physical-iPad FPS claim.
The repeatable script now uses that 30-second title hold and emits
`input-route.log` alongside the screenshot and bounded host `sample` profile.
For targeted attribution, set
`GALAXYPAD_SIMULATOR_EFB_TRACE=/absolute/output/efb-trace.csv`; the script
passes that opt-in path to the Simulator and clears it on exit. The trace
contains EFB read coordinates, guest PC/LR, and elapsed time, so the next
candidate can separate pointer-related depth waits from broader rendering
work without changing behavior.

The trace-enabled replay produced 10,365 depth-read rows after the Simulator
app was terminated to freeze the file. The whole launch-to-profile window had
a 1.242 ms mean and 11.391 ms maximum read duration; 648 reads exceeded 5 ms
and 6 exceeded 10 ms. Reads clustered at `(0,0)` and `(520,377)`, with a
smaller `(212,270)` group, and the two verified guest callers were LR
`0x80385be0` and `0x8029e6e4`. Because this includes route startup and the
bounded profile rather than a stationary-only interval, it is diagnostic
evidence for the next experiment, not a new FPS or device claim.

## R915 indexed position/texture candidate — measured improvement, device smoke

R915 specializes only the common `N == 3` indexed position and `N == 2`
indexed texture readers in `VertexLoader_Position.cpp` and
`VertexLoader_TextCoord.cpp`; all other template cases retain their original
loops and the position-cache behavior is unchanged. It was built in an
isolated iPad Simulator core and linked into a private app. With the 64-tile
EFB configuration, logging off, the same save seed and the same automated
route, the forward pair measured candidate `54.4 FPS` versus control `52.7
FPS`; the reverse-order pair measured candidate `50.0 FPS` versus control
`47.3 FPS`. Both pairs reached the same late-game plaza. The raw CPU samples
still show `StaticRecompCore`, `chassis_dispatch`, and synchronous EFB depth
waits, so this is a bounded end-to-end gain, not evidence that the EFB stall
has been solved. Artifacts are retained under
`generated/runtime/ipad-iteration-1/vertex-r915-*`.

The candidate was then rebuilt for `iphoneos`, signed with the same development
identity/profile as the protected baseline, and installed in place. The
device launched the fresh module and reported `frame_logging=0` on the first
smoke, followed by an opt-in logging run. In the active scene the iPad logged
roughly `59.8–60.0 FPS` at render scale 1, `efb_depth_peeks=7007` and
`efb_total_peek_ms=2261.174` over the retained window, while cumulative audio
underruns stayed at `3`, requested and delivered frames matched, and short
callbacks stayed at `0`. This is useful physical startup/active-scene evidence
but not heavy-scene acceptance: no unattended physical input path exists to
recreate movement or the three-dot gesture. The candidate remains installed
for observation; no claim of final device performance or pause acceptance is
made.

R915 is kept as the current measured candidate. The next loop step is a
physical comparison only when the fixed heavy scene can be reached through a
real touch/controller action, or an additional unattended Simulator candidate
targeting the measured `StaticRecompCore`/dispatch path. Do not change EFB
semantics based on the readback stack alone.

## Unattended R911 normalization differential — parked

The whole-normalization candidate passed the offline gate: 261,120 complete
routine CPU-state/memory/callback/FPSR comparisons and 69,120 callback cases.
The private Simulator module is
`generated/build/ios-simulator-normalization-r911/gRMGE01_recomp.dylib`
(SHA-256 `c2ebd795db9d0a414d368f37f23558968ccc3a571ffab39d9ba10de2193240d9`),
against control module
`generated/build/ios-simulator-fresh-module/gRMGE01_recomp.dylib`
(SHA-256 `f988f9a78f875f78c2c9ae89f458c2d85785c0e62de4595ef12d1af7734c8b03`).

The first same-host pair both reached the seeded late-game plaza with logging
off: candidate `50.0 FPS` and control `49.1 FPS`. Their bounded samples were
effectively the same (`StaticRecompCore::Run` 5,435 vs. 5,458;
`chassis_dispatch` 5,097 vs. 5,152; EFB depth waits 589 vs. 587). A
reverse-order control also completed (`StaticRecompCore::Run` 5,530), while a
reverse-order candidate replay exited before the renderer-ready signal. Its
console log contains normal startup and no GalaxyPad crash/dyld report; it has
no screenshot or profile. A subsequent control replay completed again, so the
candidate is rejected/parked rather than installed on the physical iPad.

The accepted unattended control artifact is
`generated/runtime/ipad-iteration-1/normalization-control-r911c/`; the failed
candidate artifact is retained at
`generated/runtime/ipad-iteration-1/normalization-candidate-r911b/`. The
dedicated GalaxyPad Simulator is the only surface the loop may automate; an
unrelated already-booted Simulator was preserved and is recorded in each
output, so comparisons made while it is booted are host-pressure-qualified.
Future failed runs also retain `failure-state.log` with the Simulator state,
launchd/PID state, and console tail.
The next iteration must target the measured shared execution/dispatch path and
must pass the same unattended route before any physical install is considered.

## Current interpretation

- Render resolution is not the leading lever: the earlier heavy scene was
  already measured at render scale 1.
- The three-dot menu is input-only host UI. It blocks gameplay input while
  open but must not pause the emulated CPU or audio clock. Only the app Pause
  panel, modal UI, or lifecycle interruption may request a runtime pause.
- The controller pause path now presents an app-style pause panel. “Back to
  Game” resumes; holding Start + is reserved for the original Wii-style pause
  screen and its Return to Observatory action.
- The next performance candidate should come from the measured shared native
  execution path, not another logging toggle, resolution guess, audio-buffer
  tweak, or unchanged profiler retry. The Simulator sample likewise points at
  `StaticRecompCore::Run`, `chassis_dispatch`, and
  `FramebufferManager::PeekEFBDepth`/Metal staging; it is useful for
  candidate attribution but does not replace the physical profile.
- Before changing EFB behavior, collect one opt-in EFB dispatch trace on the
  unattended late-game route and compare its wait distribution and guest PCs
  with the physical profile. No EFB semantics change is accepted from the
  stack name alone.

All loop artifacts stay under private `generated/` output. Saves, disc data,
signing material, and raw private device logs are not publication artifacts.

## Current UI/aspect correction — 2026-09-11

The latest exact private iPad install reports `aspect_ratio_mode=0` and a
normalized viewport of `{{0, 0.013671875}, {1, 0.97265625}}`, so the default
device presentation is 4:3 with small top/bottom letterboxing. Invalid saved
aspect values now safely resolve to 4:3; 16:9 remains an explicit Display
menu choice. The three-dot menu host gate is explicitly input-only and cannot
request a runtime pause; both top controls were lowered by 8 points.

The build was installed in place with the same app database UUID and a
byte-identical pre-install save backup. Focused UIKit, controller, and
strict-signature checks pass. Physical menu/controller/touch confirmation is
still pending because this desktop has no supported unattended hardware-input
route; the next device interaction should check that gameplay continues while
the three-dot menu is open and that touch/controller input returns after it is
dismissed.

The follow-up build also defaults automatic touch-control hiding on for a
connected controller, logs `connected/auto_hide/hidden` on each reconciliation,
and increases right-stick pointer response from 0.8× to 1.2×. Its fresh device
launch logged `connected=1 auto_hide=1 hidden=1`. Performance logging remains
off for normal play; the established physical evidence still points to
CPU/emulation production pressure and audio underruns, so this UI/input pass
does not claim a performance improvement.

## Final private label build — 2026-09-11 16:30 JST

The latest host rebuild is installed and running as PID 8142. The gameplay HUD
now calls the counter `emu FPS`; it is the existing frame-event rate and not a
display-completion measurement. Startup still reports `frame_logging=0`, 4:3,
and controller auto-hide enabled. This pass changes no performance path; the
slowdown and audio-underrun investigation remains the next performance loop
target.
