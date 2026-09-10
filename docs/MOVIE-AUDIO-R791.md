# R791 native movie and RemoteIO delivery

Private Simulator candidate, September 9, 2026. Not a full audio, gameplay,
physical-device or release acceptance result.

## Matched measurements

| Phase | Covered time | Frame events/sec | Output PCM frames/sec | DMA underruns | Nonzero output |
| --- | ---: | ---: | ---: | ---: | ---: |
| Airship movie | 36.900 s | 59.946 | approximately 48,009 | 0 | 100% |
| Post-movie plaza | 21.500 s | 31.953 | approximately 48,009 | 104 | 54.58% |

Movie VI estimates59.940–59.941, emulation speed0.9980–1.0033. Movie output
delta1,771,520 frames,3460 callbacks,9224 DMA granule enqueues; no backlog/full
drops or short callbacks. Post-movie output1,032,192 frames,563,402 nonzero,
2016 callbacks,2866 enqueues; no backlog/full drops or short callbacks.
Enqueues are overlapping mixer granules, not PCM frames.

Frame-event coverage and audio snapshot endpoints differ by only tens of
microseconds. These are not display-completion measurements. Output rates are
quantized by512-frame callbacks; timestamp bounds do not include independently
atomic counter sampling. Nonzero frames do not prove correct content/pitch/AV
sync. Natural silence and other mixer sources also affect the nonzero fraction.

Observed airships before capture and return to invaded plaza afterward. No
input helper ran during either capture; no build/profiler ran. Host capture
records unrelated CPU load and memory compression; both captures had zero
swapins/swapouts. This is sequential scene comparison, not controlled A/B
proof of host causation or an isolated telemetry-overhead test.

## Artifacts and reproduction

- `generated/ios-runtime-r791b.log`, console29585/PID38079.
- `generated/movie-audio-r791.json`:45s capture,7 complete frame windows.
- `generated/post-movie-audio-r791.json`:30s capture,4 complete frame windows.
- `generated/movie-start-r791.png`, `generated/movie-return-r791.png`.
- Audio command: `python3 scripts/summarize-audio-window.py generated/ios-runtime-r791b.log --start 547722 --end 547761`.
- Plaza command: same script/log, `--start 547818 --end 547840`.

Do not compare the native decoder's CLOCK_MONOTONIC numeric timestamps directly
with host CACurrentMediaTime timestamps: their origins differ in this run. Use
wall epochs to relate decoder timing to host logs; audio/frame logs share the
host time domain.

Candidate SHA85ffc10065d375062a0c445d87d0a501d4fc91e236986d6d55d74f0b8333dbcc,
module SHA3acdcddcd47812c2e2a67b8cec0cf06c17009cf1ad7f2e9dc9abd83158a1bac0,
root289a87a1499c3d0da23c21c472fd16525742208a. NativeTHP build ON/launch YES,
THP_TIMING=1, AUDIO_OUTPUT_DIAGNOSTICS=1, frame windows enabled. Normal app
and module unchanged. M5 iPad Simulator, Metal, GFX.ini InternalResolution1,
Dolphin.ini AudioBufferSize120, CoreAudio48000Hz. No device evidence.

Clean native stop09:19:19.375 reports failed0, smc_failed0, movie5591 accepted,
0 decoder fallbacks. Save99d432d517b92b19da0c403819b91288b10c7063c3ce61f5000347ef823ab64f
unchanged. No malformed-XF assertion observed, not proof that fault is fixed.

## Decision

This closes the missing *measured callback-delivery* evidence for the private
movie path, not all decoder promotion gates. Keep default OFF pending perceptual
audio/sync and remaining integration/device/rights gates. Do not repeat this
movie for ordinary throughput/counter proof.

Gameplay still produces audio too slowly while RemoteIO keeps requesting real
time output. Existing Apple adaptive resampling is bounded to±2%; a120ms reserve
cannot compensate for sustained approximately half-speed gameplay. Do not hide
this with larger buffers or claim the callback is the primary bottleneck.
Return to material native guest execution cost, using retained instruction-level
coverage and exact-policy disassembly before another build. Reject repeated tiny
helper/predicate variants. Full original PRD and SunPad requirements remain open.
