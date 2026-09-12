# September 12 performance and hardware handoff

This is an unreleased development candidate. The user reports that the new iPad
build is stable and promising, but still slows down and does not reliably respond
to Xbox Start/Menu. Physical gameplay acceptance remains open.

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
