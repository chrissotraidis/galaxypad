# R840 — compact phone defaults

2026-09-09. Previous turn was progress (menu code plus runtime verification).
Continued R838 product queue using actual overlay code; no core/profile experiments.

## Change

- Phone small buttons now have a default44pt size floor before user scaling.
- D-pad defaults use44pt cells instead of scaled36pt cells; menu becomes44pt
  instead of40pt on both device families.
- Move phone D-pad slightly upward to separate its Down target from movement.
  Shift B and C slightly left to separate A/B and Spin/C rectangular hit boxes.
- Preserve SunPad-derived appearance, button identities/mappings, explicit Spin,
  saved control origins, user size overrides, optional controls and editor paths.
  This is a default-layout correction, not a ban on user-chosen small controls.

## Evidence

One iPhone17Pro/iOS26.5 Simulator7B639924-AD8F-4D5C-AD29-71F47C768A0D,
isolated OverlayTests only. No game launched or data provisioned. Native preview
shows the same lower clusters and separate pointer field. Screenshots at
generated/ui-r840/01-phone-before.png and02-phone-after.png; these are a neutral
preview, not HUD/scene coverage or proof of physical reachability.

New UIKit checks inspect every visible default phone control including D-pad and
menu: minimum44pt, safe-area containment and pairwise rectangular non-overlap.
They exposed move/Down overlap after enlargement, then existing A/B and Spin/C
overlaps. Each was corrected in default geometry, not hidden by weaker assertions.
Final phone pass: generated/tests/mobile-ui.Qs1PUZ.

Initial cold-boot console run ArHI2x produced no completion marker; preview was
launched before that observation finished, so the run was terminated and rejected.
Subsequent tests ran serially. Failed geometry logs: Gt7DOR, hPbzo4,8qDQRz,DQDoDk.
These failures are retained, not reported as successful baseline acceptance.

iPhone shut down before booting iPad. Full same UIKit suite then passed on
iPadPro11M5/iOS26.5: generated/tests/mobile-ui.ZR0PDk. Final test executable SHA256
55eec0f81192394279b9d43b4a1da60a79572e80b408ed30537a618b527f0f7d.
`git diff --check` passes. iPad shut down afterward; no live Simulator or game.

## Next / limits

Build a private product candidate with R838 icons, R839 menu and R840 controls;
verify actual gameplay HUD/dialogue overlap and controls/settings interactions.
Do not substitute another isolated touch-test loop for that product check.
Other phone sizes/orientation, physical multitouch, gameplay feel, pointer and
full editor/menu lifecycle remain open. No performance or shipping claim.
