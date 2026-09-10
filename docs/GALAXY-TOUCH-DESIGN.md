# Galaxy touch design — R538, 2026-09-08

## R539 correction — user's SunPad reference is authoritative

The user rejected R538's visible action subtitles and upper utility row. Those
design choices below are historical, NOT accepted defaults. Use the actual
ref/sunpad/docs/readme/sunpad-delfino-plaza.jpg and SunPadGameOverlay.mm as the
visual reference: letter-only controls, asymmetric A/B/X/Y face cluster, nearby
pill controls, movement/D-pad together in the lower-left. Do not add explanatory
copy inside buttons or place1/2/+/- in an upper toolbar again.

R539 maps displayed X to existing Spin and displayed Y to existing Nunchuk C;
internal identifiers/bits remain Spin/C, so saved layouts and runtime mappings
are not silently repurposed. A/B/Z keep their existing Wii actions. Accessibility
labels retain explanations. iPad1/2 sit above movement, +/- above the right face
cluster. Positions leave hit rectangles separate; not an exact pixel clone.

Additional control-adaptation research:
https://bitbuilt.net/forums/threads/wiimote-emulation-through-gc-controller.2329/page-2
Post28 is a first-person GameCube-controller adaptation: C-stick aims IR, Y maps
to C, and additional shoulder A/B bindings permit aiming while confirming/firing.
This identifies a simultaneous-input need, not a single universal mapping.
https://github.com/Starlightbotanist/SMG-SMG2ClassicControllerDolphinPatches
documents several different mapping variants. No patch from that repository is
installed or assumed compatible with the exact AOT module. Pointer-capable right
stick and duplicate shoulder bindings need deliberate implementation/acceptance;
the current optional yellow stick still means tilt, not pointer.

## Research and product decisions

Nintendo's original manual is the authoritative control reference:
https://m1.nintendo.net/docvc/RVL/USA/RMGE/RMGE_E.pdf (controls p3–4,
actions p8–13). Movement is the Nunchuk stick; A is jump/use, shaking provides
Spin, B shoots toward the pointer, Z crouches/dives, C resets the camera, and
the D-pad changes the camera view. Spin follows jumping and serves interactions,
so a small Spin button far from A is the wrong priority.

Nintendo describes the movement/jump/spin relationship here:
https://www.nintendo.com/en-gb/News/2007/Super-Mario-Galaxy-lands-on-Wii-250077.html

The Switch handheld adaptation uses touch for the Star Pointer, demonstrating
that pointer interaction belongs in the playfield rather than being confused
with a second movement stick. Secondary report quoting Nintendo's announcement:
https://www.nintendolife.com/news/2020/09/nintendo_explains_how_motion_controls_work_in_super_mario_galaxy_on_switch
This is precedent, not proof that our interaction is equivalent or accepted.

## Implemented iteration

- Preserve SunPad's native menu, editor, stable input identifiers, saved layouts,
  controller handoff and input-release behavior.
- iPad: large A and Spin in a right-thumb action cluster. Smaller B and Z nearby.
  Retail letters remain visible alongside Jump / Use, Shoot, Crouch and Camera.
- Movement lower-left; camera reset/D-pad separately above. Secondary Wii
  1/2/minus/plus move to the upper utility area, away from primary thumb space.
- Tilt stick is opt-in through Controls > Show Tilt Stick (Ball / Ray). This
  toggles the existing virtual tilt input, not a claim that those stages work.
  Toggle clears held input; hidden tilt cannot intercept touches. The SunPad
  editor always exposes it. No gyro requirement introduced.
- Phone positions are not reworked in this iPad iteration; shared labels/toggle
  apply there, but phone sizing and reach remain unverified.

## Acceptance still required

This layout is a design inference, not an ergonomic result. Test held movement
with jump/spin, Z+A long/back jumps, simultaneous title A+B, pointer plus A/B,
and camera changes in live gameplay. A touch target's rectangle not overlapping
another is necessary but does not prove comfortable reach or simultaneous input.

The current pointer remains Classic Pointer. Do not rename it Direct Touch.
PRD product target requires context-aware tap/drag actions for file select,
Pull Stars, Star Bit shooting and other consumers, separately verified. Do not
globally synthesize A/B on every screen tap. Tilt-stage detection is not present;
the player must currently enable its control explicitly.

Performance and recurring Wii Remote communication interruption remain open;
neither is fixed by reorganizing controls.
