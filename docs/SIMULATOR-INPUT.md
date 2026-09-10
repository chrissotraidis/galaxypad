# Simulator diagnostic input

Opt-in host automation, not UIKit touch or physical-controller acceptance.
The physical-device host excludes this bridge. Normal Simulator launches also
leave it disabled. No guest patch, executable code generation or imported code.

Add `-GalaxyPadDevInputFile /absolute/path/to/input.json` to the existing
Simulator launch. This reserves the Controller mixer source; real controllers
are suppressed in this explicit diagnostic mode. Touch remains separate and
retains pointer priority. Relaunch without the argument to test a real controller.

With the title visible, from the repository root:

```sh
python3 scripts/simulator-input.py generated/ios-dev-input.json '{"buttons":3}' --seconds 1
```

Logical button bits: A=1, B=2, C=4, Z=8, Plus=16, Minus=32, Spin=64,
Up=128, Down=256, Left=512, Right=1024, One=2048, Two=4096. HOME is excluded.
Full snapshots may also contain `moveX`, `moveY`, `tiltX`, `tiltY` in [-1,1],
and `pointerX`, `pointerY` in [0,1] relative to the gameplay viewport (top-left
origin), plus `pointerVisible`. Missing controls are neutral, not retained.
Use `--aim-first 1` to settle IR with buttons released before issuing A. R542
file selection required this; simultaneous appearance+A did not select the file.
This is an observed sequence dependency, not yet an exact latency diagnosis.

The writer atomically replaces JSON and refreshes a half-second lease while
running, then publishes neutral even on interruption. Host polls on its existing
10Hz UI timer. A killed writer therefore cannot leave a permanent hold. Menu,
lifecycle and host input resets invalidate earlier commands; paused/idle input
cannot be replayed on resume. A new command must be issued after resuming.
Malformed, oversized, expired, future-dated or out-of-range input is neutral.
This timing is appropriate for held actions, not frame-exact timing acceptance.

Regression: `bash tests/test-simulator-input.sh` (Foundation + sanitizers).
