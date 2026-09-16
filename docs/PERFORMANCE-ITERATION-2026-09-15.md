# Performance iteration: September 15, 2026

> Session closed: [current build, owner assessment and research handoff](SESSION-CLOSE-2026-09-16.md).
> This document retains the evidence and acceptance limits of its dated experiment.


Follow-up: the [game-INI harness repair](SIMULATOR-GAME-INI-2026-09-15.md)
found that requested local settings were being staged in an ignored directory.
The earlier precision-timing result uses launch flags and is unaffected.

Precision waiting is not a useful throughput target in the measured slow
Observatory scene. This pass produced a rejected hypothesis and a narrower
readback investigation, not a new performance default or a claimed phone gain.

## Measurement

Ran the already prepared, private precision-timing v2 experiment in a newly
created iPhone 14 Simulator on an M3 Max, macOS 26.6.2, Simulator runtime 26.5.
The experiment is the historical host13/audio-tempo core with the retained PGO
module, not today's PR build. Its source overlay and other existing experiments
were left unchanged. Its underlying timer behavior still matches the current
pinned runtime. No patches were added to bootstrap or the maintained forks.

The isolated route used the verified 121-star save and reached the stationary
Observatory map platform, visually checked before analysis. Other work, including
one KartPad Simulator, continued on the Mac. These are diagnostic measurements,
not an uncontended hardware benchmark or a control/candidate comparison.

The measurement flag was enabled; the disable-precision flag was false and the
runtime logged precision timing active. Between 09:45:20 and 09:46:07 UTC:

| Measurement | Result |
| --- | --- |
| CPU-throttle timer calls | 12,643, all already late |
| Video-presentation timer calls | 2,032, all already late |
| New positive-delay calls, either lane | 0 |
| Timer thread CPU delta, both lanes | 4.807 ms over 46.657 seconds, about 0.0103% of one core |
| Nearby nine frame-event windows | 2,093 events / 48.100 seconds = 43.514 events/sec |

The timer clocks have uncalibrated measurement overhead. The clock deltas are
not a prediction of recoverable CPU time. Frame windows and timer publication
windows have slightly different boundaries; frame events are not display FPS.
Nevertheless, zero new positive-delay calls rules out substantial intentional
precision waiting in this particular slow workload. Do not spend another
throughput A/B/A run on simply disabling it here. A separate title-screen power
experiment remains plausible: the probe observed positive waits before gameplay.

A separate 20-second `sample` capture began at 09:46:09 UTC. It found 2,913 of
14,811 CPU-thread stack observations waiting on a float future and 2,894 of
14,806 video-thread observations in `FramebufferManager::PeekEFBDepth`, almost
all beneath Metal's `waitUntilCompleted`. These are blocked stack observations,
not percentages of CPU consumed, and the two waits must not be added together.
The capture also contained generated guest code and portable vertex conversion.

Current source confirms that a depth cache miss populates the cache and that
`needs_flush` forces readback completion before returning the depth texel.
The next diagnostic should count cache misses, invalidation reasons and actual
readback waits per frame in the maintained ModernGekko fork. Match the pointer,
camera and scene, then compare a correct cache/readback change only if those
counters establish redundant work. Keep depth semantics and Pull Stars intact.
The previously rejected direct-copy batching and fused-vertex experiments are
not revived by this stack capture.

Private receipts remain in `generated/iteration2-20260915`: artifact hashes,
the route, timing deltas, runtime logs, scene captures and a separate stack
capture. The dedicated Simulator was shut down after the run; existing devices,
test fixtures and other Simulators were preserved.

## Physical phone

Launched the existing iPhone 14 build7 in place and watched it through QuickTime.
The title screen showed 60 FPS. Instruments listed the phone offline, and a
retry using its Instruments device identifier timed out. Device launch and log
copy still worked. No usable phone CPU trace was produced and no candidate was
installed. The physical saves, game data and settings were not replaced.

A later view showed the game's Wii Remote communication-interrupted message.
Startup logs reported zero connected hardware controllers, but did not establish
the trigger for the guest message. Retained fresh logs for this separate issue;
do not call it a Bluetooth disconnect or a reproduced current-main regression.
The title/dialog workload continued near 60 frame events/sec, with thermal state
1 and roughly 81% process CPU in late windows. This is not demanding gameplay
acceptance. QuickTime was a visual monitor, not an audio-quality test.

## Further research and applicability

- [PPSSPP's IR design](https://www.ppsspp.org/docs/development/developer-tools/)
  reduces interpreted instruction work through an intermediate representation
  and optimization passes. GalaxyPad already emits native code ahead of time;
  the transferable idea is reducing generated work and memory traffic, not
  replacing it with an interpreter or assuming iOS JIT availability. Profile
  real hot blocks before another compiler transformation.
- [Dolphin 2509](https://dolphin-emu.org/blog/2025/09/16/dolphin-progress-report-release-2509/)
  changed desktop dual-core defaults for stability while retaining dual core on
  Android for performance. Thread settings are workload/device tradeoffs. This
  does not justify toggling GalaxyPad's existing dual-core default globally.
- [PPSSPP 1.20](https://www.ppsspp.org/blog/) describes optional smoother audio
  during slowdowns at the cost of latency. GalaxyPad already has audio-tempo
  work; judge any further buffering by underrun and latency measurements,
  separately from game throughput. More buffering is not a CPU optimization.
- [Apple's Metal performance guidance](https://developer.apple.com/documentation/xcode/analyzing-the-performance-of-your-metal-app/)
  recommends combined threading and GPU timelines to locate stalls. This fits
  the readback lead, but a desktop blocked-stack sample cannot establish the
  physical phone's CPU/GPU dependency timeline.

The previous importer/Game Mode draft remains separate: both hosted source and
iOS build checks passed on `dcf35c9`. No result here promotes a new runtime
default, closes the crystal-heavy iPad report, or establishes physical audio
acceptance.

Validation: the complete default `scripts/check-repository.sh` suite passed
after this pass; `git diff --check` passed. The new report is local, and no new
runtime change or device installation was made.
