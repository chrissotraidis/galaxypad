# Simulator setting override repair

The private comparison runner staged requested game INIs in
`User/Config/GameSettings/RMG.ini`. Dolphin reads local game INIs from
`User/GameSettings`. A run could therefore be labelled as a candidate while
silently retaining the default setting.

The corrected runner stages `User/GameSettings/RMGE01r0.ini`, the last and most
specific file Dolphin loads for the supported revision. It retains the requested
INI with the run evidence, backs up an existing revision-specific file, and
restores it on exit. A newly created override is removed on exit. Unexpected
writes are preserved and cleanup fails explicitly rather than overwriting them.
The obsolete, ignored directory is not deleted or treated as active settings.

The setting is loaded at startup. A route ending with `STOP_AFTER_SCENE=YES`
restores the file after startup while leaving that process running with its
loaded configuration. Restart through the runner for each control/candidate;
do not treat a later manual restart as the same configured run.

## Reproduction and validation

The existing EFB batching v2 probe, retained PGO module and verified 121-star
Observatory fixture ran in the dedicated iPhone 14 Simulator on M3 Max, macOS
26.6.2 and Simulator runtime 26.5. This historical diagnostic binary is distinct
from the current app PR. No physical installation or save was modified.

Before repair, requesting full-frame EFB caching (`EFBAccessTileSize=0`) still
produced three staging copies per active refresh. After repair the same binary
produced one: a steady diagnostic interval recorded 4,288 active refreshes,
4,288 refresh copies, zero demand copies and zero multi-copy refreshes. This
provides runtime evidence that the staged setting now takes effect. It does not
establish that copying a larger region improves performance. Repository tests
ran concurrently with that diagnostic interval; its cadence is not an A/B result.

The focused staging regression covers the correct directory, candidate bytes,
restoration of existing settings, removal of a temporary override, idempotent
cleanup, missing input, and preservation of conflicting writes. The complete
default repository suite passed after the repair.

Private receipts are under `generated/iteration3-20260915/`. The first `probe0`
run used the broken path and must not be interpreted as a full-frame experiment;
`probe0-fixed` verifies the correction. Earlier runs using
`GALAXYPAD_SIMULATOR_LOCAL_GAME_INI` also need an effective-setting audit before
their candidate labels can support conclusions. This does not invalidate runs
whose change was compiled into the binary, injected through a different verified
path, or unrelated to game-INI overrides.

## Why test full-frame caching?

[Dolphin's VideoCommon report](https://dolphin-emu.org/blog/2019/04/01/the-new-era-of-video-backends/)
describes how full-frame caching helped F-Zero GX but hurt Galaxy on the backends
tested at the time. That history argues against adopting it by analogy. The
Metal-specific hypothesis is that fewer copy/encoder operations might outweigh
the larger transfer; a corrected, logging-off control/candidate/control run is
required to evaluate it. Depth access and deferred invalidation remain enabled.

## Corrected comparison

After the repository suite finished, the same binary/module/save ran with the
probe and frame-window logging disabled, at 1x resolution. The table records
four sparse HUD observations over 30 seconds per run, not continuous average
display FPS. Initial scenes and final frames were visually checked; the same
central platform/camera remained visible, with ordinary idle animation.

| Run | HUD readings | Mean of readings |
| --- | --- | --- |
| 64-pixel control | 52.0, 50.0, 49.1, 48.2 | 49.825 |
| Full-frame candidate | 50.9, 48.2, 50.0, 52.7 | 50.450 |
| 64-pixel control retry | 49.0, 50.0, 50.9, 49.1 | 49.750 |

The candidate's roughly 0.66-event/sec difference from the mean of the controls
is smaller than the variation in these sparse observations. The Mac also had
changing background work; process inventories and thermal reports were retained.
No clear performance improvement is established. Keep the existing default;
these short windows do not support promotion, frame-tail or audio acceptance,
or an inference about physical iPhone performance.

The first repeated-control launch crashed before rendering, so the final control
is a fresh retry, not an uninterrupted adjacent A/B/A sequence. Its private crash
report records `EXC_BAD_ACCESS` in `SDL_FindInHashTable` during `Runtime::Create`
on the runtime queue. Disassembly confirms the caller boundary. This is a
separate startup issue in the historical probe binary; neither a cause nor a
current-main regression is established. The retry reached the scene and completed.
The test Simulator was then shut down. Requested INIs and backups remain with
each run, while the temporary active overrides were removed.
