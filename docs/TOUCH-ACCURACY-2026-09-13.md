# September 13 second-pass touch accuracy audit

The hardware report (pointer does not land beneath the finger, on both devices)
corresponds to an existing production coordinate-model mismatch. This pass has
not enabled a new gameplay mapping or claimed a hardware fix.

The overlay converts UIKit contact through the actual presenter rectangle in
`GalaxyPadGameOverlay.mm` (`gameplayViewport`/`updatePointer`). The renderer
publishes this rectangle divided by its backbuffer dimensions in
`GalaxyPadCoreHost.mm` (`after_present_event`). There is no hardcoded 4:3 touch
rectangle in that chain. `GalaxyPadInputDevice.cpp` then converts the normalized
screen fraction into IR direction inputs, which Dolphin `EmulatePoint` interprets
as a virtual remote rotation. Camera projection, sensor-bar offset, retail KPAD
conversion, and tracking/filtering intervene before the game places its cursor.
Normalized screen position and remote rotation are different quantities.

The existing menu model was previously checked against four independent live
coordinates. New cases in `tests/test-pointer-camera.py` quantify the production
unmodified-input path using that same neutral calibration:

| Finger (normalized viewport) | Predicted settled cursor |
|---|---|
| (0.50, 0.50) | (0.500000, 0.424760) |
| (0.25, 0.50) | (0.168191, 0.424760) |
| (0.75, 0.50) | (0.831809, 0.424760) |
| (0.02, 0.50) | (-0.146861, 0.417884) |
| (0.98, 0.50) | (1.146862, 0.417884) |

Center offset is about 35 logical pixels on a 468-high viewport. The same
normalized mismatch persists in 4:3 and 16:9; aspect changes scale the error and
cannot invert the camera projection. These are model results using the audited
menu configuration, **not fresh measurements of the user's gameplay scene**.
The model does not include temporal lag: `EmulatePoint` also accelerates toward
the target angle, and retail KPAD applies its own filtering/history.

Validation: `python3 tests/test-pointer-camera.py` passes against the checkout's
actual camera and matrix implementations under AddressSanitizer and
UndefinedBehaviorSanitizer. The existing four live fixtures still match within
0.002 logical pixels. The inverse reaches 420/441 grid targets at the default
20-degree pitch and 441/441 at 22/24 degrees, within 0.0015 normalized error.
Malformed state, missing LEDs, nonneutral pose, and unsupported menu readiness
continue to reject.

## Next experiment

The existing opt-in inverse in `GalaxyPadCoreHost.mm` is Simulator-only and
requires the 22-degree profile, exact game context observer, fresh calibration,
stable file-list/file-confirm state, and neutral orientation. Turning it on for
all gameplay would bypass these known limits; after Spin or tilt its neutral
model is invalid, and gameplay has not been shown to use the same transform.
A viewport adjustment, fixed pixel offset, or sensitivity slider would conceal
only part of the error.

Use the current read-only pointer observer in an isolated Simulator gameplay
session to capture desired touch, processed past/current cursor, calibration,
reference/acceleration horizon, pointer context, and active aspect together.
Check stationary center/quarter/edge contacts, then drag, Spin, and release in
both 4:3 and 16:9. First establish whether the existing forward model applies in
normal collection/Pull Star gameplay; extend its readiness only to contexts
proven by those captures. Preserve separate controller aim and explicit A/B,
and recheck depth-sensitive collection/shooting rather than cursor appearance
alone. No physical data, saved control layouts, or production input behavior
was changed by this audit.

## Next-candidate diagnostic bridge

The next host includes a read-only observer on both hardware and Simulator.
It attaches only after exact supported DOL size/SHA-256 verification, reads on
CPU-thread VI events, and uses the existing bounded guest readers. It samples
at most once per 120 guest fields and emits at most 96 records per session,
only with visible touch input and valid context/position/calibration snapshots.
No per-frame formatting or disk writes occur; records use the bounded async
summary writer. Temporary hash data is released before gameplay. The observer
has no module instrumentation or guest writes.

Each `touch_mapping` record includes normalized finger/contact, controller aim
visibility, both sources' tilt, held buttons, aspect setting, pointer mode,
past/current guest coordinates with validity, calibration/filter, and both
orientation horizons. Guest addresses, file paths, and identifiers are omitted.
InputMixer's diagnostic snapshot reads published states without consuming
latched button edges or running the mapper; its sanitizer regression confirms
repeated reads leave a fast A/Spin tap available to normal polling.

These snapshots are correlated observations, not proof that a particular input
revision has reached the guest. They omit between-sample taps/Spin, and a
neutral sample alone cannot prove that prior motion has settled. Compare a
stationary held finger across consecutive records before fitting coordinates;
retain the gameplay/motion transition checks above. Aspect is the session's
requested setting; verify effective guest logical width before normalizing.
The candidate logger itself passes Simulator and device CoreHost syntax checks
with the accepted frozen core/header recipes, plus input/context sanitizer
tests. Full candidate link, launch, and actual gameplay capture remain pending.
