# R819: matched plaza reached; Instruments attach path fails bounded attempts

Previous turn was progress: exclusive symbol accounting identified missing
instruction weights. This turn attempted the actual capture and established a
tool limitation, not a new performance result.

Same sole Simulator DE8E956F-6B29-4FF3-AF4A-77034CE8588A, unchanged R791 host
85ffc10065d375062a0c445d87d0a501d4fc91e236986d6d55d74f0b8333dbcc and baseline module
3acdcddcd47812c2e2a67b8cec0cf06c17009cf1ad7f2e9dc9abd83158a1bac0 verified.
Existing disc/save paths and expired/short-leased diagnostic input used; no build
or module replacement. Game PID53643/console80351 reached the existing Mario
file and visually verified neutral Star Festival starting plaza. Screenshots
generated/plaza-r819-before.png and plaza-r819-after-profiler.png confirm scene
before and after the CPU Profiler attempt. Portrait-capture geometry issue remains.

## Actual outcomes

- Host-default CPU Profiler attach could not find PID53643, exit21.
- Explicit Simulator CPU Profiler PID54071 recognized GalaxyPad but failed to
  complete a requested 10-second capture. A 40-second wall watchdog sent INT,
  with TERM fallback; process exited1 and was verified absent.
- spindump timeline/onlyTarget refused with exit77: live sampling requires root.
  No privilege change or workaround attempted.
- Explicit Simulator Time Profiler PID54233 likewise recognized the target but
  stalled past its requested 10 seconds. Same watchdog; exit1, verified absent.

Logs: generated/plaza-profiler-r819.log and plaza-time-profiler-r819.log.
Both incomplete trace directories were only 52 KiB when inspected; there is no
successful export or usable per-PC profile claim. The shell watchdog wrappers
exit0 after reporting the child outcome; child exit1 is the authoritative failure.
This reproduces the earlier R534 Simulator attach problem under a bounded guard.
Do not repeat this unchanged Instruments attach path.

Runtime log generated/plaza-profile-r819.log contains frame/audio observations,
including approximately 45 frame-events/sec in one pre-profile window. That is
not a controlled speed comparison or an improvement from code changes. No code
changed, and startup/profiler/host variation must not be conflated with a fix.

Game terminated through simctl and the sole Simulator shut down successfully.
Console80351 finished; game and profiler PIDs are absent. GameData SHA256 remains
99d432d517b92b19da0c403819b91288b10c7063c3ce61f5000347ef823ab64f.
No native clean-Stop callback, audio acceptance or gameplay completion is claimed.

## Next useful action

Before another game boot, preflight an alternative that actually preserves raw
instruction PCs: a narrow read-only Mach thread-state sampler against an owned
test process, with ordinary task-access checks, guaranteed balanced suspend/resume,
bounded duration and failure cleanup. Do not bypass task-access restrictions or
guess per-PC weights from the collapsed sample. Raw PC wall observations would
not be hardware cycle weights and must be labeled accordingly. If normal access
is unavailable, use the working macOS profiling lane to form a source-matched
hypothesis rather than repeatedly stalling the Simulator. Full original PRD,
SunPad, performance/audio/stability/progression/device objective remains active.
