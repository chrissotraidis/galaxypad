# Upstream delta

## R544: preserve hidden state during pointer reacquisition

ModernGekko-dolphin/0023-pointer-reacquisition.patch SHA256
8310e45ac65c4743924f1edf902dc056da4d54fc8eee925a474d157c1443233d.
Against pinned Dolphin13e492094902644b0d113c586300d358640f9e19.
EmulatePoint previously overwrote position.y with+2 before testing y<0, making
the documented hidden→visible immediate angle reset unreachable. Capture the
prior visibility first; existing visible motion still uses acceleration smoothing.
No changes to projection, sensitivity, depth, guest code or motion consumers.

test-pointer-reacquisition.py compiles the actual checkout function body with
narrow dependency doubles. Unchanged source fails hidden→visible smoothing-call
assertion; corrected source passes, including repeated reacquisition, continued
visible smoothing and both sensor-bar offset signs. This is branch-contract
proof, not full Dolphin integration or live-game pointer timing acceptance.
Patch reverse-check and bootstrap syntax pass; bootstrap includes hash guard,
peel/restore/apply and scope, but full bootstrap not rerun against active graph.
Incremental Simulator core/provision/app builds pass. NOT installed yet.

## R457: visible frontend startup progress

ModernGekko/0027-frontend-launch-progress.patch SHA256
c150fe4fd3feafa8583e23861872737a8e4b60972494a47f3c0b56b044635703
layers on 0013's nonblocking child monitor. It displays elapsed startup at 4 Hz,
hides after the existing module-loaded marker and processes close/quit as one
graceful child termination request. Bootstrap pins, peels before 0013 and restores
or applies after 0013; patch scope includes this delta. Initial bootstrap passes
and resulting source is byte-identical to the R456 runtime-tested candidate.
Extracted monitor tests cover success, child exit7, wait failure, quit, matching
window close and unrelated-window close; repeated events request termination once.
This is startup feedback, not faster initialization or gameplay. Runner/module
remain unchanged; frontend-only normal-package promotion and audit subsequently
pass, as do repeated bootstrap and the repository suite. Readiness uses a bounded log
tail, not a guaranteed IPC handshake; no claim of failed-kill recovery is made.

## R400: opt-in depth dispatch timing

experiments/efb-dispatch-timing.patch SHA256
5226881b8ce0f00b0b2673b68f40040fa4490771d170aade1289db00ae19b638
wraps the existing depth PushBlockingEvent/read callback with opt-in four-stage
timestamps. Disabled/open-failed output invokes original dispatch/read; depth
bits and single invocation verified under sync/future ASan/UBSan/O2 tests.
No emulated state, queue, readback or depth conversion change. Outermost
bootstrap overlay peels before context, restores/applies after it; repeat passes.
Exact-source tests preserve underlying context overlay and reject unknown edits.
Separate diagnostic package built/audited; runtime stage evidence pending.

## R397: live AOT EFB diagnostic context

experiments/efb-live-read-context.patch SHA256
4d5782faa59f0dc77bdc31c3bef75c2e8215088b427a308337bbfe21d410b775
adds a trace-enabled thread-local scoped PC/LR in both external-read hooks;
color/depth diagnostics consume it, with zero for unattributed reads.
This replaces stale mirrored-register attribution without synchronizing
emulated state or changing MMU, depth values, queue or buffering semantics.
Bootstrap outer-overlay pin/peel/restore/apply/scope and repeat run pass.
Exact-source tests cover nesting/exception/early-return/thread/TU/opt-out
and reversible patching. Separate diagnostic package built/audited;
runtime caller verification remains required. Dependency pins unchanged.

## R392: opt-in exact audio events

experiments/audio-phase-events.patch SHA256
d0f1d941e552e4baa85b9fe623922dcf8ded804d393708d3f4e321276d99bc89
adds three RecordPhase calls at existing DMA underrun/backlog/full-drop
counters. No counter or buffering semantics change; disabled phase trace
returns before clock/lock/I/O. Enabled tracing has observer overhead.
Bootstrap peels this outer header overlay first, reapplies/restores last and
verifies exact patch scope. Initial/repeated bootstrap and actual-header tests
pass; resulting header SHA256
9c11e94e0b7c22abe93b319e92f32030e436d9eefb30c487c09aee27c64f772b.
Dependency revisions unchanged. Diagnostic package is isolated from normal app.

## R365: exact two-range dispatcher build policy

