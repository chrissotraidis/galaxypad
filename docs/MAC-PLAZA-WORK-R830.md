# R830: measured macOS plaza baseline, with explicit tail-overflow evidence

Previous turn was progress: private profile/probe prepared and old platform/QoS
results reconciled. This turn ran two sequential macOS attempts using the same
R730 runner/c0021b9f module, LC byte/pair0, fallback JIT disabled, no native-THP
mod, Metal1x/Cubeb. No Simulator booted and no profiler ran.

## Initial capture rejected

PID58953/session48202, profile plaza-platform-r829: screenshots verified neutral
starting plaza before/after process capture55523. Cmd-Q exits0. Recorder16384
capacity filled and dropped1888tail samples. Last retained VI564806294581083 is
11.264seconds BEFORE the work window ends564817558348875. This measurement is
incomplete and remains rejected, including with the new prefix-aware option.

## Changed retry and accepted window

Copied Config/Wii/config.ini into new plaza-platform-r830; independent Pipe and
private BackgroundInput. Automated story advance uses10bounded1second A pulses
separated by3seconds, then neutral input and screenshot verification. No movement
commands. Original title/play fixtures select the same copied Mario file.
PID59437/session50769, input52011 and capture6354 all finish; native Cmd-Q exits0.
Pre/post CUA screenshots show Mario at starting plaza, life3, lives4, coins0,
StarBits0 and lower-right visible pointer; unchanged position, ordinary animation.
Images are retained in the conversation tool record, not new local PNG files.

Profile generated/runtime/plaza-platform-r830 contains runtime.log, process-work.json,
vi.csv, work-summary.json and timing-summary.json. The30.008625second snapshot
window contains exactly1799VI under both query-boundary interpretations:

| Metric | Measured result |
| --- | ---: |
| VI rate |59.949431/s|
| CPU-thread mean / p95 / p99 |14.226413 /15.252125 /15.691709ms|
| Wall mean / p99 |16.683333 /16.963625ms|
| EFB elapsed mean |0.895521ms|
| Throttle elapsed mean |2.202441ms|
| Idle wait elapsed mean |0.268770ms|
| Whole-process instructions/VI |212,964,174.139|
| Whole-process cycles/VI |63,291,906.827|

No invalid CPU or counter-reset intervals. Elapsed counters overlap; do not add
them as exclusive CPU states. Process work includes graphics/audio/host, not
guest-thread-only instructions. VI is not display scanout, and this stationary
window does not establish moving gameplay, audio continuity or full acceptance.

## Why the retry can be used despite dropped tail samples

The retry exports dropped=865 after filling16384rows. The recorder implementation
is append-only: it retains the FIRST capacity samples, never overwrites them,
and only increments dropped afterward. This contract was inspected and its
capacity/drop tests rerun at R829. Last retained VI565211737385833 exceeds the
final process-query bound565205632604833 by6.104781seconds. Thus the complete
measurement is retained; the865missing samples occurred later, outside it.

This explicitly refines R829's overly broad reject-any-overflow preflight. No
CSV was trimmed or header changed. summarize-process-work.py still rejects any
drops by default. New --verified-prefix-capacity16384 requires caller-verified
append-only producer semantics, exact retained capacity and all original complete
window/monotonic/identity guards. It records dropped count and tail margin in the
result. This cannot authorize arbitrary recorders that drop internally. Focused
tests reject unknown capacity, mismatched capacity and uncovered windows; original
R829 capture still fails coverage. The existing VI timing summarizer likewise
requires complete requested-window coverage.

## Boundaries and next action

Both copies of GameData remain99d432d517b92b19da0c403819b91288b10c7063c3ce61f5000347ef823ab64f.
Whole-run retry audio has5underruns and6backlog drops across startup/story/plaza;
these are not fixed-window audio acceptance. Neither attempt is pure-native
execution: interpreter fallback remains nonzero. No normal app/module/save edit.

Next collect the matching Simulator neutral plaza with VI/process-work counters,
LC byte/pair0, native-THP preference explicitly OFF, and no competing runtime or
profiler. Reuse the faster story sequence after verified selection; match pointer
position/scene before measurement. Retain Simulator host/audio differences rather
than asserting binary parity. Do not repeat this completed macOS baseline or
reopen rejected arithmetic/QoS experiments from one FPS snapshot. No runtime or
Simulator remains; original full PRD/SunPad/audio/stability/device goal is active.
