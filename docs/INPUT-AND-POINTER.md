# Input and pointer

## R867 touch tilt response options

Controls → Touch Tilt Stick provides0.5×/1×/1.5× sensitivity, vertical inversion
and recenter. Default1×/non-inverted preserves the prior normalized axes. Scaling
clamps at±1; malformed/nonfinite preferences fall back to1×. Movement/controller
axes are unchanged. Changing response or recenter clears touch input; release
still returns the stick to neutral. These are host input options, not proof that
SpherePadController, ray surfing or every mandatory tilt consumer is accepted.

## Running the isolated UIKit regressions

Run `bash tests/run-mobile-ui.sh BOOTED_SIMULATOR_UUID` with exactly that one
Simulator already booted. This builds/installs the isolated test bundle, not the
product, and leaves a unique log under generated/tests. Foregrounding the test
backgrounds the product; pause gameplay first. Return to the product afterward.
The runner requires an explicit test-completion marker and rejects FAIL lines:
simctl itself can return0 when the test process exits1 (observed R627).
Parser regressions run in check-repository.sh; the actual UIKit run remains a
separate Simulator check. Neither substitutes for hands-on gameplay or multitouch.

## R624 actual gameplay touch collection and shot

Normal app b853f060/module3acdcddc, existing R619 runtime, pointer experiments off.
Actual Y recentered Gateway camera. Corrected touch aim collected a roof Star Bit
while Mario stationary: counter0→1 and bit disappeared. Actual B then spent1→0
with impact near the retained cursor. This verifies touch collection/shooting,
not precise finger-to-screen alignment, rabbit stun/catch, or sustained movement.
Near-edge aim visibly overshoots; right controls overlap the inventory HUD.
See R624 journal and generated/ios-runtime-r619.log. No product changes this pass.

## R608 default mobile touch file-to-story route

Normal app ff855d69/module3acdcddc, no pointer experiments (context, pitch22,
calibration, observer and hooks allNO). Diagnostic A+B only at title. Actual
UIKit drag over file1 plus explicit A selected it; actual drag over Play This
File plus explicit A reached opening story. No automatic action or calibrated
inverse required for these broad targets. Private screenshot
generated/ui-r608-default-story-native.png and log generated/ios-runtime-r608.log.
Clean native exit12:53:48.805 failed=0. This is default Classic Pointer evidence,
not Direct Touch, precise full-viewport aiming, gameplay, save or performance
acceptance. Existing story text remains obscured by controls. P2-labelled icon
in detail observed but runtime second-controller cause not established.

## R541 mobile controller aim/action chord

Right Shoulder now duplicates logical Wii A instead of Nunchuk C. Right Trigger
continues to duplicate B; default Y still provides C. This keeps the aiming thumb
on the right stick for A/B actions. Editable face/left-trigger assignments and
the left-shoulder tilt modifier are unchanged; no saved mappings are reset.
The menu explanation matches the new alias.

