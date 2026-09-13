# iPhone and iPad performance research, September 13

## Current baseline

The user reports roughly 45 FPS on iPhone 14, with harder scenes dipping toward
30 and unstable gameplay. iPad also has slow scenes and intermittent audible
underruns. These are user observations, not instrumented measurements.

Fresh build 3 device logs were copied read-only to
`generated/runtime/perf-research-20260913/`. iPhone starts at 1× render scale;
iPad starts at 2×. Both have frame logging disabled and contain no frame-window
or audio-counter snapshots, so these logs cannot quantify the reported dips.
`baseline.json` retains log hashes, startup settings, and artifact identity.
The concurrent release-preparation task subsequently installed build 4;
comparisons must account for that identity change.

## Parallel investigation

CPU/render dual-core execution, asynchronous hybrid ubershaders, shader cache,
and speculative EFB readback batching are already enabled. Adding general
worker threads does not establish a useful optimization. Real EFB depth reads
must remain enabled because disabling them broke Pull Stars.

The earlier correct-depth Simulator profile measured median EFB wait 5.697 ms
but associated GPU execution only 0.05777 ms. Those historical measurements
implicate dependencies and scheduling, not necessarily GPU pixel throughput,
and do not establish physical-device timing.

### Rejected experiments

- **Metal completion mechanism:** two native and two Simulator runs completed
  7,920 byte-validated readbacks. Shared-event and condition-variable waits did
  not materially outperform `waitUntilCompleted`. Standalone Simulator waits
  were about 0.21–0.23 ms and did not reproduce the game's 5.7 ms wait. Changing
  the wait API alone is not justified. Source, raw results and primary research
  links: `generated/experiments/gpu-queue-research-20260913/`.
- **Depth prefetch history 8→2 frames:** an isolated source object compiled;
  retained-trace replay predicted 160,735→160,054 speculative tile-frame pairs
  (0.42% reduction), but 51→444 demanded tiles outside prediction. These are
  eligibility estimates, not measured GPU copy counts. The weak benefit and
  extra demand-miss risk do not justify a game candidate. Evidence:
  `generated/experiments/depth-prefetch-window-20260913/`.

### Profile-guided module candidate

Physical builds 3 and 4 contain the **unprofiled** O2 module: every file-backed
Mach-O section matches the preserved unprofiled device module. An existing
device PGO module has the same exports and iOS target, and both platform pairs
have 1,329 matching compile commands after removing only profile-use and output
paths. Module tables match; the retained validated profile and completed build
log show no profile mismatch. This is an existing compiled-artifact audit, not
a claim that historical source snapshots were reconstructed in full.

Exact provenance: `generated/experiments/physical-pgo-provenance-20260913/audit.json`.
The matching Simulator unprofiled control is the preserved
`gRMGE01_recomp.unprofiled-20260912.dylib`; the ordinary filename in that build
directory was replaced with PGO and must not be mistaken for the control.

The current-host, correct-depth A/B/A comparison supports advancing PGO:

| 60-second run | Mean of seven sparse HUD readings |
| --- | ---: |
| Unprofiled A | 39.31 FPS |
| PGO C | 48.03 FPS |
| Unprofiled D | 39.17 FPS |

All 21 screenshots show the same central Observatory scene: Luigi, 121 stars,
2,324 Star Bits, zero coins, life 3, four lives. Module selection is the only
app/workload change; host, save, 1× rendering, 4:3 and real depth remain fixed.
Every PGO reading exceeds every control reading. The descriptive improvement
is 22.4% versus the pooled control means. Initial control A had more background
FileProvider/Spotlight work; the reverse control starts without that high load
and reproduces the slowdown. Background activity and clocks are not fully
controlled. These sparse readings do not establish continuous frame timing,
stable 60 FPS, hardware gains, or a confidence interval. Run B was discarded
before measurement because delayed scene review allowed a controller-idle
disconnect; no modal FPS enters the accepted comparison.

Evidence: `pgo-aba-review.json` and the three immutable run directories under
`generated/runtime/perf-research-20260913/`.

The combined build 5 host, SHA256
`a6a3fc40f0680ff1008d4d883c21ed1191ed56545c40cc656958891f1d6a5832`,
rebuilds all 13 host objects against the unchanged accepted audio-v8 core and
matching Mixer headers. Its separate PGO diagnostic contains 57.90 seconds of
interior audio snapshots: zero new underruns/full/backlog drops or short output
callbacks, and 2,779,136 nonzero output frames out of 2,779,136 delivered frames.
The comparable unprofiled diagnostic also has zero new underruns; therefore no
audio-quality improvement is claimed. Startup totals are excluded. Full diagnostic
analysis and iPhone UI/gameplay checks follow in the retained evidence directories.

