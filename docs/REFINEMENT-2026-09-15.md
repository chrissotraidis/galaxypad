# GalaxyPad refinement pass — September 15, 2026

The maintenance criticism and the performance complaints have different status.
The fork/attribution work shipped in Preview 2. Valid WBFS conversion rejection
needed another repair. Sustained heavy-scene performance remains open.

## Complaint review

Reviewed the earlier project conversations about upstream criticism and mobile
performance, current main (`868340a`), live GitHub issues, and the GalaxyPad
Discord channel and crystal-lag help post. GitHub returned no open or closed
issues at this check. No messages were sent and no reports were closed.

| Complaint | Finding and disposition |
| --- | --- |
| Runtime patch stack and scattered credits | Preview 2 uses maintained ModernGekko, RecompCore and DolRecomp forks with pinned nested submodules. Bootstrap and the dependency lock pass in a fresh worktree. Credits and upstream links are prominent. Historical patch documents now explicitly point to the current workflow. |
| Suspected ARM64 JIT fallback bug | RecompCore PR 6 merge `202704caa71574c9a89a65c7e4f0d35cbb7e1399` is an ancestor of the pinned fork. This is not a missing fix to apply again. A different bug still needs its specific reference. |
| Valid USA revision 0 WBFS rejected | Confirmed in code and reproduced by a regression. The new importer checks bounded WBFS structure and executable content rather than one whole-container length/hash. Source repair tested, not released. |
| Import location confusion and 3–5 minute launch | The app already supports importing through its menu and enables Files sharing. The slow report does not separate copy, verification, extraction, shader preparation and later launch. The unnecessary whole-container hashing pass is removed, but no launch-time improvement is measured. |
| iPad Air M3, 2×, many crystals: 45–55 FPS | Confirmed reporter description in Discord. App/OS version and exact mission are absent. Open, not inferred to be the same bottleneck as a stationary Observatory Simulator test. |
| iPhone slowdowns | Connected iPhone 14 still has build 7; iPad Pro has build 15. Historical logs show significant phone slowdown and thermal pressure. No new physical benchmark or installation in this pass. |
| New levels/cheats | Feature requests remain separate from fixing stability and performance, consistent with the owner's stated order. |

## Import repair and validation

Keep WBFS support bounded to one disc and 5 GiB. Validate sector shifts/counts
before DiscIO opens the container. The copy uses its observed size, detects
short/growing input and checks storage capacity. Both outer and game-partition
headers must identify RMGE01 revision 0, disc 0. Before activation, require the
pinned main DOL, home-menu RSO and `product.sel` hashes. System export sizes,
file count, recursion, paths and extracted byte totals are bounded. Existing
staging ownership, cancellation, atomic activation and separate saves remain.

This verifies executable compatibility and readable extraction, not a hash of
every possible asset in an arbitrary input. ISO, split/multidisc WBFS and other
revisions remain unsupported. `config/galaxypad-disc.json` retains the original
container identity for reproducible development builds.

Validation completed locally:

- The previous transaction fails the same changed-length activation regression
  that passes with this repair. ASan/UBSan transaction and container-policy tests
  cover malformed/truncated headers, bounds, capacity, copy cancellation,
  failed extraction, cleanup and activation gates.
- The actual extractor, linked against the existing native DiscIO libraries,
  accepts the original private reference and a valid WBFS variant with 512 bytes
  of unused padding and an updated physical-sector count. All 2,382 exported
  files match SHA-256 byte-for-byte. The original input hash remains unchanged.
  This tests container independence, not the reporter's unavailable conversion.
- A private wrong-revision variant is rejected before creating extraction output.
- The complete default repository suite passes with prepared pinned dependencies.
- Both changed Objective-C++ units compile for ARM64/iPhoneOS 26.5 against the
  pinned dependency headers. This alone is not a complete app build.

Private receipts are under `generated/refinement-20260915/`, including
`native-parity.json`, `wrong-revision.json`, `baseline-regression.json` and
`ios-compile.json`. They contain no device gameplay acceptance.

## Physical evidence refreshed

Both devices report OS 26.6.2 build 23G90 in their retained sessions. The iPad
connection initially timed out, then its log transfer and installed-version
query succeeded. Device work was read-only.

| Device/session | Available observation | Limit |
| --- | --- | --- |
| iPhone14,7, build 7, September 13 | Worst unblocked full window: 40.000 frame events/s over 15.70 s, 1×, thermal state 2 (serious), 158.23% process CPU where one core is 100%. State 2 appears in 68 unblocked windows totalling about 17.9 minutes. | Historical scenes are unidentified. Heat correlates with some slow periods, but cooler periods also slow down. Group averages mix scenes and do not measure a causal thermal penalty. |
| iPad14,5, build 15, September 14 | 345 unblocked windows spanning 5,436 s average 58.745 frame events/s. Slowest full window is 54.557 at 2×, thermal state 0, 162.26% process CPU. | Not the reporter's M3 device or a known crystal scene. Native-menu flags do not identify the guest scene. |

