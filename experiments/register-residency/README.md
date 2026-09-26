# Register residency screen

This experiment asks which change to the generated C would actually make the
translated game code faster. It compares two candidates against the current
DolRecomp output for two profile-selected hot chunks. It builds no module or
app, and it changes no product source.

## Candidates

1. **Entry snapshot of the guest RAM map** (`gp_memmap.h`). Every guest load
   and store currently rereads `ram`, `ram_size`, `exram` and `exram_size`
   from `CPUState`. `StaticRecompCore::Run` assigns those fields once, before
   any translated code executes, and no MMIO callback reassigns them. The
   candidate reads them once per translated function. Any miss, active lockstep
   journal or live reservation calls the unchanged original helper out of line.
2. **Register-resident region** (`region_80517F10.c`). A hand-written model of
   what a region emitter would produce for the five-instruction search loop at
   `80517F10` in chunk `805170A0`: guest registers, CR and downcount stay in C
   locals. `CPUState` is written only at the loop exits and immediately before
   the out-of-line MMIO path, then reloaded after it.

## Results (September 26, M3 Max host, Apple clang 21)

Correctness, by `harness.c` and `loopcheck.c`: full `CPUState`, MEM1, MEM2,
external memory and the ordered MMIO/journal event log (including register
snapshots at each callback) compared between reference and candidate, from all
1,024 entries of each chunk. Modes cover journal on/off, live reservations,
missing MEM2, and callbacks that mutate registers, XER and the reservation.
All eight checks pass in both O2 and ASan/UBSan builds:

| Check | Paired runs | External events |
| --- | ---: | ---: |
| Snapshot, `805170A0`, all entries | 16,384 | 54,367 |
| Snapshot, `804B60A0`, all entries | 16,384 | 26,275 |
| Region, `805170A0`, all entries | 16,384 | 54,367 |
| Region, targeted loop cases (5.4 million iterations) | 2,592 | 557,673 |

Static iPhoneOS O2 code (`-miphoneos-version-min=16.0`, the module's flags
without PGO/ThinLTO):

| Chunk | Instructions | Loads | Stack references |
| --- | ---: | ---: | ---: |
| `805170A0` reference | 21,366 | 5,173 | 21 |
| `805170A0` snapshot | 16,992 | 3,214 | 43 |
| `804B60A0` reference | 33,005 | 6,913 | 48 |
| `804B60A0` snapshot | 28,802 | 5,067 | 66 |

The snapshot's static reduction does **not** reach executed code. Replaying
204,800 randomized entry states through `805170A0` retired about 317 million
instructions for the reference and 320 million for the snapshot (after
subtracting setup), at roughly 1.6 instructions per cycle for both. Alternating
wall-clock rounds were within noise (−4% to +2% integer, no gain FP). Most of
the static saving came from duplicated inlined miss paths that never execute.
A concurrent unrelated device build was running during these timings. Reject
the snapshot as a standalone optimization; it remains a useful building block
for regions because it keeps the map out of `CPUState`.

The register-resident loop is a real win. Hardware counters (`/usr/bin/time -l`,
difference of 20 and 60 calls, median of five pairs):

| `loop_80517F10` per guest iteration | Instructions | Cycles |
| --- | ---: | ---: |
| Reference | 44.0 | 7.50 |
| Register-resident | 32.0 | 4.01 |

That is about 47% fewer cycles for identical observable behaviour. This is one
tight loop on a Mac core, the best case for this technique. It does not predict
whole-game or iPhone FPS, and `805170A0` accounts for only a small share of
the physical profile. It is the first measured evidence that the region
compiler direction removes cost that the host compiler cannot.

## Reproduce

Requires the private generated sources and a clean RecompCore checkout at the
dependency-lock revision (`8b5cc3dfea61f1ca35c156d7581fe46a0bc03e71`):

```sh
python3 experiments/register-residency/run.py \
  --runtime <clean ref/ModernGekko>/vendor/dolphin \
  --output generated/register-residency-<date>
```

The script refuses changed input chunks (SHA-256 pinned), writes only to the new
output directory, and records commands, assembly and `report.json` there.
Private receipt for the run above: `generated/register-residency-20260926/`.

## Phone follow-up (same day)

Whole-program tooling added after the first screen; results on the iPhone are
in the [September 26 iPhone handoff](../../docs/IPHONE-PERFORMANCE-2026-09-26.md).

- `promote.py` rewrites every generated function to keep GPRs, CR, XER, LR,
  CTR and downcount in C locals with write-through to `CPUState`, reloading
  after helpers that write promoted state. `--scope loops` converts only
  outlined `loop_*` functions. All 2,275 functions convert; no unknown writes.
- `verify.py` runs the whole-chunk differential for any chunk set under O2
  and ASan/UBSan. `harness.c` gains `-DGP_CALLBACK_CONTRACT`: callbacks mutate
  only state the runtime's MMIO hooks can touch (they never write integer
  registers). 42 chunks (two hot, 40 random) pass for both the whole-program
  and loop-only transforms.
- Whole-function promotion is slower: the register allocator spilled most
  locals (2,034 stack references vs 21) and every dispatch loads all of them.
  Loop-only promotion keeps the 43% loop win (write-through 4.46 vs 7.83 cycles
  per iteration) without touching chunk bodies.
- `gp_lookup.h` / `make-lookup-template.py`: constant-folded chunk lookup in
  the module's dispatch entry. Matches `dolrecomp_find_original` on 57.4
  million addresses; 20–35% cheaper per lookup.
- `build-module.sh`, `package-candidate.py`: 7162-recipe iPhone module build
  and in-place-installable signed app. `summarize-profile.py` and
  `summarize-log.py` read Instruments exports and the app's frame log.

None of these changed the heavy-scene frame rate measurably on the phone.
