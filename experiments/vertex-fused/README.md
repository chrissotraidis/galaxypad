# Fused portable vertex experiment (2026-09-13)

**Keep experimental; do not promote on this result.** A single fused AOT converter reduced its source-extracted CPU microbenchmark by approximately 33%, but a stationary Observatory Simulator A/B/A measured **45.574 → 45.865 → 45.114 FPS**. The candidate's +0.64% versus the first control and +1.66% versus the returning control do not establish a meaningful whole-game benefit given roughly 1% control drift. This does not establish whether it could benefit a profiled A15 bottleneck.

The private format diagnostic counted 65,289,591 vertices in 13,045,760 batches after visually verifying the 121-star Observatory. One converter structure covered 72.61975% of vertices: VCD `00007e00,00000003`, VAT `40f76c07,c8241209,04824120` after masking only position and texture-0 fractional scale bits. Its stages are indexed u16 XYZ signed16 position, indexed u16 signed16 normal N, indexed u16 RGBA8888 color, indexed u16 ST signed16 texture, and the existing skip stage. The guard retains all other format bits; scales remain runtime values. Other formats retain the generic loader.

`probe.py` verifies exact source hashes from `scripts/probe-vertex-stage-unroll.py:PINS`, extracts existing converter bodies, and generates a private translation unit. It does not repeat the rejected stage-unroll experiment. Co-locating the measured stages allows actual O3 policy to inline them into a loop without indirect calls. It adds no executable-memory generation and modifies no canonical vendor source or shared core.

## Reproduce locally

These tools require this checkout's **private frozen audio-v8 Simulator build** (`generated/build/ios-simulator-audio-tempo-isolated-retry-20260912`) and **host6 objects/recipe** (`generated/build/ios-simulator-settings-perf6-20260913`). They do not download game data or build an unrelated core. The archive builder refuses a base archive other than SHA-256 `457f4dba560eab8aeb899406340852244ef8bb1554b987e2bf1f26883ed94cb8`. Use a fresh output directory:

```sh
python3 experiments/vertex-fused/probe.py --output generated/experiments/vertex-fused-new
python3 experiments/vertex-fused/extended_parity.py --experiment generated/experiments/vertex-fused-new
python3 experiments/vertex-fused/build.py --experiment generated/experiments/vertex-fused-new
python3 experiments/vertex-fused/measure_aba.py --experiment generated/experiments/vertex-fused-new --simulator YOUR_DEDICATED_SIMULATOR_UDID
python3 experiments/vertex-fused/summarize.py --experiment generated/experiments/vertex-fused-new
```

Measurement runs only on the explicitly selected Simulator. It uses the existing unattended script to back up and reseed private test NAND, then measures 45 seconds without process sampling after the Observatory screenshot. Five-second detailed logging is enabled equally; format logging is disabled. Do not run other builds/games during comparison. Visually inspect all scene screenshots before interpreting results. The archive replaces exactly `VertexLoader.cpp.o`; host6 objects, module and other core members remain the baseline. Receipts retain source/core/host hashes and actual link arguments.

## Correctness evidence and limits

The initial ASan/UBSan harness passed 13,104 complete-loop cases: counts 0/1/2/3/4/17/128, unaligned stream offsets, explicit maximum-index skip, cache/output bytes, cursors, skips, counters, fallback and fractional scales including 0 and 31. This is a source-extracted harness with simplified loader state, **not full production VertexLoaderTest or renderer integration proof**.

Extended tests use distinct array bases; strides 1/7/14/31/32; mask-preserving fractional edits; and explicit rejection of each descriptor/VAT word. Rejection cases append an observable marker to the generic pipeline, so mistakenly accepting a guard cannot silently pass. The 20,160 comparisons match. Full UBSan reports existing typed signed16 misaligned loads with odd strides in the reused generic bodies. The separate run with alignment sanitization disabled passes ASan and remaining UBSan checks without reports. Do not report the odd-stride full-UBSan run as clean, or treat disabling its check as fixing alignment semantics. A production candidate needs upstream-style alignment handling and actual loader integration parity before hardware promotion.

All three measured runs had thermal state 0, process CPU approximately 120% of one core, and zero observed DMA underrun/drop or >100 ms frame-gap counter deltas within their logged windows. The first retained frame window may begin before the observation log stream; this explains total reported window seconds differing from 45. These are event counters, not display completion, physical-device gameplay, or audio listening proof.

Private raw evidence: `generated/experiments/vertex-format-pass2-20260913/{distribution.json,formats.log,run/scene.png}` and `generated/experiments/vertex-fused-pass2-20260913/{measurement.json,receipt.json,candidate-disassembly.txt,A1,B,A2}`. The specialized object loop has no calls; generic fallback retains its indirect call. No hardware core was changed. Retain the candidate for a future measured phone vertex hotspot, rather than claiming the microbenchmark gain as FPS.
