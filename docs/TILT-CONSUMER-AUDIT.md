# Tilt consumer audit — R868

This is a source map, not gameplay acceptance or proof of exact RMGE01 machine
code parity. Read local Petari HEAD845164b4 and ModernGekko HEAD0514d9f0;
working-tree changes may exist. Petari has incomplete bodies and an RMGK01
symbol map, so do not manufacture RMGE01 patch addresses from these names.

## Distinct consumers

| Path | Observed source | Consequence |
| --- | --- | --- |
| Ball | `ref/petari/src/Game/Ride/Tamakoro.cpp:124` allocates `SphereAccelSensorController`. | Merely having SpherePadController available does not select its plain-stick behavior. |
| Ball axes | `SphereAccelSensorController.cpp`, `clacXY`: accelerometer projection, core base10°, margin5°, range25°. | Neutral host axes are not themselves proof of neutral game movement; measure guest acceleration and resulting axes. |
| Ball actions | Same file: `testBrake` uses core A (or sub Z/C); `calcJumpPower` uses core A trigger. | A replacement must preserve held versus edge semantics and alternate-controller behavior. |
| Plain sphere stick | `SpherePadController.cpp`, `clacXY` reads Nunchuk axes; `calcDirSphereMove` applies camera/gravity transform and magnitude clamp. | Reuse this narrow axis strategy only after confirming actual target/dispatch; do not replace whole controller or drop brakes/tutorials. |
| Ray steering | `SurfRay.cpp:838`, `updateRotate` reads core acceleration x/z, applies thresholds, steering accumulation and damping. | A ball-only patch does not implement ray input. |
| Ray gates | `SurfRay.cpp:1069`, `isRotateStart`: tutorial lectures7/11; otherwise speed>3 or held A. `updateRideAccel/Free` uses held A. | A stationary test outside an enabled gate can legitimately show no steering. Preserve acceleration/tutorial progression. |

## Shared host path and coupling

`apple/shared/GalaxyPadInputDevice.cpp` maps TiltX/Y to Dolphin Tilt directions,
while MoveX/Y feed Nunchuk and pointer axes feed IR independently. R867 response
settings affect only touch tilt before this device layer.

Dolphin `WiimoteEmu.cpp:779` combines tilt **and point** rotations in
`GetTransformation`; `GetAcceleration` applies it to gravity/extra acceleration.
`GetTotalAcceleration:862` uses gravity unless IMU input overrides it. Upright
is default-false in the vendor settings and is not explicitly enabled by the
mobile config. Do not infer a final guest acceleration vector from this alone:
orientation, point settings, WPAD/KPAD conversion and game filtering intervene.

`GamePadUtil.cpp:36` routes to WPadAcceleration; its reference update negates
core KPAD acceleration and includes history processing. The file has incomplete
sections and suspicious reconstructed loops. Treat it as a navigation aid,
not a trustworthy executable substitute or evidence of a runtime bug.

## Next falsifiable work

1. Resolve the named ball/ray consumers against exact supported RMGE01 DOL and
   current generated module. Confirm class dispatch and machine-code behavior
   before introducing hooks; retain original functions for comparison.
2. Observe guest acceleration and resulting movement/steering at a real mechanic
   checkpoint: neutral, ±X, ±Y, release, pointer moved/hidden, held A and A edge.
   Include tutorial gating; do not report a gated stationary sample as failure.
3. If neutral or direction is wrong, use a named mechanic-specific axis adapter,
   preserving camera/gravity, brakes, jump and tutorials. Do not globally rotate
   the Wiimote merely to fix one ride and inadvertently alter pointer behavior.
4. Complete actual ball and ray progression plus pause/resume/recenter checks.
   Input unit tests or this audit cannot substitute for that acceptance.

No game/runtime source changed, no runtime experiment or performance claim.

## R869 exact RMGE01 call-site confirmation

The existing R546 Bussun USA symbol file provides candidate labels, with its
original warning that non-Korean labels can be wrong. Current generated chunks
provided candidate call sites; `python3 scripts/audit-tilt-consumers.py` independently
checks the exact supported DOL SHA and raw relative branch operands. It passes.

Confirmed narrow relationships:

- Ball acceleration-axis candidate80330230 calls getter8033015C at803302E0.
- Getter starts with selector load at offset0xB8; core path tail-branches from
  80330170 to803D21B8 (candidate MR core acceleration).
- Plain sphere-axis candidate8033068C calls Nunchuk X/Y candidates803D2904/292C
  at803306AC/B8. This is distinct from the acceleration path.
- Ball brake calls held-A candidate803D2244; jump calls triggered-A803D25CC.
- Ray rotate candidate803327C4 calls gate803332DC at803327F4 and the same core
  acceleration getter803D21B8 at8033281C.

This supersedes the lack of any USA address evidence in R868, not its caution
about incomplete reference code. No virtual-table dispatch, full function
equivalence, constant interpretation or live acceleration values are proved.
Next verify ball dispatch/axis-return boundary and ray gate in exact code before
an opt-in mechanic-specific observation. No global getter replacement authorized
by these shared call relationships.

## R870 ball virtual dispatch and output boundary

Extended exact-DOL checks pass: Tamakoro constructor calls803300B4 at803378E8
and stores the result at actor+0x8C. Controller constructor installs805BBC30.
That vtable has shared movement8033064C at+8, jump803301E8 at+0xC,
brake80330228 at+0x10, and acceleration-axis80330230 at+0x20.
Shared movement tail-branches to803306D8; that routine loads/calls vtable+0x20
at8033070C–18 before consuming the two resulting axes.

Axis function saves output pointers r4/r5 as r30/r31 at80330278/70, then writes
f29/f26 through them at803304AC/B0 and returns via803304F8. This is a candidate
observation boundary: record original outputs before proposing any alteration.
A future narrow axis adapter could preserve shared camera/gravity processing
and separate jump/brake slots. This is architectural feasibility, not proof of
correct axes or a reason to install a patch before observing the actual ride.
Live object identity/lifetime, core/sub selector, tutorial transitions and
ray-specific behavior still require their own checks.
