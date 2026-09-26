# iOS/iPadOS performance review — 26 September 2026

> Follow-up the same day: phone profiling, device builds and the results of the
> plan below are in the [September 26 iPhone handoff](IPHONE-PERFORMANCE-2026-09-26.md).
> Stage 2 (fewer dispatcher round trips via guarded direct calls) was measured
> on the iPhone and gave no gain; the host bookkeeping moved into the boundary
> check. Stage 1 remains the main project.

This review re-reads the performance record since Preview 2, checks the build
configuration that actually ships to phones, and runs two new compiler
experiments. It changes no product source, module or installed app. The
experiment tooling and results are in
[experiments/register-residency](../experiments/register-residency/README.md).

## Where the phone's time goes

The iPhone 14 is limited by the game CPU thread running translated game code.
The last physical Observatory capture (build 7163) spent 29.33 CPU-seconds of
every 30 on that thread at about 33 FPS and 1x resolution
([session close](SESSION-CLOSE-2026-09-16.md)). Physical EFB readback service
was 42–70 ms per wall second, far below the Simulator's roughly 240 ms
([pass 3](IOS-PERFORMANCE-PASS3-2026-09-13.md)), and resolution and Game Mode
did not move the result. Reaching 60 FPS from the 33–43 FPS observed needs the
game thread to do roughly 30–45% less work per frame. No renderer, audio or
scheduling change can supply that.

## What the generated code looks like

The hot chunk `805170A0` compiles 1,024 guest instructions into 21,366 ARM64
instructions for iPhoneOS: about 21 host instructions, 5 loads and 2.2 stores
per guest instruction. Three structural reasons dominate:

1. Every guest register, CR field and the downcount lives in `CPUState`. Each
   guest instruction reads its inputs from memory and writes its result back.
2. Roughly a third of static guest instructions are loads or stores (about
   425,000 of 1.35 million). Each one rereads the RAM map from `CPUState`,
   checks MEM2 then MEM1, and may call an MMIO callback that receives the whole
   `CPUState`. The callback path merges back into the fast path, so the host
   compiler cannot keep any guest value in a register across a memory access.
3. Every call to a function in another chunk and every `blr` returns to
   `StaticRecompCore::Run` and re-enters through a jump table.

## New results

**The entry snapshot is correct but not faster.** `StaticRecompCore::Run`
assigns the RAM map fields once, before dispatching, and nothing reassigns them
during translated execution. This closes the question R452 left open, so a
translated function may read the map once on entry. The candidate passes whole-
chunk differential checks from all 1,024 entries of both hot chunks, under O2 and
ASan/UBSan, including MMIO, journal, reservation and callback-mutation cases.
It removes 20% of static instructions and 38% of loads from `805170A0`. But
hardware counters show executed instructions unchanged (about 317 versus 320
million in the replay), and timing stayed within noise. The removed code was
mostly duplicated miss paths that never run. This matches the long history of
component savings that did not become FPS: static counts are a poor proxy here.

**Keeping guest values in registers is faster.** A hand-written register-resident
form of the hot loop at `80517F10` (locals for registers, CR and downcount,
`CPUState` written only at exits and before the cold MMIO path) passes the same
differential checks plus 2,592 targeted loop cases covering 5.4 million iterations
and 557,673 MMIO events. It takes **4.01 cycles per guest iteration versus 7.50**
for the current code, 47% fewer, retiring 32 instead of 44 instructions. This
is one small loop measured on an M3 Max, the best case for the technique, and
not an FPS forecast. It is the first measured evidence that the region compiler
direction proposed on September 16 removes cost that Clang cannot remove today.

**The phone module is built for an A7 CPU model, which does not matter.**
Physical iPhoneOS builds pass no `-mcpu`, and Apple Clang defaults
`arm64-apple-ios16` to `apple-a7`; the Simulator and Mac default to `apple-m1`.
The earlier tuning audit only examined the Simulator. Recompiling both hot
chunks with `-mcpu=apple-a15` changed 21,366 instructions to 21,363 and left the
FP chunk identical. Keep the A7 baseline: the iOS 16 deployment target still
includes A11 iPhones and A9 iPads, and a higher `-mcpu` may emit instructions
those devices lack.

## The plan

### Stage 1: register-resident regions in the C emitter

This is the one change the evidence says can move the game thread materially.
It belongs in the maintained DolRecomp fork and reuses its existing CFG.

- **Regions.** Start a region at a function entry (`bl` target), a return
  continuation (instruction after `bl`) or a loop head. Extend through blocks
  reachable without crossing calls, indirect branches or unsupported
  instructions. All other interior entries keep today's all-entry code as the
  fallback, following the R182 normal-entry/fallback split.
- **State.** GPRs, CR fields, XER, CTR, LR and the downcount used in the region
  become C locals, loaded at region entry. Dirty values are written to
  `CPUState` only at exits (branches out, `bl`, `blr`, budget and exception
  exits) and immediately before cold paths: MMIO misses, SPR access, system calls
  and FP helpers that take `CPUState`. They are reloaded after those cold paths.
- **Memory.** Use the entry snapshot as the fast path, with every miss out of line.
  The snapshot only pays off inside regions, where it keeps the map from
  competing with guest values for registers.
- **FP.** First pass: keep FPRs in `CPUState` and flush only integer state
  around FP helpers. Second pass: value-based exact FP helpers, as the region
  feasibility review described.
- **Timing.** Charges, suffix-entry cycles and loop budget checks stay exactly
  as today; only where the downcount lives changes.

Gates, in order: (1) the whole-chunk differential harness passes for every
emitted chunk in O2 and sanitizer builds; (2) replayed hot chunks show a cycle
reduction with hardware counters; (3) a full module passes the existing
Simulator gameplay and save checks; (4) matched physical A/B on the iPad, then
the iPhone. Pilot on the three or four chunks that lead the physical profile
before converting the generator wholesale. Expect a multi-week compiler project.

### Stage 2: fewer dispatcher round trips

After Stage 1, measure how often `bl`/`blr` leave native code using the
existing dispatch counters, then decide whether known-target calls inside the
module should chain directly. Regions make this cheaper, because live state is
already explicit at call sites.

### Stage 3: physical measurement without the owner playing

Nearly every decision so far was measured in the Simulator on an M3 Max. Its
EFB profile differed from the phone's by 4–6×. Add an opt-in benchmark launch
mode that loads a fixed save, replays fixed input for a set time, writes the
existing VI/CPU logs and exits. That lets `devicectl` run matched A/B trials on
an attached iPad or iPhone, and it should be ready before Stage 1's device gate.

## Not worth repeating

Do not spend time on more instruction-count trimming, mapping caches, lookup
snapshots, aliasing hints, resolution changes, Game Mode, QoS changes or CPU
tuning flags. Each has either been measured without a gain or, as above, removes
code that never runs. Previously rejected items are listed in the
[session close](SESSION-CLOSE-2026-09-16.md) and
[architecture review](ARCHITECTURAL-PERFORMANCE-2026-09-16.md).

## Repository state for this review

Local `main` was fast-forwarded to `origin/main` (Preview 4, `13665c9`). The
unpushed pass-3 research commits (EFB readback batching and drawable waits) are
carried on this branch with their original messages, together with two
previously uncommitted pass-3 experiment folders. The primary checkout's
`ref/ModernGekko` is an older patched clone on the upstream revision with local
edits, not the pinned fork. It was left untouched and backed up; build from a
clean checkout at the dependency lock until it is migrated.
