# GalaxyPad iPad resume note — 2026-09-11

## Stop point

The latest known-good private iPhoneOS candidate was installed in place on the
physical iPad and relaunched successfully today. The staged bundle is
`generated/device-stage.JOtjGn/GalaxyPad.app`; the current run was alive as
device process PID 8171 when this note was written. Its development signature
passes strict verification. No uninstall, app-data reset, save replacement, or
WBFS change was performed.

The preserved save backups before and after the install have the same SHA-256:
`cd8d1fa98c266aa321dbb018247e5df7a084e5330ffa55f2012df4971b1bc473`.

## Proven this session

- iPad startup defaults to 4:3; explicit 16:9 remains available.
- Frame logging is off by default (`frame_logging=0`).
- The Xbox handoff was captured on the physical device: disconnected
  `hidden=0` → connected `hidden=1` → disconnected `hidden=0`; ownership and
  held input were cleared on each transition.
- The latest Simulator recheck reached the late-game Observatory plaza with
  logging off at 47.3 `emu FPS`. Its bounded sample still points at
  `StaticRecompCore::Run()` and `chassis_dispatch`; this is not an iPad FPS
  result.
- The three-dot menu source fix is present: it blocks gameplay input but is
  runtime-neutral (`pause_runtime=0`). Direct physical open/dismiss gameplay
  continuity and audio behavior still need confirmation.

## Parked candidate

The two-range dispatcher candidate was built and strict-signed, but its
unattended Simulator launch crashed before renderer readiness with
`EXC_BAD_ACCESS` at a null instruction pointer in the candidate module during
runtime startup. It was not installed on the physical iPad. The crash report
is `/Users/chrissotraidis/Library/Logs/DiagnosticReports/GalaxyPad-2026-09-11-170551.ips`.
Do not promote that candidate without isolating the null indirect call.

## Resume sequence

1. Keep the physical iPad baseline on the staged bundle above. Do not erase
   its app data or replace the advanced save.
2. Directly test the three-dot menu in the fixed heavy scene: opening it must
   not pause or freeze gameplay/audio; the top Pause control is the intentional
   pause path.
3. Reconfirm Xbox connect/disconnect, touch-control visibility, and right-stick
   pointer response (1.2×). Treat the physical device as the acceptance gate.
4. Continue performance work with one measured candidate at a time. Use the
   logging-off matched-scene loop and retain CPU/audio/lifecycle evidence.
5. For unattended Simulator work, resume with:

   ```sh
   GALAXYPAD_ALLOW_OTHER_SIMULATORS=1 \
   GALAXYPAD_SIMULATOR_PROFILE_SECONDS=8 \
   GALAXYPAD_SIMULATOR_FRAME_LOGGING=NO \
   bash scripts/galaxypad-unattended-simulator-loop.sh \
     generated/build/ios-simulator-app/GalaxyPad.app \
     generated/runtime/ipad-iteration-1/<new-run-directory>
   ```

The broader repository gate is not a clean green gate because the private
fixture `generated/thp-kernels-r198-exits/candidate.c` is unavailable. That
limitation, the physical performance cause, and direct three-dot continuity
remain open for the next session.
