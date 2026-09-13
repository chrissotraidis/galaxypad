# Neutral gameplay pointer experiment

The September 13 interim Simulator host7 Observatory captures show the existing
neutral camera model applies to mode25 as well as the separately audited menu.
At a 20-degree total pitch, 25-degree total yaw, and sensor height .1, actual
Dolphin Camera/Matrix projection plus retail conversion predicts these points:

| Sample | Touch | Observed guest | Modeled guest after clipping | Maximum error |
|---|---|---|---|---|
|35|.25,.49817|141.170,192.679|139.934708,192.678619|1.235292px|
|61|.75,.49817|690.957,192.679|692.065308,192.678619|1.108308px|
|77|.02326,.49817|0,189.589|0,189.571793|.017207px|
|93|.5,.74011|414.789,310.054|416,310.079193|1.211px|
|96|.31347,.57129|212.925,228.120|211.028427,228.101212|1.896573px|

Coordinates use 832×456 guest units. All samples have calibration center(0,-.2),
scale2.272727, radius.03, sensitivity.5, filter0, reference(1,0), acceleration(0,-1).
No controller aim, held buttons or tilt were present in those samples. The edge
has direction(.999901,-.014083), reflecting projected LED geometry. It is not
evidence of nonneutral motion. The raw edge model X=-118.469925 is clipped by
gameplay to zero. Quarter/center X continues to settle slowly; the comparison
tolerance is 2px, not the .002px tolerance of fully settled menu fixtures.

Source receipt: `generated/runtime/hardware-pass2-20260913/sim7-smoke/runtime-touch-samples.log`.
The logger hit its 96-record cap at the manually calculated inverse-position
sample. These observations do not validate continuous correction, Spin recovery,
drag feel, 4:3 conversion, depth-sensitive gameplay, or either physical device.

`neutral-gameplay-probe.py X Y [PITCH]` compiles actual camera/matrix code with
address/undefined sanitizers, prints forward guest coordinates, and produces a
bounded inverse input. `--fixtures` compares the recorded samples. Existing
`tests/test-pointer-camera.py` covers the 441-point inverse grid: default pitch20
solves420/441, while the lowest row is unreachable and rejects. No pitch change
is included in this experiment.

`make-corehost-overlay.py` creates a CoreHost copy and Clang VFS overlay in
`generated/experiments/pointer-gameplay-pass2-20260913`. Build with that overlay
and repository root include path. Enable only in Simulator using
`GalaxyPadDevNeutralGameplayTouch=true` and `GalaxyPadDevPointerPitch22=false`.
The canonical CoreHost is not modified by the generator.

The experiment observes exact supported DOL/calibration/context25 on the CPU
each VI. It waits180 uninterrupted neutral fields, resets on Spin (including
consumed latched taps), tilt, controller aim, context/calibration changes, missing
or stale observation, discontinuity, and lifecycle pause. Conversion snapshots
expire after100ms. It caches the inverse for an unchanged touch; unsupported
states and unreachable targets preserve original touch input and all buttons.
Switching to baseline during Spin/cooldown can move the cursor and requires
explicit runtime evaluation. The cooldown is a conservative experiment setting,
not measured proof of physical motion settling. No new production mapping is
enabled, and the overlay must pass compile and runtime tests before promotion.

The isolated CoreHost overlay compiled, linked against final7 objects/core, and
ad-hoc signed successfully after the performance benchmark released the host.
`build-simulator-experiment.py` reproduces this build and records source hashes
and exact commands in the generated `recipe.json`. Host SHA-256 is
`e306033c226122ef137ba922d9db7df044b1aa56dd5355150eec7b575bc6d3ca`;
preserved core SHA-256 is
`457f4dba560eab8aeb899406340852244ef8bb1554b987e2bf1f26883ed94cb8`.
All five stored live comparisons passed the sanitizer probe.

`test-neutral-gameplay.cpp` passed address/undefined sanitizers for neutral
settling, latched Spin, stale/future/repeated observations, context, profile,
calibration and horizon rejection. This is a readiness contract test; camera
behavior and gameplay acceptance remain separate.

## Candidate1 corrected runtime and Spin failure