ModernGekko0025-rmge01-two-range-policy.patch SHA256
1a8378b059fc3ef9ff00285c23d491200ed404a2245ac789e90d8413c4d169bc
adds the R364 compiled policy, identical to runtime-tested candidate lookup.
Exact RMGE01 DOL/C/1024/indexed eligibility, generated-header SHA refusal,
cache identity and manifest field two_range_policy=rmge01-two-range-v1;
applies after existing transforms and before generated.h normalization.
Callbacks, physical aliasing, guest cycle accounting and chunk bodies unchanged.
Bootstrap pins patch, allows its exact file scope, peels before DCBZ and
restores/applies after DCBZ. Initial scope-list omission caused refusal;
fixed inventory plus explicit regression check, corrected and repeat runs pass.
No dependency revision change. This wires the build, not a new packaged/runtime
artifact claim; installed app and selected module remain unchanged.

## R279: opt-in eight-site decoder line preparation

ModernGekko0021 (ef5ce417...c0e3b) adds a default-off generated-source policy,
not a global memory-helper change. It prepares a guarded full mapped line once,
retains the generated loop for PGO, and preserves original per-word behavior for
journals, callbacks, partial maps and CPU-state overlap. Canonical C++ output
matches the R277/R278 tested source byte-for-byte. Exact DOL/backend/chunk/source
identity and eight-site count guards fail closed. Separate enabled cache key;
normal app unchanged. Integration does not prove runtime gain or G6 acceptance.

## R173–R174: exact-decoder FPRF policy (integration, not package promotion)

ModernGekko0015 (`881996463a31728375b651b5cdf96f165f5a087ccc5c85d94851fc4a21421488`) adds exact-input generated-source policy and cache/manifest identity. Dolphin0014 (`661f2a2452e2240018140fedae6baaeea3b5c3e723d9266e3644f42581d1d019`) appends four unchanged-arithmetic helper variants omitting only intermediate FPRF classification. Neither changes CPU clocks, exception delivery, memory callbacks, original helper entry points or guest instructions. Guarded transformation changes119calls in804520A0; arbitrary source drift fails closed.

Evidence: 256k arithmetic chains,80k emitted entry/exception/cycle cases,64.8k actual candidate-chain/suffix cases; static boundary guards and canonical C++ output comparison. Experimental module movie53.6FPS versus accepted51.5/51.6833; real-save/pause/input smoke passes. Canonical source/bootstrap applied, but canonical module rebuild/package validation still pending. Do not count this as G6/60Hz/audio acceptance.

## Baseline decision

GalaxyPad begins with the coherent SunPad-known graph from the PRD. The newer upstream graph remains evaluation-only until the Wii/Broadway capability probe proves the known Apple track insufficient.

The supplied SunPad checkout is 10 commits newer than the reviewed `efd42ca…` baseline and adds the Preview 11 record plus a native tvOS preview. GalaxyPad will not silently inherit tvOS scope or newer patch snapshots. A separate ignored checkout at the reviewed revision is used for baseline comparison; the supplied checkout remains a secondary source reference.

The selected graph applies the two complete patch snapshots from the reviewed SunPad revision, after verifying their SHA-256 identities:

- ModernGekko Apple runtime: `aa06ac920002fc94f8f96f684309f291e6b8cb882c694f894a9226d100abadbe`
- RecompCore/Dolphin Apple/iOS runtime: `b872dfe002d3d106af92f5dbc3dfcd3d20c43358e7681084ad41ee367cad214a`

The bootstrap verifies that dependency dirt is limited to paths declared by those patches. GalaxyPad then applies one narrow, root-owned overlay:

- ModernGekko headless shader-wait guard: `60d60d41d792c426f428fc3aaf2fce57962d870cefb181cee7fba90846948ce0`
- ModernGekko runner graphics diagnostics: `db85b6f6eceab1e3f0d9663f04f0dc5fc5745993d6ee546242865c1fc06978f0`
- ModernGekko runner I/O diagnostics: `69a455e348f79246519a511944b8ed691660d3eea5fae0fd42dfdf7aacfdd79d`
- ModernGekko explicit headless-audio diagnostic: `ca5b3908ecc2312cf04a0295274d8a3155d0f7013b17dd947f9616ffa7a73ef7`
- ModernGekko runner cadence diagnostics: `73dbe799b0d878edba640ffced0bcb9a0d1451427719371e2d7761c3001d57eb`
- ModernGekko exact-RMGE01 StaticRecomp idle hint: `f432d83b07ffbb11a66d3ef4da10ff7d8a01718099def9a3cb6b3578a55d53d7`
- Dolphin I/O counter hooks: `17b48cebc5eb1e5f372dda98d0885705bb47d2329ce84ccfa1b809104b118dd0`
- Dolphin diagnostics header: `e4498014739c15a102ce0e86729f69d7b06e4b1c97fb3ba8a93b47f3bc1757af`
- Dolphin Apple StaticRecomp audio reserve: `984481b78034018c67ed2f0ed79c8b86833045a159f47ab924c17af483bffbfe`

