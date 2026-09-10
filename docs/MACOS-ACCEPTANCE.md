# macOS acceptance checkpoint — updated R457, 2026-09-08

## R456 startup-progress candidate — 2026-09-08

Isolated progress-r456 app with frontendc283de0c and unchanged accepted runner/
module passes visible startup message → hidden parent at ready → title → real
save Observatory → movement → clean Command-Q. Save106e unchanged. Controlled
child cancellation R455 and failure dialog R456 separately pass. This candidate
was subsequently integrated and promoted to the normal package in R457 (below).
Fresh full gameplay log retained under generated/runtime/frontend-progress-game-r456,
with generated/progress-game-*-r456.png captures. Whole-run1underrun/4backlogs
does not close audio/performance or G6. No initialization-speed improvement claimed.

## R448 executed packaged-entry check — 2026-09-07

Evidence correction R455: controlled frontend tests mistakenly reused this XDG
profile, and the launcher's normal truncate-on-launch behavior replaced its
ModernGekko.log. The original full R448 runtime log is no longer retained at
that path. R448 screenshots, unchanged-save verification and shutdown counters
quoted in the session/journal remain, but do not cite the current log as R448
evidence. Future dummy tests use frontend-progress-r455 with no Wii/save copy.

The R447 prepared test is now executed, not pending. Packaged frontend79088
launched child79154 via actual Play (Ctrl+Tab, Tab, Return). The isolated XDG
profile and existing Pipe config were used; only its missing FIFO was created.
CUA attachment timed out and spawned duplicate frontend79100, immediately stopped
before Play. No second game or Simulator ran. Subsequent UI targeted exact PIDs
through System Events; do not repeat the CUA app-path attachment.

The bundled module loaded, title accepted A+B, and
`g6-observatory-save-load.json` restored the real one-star Observatory save.
`g6-observatory-control-smoke.json` produced visible displacement. Native Misc →
Toggle pause displayed Paused; a second toggle resumed and a second control route
produced visible movement. Command-Q cleanly ended child and parent (session24515
exit0). This closes this narrow packaged-frontend/Pipe/save/pause/resume/exit
check. It is NOT Finder-wrapper, physical-controller, full HOME-menu, audio,
stuck-input stress, full-route or performance acceptance.

Evidence: ignored `generated/frontend-{title-ready,observatory,movement,paused-later,resumed}-r447.png`,
`generated/runtime/frontend-acceptance-r447/GalaxyPad/Logs/ModernGekko.log`,
`generated/frontend-startup-r447.sample.txt`. Original and test save SHA256 remain
106e8248bd8081404e8258a7ca33c54e0d476d651f139fde5ee2e4aad7302c90.
Runner/module unchanged. No fallback or failed SMC verification. Shutdown reports
3 underruns and5 backlog drops; no perceptual audio pass. Window snapshots show
59.7–60.0FPS in this short Observatory check, not a sustained cadence measurement.
The ~19.8s max graphics/audio gap includes deliberate pause; do not classify that
whole-run maximum as spontaneous stutter. Startup took roughly40s before native
window creation; sample taken afterward shows a responsive main event loop, not
the cause of the preceding delay.

**Next:** execution-plan step2: reuse existing matched slow-scene timing/profile
evidence and isolate a new source-supported cause of the AOT execution-cost gap.
Do not repeat this now-completed frontend smoke, import, or parked microbenchmarks.

## Preparation checkpoint (historical)

The original PRD and G0–G15 remain authoritative. G6 is still unmet; mobile
promotion remains held for macOS performance/stability. Do not restart passed
feasibility steps or interpret historical pending actions as current.

| Requirement | Evidence and limitation |
| --- | --- |
| Current package integrity | R447 fresh app audit passes. Runner671729c6…d762, module1fb635f7…1dc7a match R390. This is not gameplay proof. |
| Nunchuk generation / explicit import selection | R77 fixed sideways generation and arbitrary discovery; current launcher/config source retains these paths. Physical controller play remains separate. |
| Actual import and frontend handoff | R78 native picker/extraction/child launch recorded. R80 fixed blocking parent wait and verified responsive monitoring. Do not redo extraction to replace missing child-gameplay evidence. |
| Current packaged game smoke | R390 bundled-module, real-save Observatory/movement/clean exit; direct-runtime binding. Does not by itself prove current frontend-to-visible-gameplay flow. |
| First Grand Star / normal save / relaunch | R60/R61 proven; R363 newer save/relaunch. Preserve progress. Current complete-route timing/audio acceptance remains open. |
| Gameplay cadence | R421 moving route57.733VIHz; late R431/R432 near55Hz. User-reported20–40FPS episodes are not explained universally. No stable60Hz pass. |
| Audio | R393 quiet diagnostic window has zero event-counted underruns; startup/transition/sustained-movie deficits and perceptual/speaker/lifecycle/soak remain open. Diagnostic silence is not current normal-app audio acceptance. |
| Complete macOS / mobile / shell | Original story/mechanics/stability gates precede iPad then iPhone; full touch/pointer/Spin/tilt/three-dot menu and physical-device/release gates remain required. |

Next bounded acceptance action: current packaged frontend Play into visible child
gameplay using prepared disposable profile, no rebuild/import or emulator state.
Verify foreground/input ownership, real-save load, native pause/resume and clean
child/parent shutdown, keeping timing/audio observations separate from acceptance.
This closes a product-path evidence gap; it does not fix or waive the performance
blocker. No new profiling or parked microbenchmark is justified by this check.

Preparation: `generated/runtime/frontend-acceptance-r447/preparation.json`.
The frontend supports isolated XDG_DATA_HOME; the app wrapper overwrites it.
Launch the packaged frontend directly for this isolated test and state that
boundary, rather than claiming a Finder/dock wrapper test. No game is launched
by preparation. Never attach CUA before the actual child is ready or create a
second app to find its window. At most one game and one Simulator; no Simulator
is needed here. Review source profile Pipe configuration before input automation.
# R457 normal-package frontend promotion — 2026-09-08

Normal app now uses R456's tested frontend SHA
c283de0c3dee9e3f0b01d85f961eeb7515060fd57019aeefd875674ccd4956fc.
Runner671729c6/module1fb635f7 unchanged; previous frontend backed up in
generated/frontend-before-r457. Canonical bootstrap and repeat pass; extracted
monitor regression/full repository suite and candidate/installed package audits
pass (generated/*r457.log). No new game session this turn: R456 same-binary
runtime evidence is retained with its original scope. This is startup-feedback
promotion only; performance/audio/stability acceptance and G6 remain open.
