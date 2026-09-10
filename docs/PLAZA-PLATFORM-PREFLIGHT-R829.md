# R829: platform reconciliation and ready plaza measurement profile

Previous turn made progress: compact normalization was closed by a qualified
cost screen. This turn audits the retained platform evidence before repeating
old experiments. No new game or Simulator launched.

## What existing evidence already answers

R639/R640 original work-summary and timing JSON files remain available and agree
with PERF.md. Native file selection59.823VI/s, CPU11.101ms/VI, EFBelapsed0.318ms;
Simulator53.014VI/s, CPU15.208ms/VI, EFBelapsed2.210ms. Whole-process instruction
counts are192.777M/VI native versus178.935M/VI Simulator. Those counters include
different host backends and exclude external SimMetalHost work: lower process
work does not prove lower guest work or identify clock/core effects.

R641/R642 CPU-priority A/B is already closed: CPU15.719 versus15.779ms/VI,
roughly3% VI-rate variation, no material gain. Do not repeat QoS tuning.
R638 already verified both module compiler drivers target apple-m1 and refuted
a fixed35FPS Simulator ceiling. Do not rediscover those as new explanations.

Current copied/native and Simulator configs both have CPUThread=True, CPUCore6,
Metal, internal resolution1, DSPThread=True, idlePC804ab358 and shader mode2.
Native uses Cubeb; Simulator uses the SunPad audio path. Current config files are
not proof of every historical launch override. R821 additionally forced LC byte/
pair1; earlier R639/R640 comparison used0. Keep those different runs distinct.
Simulator R819 loads the optional native-THP mod and invalidates its decoder
chunk; macOS R821 does not. Neither804520A0 nor804530A0 appears among R822's
sampled generated-chunk symbols, so this is not evidence that decoder arithmetic
dominates the neutral plaza. Match that option rather than guessing causality.

R813's27.064frame-events/s window and R822's macOS title FPS/whole-run counters
cannot form a matched plaza CPU-work comparison. R813 has process ps/VM snapshots
and after-frame-event windows, not bracketed VI/work counts. R822 records a CPU
profile and shutdown totals spanning title/story/plaza/profiling. No exact
cross-platform multiplier follows. Current devicectl refresh: no devices found.

## Prepared next run — do not repeat preflight

Private profile: generated/runtime/plaza-platform-r829. Copied only R821
Config/Wii/config.ini; no emulator states, profiler data or caches copied.
Independent Pipe configured; BackgroundInput enabled only in this private copy.
GameData SHA99d432d517b92b19da0c403819b91288b10c7063c3ce61f5000347ef823ab64f
matches the protected source. Normal profiles/saves unchanged.

Reverified R730 runner SHA871f4f8726cf1e12c56022a61dfbd013cbfa6614ce68ee6873982e869a9f4faf;
it contains GALAXYPAD_VI_TIMING. Simulator baseline module remains
3acdcddcd47812c2e2a67b8cec0cf06c17009cf1ad7f2e9dc9abd83158a1bac0.
Use macOS module c0021b9f at the same R821 explicit path. No new module build.

Built generated/process-work-snapshot-r829 with Wall/Wextra/Werror; bounded
self-test passes. Process-work snapshot/identity/bracket tests, VI summary and
buffer/recorder tests pass. Existing capture-process-work.py has10s warm-up and
30s measurement, no focus mutation. Summarizer requires exact PID/start identity,
bracketed VI coverage and zero recorder drops; VI is not physical presentation.

Next launch the private macOS runner with explicit:

- GALAXYPAD_VI_TIMING pointing to this profile's new vi.csv;
- STATICRECOMP_NO_FALLBACK_JIT=1;
- GALAXYPAD_LC_BYTE_FAST=0 and GALAXYPAD_LC_PAIR_FAST=0;
- no native decoder mod, direct-call binding or other profiler;
- same explicit game/module, Metal/Cubeb and profile as R821, with this new user-dir.

Use R821 title/play/advance fixtures with screenshot verification to reach neutral
starting plaza, life3/coins0/StarBits0 and matching pointer position. The final
story advance needs1second A pulses, not repeated ineffective short taps.
Capture using current probe after visible scene verification, then inspect scene
and clean native Quit. Recorder capacity16384VI is only about273seconds at60Hz;
complete navigation/capture promptly and reject overflow, never trim it away.

Only after macOS is stopped, collect the matching Simulator plaza with LC paths
and native-THP preference explicitly off, same VI/work counters and no profiler.
Retain input, host-version and audio/backend boundaries. Compare CPU-thread time/
VI, whole-process instructions/cycles per VI, and elapsed EFB/wait distributions
without summing overlapping counters. This compares existing baselines; it does
not establish a new optimization, audio acceptance or physical-device performance.

No process is currently live; next action is the prepared macOS launch. Full
original PRD/SunPad/gameplay/audio/stability/device goal remains active.
