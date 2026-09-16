# Physical sustained run and dispatcher experiment

> Session closed: [current build, owner assessment and research handoff](SESSION-CLOSE-2026-09-16.md).
> This document retains the evidence and acceptance limits of its dated experiment.


Build 7151 remained installed on iPhone 14, iOS 26.6.2. The user reported about
40 FPS. A 90-second Time Profiler capture and a subsequent unprofiled window
show that this initial reading did not persist. QuickTime showed Luigi closer
to Rosalina's map than in the earlier build-7 capture, so the runs are not a
controlled before/after scene comparison.

## Sustained result

The trace ran from 23:10:46 to 23:12:17 JST. Five complete log windows wholly
inside it covered 78.8 seconds and 2,733 frame events: 34.68 events/sec.
Nine complete unprofiled windows covered 142.3 seconds and 4,962 events:
34.87 events/sec, with individual windows from 33.80 to 35.19. Process CPU was
approximately 151% of one core in both periods. Thermal state remained 2
(serious), low-power mode was off and render scale was 1x. A later screenshot
showed 35.0 FPS. Thermal state does not establish actual clock frequency.

The 90-second trace's sampled CPU weights were:

| Work | Sampled seconds | Approximate share of one core over 90 seconds |
| --- | ---: | ---: |
| Game CPU thread | 86.076 | 95.6% |
| Video thread | 35.933 | 39.9% |
| Audio I/O thread | 9.404 | 10.4% |
| Generated module, leaf samples | 64.438 | 71.6% |
| StaticRecompCore::Run, self | 13.065 | 14.5% |
| chassis_dispatch, self | 6.025 | 6.7% |
| AudioTempo::Synthesize, self | 3.933 | 4.4% |

Rows overlap: module samples include chassis_dispatch; all functions are also
included in their threads. Do not sum them. Waiting threads were not sampled.
The audio synthesis rate is lower than the earlier 1.808 s / 30 s (6.0%) result,
consistent with the batched-search change, but scene/supply differences preclude
claiming a controlled 27% hardware improvement. The unprofiled EFB counter window
accumulated 3.684 seconds of peek service across 142.300 seconds; this counter is
not a GPU utilization measurement. There were 748 additional frame gaps >=33 ms
and zero additional gaps >=100 ms in that counter interval.

These results support prioritizing generated CPU execution and dispatch work.
The small audio saving does not resolve the sustained 35 FPS ceiling.

## New opt-in dispatcher path

Exact binary UUIDs were matched before mapping sampled instruction addresses.
Hot dispatcher observations include register restores, table lookup loads and
entry state stores. The dispatcher combines ordinary native calls with optional
hooks, replacement calls and physical-address alias retry, enlarging its common
register-save requirements.

`GALAXYPAD_OUTLINE_DISPATCH_SLOWPATH=1` in the maintained RecompCore
`module-template/module_export.c` now keeps that general implementation in an
out-of-line helper. With replacements compiled in, the original path is used
unconditionally. Otherwise, a non-null host hook uses the helper; without a hook,
the wrapper attempts the unchanged original lookup and calls its result. A
lookup miss falls back to the original implementation, retaining alias behavior.
No timing, interrupt, invalidation, lookup-table or module ABI changes are made.
The default is unchanged; this is not a bootstrap patch.

The first prototype explicitly checked the address class before lookup. It
passed correctness checks but its short benchmark was 6.4% slower and was
rejected. The retained revision uses lookup success to select the fast path.
Nine alternating 200-million-call runs with the real generated lookup tables
and synthetic chunk bodies had median times of 0.983433 s (control) and
0.712791 s (candidate): 27.5% lower dispatch-only cost. This excludes actual game
work and is not an FPS prediction. Even eliminating the entire measured
dispatcher would remove only one fraction of the CPU-thread cost.

`tests/test-module-dispatch-outline.py` extracts the actual emitted dispatch
methods and the actual module wrapper. Across hooks that change CPU state and
hook pointers, replacement callbacks, valid/invalid/unaligned addresses, physical
aliases and RAM bounds, 86,016 comparisons preserve return values, complete CPU
state and callback event order. Optimized and ASan/UBSan variants pass.

The complete private iPhoneOS PGO/ThinLTO module was linked using the original
game objects and the new wrapper object. Input size/mtime stamps remained
unchanged. Architecture, iOS 16 minimum target, exported module entry and install
name checks passed. Inspection of the final linked dispatcher confirms a
32-byte stack frame versus 64 bytes in the installed module. It also reveals an
out-of-line lookup helper call in the PGO-linked result: the synthetic benchmark
does not establish the net cost of that final shape. One old function profile
entry no longer matches and is ignored; this remains visible in build provenance.
No new module was installed and no gameplay performance claim is made. The next
gate is a complete linked-module Simulator comparison before physical promotion,
with the same game module inputs and maintained source provenance.

The complete default repository suite passed, including the new dispatcher
regression. No new production default or bootstrap patch was introduced.

Private receipts are in `generated/audio-search-20260915/hardware-candidate`
and `generated/dispatch-outline-20260915`. They include device and game-derived
data and must not be published. The phone remains on audio candidate 7151.
