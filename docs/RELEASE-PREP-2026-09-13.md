# September 13 build 4: reporting, pause and device transfer

Build 4 is installed and launch-verified on the attached iPad and iPhone. This is
an input/reporting update, not performance acceptance or a public release.

## Changes and checks

- Visible Pause, touch Start + and Xbox Menu send original Wii Plus; Xbox View
  separately pauses/resumes the app. Controller event regressions and isolated
  UIKit runtime pass. Actual Simulator Pause opens the original Observatory menu;
  a second press resumes. In-level exit and physical Xbox acceptance remain open.
- Report a Problem opens a reviewed GitHub issue draft. Sanitized logs are optional
  and off by default; Share Log exports a file for manual attachment. Preview,
  sharing sheet and encoded draft URL were exercised. No issue was submitted.
  The repository is still private, so unsigned-in browser access returns 404.
- HUD says FPS. README uses the supplied Mario hero and two other unchanged
  screenshots, badges and FAQs. The old HUD wording remains in those captures.
- Boot failures show actionable import/transfer recovery text and export a stable
  `core/boot_failed` code. This does not remove runtime attribution from docs.

## iPhone failure and recovery

The iPhone attempted startup at 11:24 local while the WBFS transfer finished at
11:25. It rejected the incomplete image. After completion, all eight game files
were byte-identical to the iPad copy. AFC placed the save under a nested Wii/Wii
folder after the runtime created Wii; explicit per-file copying corrected the
active location. All 21 copied save files then matched. The unused nested backup
was retained. Subsequent startup no longer exited with disc rejection.

Build 4 installation preserved all 33 iPad and 54 iPhone protected files
(saves, configuration and preferences) byte-for-byte before launch. No uninstall
or data reset occurred. iPad preferences were not copied to iPhone. The game image
is the user's existing WBFS, not a converted ISO. Successful launch is not proof
of playable physical performance or input acceptance. A later process inventory
found iPad running and iPhone absent. The iPhone build4 log records several minutes
of runtime and foreground transitions without a boot failure; why that process
subsequently ended remains unestablished and is handed to the parallel task.

## Artifact identity and reproduction

Signed host SHA-256:
`f33c9116df400111016fcb661b407da85c20ef77bd9dfc9534fadc5ad39bf98c`

Signed nested module SHA-256:
`4f9a58477fa74778ff77a58d9fcb6a12daff00839ef366e512fb3bc57c0baa5f`

Unsigned device host:
`446858a91a03f7b8376db83fe9ce162845a93f572654175ae05bd16e9c5c4200`

Simulator host:
`eb9271849d54a54e920231b06e99a1c232f627bc22d52326d423825c12e8cb76`

Unchanged Simulator PGO module:
`90e24dfb4e96597686b8fccf09bb55efdcbd7d059dd3ff710a9f32fab26f353f`

Both builds rebuild 13 host objects with immutable source hashes and frozen
accepted audio/core ABI. The physical module was retained; do not infer that it
uses the Simulator PGO profile. A parallel task is auditing physical PGO provenance.

Private reproducible commands and receipts:

```sh
python3 generated/build/ios-device-release-prep-bootfix-20260913/rebuild.py
python3 generated/build/ios-simulator-release-prep-bootfix-20260913/rebuild.py
python3 generated/runtime/release-prep-20260913/deploy-build4.py sign
python3 generated/runtime/release-prep-20260913/install-build4.py
bash tests/test-controller-pause-events.sh
```

The private build/install scripts are single-use evidence recipes, not commands
to rerun against existing output directories. Their manifests retain full compile,
link and signing inputs. Evidence root:
`generated/runtime/release-prep-20260913/`; see `signed-build4-candidate.json`,
`build4-iPad/preservation.json`, `build4-iPhone/preservation.json`,
`iphone-transfer-corrected-verification.json`, and `iphone-after-transfer-logs/`.
UIKit pass log: `generated/tests/release-ui-runtime-20260913.log`.
Foundation reporting/privacy regressions pass. The broad repository gate still
has the historical missing private THP fixture; it is not claimed green.

## Remaining performance work and handoff

Release remains NO-GO. User now reports iPhone 14 around 45 FPS with dips near30
and occasional iPad dips/audio underruns. These are user observations, not matched
benchmarks. Real-depth heavy Simulator baseline remains45–49; earlier depth-off
60 FPS results do not establish playability. Audio stays120ms, default aspect4:3.

The parallel performance/settings task owns subsequent Simulator work and will
receive GameOverlay/UIKit/settings files after this checkpoint. Next hypotheses:
verify physical versus Simulator PGO provenance and measure matched candidates;
continue investigating EFB submission/completion latency while retaining real
depth. Settings aspect actions and restoration of hidden auxiliary touch buttons
are separately being repaired there. No sustained60 or audio fix is claimed here.