The overlay changes only `src/runtime/dolphin_runtime.cpp`: visible renderers retain the existing wait-for-shaders behavior, while headless/Null does not invoke the ImGui-backed progress path. This fixes a deterministic contextless `ImGui::GetIO()` assertion without changing guest execution, the visible Metal path, or fallback policy.

The diagnostics patch changes only `tools/moderngekko_run.cpp`. At shutdown it prints the runtime graphics snapshot already maintained by the Apple runtime: frame count, projection hash, draw/primitive and BP/CP/XF load counts, shader changes, scissor count, and texture/shader creation counts. It changes no guest state or renderer policy.

The I/O overlays add passive atomic counters at the existing Cubeb callback/state, EFB peek, and emulated-P1 input-state boundaries, expose them through `RuntimeDiagnosticsSnapshot`, and print one bounded shutdown summary. They record counts, aggregate timing, the final EFB coordinate/depth, and final button/IR state; they do not capture raw audio, input history, game memory, or change emulation policy.

The explicit headless-audio overlay changes only backend selection when a caller deliberately supplies a valid audio backend. Ordinary headless runs still select Null audio, while `--headless --audio Cubeb` keeps Cubeb active for renderer-independent FIFO diagnostics. Visible runs and packaged defaults are unchanged.

The cadence overlay extends those aggregate diagnostics with first-to-last active spans, maximum frame gap, and fixed threshold gap counters. It records no event timeline or payload data and changes no scheduling or emulation policy.

The RMGE01 idle overlay supplies the existing StaticRecomp core with the exact scheduler-spin PC that Dolphin's dynamic cores ordinarily detect while compiling guest blocks. It is gated by both `RMGE01` and the accepted DOL hash, and calls Dolphin's established `CoreTiming::Idle()` path only after the generated loop returns at its normal timing boundary.

The Apple audio-reserve overlay broadens the existing iOS-only StaticRecomp queue servo to macOS and moves its target from 50% to 80% of the configured reserve. The correction remains clamped to ±2%; an exact-route G5 trace with a 200 ms buffer retained continuity across a 156.6 ms producer gap with zero underruns or hard queue drops.

## 2026-09-06 — macOS window-close shutdown

GalaxyPad overlay `ModernGekko-dolphin/0008-macos-window-close-shutdown.patch` (SHA-256 `11b547780a986bc3fc7ec1078491ddb7b3e48b40cd92a14d3d4b97452cde9f0f`) targets the pinned vendor revision `13e492094902644b0d113c586300d358640f9e19`. The existing window-close callback only restored the cursor while the manually pumped platform loop continued. A `windowShouldClose:` delegate now invokes the existing Quit shutdown path and defers window destruction until the runtime has stopped the core and renderer. No guest or module change is involved.

Bootstrap applies and hash-checks the overlay; two consecutive bootstrap runs pass. Both the running startup test (R56) and paused gameplay restored from protected slot 3 (R57) exit via the red close button with status 0, native dispatch, `fallback=0`, and `smc_failed=0`. Logs remain under ignored `generated/runtime/`. No orphan runtime remains after either test.

## 2026-09-06 — native pause indication

`ModernGekko-dolphin/0009-macos-pause-indicator.patch` (SHA-256 `a23f92e1a6a4a00aeaa4107c2952a63bbff0905315945f058e9e9515386f0d5c`) targets the same pinned vendor revision. It displays a native window subtitle when the core is paused and clears it otherwise. The existing event loop observes the real state; no pause action, menu binding, guest behavior, or timing is changed. This addresses misleading retained FPS titles during intentional pauses, not actual guest deadlocks or frame-rate dips. Bootstrap hash-checks and scope-checks the overlay.
## R386 — exact quantized-store scale factor

Prepared/tested overlay now bootstrapped as
`patches/ModernGekko-dolphin/0022-psq-store-scale.patch` (SHA256
`74ca7e8c82bf32d25af12bde4cf1b4318ceb7a34ad7e0925540e415227fd7486`).
It changes only `GXRuntime/src/core/cpu.c` quantizer factor: exact IEEE float
power-of-two bits for signed6-bit GQR scales, original libm fallback otherwise.
No conversion, multiply, clamp, lane ordering, callback or guest timing change.
Source becomes05e221c0...36ea, byte-identical to isolated tested candidate.
Bootstrap peels before older CPU overlays, applies after their original-source
hash gate, checks final source hash, restores on failure and audits file scope.
Two bootstrap runs pass. Historical pinned tests reconstruct original1350d119
source from either of exactly two known hashes; unknown source fails closed.
Runtime movie pairs show about1%gain; gameplay mean/cadence effectively unchanged,
not full60Hz/audio acceptance. Canonical rebuilt module/package remains pending;
installed app still uses previous module. No upstream revision change.
