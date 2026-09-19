# Gyro cursor — 2026-09-19 candidate

Status: implemented locally; device and Simulator hosts compile/link. Headless
Simulator tests execute real UIKit menu actions and production sensor-adapter
logic with synthetic samples. No physical sensor or retail-game acceptance yet.
No device install, IPA publication or save modification performed.

## Usage

Open **Controls → Gyro Cursor**, then choose **This Device** or **Controller**.
The setting defaults to Off and persists alongside sensitivity and inversion.
This Device uses the iPhone/iPad, including when a controller is connected.
Controller uses the same controller that owns gameplay input; it never takes
motion from an unrelated second controller.

Move to aim the Star Pointer. The right stick can adjust the same cursor. A held
touch takes aim ownership and anchors the gyro cursor, so releasing the finger
resumes at that location. A/B and movement remain independent input paths.
Use **Recenter Gyro Cursor** or click the right stick to center the cursor while
holding the device/controller comfortably. Recenter happens once per stick-click
press. The Response menu offers 0.5× / 1× / 1.5× and vertical inversion.

This is relative gyro aiming, not an absolute sensor-bar pointer. Small stationary
rates are suppressed; slow accumulated drift can still require recentering.
Landscape-left and landscape-right transform device rotation into screen axes.
Changing screen orientation resets aim to center. Controller yaw uses rotation
about gravity's up direction when the profile supplies gravity, with local yaw
as the fallback; pitch uses the controller's local X axis.

## Input and lifecycle behavior

- Core Motion device samples are polled at 60 Hz using fused device-motion
  rotation rates and sensor timestamps. Repeated polling of one sample does not
  integrate it twice. A gap longer than 100 ms is not integrated as movement.
- Controller motion uses `GCMotion.hasRotationRate` and motion callbacks. Only
  sensors activated by this adapter are deactivated by it. Generation checks
  discard queued callbacks from a previous controller connection/reset.
- Samples older than 250 ms, invalid numbers and future timestamps cannot add
  angular motion. Once gyro owns aim, a sensor gap freezes its cursor rather than
  reviving the controller's old independent pointer; stick adjustment continues.
- With no usable motion sample, the original touch/right-stick path remains
  available. The menu reports unavailable motion or waiting for samples.
- Native menus, pause, backgrounding and stop release the motion sources and
  clear pending input. Resuming starts from center without replaying old motion.
- Ray Surfing and Star Ball modes, and the legacy Left Shoulder tilt chord,
  suspend gyro cursor input. Wii pointer motion
  contributes to the emulated remote pose, so running both simultaneously would
  contaminate the ride tilt. Gyro cursor aiming does not implement gyro ride tilt.
- The mixer accepts gyro coordinates only, never gyro buttons/movement. Held
  touch has priority, followed by gyro and the original controller/touch fallback.

Sources: Apple's [device motion polling API](https://developer.apple.com/documentation/coremotion/cmmotionmanager/startdevicemotionupdates(using:)),
[controller motion profile](https://developer.apple.com/documentation/gamecontroller/gcmotion),
and [sensor activation contract](https://developer.apple.com/documentation/gamecontroller/gcmotion/sensorsactive).
The installed iPhoneOS SDK headers were checked for capability and lifetime rules.

## Verification

Passed:

- `tests/test-gyro-aim.sh`: rotation signs/orientations, independent sample cadence,
  repeated/stale/invalid samples, recenter, inversion, stick integration and bounds
  under ASan/UBSan.
- `tests/test-gyro-adapter.sh BOOTED_SIMULATOR_UUID`: production adapter with fake
  Core Motion/controller sources, touch handoff, once-per-press recenter, stale
  sample hold, pause, unsupported device sensors, old callback rejection and
  sensor activation ownership. This is a headless process, not a sensor test.
- `tests/test-gyro-menu.sh BOOTED_SIMULATOR_UUID`: dispatches actual UIActions via
  UIButton; verifies source selection, checkmarks, persisted response settings,
  recenter callback, status subtitle, ride selection and return to Normal.
- Existing input mixer, controller, settings, pause-event and stick-route tests.
- iOS host compile check; full device and Simulator app compile/link; full UIKit
  test-host build. The complete visual UIKit suite was not launched.

Before release: physically test iPhone and iPad in both landscape orientations,
stationary drift, slow/fast aiming, screen edges, sensitivity and inversion,
A-hold Pull Stars, B shooting, touch release, stick adjustment/recenter, app
pause/background/resume and controller disconnect/reconnect. Test each advertised
motion-capable controller model and a controller without motion support. Verify
ride-mode suspension and return to Normal in the retail game. These are remaining
acceptance checks, not claims established by synthetic samples or compilation.