Counters represent frame events, not display completion or audio listening.
Pause/resume creates large cumulative maxima; those are not gameplay stalls.
The phone's RemoteIO output counters remain disabled, so DMA analysis failures
must not be reported as audible silence. Full summaries are retained privately
in `hardware-log-summary.json`.

## Research decisions

Apple recommends identifying the app as a game and explicitly supporting Game
Mode. Both app manifests lacked those declarations. This pass adds the game
category, `LSSupportsGameMode`, and the legacy `GCSupportsGameMode` key for older
systems. This is a documented platform integration correction, not measured FPS
improvement. Activation and sustained behavior need device checks.
[Apple game technology guidance](https://developer.apple.com/videos/play/meet-with-apple/240/),
[legacy key documentation](https://developer.apple.com/documentation/bundleresources/information-property-list/gcsupportsgamemode).

Apple's scheduling guidance emphasizes dependency-aware work and avoiding CPU
contention. With the observed phone thermal pressure, measure useful CPU work
and idle spinning before changing QoS or increasing workers. Sustained Execution
Mode needs platform eligibility and provisioning review, so it is not silently
added to a sideloaded app or assumed to work on A15.
[CPU scheduling](https://developer.apple.com/videos/play/tech-talks/110147/),
[power and scaling](https://developer.apple.com/videos/play/meet-with-apple/242/).

Dolphin documents EFB cache improvements specifically for Galaxy and GPU-thread
optimizations benefiting other games. GalaxyPad already packages `RMG.ini` with
EFB access and deferred invalidation, loads game configuration, and enables
hybrid ubershaders. Skipping EFB depth breaks Pull Stars. These existing settings
are not new optimization proposals.
[Dolphin's 2022 performance work](https://dolphin-emu.org/blog/2022/12/21/dolphin-progress-report-september-october-november-2022/).

Upstream's ARM64 static-recompilation report compares Mario Kart Double Dash,
Luigi's Mansion, Colosseum and TTYD. It distinguishes getting native modules to
execute from outperforming a JIT and reports unresolved correctness limits.
GalaxyPad already contains the fallback-contract fix. Other games' benchmark
numbers cannot be transferred to Galaxy or iPhone, but they reinforce the need
to examine generated CPU work rather than assume AOT is automatically cheaper.
[RecompCore PR 6](https://github.com/ExpansionPak/RecompCore/pull/6).

The latest reviewed ModernGekko commit `5417826c31187d4dadf8588c7aa25bf107782936`
adds PGO support and runtime automation among other changes. This project already
has a measured PGO path. The upstream RecompCore comparison contains extensive
reorganization, so a wholesale dependency bump is not an isolated performance
experiment. Evaluate specific semantic fixes in maintained forks with their own
regressions and ABI/module validation.
[ModernGekko change](https://github.com/ExpansionPak/ModernGekko/commit/5417826c31187d4dadf8588c7aa25bf107782936).

## Next performance loop

The [follow-up timing experiment](PERFORMANCE-ITERATION-2026-09-15.md) rules out
substantial precision waiting in the measured slow Observatory scene and records
a fresh depth-readback lead. Its physical-phone checks remain title-screen only.

Do not repeat the rejected Simulator changes unchanged: direct-copy batching
underperformed both controls, reduced resolution barely changed the measured
Observatory workload, and fused vertex conversion's microbenchmark gain did not
produce a meaningful whole-game gain. These results do not rule out different
physical-device bottlenecks. See the September 13 performance and experiment
records before attempting them again.

1. Establish a named crystal-heavy mission on the current candidate and retained
   control, with identical saves, camera, pointer, resolution and logging. Record
   device/OS, host/module hashes, battery/charging and thermal state. An iPad Air
   M3 report is not reproduced by an iPhone-layout Simulator on Mac compute.
2. Measure cold and sustained runs separately. Capture normal frame/audio counters
   without a profiler, then a short Instruments CPU/Metal trace separately to
   attribute costs. Enable existing detailed output counters before audio starts
   only for the diagnostic arm. Do not mix its cost into timing comparisons.
3. Use 2×/1×/2× on the physical crystal scene to separate fill/fragment work from
   CPU/driver cost. Compare visible and hidden pointer cases with identical game
   state only as attribution, preserving real depth and testing Pull Stars.
4. If guest CPU dominates, profile the heavy scene for the existing PGO build and
   evaluate a representative-profile candidate. If vertex conversion dominates,
   revisit a portable specialization with actual format coverage and alignment
   correctness. If video-thread idle spin dominates, test bounded waiting in the
   fork. Do not select one from aggregate CPU or stack samples of blocked threads.
5. Accept only a repeatable improvement against returning controls, with stable
   audio, pointer/Pull Stars, controls, pause/resume, and sustained temperature.
   Otherwise record rejection and move to the next evidenced cost.

Every iteration ends with a tested fix, measured rejection or a specific blocker.
The importer fix and platform declarations are reviewable now. A new gameplay
performance gain remains blocked on a named physical scene and comparable runs,
not on a lack of additional generic optimization toggles.
