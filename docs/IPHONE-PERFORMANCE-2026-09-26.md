# iPhone performance session — 26 September 2026

**Start here next time.** This is the current handoff for iPhone/iPad performance
and touch work. It supersedes the priorities in the
[September 16 session close](SESSION-CLOSE-2026-09-16.md) and extends the
[September 26 review](IOS-PERFORMANCE-REVIEW-2026-09-26.md). Everything below is
experimental: no IPA, release or public build changed. The latest public release
is still Preview 4.

## Where things stand

On an iPhone 14 at 1x, the heavy part of the Comet Observatory runs at **33–38 FPS
and about 0.6x game speed** while the phone is hot, and 45–53 FPS in busy areas
when it is cool. Lighter areas hold 60 FPS. The iPad Pro (M2) is fine. The game
CPU thread is saturated; reaching 60 FPS in heavy areas needs about 1.7x more
game-thread throughput on a hot phone. None of today's performance changes moved
the heavy-area frame rate by a measurable amount. The touch pointer was
recalibrated so a tap should land under the finger; player confirmation is pending.

The phone currently has private build **7202** installed (touch calibration,
loop promotion and fast chunk lookup). All installs preserved the 54 save,
configuration and preference files byte for byte.

## What is in source after this session

| Change | Where | State |
| --- | --- | --- |
| Touch pointer calibration: IR yaw 18.75°, pitch 18.75°, vertical offset 15 cm | `apple/shared/GalaxyPadInputDevice.cpp` | In source; modeled mean error 81 → 3 points; needs player confirmation |
| Loop-function register promotion | `experiments/register-residency/promote.py --scope loops` | Experimental module transform; 43% fewer cycles on one hot loop (Mac); no measured FPS change |
| Constant-folded chunk lookup | `experiments/register-residency/gp_lookup.h`, `make-lookup-template.py` | Experimental module template; 20–35% cheaper lookup; ~1–1.5% expected |
| Cheaper direct-call boundary hook | `experiments/direct-calls/StaticRecompCore_Run.hook.patch` | Patch only, not in the RecompCore fork; direct calls showed no gain |
| Build, package, profile and log tooling | `experiments/register-residency/*.py`, `experiments/touch-calibration/*.py` | Reusable |

Private test builds (none published; build numbers start at 7201 because public
Preview 4 already used 7168):

