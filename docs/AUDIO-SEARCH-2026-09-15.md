# Batched audio correlation experiment

The physical iPhone 14 slow-scene trace attributes 1.808 seconds of CPU samples
in a 30-second window to `AudioTempo::Synthesize`, approximately 6% of one core.
The game CPU thread separately accounts for 29.274 seconds: this audio change
targets auxiliary CPU and sustained power cost, not the entire game bottleneck.

The maintained RecompCore fork now has an opt-in
`GALAXYPAD_AUDIO_BATCHED_SEARCH=1` path. It accumulates four independent search
positions together, sharing overlap loads and permitting compiler vectorization.
Each position retains the scalar sample accumulation order, float products,
double accumulators, normalization, center preference and ascending tie order.
The remaining positions use the original scalar loop. No search range, buffer,
queue, resampler, latency policy or class layout changes. Default builds remain
scalar pending physical acceptance. This is not a bootstrap patch.

`tests/test-audio-search-batching.py` builds both variants from the maintained
header with `-O3`, and again with ASan/UBSan. Thirty-two comparisons cover unity,
60–85% supply, periodic/mixed signals, ring wraps, changing supply, stalls,
recovery, burst delivery, reset and flush. All produce identical PCM bytes and
identical accounting/provenance results. Alternating nine control/candidate
12-second synthetic runs showed approximately 36–37% lower median Pull processing
time on the Mac. This is an offline component result, not an iPhone FPS result.

The iPhone trace's host and module UUIDs both match the preserved build-7 package.
Private matched device builds reuse all thirteen host objects and the same game
module. They replace only the Mixer object compiled against the identical frozen
Mixer layout, with batching either disabled (build 7150) or enabled (7151).
Both are linked with the same recipe and verified using the original signing
identity. Private build recipes, hashes, test results and traces remain under
`generated/audio-search-20260915`; these include sensitive device evidence and
must not be published.

Physical comparison must match the Observatory scene, camera, render scale,
audio route and thermal state. The original slow trace had serious thermal
pressure. Compare audio-thread CPU time first and unprofiled frame cadence
separately; a faster component is not automatically faster gameplay. Existing
build 7 lacks output-audio instrumentation, so its DMA counters cannot establish
output quality. Human listening remains required.

The larger follow-up is dispatch overhead. Exact installed-binary mapping places
the most sampled `StaticRecompCore::Run` instructions around per-dispatch state,
cycle accounting and eligibility/interrupt checks. Their weights are not proof
that those checks can be removed. Preserve timing, exceptions, host calls and
module invalidation semantics before testing a narrower fast path.
