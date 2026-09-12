# September 12 performance and hardware handoff

This is an unreleased development candidate. The user reports that the new iPad
build is stable and promising, but still slows down and does not reliably respond
to Xbox Start/Menu. Physical gameplay acceptance remains open.

## September 13 correction: depth access was disabled

The packaged `Sys/GameSettings/RMG.ini` in both the Simulator and installed iPad
candidate sets `EFBAccessEnable = False`. This performance shortcut makes skipped
`GXPeekZ` reads return zero. Galaxy's 3D pointer target test uses depth to reject
occluded targets, while its 2D menu pointer can still work. Initial Simulator dome
tests show cursor overlap without Pull Star activation. A source candidate now
forces EFB access on before runtime startup. The same Terrace dome now acquires
the hand cursor, pulls Luigi up with held A, opens galaxy selection and enters
Loopdeeloop Galaxy. Physical controller acceptance remains pending.

The FPS/audio comparisons below used the same disabled-depth policy in both arms.
They remain evidence of a relative threading/audio gain, but **are not acceptance
of a correct playable configuration**. Prior zero EFB counters do not establish
that the game needs no depth reads. The depth-enabled candidate's heavy-scene
performance must be measured anew, and level selection must actually work.

## What improved

The iOS host previously left Dolphin's CPU-thread setting at its single-thread
default. Setting `MAIN_CPU_THREAD` for the session before runtime initialization
lets native recompiled CPU work overlap Metal rendering. The setting must never
be changed while a game is running.

The fixed Simulator route uses the same RMGE01 module, 121-star Observatory save,
central platform, 1× rendering and 4:3 aspect. Logging and CPU sampling are disabled
in performance windows. Scene images distinguish actual gameplay from the game's
idle-controller disconnect dialog.

| Measurement | Unchanged control | Combined threading/audio candidate |
| --- | --- | --- |
| Logging-off HUD readings | 41.8–46.4 frame events/s over 60 seconds | Approximately 56–60 over 120 seconds |
| Separate diagnostic audio window | 157 new underruns over 58.200 seconds | 0 over 53.100 seconds |
| Nonzero output in that diagnostic window | 74.324% | 99.999961% |
| New frame gaps ≥33 ms in that diagnostic window | 2 | 0 |
| Diagnostic estimated emulation speed, mean | 73.30% | 96.80% |

The roughly 44→58 frame-event improvement is supported by repeated matched-route
runs. HUD samples do not prove continuous displayed FPS. Logged speed, audio and
tail measurements are separate evidence and are not logging-off FPS acceptance.
A longer four-minute candidate capture exists; its full review and matched control
are still pending.

The audio candidate adapts DMA audio duration while preserving pitch. It uses a
bounded stereo overlap algorithm and the existing interpolation path, with no
extra audio reserve beyond the configured 120 ms. Offline tests cover slow and
bursty production, stereo, pitch, stalls, and mixer pause/save-state paths.
A complete core and all Mixer layout consumers were rebuilt for each platform.

A private diagnostic recorded the actual final mixer PCM. In seconds 60–120,
2,879,999 of 2,880,000 stereo frames were nonzero; the only exact-zero frame lasted
20.83 microseconds. There was no clipping or sustained silence in that interval.
This is signal-continuity evidence, not a listening test or hardware audio capture.
Startup/navigation silence and transients require comparison with a control.
The candidate currently requires 32 kHz DMA; other rates fail explicitly. Its
full-drop counter counts rejected input calls rather than the old queued granules,
so cumulative counts in those two implementations must not be compared directly.

## Hardware candidate and preservation

The user explicitly requested the hardware update. The signed candidate was
installed in place under the existing bundle identifier. Both nested module and
outer app were signed and verified. The physical module's code was retained from
the previous device candidate; signing changed its file hash. Simulator modules
are not device-compatible and were not copied to the iPad.

| Artifact | SHA-256 |
| --- | --- |
| Simulator combined host | `ef9898603ebf4eddf7fb01f6406f862aa20e03ad808025cf48078b50bcc69953` |
| Simulator unchanged PGO module | `90e24dfb4e96597686b8fccf09bb55efdcbd7d059dd3ff710a9f32fab26f353f` |
| Installed candidate's signed physical host | `85d84c887cae4b3736b5304cbf757a0543d74e99b4e418e3618184c73b00d0ad` |
| Signed physical module | `aa7d6b6f38d0fae938dcc83509672e6d5ef822567eb0d5d005e5547b3c1e55d2` |
| Physical module before re-signing | `919b2382ebf37007bf86865f1d2f46ca048bec61b45574797483684a039a047b` |

These are staged artifact hashes backed by the installation receipt, not direct
hashes read from the installed executable. A subsequent device process inventory
and the user's gameplay report establish launch.

