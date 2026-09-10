# R844 — real HUD/settings comparison and branding

2026-09-09. R843 was progress (candidate geometry plus tests). Ran unchanged
private fdf7539e588943c4fbcfa5374bcebdaffe4c0bd66b72b38faa5104a5fb7be14e host
with module3acdcddcd47812c2e2a67b8cec0cf06c17009cf1ad7f2e9dc9abd83158a1bac0.
Only iPadPro11M5/iOS26.5 DE8E956F-6B29-4FF3-AF4A-77034CE8588A booted.
Console97077/PID76635. All private run artifacts in generated/runtime/product-r844.

## Actual observations

1. Exact existing file1 selected through explicit diagnostic A/B/pointer steps.
   Story sequence ended at Peach's letter; bounded finish sequence reached plaza.
   No fixture outcome assumed without the current screenshot.
2. plaza-hud.png shows life icon/count and coin/Star Bit counters unobstructed,
   unlike R841. This closes that one scene's specific overlap, not all-game layout.
   Controls are farther inward; physical thumb reach is unproven. File-details
   Play/Back still share space with controls. Do not call the layout shippable.
3. settings-compact.png shows R842's smaller touch-only panel in the actual game,
   no low-contrast duplicate render segment row. Native close returns to gameplay.
   Actual A UI click afterward produced a visible Mario jump/landing response;
   not simultaneous physical multitouch or complete input acceptance.
4. Confirmed native Stop completes failed=0 at18:29:04.483. GameData before/after
   SHA99d432d517b92b19da0c403819b91288b10c7063c3ce61f5000347ef823ab64f matches.
5. After termination, home-icon.png shows GalaxyPad's original spiral icon with
   iPad's rounded mask on home screen and recent Dock. iPhone/light-dark variants,
   macOS Dock and editable-source requirements remain open.

No matched performance comparison conducted. Title/story counters near60 do not
prove gameplay stability; audio underruns occurred. No full-game/device acceptance.
Previous85ffc app reinstalled and sole Simulator shut down. No save restoration
needed, no data deletion or public publication.

## macOS branding implementation

Added scripts/build-macos-icon.sh: deterministic slot derivation with sips and
iconutil, output generated/branding/GalaxyPad.icns (recognized Mac icon,2,840,001B).
build-macos-app.sh now generates it before replacing an existing output bundle
and copies it into Resources; Info.plist names it. Added branding/PROVENANCE.md
linking exact retained source/prompt and honest editable-source limitation.
Script/plist checks, test-macos-app-config.sh and test-ios-icons.py pass.
Did not rebuild/promote a full macOS game app during the Simulator run.

## Next

Advance remaining product requirements beyond repeating this plaza: verify icon
packaging on Mac/iPhone, compact settings/editor on phone, and full controller/
pointer/lifecycle behavior. Keep inset layout unaccepted for physical reach;
do not trade the SunPad usability target for a passing HUD rectangle test.
Return to bounded performance experiments with a new falsifiable hypothesis,
not previously parked QoS/normalization/microbenchmark lanes.
