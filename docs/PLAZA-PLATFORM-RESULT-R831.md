# R831: matched neutral-plaza platform cost

R830 completed the native baseline. R831 ran only the existing R791 iPad
Simulator app, with the existing 3acdcddd module, LC byte/pair0, fallback JIT
disabled, native THP OFF and CPU QoS experiment OFF. No rebuild or profiler.
Original full PRD and performance-first priorities remain active.

## Capture and validity

Artifacts: `generated/runtime/plaza-simulator-r831/`: runtime.log,
process-work.json, vi.csv, input-sequence.py and GameData.before.bin.
App PID60333, console session94462; Simulator
DE8E956F-6B29-4FF3-AF4A-77034CE8588A. Launch command is retained verbatim in
process-work.json. Installed app/module identities and configuration boundaries
are recorded in PLAZA-PLATFORM-PREFLIGHT-R829.md and the preceding handoff.

CUA verified landscape and neutral starting plaza before/after measurement:
Mario at starting position, life3, lives4, coins0, StarBits0. No movement input.
A leased lower-right pointer snapshot was held for55s around the10s warm-up plus
30s capture, then released. The post-capture screenshot was taken after that
lease expired, so it verifies scene/HUD, not pointer persistence throughout the
window. Screenshots are in the conversation tool record. This is not touch UX
or continuous gameplay acceptance.

Capture first-before565914993912000, last-after565945004832625. Both uncertainty
bounds give921VI in30.010898646s. Recorder retains16384 initial rows and reports
2790 later drops. The retained tail exceeds the complete window by67.780889s;
the R830 append-only prefix contract applies. No trace was trimmed or altered.
All920 complete timing intervals have valid CPU clocks and no counter resets.

Reproduce:

```
python3 scripts/summarize-process-work.py generated/runtime/plaza-simulator-r831/process-work.json generated/runtime/plaza-simulator-r831/vi.csv --verified-prefix-capacity 16384
python3 scripts/summarize-vi-timing.py generated/runtime/plaza-simulator-r831/vi.csv --start-ns 565914993912000 --end-ns 565945004832625
```

## Comparison

| Metric | Native R830 | Simulator R831 |
| --- | ---: | ---: |
| VI/s |59.949431|30.688851|
| CPU-thread mean ms/VI |14.226413|29.490213|
| CPU-thread p99 ms |15.691709|38.325542|
| Wall mean ms/VI |16.683333|32.586095|
| EFB elapsed mean ms/VI |0.895521|2.209620|
| Throttle elapsed mean ms/VI |2.202441|0.001544|
| Idle-wait elapsed mean ms/VI |0.268770|0.472169|
| Whole-process instructions/VI |212,964,174|218,987,996|
| Whole-process cycles/VI |63,291,907|62,505,122|

Simulator instruction work is only about2.83% higher, while CPU-thread duration
is about2.07x. Whole-process cycles/VI are about1.24% lower. Disc/gather waits
are negligible; every complete Simulator CPU interval exceeds the60Hz budget.
This argues against doubled total instruction work or deliberate throttling as
the explanation. It does NOT establish a clock-frequency ratio: counters are
whole-process, CPU time is one thread, host/audio versions differ, and external
SimMetalHost work is excluded. No measured core-residency/thermal/frequency
evidence exists for this window. Elapsed stage counters overlap, not an additive
cost breakdown. VI is not physical presentation; this is not an optimization.

## Disposition and next experiment

Do not repeat either completed plaza capture, reopen the failed QoS experiment,
or select another tiny arithmetic helper from these aggregate results. The next
question is whether the CPU thread itself executes materially different work,
or takes longer for similar work under this host environment. First establish
a bounded, opt-in, self-thread instruction/cycle counter's availability and
clock units with a tiny standalone probe, separately on native and Simulator;
do not rebuild the full game merely to discover that collection is unavailable.
Do not infer guest-thread work from task totals or bypass denied profiler access.
If unavailable, retain that uncertainty and choose a source-matched host-cost
comparison rather than another unchanged attach attempt. Historical P-core and
thermal observations in PERF.md are not evidence for this specific window.

Menu Stop Game completed with runtime exit failed=0 and VI export_result=1.
The stopped app was then terminated and the sole Simulator shut down. Protected
GameData is unchanged:99d432d517b92b19da0c403819b91288b10c7063c3ce61f5000347ef823ab64f.
No normal module/preferences were promoted. Audio underruns persist in the
whole-run log; no fixed-window audio or physical-device acceptance is claimed.
