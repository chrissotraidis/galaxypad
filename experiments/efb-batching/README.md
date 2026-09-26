# EFB readback batching opportunity probe

This experiment measures actual Metal staging-copy encoding. It does not batch,
remove, reorder, wait for, or otherwise change any GPU operation or depth value.
Product source and the accepted archive remain unchanged.

`python3 experiments/efb-batching/prepare.py` writes source snapshots, VFS overlay
and exact build commands to `generated/experiments/efb-batching-20260913`.
It does no compilation or large artifact copying. After the owning timing run
releases the host, `python3 experiments/efb-batching/build.py --build` runs the
small sanitizer recorder contract, rebuilds FramebufferManager/MTLTexture/
MTLStateTracker and CoreHost, replaces only those three core archive members,
and relinks/signs a separate app against frozen host13 objects. Both existing
audio overlays remain in the compile recipes. No installation or launch occurs.

Enable `GalaxyPadDevEfbBatchProbe` in the isolated Simulator app's defaults.
The host samples at most128 records, every120 guest VI fields, using the existing
bounded asynchronous performance writer. Disable the preference for the
instrumented-but-off overhead control. Original accepted app is the independent
uninstrumented control. Restart the process between runs.

GPU-owned thread-local counters perform no timing, allocation, formatting or IO.
Cumulative values publish through atomic stores every64 copy-bearing refreshes; CPU
snapshots carry the published refresh count and can lag current gameplay. Use
the published counter endpoints, and do not treat them as exact time-window
alignment with a separately sampled EFB duration. Snapshot retries are bounded.

`efb_batch_probe` records:

- `refresh`: all RefreshPeekCache invocations, including early returns.
- `active`: refreshes with an actual EFB staging copy.
- `refreshCopies` / `demandCopies`: staging copies within / outside refresh.
- `direct` / `intermediate`: copies classified by the actual PopulateEFBCache
  decision, not inferred from the requested render scale.
- `blitEncoders`: actual EFB staging blit encoders created.
- `contiguousPairs`: consecutive copies within one refresh and command buffer,
  with no intervening observed render, compute, upload, texture-copy, resolve or
  command submission. Existing encoder end/start between the copies is the
  candidate removable work, so it does not itself break the pair.
- `sameResourcePairs`: the subset retaining source texture and destination buffer.
- `multiCopyRefresh`, `maxCopies`, `maxRun`: refresh distribution and cumulative
  maxima. Maximum values are not additive window counters.

Resource identities are compared transiently and never logged. Boundary hooks
are conservative: an upload-encoder request or empty flush can break a run even
without useful GPU work. Counts therefore identify a conservative batching
opportunity, not a guaranteed optimization or exact GPU timing.

The first built probe published every64 total refresh invocations. Actual runtime
revealed that early-return polling occurs millions of times per second, making
that publication rate too high for a minimal probe. The source now publishes
only at each64th copy-bearing refresh; an explicit copies guard prevents repeated
publication during empty calls when the active count is a multiple of64. Empty
invocations still increment the local total and appear in the next active
publication. Counters can remain stale indefinitely while no copies occur.
The recorder regression covers one million consecutive empty calls with zero
extra publications, followed by exactly one publication after64 active calls.
The original built probe and its measurements must not establish low-overhead
performance equivalence. This correction has not rebuilt that app.

At2× each tile can require a utility draw before its staging copy. Those draws
must break contiguous runs. Many copies with zero contiguous pairs argue against
simple blit-encoder reuse; they do not authorize combining render passes or
changing EFB cache coverage. A1's239ms/s EFB service alone does not identify how
much is encoder CPU time, queue dependency or GPU execution.

Decision gate: compare matched1× and2× records with the same scene/core/module.
Only frequent multi-copy runs with meaningful `contiguousPairs` justify a bounded
encoder-reuse prototype. Preserve all rectangles, depth bytes, cache invalidation,
ordering and completion fences. First compare instrumented-off and on frame
windows to bound measurement overhead. No optimization is implemented here.

Build verification completed after the owning A/B/A timing run ended. The
ASan/UBSan recorder contract, all four isolated compiles, archive-member scope
check, link and strict ad-hoc signature verification passed. Linked symbols
confirm one shared probe publication state and one thread-local recorder entry.
The app was not installed or launched by the builder.