The same-host diagnostic comparison also records 39.60→48.17 frame events/s
and 6.01→1.16 gaps of at least 33 ms per second. Neither window adds a gap of
at least 100 ms. Cumulative startup maxima are not attributed to these windows.
DMA input production rises 165.16→200.85 enqueues/s; both output streams remain
fully nonzero. These separate logging-enabled measurements support a reduction
in long frame-event gaps and audio-counter nonregression, not listening quality
or display-presentation timing. See `pgo5-diagnostic-comparison.json`.

The user is now away from home: physical devices must remain untouched,
including experimental installs, launches and input tests. Continue on
Simulators only until that restriction is explicitly lifted.

## Settings repair

An isolated UIKit candidate removes the unconditional aspect-choice disable and
adds Show/Hide in game for selected auxiliary controls and Tilt in Move Controls.
The existing grouped preference for 1/2/minus is preserved. Baseline fails the
new aspect-selection regression; candidate passes visibility persistence and
iPhone-sized safe-area/editor hit-testing checks. Evidence:
`generated/experiments/settings-restore-20260913/`.
The patch was applied after the concurrent owner's source checkpoint `7dd4413`.
The initial edited files matched the passing isolated candidate byte-for-byte. Work now
continues on `codex/ios-performance-settings-20260913`, based on their final
checkpoint `6e1f11d`; their release-preparation PR is separate.

Actual iPhone 14 Simulator testing then found a 0.48-point overlap between the
default A and Z hit boxes. A small phone-only default-position clamp provides
a 6-point gap before saved origins are applied, preserving customized layouts.
The final full UIKit suite passes on the phone. Actual UI interaction verifies
Touch Control Settings → Move Controls → select 2 → Show in game → Done, with
1/2/minus remaining visible. Menu → Display → Aspect Ratio → Native 16:9 opens
the restart alert and persists aspect mode 1. Scrolling, hiding again, Tilt
restoration, and hit testing also pass. Preview-only presentation interception
in the test host was corrected; it was not a product-menu defect.

Evidence: `generated/tests/iphone14-settings-20260913/verification.json` and
`generated/tests/mobile-ui.RdN7zj`.

The final build 6 Simulator host includes that phone geometry fix:
`generated/build/ios-simulator-settings-perf6-20260913/GalaxyPad.app`, SHA256
`66b3cc8f381a66e5d0d64bc46e3c81df37cc6fe47f57b5e5b74e39b542b9fea0`.
It uses the same accepted audio core and profile-guided game module. The dedicated
iPhone 14 Simulator uses Mac compute; it cannot establish A15 performance.

The final build 6 iPhone-layout pair observed mean sparse HUD readings of
36.94 FPS unprofiled and 45.07 FPS PGO, with all 14 screenshots confirming the
same scene and no modal. The host, module pair, 1×/4:3 and disabled logging match.
Compiler activity was present before the control and other background load was
unequal, so this single pair is supporting evidence for the stronger iPad A/B/A
result, not an independently isolated 22.0% causal estimate. No physical iPhone
performance is inferred. Evidence: `iphone-comparison.json`.

## Retained candidate and next gate

The final private Simulator package embeds the exact PGO module rather than
relying on an external module argument:
`generated/simulator-stage.DmuSkj/GalaxyPad.app`.
Resource resealing changes the executable's signed-file hash to
`75240e055dc6f4d258024c9d5d5ab90324c6ddf9ffc645eb118d99328058c5d6`;
the module remains byte-identical at `90e24dfb…`. Deep/strict ad-hoc signature
verification passes. Installation on the dedicated iPhone Simulator preserves
the expected host/module hashes. A launch without a module override renders
the wrist-strap screen, and a live `lsof` text mapping identifies the bundled
Frameworks module. This final check establishes packaging/startup only; measured
gameplay above used the same source host before resource resealing and identical
PGO module. Receipts: `final-simulator-package.json` and
`embedded-package-smoke/receipt.json`.

Test runtimes were terminated and both Simulators shut down after evidence
collection. No experimental physical install, launch or input test was performed
by this task. The earlier read-only build 3 log pulls preceded the away-from-home
restriction; the other task's build 4 deployment is separately documented.

The 60 FPS goal is still open. When the user permits hardware work again, use
the audited device PGO module with the final device host, preserve signatures,
saves and settings, and compare fixed scenes at the same active resolution.
Measure actual iPhone/iPad frame pacing, audio and thermal behavior before
claiming device gains. Further GPU scheduling work needs physical attribution;
the rejected wait/prefetch experiments should not be retried unchanged.

## Primary references

- [Apple CPU scheduling guidance](https://developer.apple.com/la/videos/play/tech-talks/110147/)
- [Apple Metal performance analysis](https://developer.apple.com/documentation/xcode/analyzing-the-performance-of-your-metal-app)
- [Metal completion semantics](https://developer.apple.com/documentation/metal/mtlcommandbuffer/waituntilcompleted())
- [Metal Simulator limitations](https://developer.apple.com/documentation/metal/developing-metal-apps-that-run-in-simulator)
- [Dolphin hybrid ubershaders](https://dolphin-emu.org/blog/2017/07/30/ubershaders/)