The owning session installed candidate1 and exercised actual Simulator touch in
the Observatory. Frozen observations are in
`generated/experiments/pointer-gameplay-pass2-20260913/runtime-candidate1-before-candidate2.log`.
Against desired touch×(832,456), the corrected center was (416,227.089), error
(0,-.07652)px across nine identical records. Quarter sample33 was
(208.890,226.769), error(+.890,-.39652)px. Edge sample96 was (20.046,227.036),
error(+.69368,-.12952)px. The original center Y was192.679. This validates the
neutral coordinate correction in the observed Simulator context.

Spin exposed a concrete defect in candidate1's fallback policy. Eligibility
changed to false at field9221 and true at9408,187 fields/4.024 wall seconds later.
With the finger unchanged at(.25,.49817), sample34 reported(137.003,190.717):
error(-70.997,-36.44852)px, about79.81px Euclidean distance. These sparse records
provide a lower bound on the transient maximum, not a frame-by-frame peak. After
reacquisition sample36 was within2.304px per axis; sample63 reached
(-1,-.75852)px error. The baseline fallback deliberately created an extra Point
target excursion during Spin. Candidate1 is not suitable for production.

## Candidate2 retained neutral Point base

`WiimoteEmu.cpp`792–802 composes separate Shake translation, Tilt rotation, Point
rotation, Swing rotation and positional state. `Dynamics.cpp`224 onward drives
Point independently from cursor input. This supports testing a stable calibrated
Point target through additive Spin, without claiming the neutral model predicts
or cancels the instantaneous shaking cursor.

`make-corehost-overlay.py --retain-neutral-base` and
`build-simulator-experiment.py --retain-neutral-base` create the separate
`generated/experiments/pointer-gameplay-pass2-v2-20260913` candidate. It establishes
the base from180 fresh neutral fields, then retains it through Spin and finite
residual horizon changes. Explicit tilt, controller aim, context, calibration,
profile, stale/invalid observations and lifecycle changes still invalidate it.
The candidate2 sanitizer tests verify those boundaries and reject establishing
a base from a moving pose. Its isolated CoreHost compiled, linked and signed;
candidate1 binaries and receipts remain intact.

Candidate2 was then installed and exercised through actual quarter-position
Spin, a drag to the opposite quarter, and another Spin. Eligibility remained
continuously true after its initial mode25 activation at field2866.

| Candidate2 window | Observed guest | Error from desired touch, pixels | Euclidean error |
|---|---|---|---|
|Before late Spin, sample76|207.161,226.409|-.839,-.75652|1.129709|
|Late Spin, sample77|205.789,225.375|-2.211,-1.79052|2.845080|
|Recovery, sample85|206.935,226.163|-1.065,-1.00252|1.462625|
|Opposite quarter drag/Spin, sample86|622.187,225.749|-1.813,-1.41652|2.300760|
|Opposite quarter settled, samples88–96|624.187,226.765|+.187,-.40052|.442024|

The largest error among all96 candidate2 records was2.903132px at sample24;
the late Spin window77–85 peaked at2.845080px. Candidate1's observed79.806445px
fallback excursion did not recur in these samples. The120-field sampling interval
does not capture peak frame-by-frame shake or drag latency, so this comparison
is evidence of improved target continuity and reacquisition, not a transient
accuracy guarantee. The final nine identical right-quarter observations provide
stronger settled-coordinate evidence than a single screenshot.

Immutable candidate2 observations and calculated per-sample errors are
`generated/experiments/pointer-gameplay-pass2-v2-20260913/runtime-candidate2-spin-drag-96.log`
and `runtime-candidate2-errors.json`. Log SHA-256:
`2b3f8ab1ef36c1be35018697a82bf517b715bf95e65bee9d5189ce7749b7b22c`.
Candidate2 host SHA-256:
`9d1998d53275d5491bf4b71fc4a0994059531b7da5a057047c21e3f6a8fd25ee`.

Candidate2 still needs lower-edge/reachability, aspect, sustained tilt,
controller handoff and depth-sensitive gameplay checks, plus higher-frequency
motion/drag observations. The pitch20 inverse still rejects the lowest grid row.
Hardware touch accuracy and responsiveness remain unverified, so neither
candidate is a complete physical-device pointer fix.