| Build | Host | Module | Result |
| --- | --- | --- | --- |
| 7167 | 7166 | fresh control, same recipe as 7162 | baseline for the new toolchain |
| 7168 (private, collides with Preview 4's number) | 7166 | loop promotion | 45–60 FPS at 1x on a cool phone; no matched baseline |
| 7201 | main + touch calibration | loop promotion | touch fix; 2x hot run: 30–35 FPS |
| 7202 (installed) | same as 7201 | loops + fast lookup | 1x hot: ~29–36 FPS in main area |
| 7203 | same as 7201 | loops + lookup + direct calls | on/off identical: 34–38 FPS |
| 7204 / 7205 | cheaper hook core object | same as 7203 | on: 33–38 FPS, no gain |

## Where the iPhone's time goes

Instruments Time Profiler on the phone during heavy gameplay (build 7201, game
thread ~92% busy):

| Share of game-thread samples | What |
| ---: | --- |
| ~52% | Translated game code (`func_*` bodies) |
| ~30% | Switching between chunks: host `Run` loop 16%, chunk lookup 4%, module dispatch entry 3%, chunk prologue/entry jump ~7% |
| ~8% | FP and paired-single helpers (some not inlined) |
| ~2% | Graphics command writes (`HookExternalWrite` → GPFifo) |

The video and audio threads are not the limit. There are roughly 900,000
dispatches per frame at about ten guest instructions each.

## What was tried and what happened

| Idea | Result |
| --- | --- |
| Per-function RAM-map snapshot | Exact; −20% static instructions but executed instructions and time unchanged. Rejected alone. |
| Whole-function register promotion (write-through locals) | Exact across 42 chunks, but the register allocator spilled most values (2,034 stack refs vs 21); slower. Rejected. |
| Loop-only register promotion | Exact; −43% cycles on a hot loop; no visible phone change. Kept as an option. |
| Constant-folded chunk lookup | Exact on 57M addresses; ~1–1.5% expected. Kept as an option. |
| Guarded direct calls (existing mechanism) | Moved `Run` cost into the boundary hook (~21%); no gain. |
| Direct calls with a cheaper hook | No gain in the heavy area (33–38 FPS on vs 35–38 off). Not enabled. |
| `-mcpu=apple-a15` for the module | Phone builds default to an A7 model, but A15 tuning changes nothing (21,366 vs 21,363 instructions). |
| Host-call double check in module dispatch | Irrelevant: no mods are loaded, so the check short-circuits. |
| 2x render scale on iPhone 14 | Much slower in heavy scenes (depth readback cost rises). Use 1x. |

Earlier rejected items remain in the [September 16 session close](SESSION-CLOSE-2026-09-16.md).

## Open technical problems

1. **Heavy-scene iPhone speed.** 0.6x game speed in the heavy main area on a hot
   iPhone 14. Needs ~1.7x game-thread throughput. See the plan below.
2. **Thermal throttling.** Every log this session reported thermal state 2
   (serious). A cool phone ran the busy area about 30% faster. Measurements are
   only comparable at the same thermal state and scene.
3. **Dispatch overhead (~30%).** Two attempts to bypass the dispatcher only moved
   the bookkeeping. The per-transfer obligations (cycle charge, timebase,
   exceptions, idle loop, self-modifying-code validity) are the cost.
4. **Translated code efficiency.** About 21 ARM64 instructions per guest
   instruction in hot chunks; guest registers live in `CPUState` memory and every
   guest load/store rereads the RAM map and may call a callback.
5. **Touch pointer accuracy.** Calibration fixed in the neutral-pose model; not
   yet confirmed by a player, not modeled after tilt or Spin. Gyro aiming uses the
   same IR settings and may feel slower.
6. **Audio chopping in demanding scenes.** Unchanged from September 16; it
   follows the game-thread slowdown.
7. **Build reproducibility.** The phone host links the retained Preview 3 core
   archive (`galaxypad-refinement/generated/audio-slowdown-7165-20260916/libGalaxyPadCore.a`)
   and retained 7163 compile commands. The original `generated/build` trees are
   gone. The primary checkout's `ref/ModernGekko` is an older patched clone, not
   the pinned fork; build from a clean checkout at the dependency lock. A full
   core rebuild from the pinned fork for iOS is needed before any host-core change
   can ship normally.
8. **PGO profile staleness.** Modules use the 2026-09-12 Simulator route profile;
   transformed chunks lose profile data.
9. **Tooling flakiness.** `xctrace` sometimes reports "Timed out waiting for
   device to boot"; relaunching the app under a recording loses the trace. Stop
   recordings before relaunching.

## Plan

### 1. Register-resident region compiler (main project, multi-week)

The only change with a large measured win (−45% cycles on a real game loop).
Build it in the maintained DolRecomp fork, not as a patch stack.

- **Regions:** start at a function entry, return continuation or loop head; grow
  through blocks reachable without calls, indirect branches or unsupported
  instructions. Keep today's all-entry code as the fallback for other interior
  entries (the R182 normal-entry/fallback split).
- **State:** GPRs, CR, XER, LR, CTR and downcount in C locals scoped to the
  region, loaded only for registers the region reads. Whole-function locals
  failed because of spills; keep live ranges short.
- **Memory:** entry snapshot fast path, every miss out of line. Real MMIO hooks
  never write integer registers (verified in `StaticRecompCore_Hooks.cpp`), so
  locals can stay live across the slow path when writes are write-through.
- **Gates, in order:** `experiments/register-residency/verify.py` differential
  checks (O2 + sanitizers) on hot and random chunks; hardware-counter cycles on
  replayed chunks; Simulator gameplay and saves; matched iPad and iPhone runs at
  the same thermal state.
- **Pilot first** on the chunks that lead the phone profile (`804B60A0`,
  `805170A0`, `800180A0`, `804330A0`) before converting the generator.

### 2. Supporting work

- **Reproducible iOS core build** from the pinned fork, so host-core changes
  (like the cheaper hook or a leaner `Run` loop) stop depending on retained
  archives.
- **Unattended on-device benchmark**: a launch option that loads a fixed save,
  replays input, logs frames and exits, so builds can be compared without a
  player and at controlled temperature.
- **Helper inlining** for `ppc_psq_load_inline` / `ppc_psq_store_inline` and
  paired-single ops (~2% possible).
- **Fresh device PGO profile** once code generation stabilizes.

### 3. Not worth repeating

Instruction trimming without register residency, mapping caches, aliasing
hints, CPU tuning flags, chunk-size changes, 2x on iPhone, and bypassing the
dispatcher while keeping per-transfer host bookkeeping.

## How to rebuild, deploy and profile

Work from a checkout with clean pinned dependencies. Paths below are relative to
that checkout; `<retained>` is the `galaxypad-refinement` checkout that holds the
retained 7163/7165/7166 inputs.

1. Transform generated code (optional):
   `python3 experiments/register-residency/promote.py --scope loops --input generated/aot/device-fresh/RMGE01_generated --output <new dir>/RMGE01_generated`
2. Check it: `python3 experiments/register-residency/verify.py --original … --candidate … --runtime ref/ModernGekko/vendor/dolphin --output <new dir> --chunks <hot chunks> --random 40`
3. Build a module (7162 recipe, PGO profile, optional template):
   `MODULE_TEMPLATE=<template> bash experiments/register-residency/build-module.sh <generated> ref/ModernGekko/vendor/dolphin <build dir> <profdata>`
4. Build a host from this checkout:
   `python3 experiments/touch-calibration/build-host.py --retained <retained> --overlay-inputs <Preview 4 build records>/header-inputs --output <dir> --build <number>`
5. Package and sign with the installed app's identity:
   `python3 experiments/register-residency/package-candidate.py --baseline-app <host app> --signer-app <installed 7166 app> --module <dylib> --build <number> --output <dir>`
6. Back up `Library/Application Support/GalaxyPad/{Config,Wii}` and
   `Library/Preferences` with `devicectl device copy from`, install in place,
   read back and compare hashes.
7. Profile while the player plays: `xcrun xctrace record --template 'Time Profiler' --device <udid> --attach <pid> --time-limit 60s`,
   export the `time-profile` table, then run `experiments/register-residency/summarize-profile.py`.
   Summarize frame logs with `summarize-log.py`.

Private evidence from this session (logs, traces, receipts, backups, modules)
is under `generated/` in the primary checkout (`iphone-20260926/`,
`modules-20260926/`, `run-rebuild-20260926/`, `promote-*`, `direct-*`) and
the signed test apps and host builds are under `generated/` in the
`~/.codex/worktrees/galaxypad-preview4` worktree. None of it is tracked.
