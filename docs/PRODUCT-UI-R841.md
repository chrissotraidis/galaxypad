# R841 — product candidate, real opening/plaza UI

2026-09-09. Previous R840 made tested control changes. This pass builds and runs
the actual app, not another isolated preview. No performance optimization applied.

## Artifact and run

Configured `apple/ios` with Release/Ninja/ios-simulator-toolchain into
`generated/candidates/product-r841`, native THP OFF. Built with parallel4, icon
target included, ad-hoc signed and deep/strict signature verified. App SHA256
0a1fe67e4ff67ec650dba191f0911101ce8f905f623564a00056a37a0100051f.
Unchanged module3acdcddcd47812c2e2a67b8cec0cf06c17009cf1ad7f2e9dc9abd83158a1bac0.
Build emitted20 existing vendor unused-parameter warnings, no build failure.

Only iPadPro11M5/iOS26.5 DE8E956F-6B29-4FF3-AF4A-77034CE8588A booted.
Candidate installed over existing app without data erase. Save copied to
generated/runtime/product-r841/GameData.before.bin, SHA99d432d517b92b19da0c403819b91288b10c7063c3ce61f5000347ef823ab64f.
Console session12025/PID73986; log generated/runtime/product-r841/runtime.log.
Launch uses exact extracted/run1, ref/supermariogalaxy.wbfs, unchanged module,
private input.json, nativeTHPNO/QoSexperimentNO/frame-windowloggingYES.

## Visible results

1. Strap/title/file select render with new menu/control geometry. Diagnostic
   A+B advanced title; explicit pointer(.375,.66)+A selected file1, then
   (.73,.88)+A activated Play. This is injected navigation, not touch acceptance.
2. Bounded copied R836 story sequence completed and reached real opening plaza.
   Story text sample stays readable; file-details Back/Play still share lower
   space with controls. Screenshot story-layout.png retained privately.
3. Plaza screenshot plaza-layout.png shows upper HUD clear, but right Spin/control
   cluster crowds Star Bit count and movement stick covers part of life icon.
   This contradicts full HUD-clearance acceptance; next geometry change must
   address actual game coordinates and remain tested against editor overrides.
4. Real menu exposes host actions including Stop. Controls → Touch Control Settings
   opens/closes successfully. settings-layout.png shows low-contrast unselected
   render segments and duplicate Display functionality inside touch settings.
   Remove that duplicate row or correct it as part of a focused settings pass.
5. Native Stop confirmation exercised; runtime exit failed=0 at18:09:50.613.
   GameData hash unchanged. No new file/star/save-progress claim.

Title windows near60 and plaza sample windows50.76–57.31 after-frame events/s
are observations only, not matched performance improvement or smooth60 acceptance.
Audio underrun count increased; no audio acceptance. No physical-device evidence.

Previous85ffc100 normal app retained and reinstalled after stopping the candidate;
sole Simulator shut down. Candidate remains available, not promoted. Container
paths change on install; resolve fresh for the next run.

Next: fix measured HUD intrusion and touch-settings duplicate/contrast, then
rebuild this private product candidate and repeat real-game check. Keep full PRD,
performance, icon home-screen/macOS, and device gates open.