Rationale: [first-person Galaxy GameCube adaptation, post28](https://bitbuilt.net/forums/threads/wiimote-emulation-through-gc-controller.2329/page-2)
describes secondary shoulder A/B for simultaneous IR aiming and actions. This is
an ergonomic precedent, not evidence that GalaxyPad gameplay passed.
Regression reproduces old alias failure, then verifies aim+A, aim+A+B, independent
release and retained Y/C. Controller/input sanitizer tests and Release iOS build
pass. Not installed or hardware-tested yet; current visible app remains R540.

## R417 diagnostic host policy and Good Egg selection

Explicit runner --background-input preserves RuntimeConfig's opt-in through
runtime initialization; post-exit INITrue confirms persistence. Actual live
pointer/button input advanced Terrace tutorial, unlocked/selected Good Egg,
activated Fly to This Galaxy and selected Dino Piranha. Arrival and subsequent
movement visible.750button samples/64transitions, all136246input samples report
IR visible, finalbuttons0, native-only cleanexit/saveunchanged. Normal app and
default policy unchanged; not all lifecycle/input correctness acceptance.
New private arrival slot1 in background-r416 is untested for reload. Whole-run
VI overflow/audio underruns prevent performance/audio acceptance.

## R361 candidate Terrace interaction

Candidate549988...692e1 with actual one-star save (no emulator state load)
visibly reaches Observatory, moves after native pause/resume, enters Terrace,
advances Luma/tutorial dialogue and activates the transformed Pull Star into
galaxy-selection tutorial. Interior aim x0.06/y0.5 produces hand cursor on
the Pull Star; A activation verifies behavior, not cursor appearance alone.
g6-terrace-pull-star-aim.json assumes that specific interior camera.
g6-observatory-terrace-approach.json is a short directional segment used with
visual route checks, not an automatic whole-route guarantee. Real depth peeks
recorded; no EFB shortcut. Other pointer/motion mechanics remain open.

Status: **macOS file-select path proven; gameplay and lifecycle matrix pending**

## Desktop profile

The packaged default profile is a Wii Remote plus Nunchuk in upright mode. Mouse movement feeds absolute IR position. Keyboard defaults are J=A, K=B, U=C, I=Z, Return=Plus, WASD=Nunchuk stick, and L=dedicated three-axis shake/Spin. This is a desktop diagnostic profile, not the final editable Apple control model.

`scripts/wii-pipe.py` provides a deterministic Pipe controller for reproducible press, hold, release, simultaneous-input, Nunchuk-stick, and absolute-pointer steps. Its fixtures contain commands only; they contain no game data or captured raw input history.

The G6 progression fixtures intentionally include short axis and diagonal variants. The game's camera rotates independently while a fixture is held, so a long fixed stick vector can cease to match the apparent screen direction mid-step. Progression evidence therefore uses short, screenshot-verified segments; fixture names describe the emitted stick vector, not a guaranteed screen-space direction.

## Pinned Pipe backend quirk

In the selected Dolphin vendor, Pipe token `Button B` did not assert the emulated Wii Remote B bit during RMGE01's held-A+B title gate. Pipe token `Button X` did. GalaxyPad therefore maps semantic Wii Remote B to Pipe X and semantic Nunchuk C to Pipe B. This is deliberately confined to the diagnostic Pipe profile; the keyboard/mouse profile continues to use ordinary independent host keys.

The independent mapping was re-run from the title with Pipe A+X held for two seconds. It advanced to file select. This excludes the earlier diagnostic same-token A/B mapping as acceptance evidence.

## G5 live evidence

On the private packaged app, deterministic absolute IR movement visibly moved the star pointer, highlighted slot 1, selected Yes in the new-file dialog, selected the Mario icon, confirmed it, and returned to file select with Mario occupying slot 1. A native runtime screenshot records the resulting rendered file-select state, but remains ignored with all other protected evidence.

The correlated diagnostic rerun recorded 25,967 P1 input samples, 403 button-active samples, four button transitions, and IR visibility for every sample. While the Pipe remained connected, the last sensor position was `(655,529)`, matching the deliberate off-center absolute-pointer command. The same file-select interval recorded zero CPU EFB peeks; this is evidence that the menu pointer path did not request depth readback, not evidence that EFB instrumentation failed. Other instrumented scenes produced depth-peek counts and timing.

This proves host input reached the guest and that pointer coordinates selected the intended visible targets in this scene. It does not yet prove gameplay `GXPeekZ` target identity, controller support, held-input clearing, gameplay pointer mechanics, or any mobile touch mode. Those remain required.
# Foreground requirement for desktop input evidence

September 6 R57: explicitly foreground the runtime before issuing short Pipe-controller sequences. A down-stick pulse left Mario stationary without foreground ownership; with the process frontmost the same direction moved Mario to the Goomba encounter. Menu clicks and screenshots alone do not prove foreground input ownership. Keep background-input policy unchanged, clear the stick at the end of each sequence, and record intentional pauses separately from gameplay cadence.
