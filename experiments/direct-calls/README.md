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

## Result (iPhone 14, 1x, thermal state 2, heavy Comet Observatory area)

| Build | Direct calls | FPS | Game speed |
| --- | --- | ---: | ---: |
| 7203 | off | 35–38 | 0.59–0.63x |
| 7203 | on, original hook | 34–36 | 0.59–0.62x |
| 7204 | on, cheaper hook | 33–38 | 0.55–0.65x |

No gain. An earlier 60 FPS stretch in the 7204 session was a lighter scene.
The host bookkeeping each transfer must do (cycle charge, timebase, exception,
idle-loop and self-modifying-code checks) is the cost, wherever it runs.
Direct calls stay off; the app does not enable them by default. Keep the patch
for reference if a later design needs a cheaper boundary.
