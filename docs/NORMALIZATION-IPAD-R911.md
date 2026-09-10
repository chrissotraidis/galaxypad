# R911 — private candidate reaches actual iPad runtime

Previous status-answer turn was no progress, followed here by live runtime,
visible file selection/story navigation, counter observation and save verification.
Root289a87a1499c3d0da23c21c472fd16525742208a; unrelated dirty work preserved.

R910 build34260 exited0. Candidate module SHA
d966417b8ae1f2b5b82b23f39fed2df38fbd747056ee9224f58038f6fc9eb867,
IOSSIMULATOR min16/sdk26.5, signature verified. Normal baseline remains
3acdcddcd47812c2e2a67b8cec0cf06c17009cf1ad7f2e9dc9abd83158a1bac0.

Evidence/backups: generated/runtime/normalization-ipad-r911. Original installed
app is preserved in original.app (runner85ffc100); GameData.before.bin has SHA
99d432d517b92b19da0c403819b91288b10c7063c3ce61f5000347ef823ab64f.
Private measurement host is existing thread-work-ipad-r890/candidate/GalaxyPad.app
(runnerbdd8633e), not latest product UI. Only iPad
DE8E956F-6B29-4FF3-AF4A-77034CE8588A is booted. Runtime PID19845,
console98501; runtime.log records exact private module load. VI/work outputs are
vi.csv/work.csv on clean stop. Native THP on, QoS experiment off; input.json is
leased. No normal module replacement or runtime JIT introduced.

CUA verified landscape file selection, existing zero-star Mario file, then
opening story. File slot(.37,.67), Play(.73,.88). advance-story.py in evidence
directory adapts existing R890 input sender to this run; sequence82530 exited0.
New data container1F8C2F37-C957-45E7-A023-DF60102B1FBF save independently rehashed
to99d432d5 after load. No save write requested.

Debugger attachments79848/35008 both exited0 and detached. Module load base
0x12dd04000; counters at0x134910018/20. First read fast43,442,348,
rejected18,218,166 (~70.45% accepted), cumulative mixed startup/file/story.
No timing window overlaps debugger attachment. This proves the candidate runs,
not its gameplay hit rate, frame-rate benefit or correctness acceptance.

Next: reach stationary playable plaza; sample counter deltas outside timing,
then same-host/module-only matched gameplay windows. Do not compare title frame
events or historical different scenes as performance gain. No full regression
suite rerun during live measurement. Full PRD remains open.

## Final capture and cleanup

Stationary starting plaza visibly verified before/after process-work99973,
which exited0 (30-second window606958088005875–606988100040625). No movement;
life3/lives4/coins0/bits0. Retained plaza-before.png/plaza-after.png.
Thermal84974 exited0, reported fair; unrelated Logitech updater/WindowServer
load observed. Debugger67526 before capture: fast44,623,043/rejected19,032,207.
Debugger24012 after capture:45,648,318/19,647,217. Both detached. Delta
1,025,275 accepts/615,010 rejections (~62.5% acceptance) spans more than the
timed window, but stays in the starting plaza. Not a performance gain.

Important failure: SIGTERM19845 ended console98501 with exit0 but produced no
vi.csv or work.csv. Therefore process snapshots cannot be normalized or used as
valid gameplay performance evidence. Correct future method is native menu Stop,
verify recorder export, then exit. Do not infer clean application shutdown from
console exit0. No crash cause claim. No rerun solely to repeat this counter result.

Original85ffc100 app restored via install95059 exit0. Save in new data container
8F624B39-6FC1-4998-A159-F5D33ACD41B9 rehashed unchanged99d432d5. iPad shutdown
71107 requested; verify terminal and boot inventory. Backups retained.
Current next priority: physical-iPad first test preparation, with stable device
module rather than promoting this unproven optimization.