Candidate host SHA-256:
`18450ec359e4ff563b9044aaa270016c937446958bb86263b510995fe5361a51`.
Candidate core SHA-256:
`475e8d44cf6727c651d1c5248f18af3cd1a0698ee315935b8c69af56ce95d7fe`.
The original accepted core remains
`457f4dba560eab8aeb899406340852244ef8bb1554b987e2bf1f26883ed94cb8`.
Exact commands, source hashes and verification are in the generated
`recipe.json` and `verification.json`.

## Corrected probe and direct-copy candidate

The publication correction was separately built in
`generated/experiments/efb-batching-v2-20260913/GalaxyPad.app`:
host `eb0dbaabbfd4203b631d0eb875343e7e0b8ff84a5f21358a55716978447eb729`,
core `9ad1e76d2bccdd6e2a53a3acb6ef8616db95184f232a84bf67385945d1c444aa`.
The original probe app/recipe remain intact, with its exact header recovered and
verified against the original recorded SHA-256.

The owning session observed 360 active refreshes,1080 copies and720 same-resource
contiguous pairs over120 guest fields at1×: three copies and two candidate
encoder boundaries per refresh. At2× the same-sized delta had1080 intermediate
copies, zero direct copies/pairs and maximum run1. The2× utility draws therefore
exclude straightforward encoder reuse; the high EFB duration alone is insufficient.

Prepare the separate prototype with:

```
python3 experiments/efb-batching/prepare.py --batch --output generated/experiments/efb-direct-batch-20260913
```

The independent, default-off switch is `GalaxyPadDevEfbDirectBatch`.
`GalaxyPadDevEfbBatchProbe` still independently controls measurement. One candidate
binary can therefore supply off/on A/B without changing probe settings.
Batch eligibility exists only in a copy-bearing refresh and its direct-copy path.
The helper retains an encoder only for the same command buffer/source texture/
destination buffer. Every generic EndRenderPass, command flush, upload-encoder
request and refresh exit closes it. Only the eligible staging-copy continuation
can skip the generic close. All copy arguments and completion waits are unchanged.

The builder runs CPU scope/switch contracts and a native Metal parity harness
before building the candidate. That harness uses the exact shared batching
helper, spatially varying D32F depth,640×528 staging buffers, a partial bottom
tile, untouched-byte checks and render/compute/blit/resource/command-buffer
boundaries. It runs with Metal API validation. GPU tests and compilation must
wait until unrelated timing runs release the host. App installation, actual
gameplay correctness and performance A/B remain with the owning session.

The direct-copy candidate built and passed on 2026-09-13. Host SHA-256:
`cb092f7fa2cef3c234882e16e6f99d3110b5cc8f19500b861189eaf09af06a56`;
core SHA-256:
`9f3f796fc80eb1a98ec9fc4e964c5af37d2f5ed89a2e620667cc05c6a5ff1c17`.
CPU recorder and scope contracts passed AddressSanitizer/UndefinedBehaviorSanitizer.
Native Metal API validation passed 112 trials: 336 baseline encoders versus 224
candidate encoders across the boundary cases, with full staging-buffer, spatial
depth and untouched-byte parity. This establishes the helper's copy behavior;
it does not replace actual gameplay checks of the integrated call sites.
Compilation, archive member scope, link, ad-hoc signing and strict signature
verification passed. The app was not installed or launched by this builder.

The corrected v2 control and batch candidate now each have `frozen-inputs`,
including their exact probe header, batch helper where applicable, and test
sources. Their VFS overlays resolve original header paths to these snapshots;
`build.py --output ...` validates these frozen inputs rather than mutable shared
headers. `recipe-before-input-freeze.json` preserves the original build receipt.
The freeze changes no app bytes. Use `freeze.py OUTPUT [--probe HISTORICAL_HEADER]`
after preparing/building future experiments to preserve these inputs. Re-running
`prepare.py` replaces the prepared experiment; use a new output directory for a
new variant. Original v1 remains a historical artifact/receipt with its recovered
`EfbBatchProbe-v1.h`, not a claim of rebuild support from current test sources.


## Integrated timing decision

Same-binary batch-off/on/off, probe disabled, measured49.76/46.63/48.51 frame
events/s in the fixed1x Simulator scene. The candidate is **not promoted**.
A separate probe-enabled integration run confirmed1,152 copies using384encoders
in one published interval: batching operated but did not establish a speed gain.
See [pass3 results](../../docs/IOS-PERFORMANCE-PASS3-2026-09-13.md) for method,
hardware limits and the unresolved generic runtime-error caveat.