Before installation, 33 Wii/configuration/preference files were copied locally.
The game save `GameData.bin` remains byte-identical in the post-install snapshot.
The complete snapshot was not identical: configuration, play-history/network
metadata and the render-scale preference changed while the user began using the
app. No backup was restored over that newer state. The 3.5 GB game-image directory
was retained; no uninstall, save replacement or app-data erase was performed.
The selected render-scale preference changed from 1× to 2×. That selection alone
does not prove the active runtime resolution; physical performance needs a known
active setting before comparison with the 1× Simulator lane.

## Input and next work

The installed build allows controller Menu/Options to resume a native pause and
rearms after the pause buttons are released even when a stick is held. Simulator
checks passed menu dismissal, repeated native pause/resume, and blocking injected
movement/jump while the three-dot menu was open. The user's physical report shows
that quick Xbox presses are still unreliable. The follow-up source fix now consumes `pressedChangedHandler` event state rather
than rereading mutable button snapshots. The exact old adapter fails a queued
quick-press regression test; the fixed adapter passes, including held buttons,
held-stick resume, modal gating, ownership changes and reconnects. Both iOS target
compiles and the complete UIKit runtime fixture pass. This fix is newer than the installed artifact above and still
requires physical confirmation.

Touch Start + is the original Wii Plus input. To leave Galaxy's menu, point at
Back and press A. Native Pause is a separate, intentional runtime pause. Controller
touch handoff and cursor alignment still need physical acceptance. No iPhone
performance conclusion follows from the current iPad or Simulator measurements.

Several alternatives were rejected or left unselected: heavy-route PGO, O3,
preserve-none dispatch, coarse lookup tables, shared paired-single rounding,
MEM1-first helpers, M3 tuning, and simple audio replay. Their source experiments
and tests are retained; they are not shipped optimizations.

## Architecture claim

GalaxyPad is a native Apple app with ahead-of-time ARM64 game code and a
Dolphin-derived Wii runtime. It does not use a runtime PowerPC JIT on iOS. Native
dispatch still has interpreter fallback paths, and the runtime implements Wii
hardware and system services. “Emulator-free” or an unqualified “not emulation”
would therefore be inaccurate. The physical module audit found 1,322 generated
native symbols and identical file-backed code sections before and after signing.
See `generated/architecture-claims-audit-20260912/README.md` for source and binary
evidence; no iPhone performance promise follows from this architecture.

## Reproduction and local evidence

The normal host source enables CPU/render overlap. The audio candidate is retained
as `patches/experiments/audio-tempo-v8.patch` and explicit isolated build recipes;
it is not silently enabled by dependency bootstrap. The frozen recipes preserve historical input identities and intentionally reject
the subsequently changed canonical host. They are audit recipes, not a current
one-command rebuild; a new candidate requires a fresh reviewed recipe.

Relevant commands, after preparing the identity-matched local workspace:

```sh
python3 scripts/galaxypad-simulator-comparison-loop.py launch APP MODULE OUTPUT
python3 scripts/galaxypad-simulator-comparison-loop.py capture OUTPUT --provisional --seconds 120
# Review every captured scene before accepting the comparison.
bash tests/test-controller-pause-events.sh
python3 tests/test-audio-tempo.py --output generated/tests/audio-tempo-review
python3 tests/test-audio-tempo-mixer.py \
  --candidate generated/experiments/audio-tempo-integration-v8-20260912 \
  --output generated/tests/audio-tempo-mixer-review
```

Private evidence under `generated/runtime/ipad-iteration-1/`:

- `dual-core-comparison-20260912/summary.json`: repeated threading comparison.
- `dual-core-audio-tempo-comparison-20260912/candidate/`: combined logging-off run.
- `dual-core-audio-tempo-diagnostic-20260912/comparison-summary.json`: fresh audio and tail comparison.
- `dual-core-audio-tempo-pcm-retry-20260912/audio-analysis.md`: captured PCM analysis and exact timing bounds.
- `physical-dual-core-audio-tempo-20260912/`: signatures, install receipt, backups and readback differences.

Private module binaries, game images, saves, recordings, device identifiers and
signing material remain outside version control. There is no release approval.

## Merge validation

The focused controller adapter regression, both platform translation-unit compiles,
controller mapping checks, seven isolated-core recipe checks, and diagnostic PCM
O3/ASan/UBSan roundtrip tests pass. The tracked audio patch passes `git apply --check`
against the current pinned Dolphin tree. Existing audio experiment evidence is
retained without treating synthetic tests as real-game acceptance.

