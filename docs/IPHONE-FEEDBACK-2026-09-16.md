# iPhone feedback: build 7162

## Installed identity and live evidence

Read-only CoreDevice inspection confirmed the installed app is build 7162,
version 0.1.0. The user reported roughly 43 FPS during light gameplay at 1x,
with no noticeable gain. This is not acceptance of the void-dispatch candidate.
The running app was left undisturbed: no install, restart or preference write.

A copy of the live runtime log contains ten final windows totaling 157.600 s:
7,386 after-frame events, 46.866 events/s, mean process CPU 155.779% (100% is
one core), render scale 1, and serious thermal state throughout. These windows
span the user's live session and are not the exact instantaneous 43 FPS sample,
a controlled comparison, or a display-presentation count. Thermal state alone
does not quantify how much slowdown is thermal throttling.

The same windows record 14,770 depth peeks and 0.436 ms recorded EFB peek time
per frame event, about 2.04% of wall time. Even eliminating that recorded cost
would not bridge the observed gap to 60; this is not a complete GPU/stall
attribution. Do not disable depth access: depth-sensitive pointer interactions
need it. Previous CPU sampling still supports investigating generated game
execution and its runtime boundary, but it predates this candidate and does not
establish the new distribution of CPU costs.

The startup line says detailed_frame_logging=0, consistent with the user's
setting taking effect on the *next* launch. Standard window logging is already
available. Do not restart an active play session merely to enable more logging.
Private evidence: generated/iphone-feedback-20260916/runtime.log and observation.json.

## Pause control repair

Both visible Pause controls sent Wii Plus. Removed the top duplicate and changed
the surviving touch control's label from Pause + to +. Its input identity, saved
layout, generous target, accessible description, polling pulse and held-input
behavior remain intact. Controller View/Select and lifecycle app pause remain.
Updated help text and isolated UIKit behavioral regressions.

The isolated iPhone Simulator UI suite passed, including Plus with held A,
short taps, accessibility activation, native pause/resume and controller paths.
The complete default repository suite passed. This is a source/Simulator repair;
it has not been installed over the user's active iPhone session.

## Finger tracking: unresolved, specific next work

The overlay already normalizes touch into the presenter viewport. The remaining
known discrepancy is downstream: a normalized touch drives a virtual Wii Remote
rotation, then sensor projection and Galaxy's own cursor conversion. The existing
neutral-gameplay experiment documents edge overshoot and a calibrated inverse.
Candidate 2 improved recorded neutral/spin target continuity in Simulator, but
lower-edge reachability, aspect changes, sustained tilt, controller handoff and
physical drag latency are unfinished. The default pitch20 inverse rejects the
lowest grid row; blindly enabling it or increasing sensitivity is not a complete
repair. See experiments/pointer/README.md for measurements and limitations.

[Dolphin's Android touch work](https://cs.dolphin-emu.org/blog/2019/02/01/dolphin-progress-report-dec-2018-and-jan-2019/)
provides a relevant precedent: tuning pointer mapping for games including Galaxy.
The next pointer experiment should finish full-viewport reachability and transition
behavior before porting the calibrated path to hardware. No pointer accuracy or
performance improvement is claimed in this pass.
