# GalaxyPad 0.2.3 — touch controls with a controller, and external displays

Version **0.2.3 (build 7219)** changes two things on iPhone and iPad.

**Touch controls with a controller (#35).** While the touch controls are hidden,
by the manual hide or because a controller is connected, **Show Touch Controls**
is the first row of the ⋯ menu. It brings them back, working, with the
controller still connected, and turns auto-hide off until you turn it on again.
**Controls → Touch → Auto-hide Touch Controls with Controller** is a checkmark
for the same saved setting as the switch in the touch control panel. Auto-hide
now counts only the controller GalaxyPad assigns to player 1. Hiding releases
held touch input, and hidden controls ignore presses. Both engines use this
overlay.

**External displays and orientation (#34, #36).** GalaxyPad's scene delegate
gives a game only to the app's own scene, so an external display or TV scene is
left to iPadOS (mirroring or an extended display). The New engine pin moves from
2817f5fd to galaxypad-engine `2a759adf`, whose SDL runs only in that scene,
adopts a replacement scene if iOS discards the first, and takes orientation from
the scene's geometry, which iOS 27 scene apps need.

## Install or update

Build with [PadMint](https://github.com/chrissotraidis/padmint/releases/latest)
on an Apple silicon Mac, as for 0.2.2, and install over your existing GalaxyPad
with the same sideloading tool and Apple ID; do not uninstall first. Game data,
saves and settings stay in the app.

## Validation

- The UIKit overlay suite passes on an iPad Pro 13-inch / iOS 27 Simulator,
  including the new player 1 ownership, auto-hide and Show checks.
- GalaxyPad's PadMint iOS route built an unsigned IPA with the new engine pin.
  The engine framework contains SDL's scene-geometry functions, and the SDL
  harness on the iPadOS 27 Simulator showed orientation following the scene, no
  second `main` and no SDL delegate on an external-display session.
- PadMint's player check ran before tagging on the release commit, with current
  PadMint `main`, Apple's Python 3.9 and an empty PadMint folder; the GitHub
  release records the result.

**Not verified yet:** a physical TV or external display, a physical controller
on an iPad, and the menu on a device. That acceptance is pending. These checks
do not establish gameplay, audio or full-game completion.

## Reproduction

The app input is the `v0.2.3` tag (build 7219). The New engine is
`2a759adf` ([dependency lock](../config/dependencies.lock.json)); build steps
are in the [PadMint recipe](../padmint.json). Supply your own supported game
image privately in the app.