`bash scripts/check-repository.sh` passed its initial input, settings and import
checks, then stopped at the historical `tests/test-thp-dead-pc.py`: the ignored
fixture `generated/thp-kernels-r198-exits/candidate.c` is absent. The full repository
suite has therefore not passed; the missing test was not disabled. No GitHub CI
workflows or named check runs were discoverable. Merge is a development checkpoint,
not a release or hardware acceptance decision.

## Newly reported level-entry blocker

The user reports that right-stick aiming at the blue Pull Star inside a dome and
pressing A does not pull Luigi into the galaxy-selection interface. RT consumes
Star Bits. The screenshot shows the dome, 121 stars and 2,254 Star Bits; its single
60.0 HUD value does not establish sustained performance or functional acceptance.

[Nintendo's original manual](https://m1.nintendo.net/docvc/RVL/USA/RMGE/RMGE_E.pdf)
requires aiming until the hand cursor appears, then holding A. GalaxyPad maps Xbox
RB to Wii A as a fixed duplicate, allowing aim and hold together; RT maps to Wii B
and shoots Star Bits. The current report remains an unresolved pointer/interaction
blocker, not an assumed user mapping error. Reproduce the exact dome, verify hand
cursor acquisition and held-A delivery, then confirm galaxy selection opens before
accepting a fix. Simulator reproduction and controller-path audit are in progress.

## September 13 continuation: merge and pointer ownership

The September 12 checkpoint was pushed and merged in PR #1. Main commit is
`892ff71e208b07d3d790c697b83e63678361d5f4`; it includes the controller Menu event fix,
CPU/render overlap, experimental audio sources, exact evidence and open blockers.
The physical iPad still has the earlier signed host listed above.

A subsequent source audit found a mixed-input defect: after a touch lifted, its
retained visible cursor could indefinitely override right-stick aim. The follow-up
separates active contact from retained touch aim. Active contact wins, then visible
controller aim, then retained touch aim. This preserves touch-only aim followed by
a separate A/B press. It is not established as the cause of the user's dome report,
whose screenshot has auto-hidden touch controls.

ASan/UBSan mixer tests, controller pause regressions and the full UIKit Simulator
fixture pass, including held A, touch lift, controller restoration and cancellation.
A fresh Simulator host rebuilt all 13 host objects against the unchanged accepted
v8 audio core and matching Mixer headers. The core dependency graph has no
GalaxyPadInput.h consumers. Candidate host:
`02c7e5e498183e3c065a9c36be4fd517b2c70307a060cca08abaa65125dcfeed`.
Private build recipe/log: `generated/build/ios-simulator-pointer-handoff-20260913/`.
UIKit evidence: `generated/experiments/pointer-handoff-20260913/uikit.log`.
Product route and physical promotion remain pending.

The dome's reference source first enters its Pointing state when it recognizes
the target, then requires a fresh A trigger. This supports aim until hand cursor,
then press and hold A/RB. It does not prove that the installed pointer path works.
Actual dome reproduction is the next acceptance gate; no guest behavior has been
changed to bypass target acquisition.


## September 13: Pull Star cause reproduced and corrected

The control host `02c7e5e498183e3c065a9c36be4fd517b2c70307a060cca08abaa65125dcfeed`
showed pointer overlap without a hand cursor or pull in the Terrace dome. Its
packaged RMG EFB access was disabled. `StarPointerPeekZ` uses GXPeekZ;
`StarPointerController` projects that depth and `StarPointerTarget` rejects the
3D target when the returned depth is zero. The host now explicitly enables
`GFX_HACK_EFB_ACCESS_ENABLE` before Run. Real depth and target checks are retained.

Fresh Simulator host SHA-256:
`0baf09083c5accb108f32a77b95bc4ae64b4ab7cb2c57a25459b79b60825dd41`.
Build command: `python3 generated/build/ios-simulator-pointer-depth-20260913/rebuild.py`.
All 13 host objects were rebuilt; accepted v8 core and validated PGO module were
unchanged. Recipe, commands, source hashes and signing verification are retained
in that private build directory.

Private route evidence: `generated/runtime/ipad-iteration-1/pull-star-depth-20260913/`.
`star-hover.png` shows the hand cursor; `star-held-a.png` shows genuine galaxy
selection. `galaxy-select-2.png` selects Loopdeeloop, `fly-confirm.png` shows its
mission star and `mission-select.png` actually shows Luigi inside that level.
A diagnostic input idle/disconnect dialog appeared between actions and was
acknowledged with neutral-stick A; that dialog is not performance evidence.
The control's grid1–5 images instead show Luma conversation/Universe Map and
are excluded as Pull Star evidence. The user pictured a different dome; the
shared interaction now works in the Terrace, but their physical Xbox route is
not yet accepted.

At the centered dome floor, reproduce the successful interaction with:

```sh
python3 scripts/simulator-input.py generated/ios-dev-input.json '{"pointerVisible":1,"pointerX":0.53,"pointerY":0.24,"buttons":1}' --aim-first 2 --seconds 8
```

The depth-enabled stationary Observatory logging-off 60-second window reads
46.0, 45.5, 45.5, 45.0, 47.0, 45.4 and 49.0 frame events/s. All seven window
images were reviewed: same central scene, no modal or disconnect dialog.
Process snapshots span 111.8–122.7% CPU and 749472–750896 KiB RSS. Host and thermal
snapshots are retained. Sparse HUD values do not provide a continuous frame-time
tail, speed or audio acceptance. The earlier 56–60 result was depth-disabled;
it must not be used as acceptance for this corrected configuration.

Decision: retain the gameplay correctness fix; reject EFB-disabled operation as
a performance solution. The next measured hypothesis is depth-readback cache
miss/submission cost with real EFB access enabled. Existing caching already batches
async refreshes. Measure sync misses and service time separately from FPS; only
then compare the existing full-EFB tile setting against 64-pixel tiles if multiple
misses justify it. Do not remove waits, fabricate depth or reinstate disabled EFB.
Recheck audio underruns and frame tails on this correct configuration before
claiming the earlier audio results generalize. Physical build/promotion pending.


## September 13 physical update

The corrected host is now installed in place and launch plus a fresh running-process
inventory succeeded. Signed host SHA-256:
`13b32e380581253ca0da7d076ce18c7eb0a54d2e136dec83a449df33089cadc8`.
Unsigned host: `5d398ab6ebe5678a114127aa89339757d2ea2e86718c4be06ec04e4a1f8954ed`.
Signed nested module: `a45788153abfc39b90bf332de7d623874224f6ce66f8b25ac0dcc3858d9a898d`.
The physical module code was retained; both nested module and outer app were signed
with the existing identity/profile, and deep strict verification passed.

All 13 host objects were recompiled against the unchanged physical v8 audio core
`7fe0ea02261edb7d89853e6d83f8a687b5783cf3f50b0b67671591d6effb4e5a`.
Private rebuild/verification: `generated/build/ios-device-pointer-depth-20260913/`.
Deployment recipe: `python3 generated/runtime/ipad-iteration-1/physical-pointer-depth-20260913/promote.py`
with sequential `prepare`, `backup`, `install`, `launch` steps. This one-use recipe
retains exact commands and private signing/device lookup; do not replay without
fresh state and output directories.

Preinstall backup and postinstall-before-launch readback contain the same 33 files,
all byte-identical, including GameData.bin, configuration and preferences. The
existing game image remained in the container; no uninstall, erasure or save
replacement occurred. Receipt, manifests, signature logs and launch/process proof
are in `generated/runtime/ipad-iteration-1/physical-pointer-depth-20260913/`.
These hashes identify staged installed artifacts, not a readback of the installed
executable. User confirmation of Pull Star activation, Xbox Menu repeat pause,
touch/controller handoff and audible audio remains pending. This correctness
repair is promoted despite its exposed performance cost; it is not an accepted
FPS optimization or a release candidate.

## Correct-depth diagnostic: reject the whole-EFB cache hypothesis

A separate logging-on, visually checked Observatory window retained 5,273 paired
EFB/dispatch reads across 40.691 seconds and 1,758 frame ordinals. Service totaled
10,184.049 ms (25.03% of wall time, not CPU utilization or GPU execution time).
The fixed pointer read at (520,377) accounts for 99.9575% of service: 1,757 reads,
median 6.455 ms, p95 8.459 ms. Corner and moving reads together cost about 4.3 ms
in the entire window. Only four frame ordinals contain multiple service spans
above 100 microseconds. Larger cache tiles are therefore rejected as the next
optimization for this scene: additional tile misses are negligible.

The interior native counter interval is 36.900783 seconds: zero new underruns,
backlog/full drops, short callbacks or producer gaps >=50 ms. All 1,771,520
requested output frames were produced and nonzero. There were 166 new frame gaps
>=33 ms, none >=100 ms. Lifetime maximum counters cannot establish a window maximum.
This is diagnostic evidence, not FPS acceptance, listening or physical audio proof.

Private evidence: `generated/runtime/ipad-iteration-1/depth-enabled-diagnostic-20260913/`.
`analyze-depth-window.py` records complete-line CSV snapshots, their hashes and
clock calibration: libc++ steady_clock differs from Python/native mach time;
eight cumulative EFB anchors validate the converted bounds. Start/end screenshots
show the same central scene without a modal. Next hypothesis: copy/setup versus
Metal completion inside the one dominant read. Reuse the existing opt-in staging
probe in a separate candidate, preserving real depth and the unchanged FPS control.
