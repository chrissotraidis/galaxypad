# R568 touch layout audit and compact auxiliary keys

2026-09-08. Scope: current iPad overlay and SunPad reference, not complete
touch-playability acceptance. Product Design audit used live Simulator capture;
SunPad's user-requested reference is `ref/sunpad/docs/readme/sunpad-delfino-plaza.jpg`
and the actual `SunPadGameOverlay.mm` layout/style implementation.

1. Before: `generated/ui-r568-before.png`. Letter-only A/B/X/Y/Z and separate
   movement/D-pad already exist. Pause keys still consume two broad stacked rows;
   1/2 retain unnecessary pill width. Code inspection also found phone auxiliary
   defaults still at the top. A guest controller-communications interruption was
   visible after the long native-menu pause; title FPS is not gameplay evidence.
2. Change: retain SunPad colors, letter faces, action cluster, editor identifiers,
   and input masks. Compact 1/2 and +/- to square hit boxes with circular styling;
   +/- share a row above the right cluster. Phone auxiliaries move to lower-center
   pairs. Saved custom layouts are deliberately not erased or migrated.
3. Verification: isolated UIKit host on the sole iPad Simulator passes default
   non-overlap and >=44pt targets, auxiliary geometry, single-letter faces, A+B
   callbacks/release, pointer independence, and editor selection/resize/persistence.
   Release app build passes and is installed. Title and scripted A+B transition
   to file select verified; accepted after image `generated/ui-r568-file.png`.
   Earlier `ui-r568-after.png` caught a transition flash and is not the final audit.
   File screen shows27.3FPS instantaneously; performance is still inadequate.
   Physical multitouch, thumb reach,
   phone rendering, large custom scales, and full accessibility are not proven.

Research: Nintendo's original Wii manual, controls pp.3-4 and actions pp.8-9:
https://m1.nintendo.net/docvc/RVL/USA/RMGE/RMGE_E.pdf
Movement is Nunchuk stick; A jumps/uses, Z crouches, C resets camera; pointing
and B shooting are separate, shaking provides spin. Thus a SunPad/GameCube-style
visual layout must not silently reuse Sunshine's game input semantics. Auxiliary
pause keys should not compete visually with these primary interactions. This
manual is evidence for Wii behavior, not a claim of native GameCube support.

Next: actual gameplay combinations
and pointer/latency validation. No performance gain is attributed to this UI edit.
