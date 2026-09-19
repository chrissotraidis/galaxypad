# Ride controls investigation — 2026-09-19

Status: local candidate, compiled and host-tested. No claim of passing a retail
ride tutorial or completing a course on a physical device. No release published.

## Findings

The existing controller adapter already sends right-stick tilt while Left
Shoulder is held. It hides controller pointer input but does not select an
upright remote pose. Touch has a separately enabled yellow tilt stick. The old
fallback could plausibly pass the surfing tutorial; the reporter's exact failure
has not been reproduced. Discoverability and the missing Star Ball pose are
separate problems.

The local Petari reference provides specific predicates:

- `src/Game/Ride/SurfRayTutorial.cpp`: straight requires absolute acceleration X
  below 0.25 and Y below 0.45; left/right require X at or beyond -0.65/+0.65 and
  reject Y below -0.5. An upright pose is therefore inappropriate for surfing.
- `src/Game/Ride/TamakoroTutorial.cpp`: the remote must be within 30 degrees of
  acceleration (0, -1, 0).
- `src/Game/Ride/SphereAccelSensorController.cpp`: the ball movement sensor uses
  a 10-degree pitch center, 5-degree margin and 25-degree movement range. A is
  used for jumping. Neutral tilt does not erase physical momentum.
- `src/Game/Ride/SurfRay.cpp`: A accelerates; Wii shake triggers a jump. GalaxyPad
  already supplies shake through Spin. A separate arbitrary B jump would not
  preserve these semantics.

Nintendo's [original manual](https://m1.nintendo.net/docvc/RVL/USA/RMGE/RMGE_E.pdf)
also distinguishes upright ball control from ray steering.

The reported four galaxies are not an exhaustive scope: **Melty Molten — Through
the Meteor Storm** also contains a Star Ball section. See the
[mission description](https://www.mariowiki.com/Melty_Molten_Galaxy). This is an
additional reason not to switch input based on a four-galaxy name list.

## Candidate behavior

Controls → Stick Mode (Touch / Controller):

| Mode | Main stick | Remote pose | Actions |
| --- | --- | --- | --- |
| Normal | Nunchuk movement | Standard | Existing mappings |
| Ray Surfing | Horizontal tilt, up to 60 degrees | Standard | Hold A to accelerate; Spin to jump |
| Star Ball | Two-axis tilt, 25-degree range | Upright, 10-degree resting pitch | A to jump |

The mode is shared by physical-controller left-stick and touch movement input.
The optional yellow stick and Left Shoulder + right-stick route use the selected
pose too. Pointer input is hidden during ride modes so aiming cannot add unwanted
pitch to the remote. The existing remappable buttons and shoulder duplicates
remain available. Mode changes clear held input and reset controller readiness.
Mode selection lasts for the app session; the user must return to Normal for
walking and pointer menus. This deliberately does not infer a ride from the galaxy.

The common mixer applies the pose; `Hotkeys/Upright Hold` drives Dolphin's
existing upright orientation modifier. The tilt angle is explicitly 85 degrees
in the profile so the mixer can express the desired angular range. No private
game-code patch or replacement asset is involved.

## Verification and remaining acceptance

Passed:

- ASan/UBSan mobile input tests: mode changes, source routing, button preservation,
  cleared input, upright state and restoration to normal movement.
- Settled gravity model checks against both surfing turn predicates and the ball
  upright predicate/neutral pitch. These are mathematical checks, not guest execution.
- Existing controller and touch-stick routing tests.
- iOS host compile check and UIKit regression-host build.
- Full Simulator app compile/link, including the input device and main UI wiring.

The full UIKit regression host was built but not run. A new headless Simulator
check did execute the real gyro/ride menu actions, selected-state persistence,
recenter callback and return to Normal. It leaves other apps in the foreground.
No physical app, save or game data was replaced.

Before release, verify both Surfing 101 tilt directions, Rolling in the Clouds'
upright prompt, forward/back/left/right ball steering, jump, releasing the stick,
death/retry, pause/resume, controller reconnect and returning to Normal. Complete
Loopdeeloop, Loopdeeswoop, Rolling Green, Rolling Gizmo and Melty Molten's mixed
walking/ball mission with both touch and a controller. Tune response only after
those measurements; mathematical pose checks do not prove camera-relative feel.

## Gyro and automatic switching

Gyro **cursor aiming** is now implemented separately: see [Gyro Cursor](GYRO-CURSOR.md).
Gyro **ride tilt** remains unimplemented. It would need a calibrated neutral pose
and the separate ray/ball transforms, rather than reusing pointer angular rates.
Keep sticks as the fallback.
Automatic switching should observe actual ride/tutorial activation and exit,
including death and scene changes, rather than an entire galaxy's name. The
manual modes provide a fallback while that runtime boundary is investigated.
