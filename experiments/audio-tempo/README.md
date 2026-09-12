# Isolated DMA tempo experiment

This remains an opt-in runtime experiment. The combined threading/audio private
candidate passed matched Simulator checks and was installed on the iPad; subjective
physical sound acceptance remains open. Canonical Dolphin audio sources are
unchanged; the normal host now enables CPU/render overlap. See the
[September 12 handoff](../../docs/PERFORMANCE-2026-09-12.md).

`AudioTempo.h` uses one stereo-correlated overlap-add offset for both channels. It changes analysis position to match real input supply while keeping output sample frequency fixed. A 1x path copies raw input exactly. Producer input, rejected input, consumer retirement, explicit stall/flush discards, synthesis output, and genuine unavailable windows remain distinct. Push/Pull allocate no memory and take no locks. Reset requires both threads stopped; concurrent lifecycle work uses consumer-only flush.

## Reproduce

```sh
python3 tests/test-audio-tempo.py --output generated/experiments/audio-tempo-new-run
python3 scripts/create-audio-tempo-integration.py --output generated/experiments/audio-tempo-new-copy
python3 tests/test-audio-tempo-mixer.py \
  --candidate generated/experiments/audio-tempo-new-copy \
  --output generated/experiments/audio-tempo-new-mixer-run
```

The generator requires a new output directory. It creates copied Mixer.cpp/h, a copied tempo header, patches, and SHA-256 manifest. It does not edit canonical runtime sources or build/install an app.

## Frozen evidence

- Standalone v15: `generated/experiments/audio-tempo-v15-20260912/results.json`; 52 O3 and ASan/UBSan cases pass. True 1x input identity, return to identity after sustained recovery, 55–997 Hz pitch, stereo phase/anti-phase, transients, producer fractions 0.67–1.0, packet jitter, speed steps, actual long stall, pause/reset/consumer flush, allocation and input accounting checks. Exact final SPSC ownership/flush TSan passes separately. Apple arm64 device and Simulator header probes pass.
- Copied mixer v8: `generated/experiments/audio-tempo-integration-v8-20260912/`. Both exact Mixer translation units compile for arm64 iPhoneOS and iPhoneSimulator 16, with the control compiler settings; logs/commands are beside the copies.
- Exact 48 kHz mixer fixture: `generated/experiments/audio-tempo-mixer-v8-final-20260912/`; 30 render cases including O3 and ASan/UBSan. Genuine unavailable count is zero in tested producing 0.67–1.0 steady/bursty/step streams and pause/actual DoState restore recovery; a one-second producer stall still increments it. Accepted-input/128 equals legacy DMA enqueue count, independently of synthesized output.
- Worst measured input-arrival-to-output age is **118.625 ms**, including both DPSS-windowed granules and all six Hermite taps. This is measured wall age in the tested schedules, not a guarantee inferred from raw ring capacity; hardware output latency is outside the fixture. A 64 ms delivery schedule is tested. Longer stalls necessarily exhaust finite real input and remain reported.
- At 1x, time-aligned 48 kHz PCM versus the unchanged fixed-rate legacy window/Hermite/quantization path has **0.575 s16 units RMS error and 2 units maximum error**. It is not bit-identical after the different startup phase/quantization history. The original Apple dynamic-rate control itself measured 997.8 Hz for a 997 Hz input; the candidate and fixed-rate reference measured 997 Hz.
- Standalone O3 processing cost peaked at 1.61% of one host core; max measured Pull was 0.473 ms. These are host synthetic timings, not iPad CPU/FPS acceptance.

## Mixer integration contract

Only DMA PushSamples uses tempo input. Other FIFO behavior stays unchanged. There is one tempo object in Mixer, not one per peripheral FIFO. The copied mixer bypasses the old DMA reserve and +/-2% pitch-rate adjustment; it does not queue tempo output into a second legacy FIFO. Instead it pulls exactly the callback's required 128-frame hops into fixed scratch storage once, then uses the exact existing DPSS window, Hermite interpolation, volume, and quantization. Requests above 2048 output frames are processed immediately in bounded pieces.

The callback-wide pull is essential: the rejected first integration called Pull(128) repeatedly inside a callback, assigning one whole producer packet to its first 4 ms slice and zero supply to the remaining slices. It exceeded 120 ms under bursts; lowering only the target also caused real starvation. V8 restores the frozen standalone parameters and corrects that scheduling boundary. Rejected v2–v7 artifacts remain for audit.

Pause and restore flush only the consumer tail/local buffers; producer head is never reset concurrently. Unsupported DMA divisors latch an explicit candidate failure and log an error **before** altering queued-data interpretation. The candidate then silences its DMA path until stream recreation; it does not silently reinterpret 48 kHz input at 32 kHz. This candidate is limited to the game's verified 32 kHz DMA path.

Mixer.h changes its allocation size. Integration requires a full isolated core rebuild of all dependent translation units plus GalaxyPadCoreHost.mm. Use the reviewed `scripts/prepare-audio-tempo-core-host.py` recipe; never replace only Mixer.o in a core built with the old layout. Preserve the old canonical PGO profile and normal control module to isolate audio behavior. Actual Simulator diagnostics and logging-off comparison are recorded in the linked handoff. Subjective/device sound acceptance remains required before release promotion.
