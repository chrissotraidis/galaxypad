# iPhone feedback: build 7162

> Current checkpoint: [September 16 session close](SESSION-CLOSE-2026-09-16.md).
> The dated evidence below is retained; older build identities and next steps are historical.


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

## Build 7163 deployed on request

Rebuilt the current app host at 9736708 for iPhoneOS, retaining the exact signed
7162 game module and runtime archive. Regenerated disc identity from the current
configuration/template, used prepared external headers, and retained the audio
header overlay matching the archive. The private receipt records compile/link
arguments and source/object/archive/module hashes. This is an incremental test
build, not a newly qualified public release or a new performance candidate.

Verified the same signing identity, entitlement and profile compatibility, then
deep strict code-sign verification and iPhoneOS platform. Rediscovered the attached
iPhone 14, stopped the old process, backed up 54 Wii/configuration/preference files,
installed in place and read them back before launch: all 54 byte-identical, no
added files. CoreDevice reads back build 7163. No app data was cleared.

Launched PID 4539; the mirrored physical screen shows the Wii startup screen,
one + control and no duplicate Pause. The runtime reports void-dispatch=1 and
detailed_frame_logging=1 at render scale 1. Startup settles near 60 frame events/s;
this is not demanding-gameplay performance proof. The existing single redacted
runtime error event also recurred; rendering continued, but its cause is unresolved.
Private artifact/receipts: generated/iphone-ui-7163-20260916/.

## Next performance decisions

43 to 60 FPS requires about 28.3% less elapsed time per frame, if the work/scenario
is otherwise comparable. No new FPS gain is established by this UI deployment.

A newly reviewed primary precedent is [Dolphin PR 13951](https://github.com/dolphin-emu/dolphin/pull/13951):
it specializes the cached interpreter's common Interpret call, allowing inlining;
the author reports roughly 10% on M1/Skylake and supplies M1 branch-counter data.
Galaxy's main path is static recompilation, so importing that interpreter change
would not optimize the dominant generated-code workload. The applicable idea is
to specialize common paths only where the native code and actual counters show
that indirect calls or state visibility prevent optimization.

Prior direct-call experiments and conservative state forwarding did not establish
an overall win; simply enabling them again is not a new plan. Prior broad machine
outlining shrank a chunk but made tested paths much slower. Prefer two bounded
architectural experiments: (1) connected hot regions with audited register/helper
effects and fallback at observers, and (2) whole high-cost routines such as
animation or matrix work replaced behind a verified input/output boundary. Both
require actual hot-path attribution before selecting routines; the current data
does not establish animation as the leading cost. Per-region equivalence plus
actual native-code/cycle reduction are prerequisites before another phone build.
These mechanisms can be shared across Wii/GameCube ports; per-game hot routines
and correctness boundaries still need validation. Reducing total work also targets
sustained thermal behavior, but no thermal benefit is yet measured.
