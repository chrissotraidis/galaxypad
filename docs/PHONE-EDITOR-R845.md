# R845 — compact settings and usable editor

2026-09-09. Prior R844 was progress: real plaza/settings/icon evidence plus Mac
branding implementation. This pass inspected actual UIKit editor interactions on
one iPhone17Pro/iOS26.5 Simulator, not game execution.

## Defects reproduced and corrected

- Compact settings placed below the menu partly clipped Reset. Use a taller panel
  near the top, inset left of the menu on short screens; keep all geometry within
  safe area. Larger iPad placement is retained with bounded available height.
- Bottom editor toolbar covered the extra1/2/−/+ controls while asking users to
  tap controls for resizing. Move toolbar to the upper safe area, reserving menu
  space. Done height40→44pt. Preserve mappings, sizes and stored control positions.
- Added stable accessibility identifiers and UIKit checks for panel containment,
  fully visible Reset at320pt height, Done target size, menu clearance and exposed
  auxiliary keys. Existing input/editor/size regressions remain intact.

## Verification

Baseline phone tal8E6 passes but does not detect these visual defects. After fixes,
phone3Coggq/qlRMQy and subsequent iPad H2Rh0i pass. Device order was phone shutdown,
then iPad boot; no simultaneous Simulators. No game/saves touched.

Live phone UI: settings Reset fully visible; Move controls opens upper editor;
actual tap on2 selects it and enables its slider; actual Done closes editor and
hides optional keys. Screenshots generated/ui-r845/settings-phone.png and
editor-phone.png. No claimed physical multitouch or gameplay acceptance.

Preview detail: selected2 slider shows1.25 retained in the singleton from the
preceding test's resize although preview clears preferences. Selection reachability
is valid; that value is not evidence of a new manual resize or clean-default scale.
The preview harness should clear the settings size cache when clearing preferences.

Private product rebuild/signature passes:
generated/candidates/product-r841/GalaxyPad.app/GalaxyPad SHA256
79ebf127db113e3d0b1aeeb47682651ff669a57e12a349143b92ca9ad224357f.
Not installed or promoted. Both Simulators shut down after testing.

Next actual iPhone product run including branding/import/lifecycle and touch UI,
not another unchanged isolated preview. Full first-play, physical ergonomics,
performance/audio, all-game progression and original PRD gates remain open.
