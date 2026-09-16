# iPhone audio starvation below 36 FPS

The owner reported severely choppy audio in build 7164. Its live iPhone 14 log
confirms 2,176 new unavailable synthesis windows in 32.199 seconds. Real input
supply, calculated from enqueue deltas, was 56.995% of full speed. Output callback
short-count delta was zero: filling the output buffer does not mean it contains
continuous game audio. Gameplay was about 34 FPS, 1x, with serious thermal state.
This pass used the uninterrupted log rather than opening QuickTime, which had
previously interrupted the phone's audio session.

## Reproduced cause and repair

The audio controller enforced a 0.60 minimum analysis rate. Sustained 0.57 input
therefore consumed its reserve, then repeatedly failed to synthesize. The exact
maintained header reproduced 4,561 unavailable windows in a 30-second steady
0.57-supply fixture. Merely caching search energies cannot repair this mismatch;
that cache did not introduce the floor and is retained.

The maintained RecompCore `GALAXYPAD_AUDIO_LOW_SPEED=1` candidate:

- Lowers the floor to 0.45, leaving correction headroom below tested 0.55 supply.
- Reduces the queue control target by one 128-frame hop, without changing startup
  or capacity, to preserve the older range's latency bound.
- Leaves unity bypass one hop earlier when the smoothed supply estimate falls
  below 0.90. Instantaneous packet supply was rejected because it incorrectly
  left bypass during healthy full-speed packet jitter.

Lowering only the floor exceeded the historical mixer latency gate. Reducing the
reserve alone exposed four unavailable windows on a 1.0-to-0.55 transition.
Both were rejected before installation. The final combination passes those cases.
There is no unbounded replay, fake supply, larger allocation, pitch-rate change,
class-layout change or disabled true-stall counter. Below tested supply, including
complete stalls, continuous output is not promised. This is not an FPS repair.

## Validation

`tests/test-audio-low-speed.py` reproduces the faulty control and passes 42
release/sanitizer cases against the maintained header. These cover steady and
bursty supply, slowdown/recovery, stall, reset, flush, accounting, allocations,
silence gaps and exact full-speed PCM. The default repository suite includes it.

`tests/test-audio-tempo-mixer.py --low-speed` additionally executes the actual
maintained mixer methods, including windowing, resampling and output quantization.
58 candidate cases pass, with zero unavailable windows in tested producing
streams and positive counts during a real one-second stall. Tone pitch error is
at most 2 Hz and target-band power exceeds 85% in the tested tones. The old
0.67–1.0 supply cases retain their 120 ms wall-age gate; new 0.55–0.60 cases have
an explicitly separate 160 ms gate. Final observed maximum across all mixer
cases is 134.625 ms, excluding hardware output latency. At full speed, comparison
with the historical fixed-rate mixer remains 0.575 s16 RMS / 2 units maximum
error after time alignment. No existing gate was relaxed to accept the repair.

The complete default repository suite passed. The actual arm64 iPhoneOS mixer
object compiled and linked with the three audio experiment flags. Device-build
receipt hashes identify the final maintained header and retained inputs.

Private evidence is in generated/audio-slowdown-20260916/: live-baseline.json,
control/candidate probes, rejected variants, rate-gate-regression.log,
rate-gate-mixer/results.json and repository-final.log. The separate
generated/audio-slowdown-7165-20260916/ directory holds the build and deployment.

## External precedent and scope

[Dolphin's audio report](https://dolphin-emu.org/blog/2025/06/04/dolphin-progress-report-release-2506/)
describes the shortage of audio when emulation slows and the latency/continuity
tradeoffs of stretching and gap filling. Our failure is more specific: the
controller's minimum consumption exceeded measured production. The fix changes
that controller; it does not establish subjective sound quality or faster game
execution on the phone.

## Deployment

7165 is installed on the rediscovered iPhone 14, in place over verified 7164.
The exact final maintained header compiled with low-speed, batched-search and
cached-energy flags; only the mixer archive member was replaced before relinking
the retained 7163 host. The game module is unchanged. Same signer/entitlements/
profile checks and deep strict iPhoneOS verification passed. All 54 protected
save/configuration/preference files were byte-identical on readback before launch.
PID 4560 starts build 7165, reaches sustained startup frame events around 60/s
and produces nonzero audio after the initial quiet startup. It is unpaused at
1x with detailed logging. Startup had 23 unavailable windows and input drops;
these cumulative counters are not a steady-gameplay result. The prior redacted
runtime error recurred without stopping the process. Demanding-gameplay audio
and FPS acceptance remain open. No public release or default promotion.


## Owner feedback supersedes counter-based acceptance

After testing 7165, the owner reports audio remains bad during demanding gameplay
and no noticeable performance improvement. Physical audio acceptance is **failed**.
An observed 74.10-second post-transition interval had zero new unavailable windows,
nonzero audio output and varied 30.39–60.00 frame-event rates. This proves only that
one counted starvation mechanism stopped during that interval, not that audible
quality improved. Stretch artifacts, rate changes and other mixer behavior remain
unresolved. The owner reports sound becomes acceptable in less demanding areas.
No further build should be presented as improved audio based only on this counter.
The live-gameplay.json receipt preserves that distinction and the earlier transition
underruns. The game-performance goal is not achieved.
