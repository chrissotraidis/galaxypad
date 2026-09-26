# Guarded direct calls on iPhone

Cross-chunk `bl` sites call the target chunk natively after a host boundary
check, then continue at the caller's label, instead of returning to
`StaticRecompCore::Run` twice per call. The generator overlay is the existing
`scripts/prepare-direct-call-overlay.py`; the host half is
`HookDirectCallBoundary`, enabled by `GALAXYPAD_GUARDED_DIRECT_CALLS=1`.

## What changed

The first phone test (build 7203) showed no gain: the `Run` loop fell from
16% to 4% of game-thread samples, but the boundary hook took about 21%, because
it called `FastDispatchableAt`, `AdvanceGuestTimebase`, `IsHostCallAddress`
and two `System` getters out of line on every check, twice per call.

`StaticRecompCore_Run.hook.patch` keeps every condition and its order and
evaluates them the way `Run()` already does: the same inlined lookup-table
dispatchability test (falling back to `FastDispatchableAt` when forced ranges
exist), the host-call test only when a host-call hook is installed, the
timebase arithmetic inline, and the CPU state and PowerPC state through
file-local pointers set when `Run()` starts. The class layout is unchanged.

Apply it to the maintained RecompCore fork. For a device test against the
retained Preview 3 core archive, the modified object was compiled with the
recorded 7162 compile command and replaced in a copy of the archive; its
external symbols matched the unmodified rebuild exactly.

## Results so far (iPhone 14, 1x, thermal state 2)

| Build | Direct calls | Heavy main-area windows |
| --- | --- | --- |
| 7203 | off | 35–38 FPS, 0.59–0.63x speed, ~152% CPU |
| 7203 | on, original hook | 34–36 FPS, 0.59–0.62x speed, ~152% CPU |
| 7204 | on, cheaper hook | 60 FPS, ~1.0x speed, ~100–115% CPU (scene match unconfirmed) |

The 7204 row still needs confirmation that it was the same scene.
