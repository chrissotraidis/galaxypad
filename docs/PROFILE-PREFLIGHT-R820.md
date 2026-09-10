# R820: macOS CPU profiling works; ordinary raw-task sampler is unavailable

Previous turn was progress: actual Simulator capture failures were bounded and
recorded, with the game and save preserved. This turn preflighted the alternatives
on a small owned test workload before launching another game.

tests/probe-raw-thread-pc.cpp builds with C++20/O2/Wall/Wextra/Werror. Its ordinary
task_for_pid attempt against its own self-terminating child returned KERN_FAILURE
(5). Zero register reads occurred; child54501 exited0 and was reaped. Probe exit2
is the expected unavailable result, not a passing sampler test. It has no calls
to suspend/resume, target-write or privilege-changing APIs. Do not expand this
sampler or use it on GalaxyPad under the current access conditions.

The same fixture's --workload mode provides eight seconds of deterministic
integer-loop work without task access. CPU Profiler launched this macOS workload
for a requested three-second capture and completed/saved promptly. Command exit54
reflects the time-limited launched target: TOC explicitly records SIGKILL of test
PID54555 at the recording limit. This is not a clean target exit or a game crash.
Do not launch the real game under a short profiling time limit; attach instead.

TOC and cpu-profile exports both completed exit0. The checked CPU export has
9,083 main-thread samples, cycle-weight sum8,943,965,870; 9,038 samples are in the
deliberately busy work(unsigned int) function. Binary-relative PCs and their
weights are retained in pc-preflight-r820-summary.json. This proves the host
profiling/export path can provide the missing kind of evidence, not a game cost.
The capture is 6.5 MiB, not a system-wide oversized trace.

Artifacts under generated/: probe-raw-thread-pc-r820/r820b, pc-preflight-r820.trace,
pc-preflight-r820-toc.xml, pc-preflight-r820-cpu.xml and pc-preflight-r820-summary.json.
No profiler, test child, game or Simulator remains running. No installed app,
module, save, disc or access policy changed.

## Next action

Use the working macOS lane for one visually verified plaza profile. First resolve
the exact current macOS runner/module/build provenance and compare generated
source/compile policy with the Simulator baseline. Capture by attaching to the
existing runtime, not by time-limited launch that kills its target. Retain binary
hashes and load bases; aggregate per-PC weighted instruction categories across
sampled chunks. Treat differences in host/platform policy as explicit limits on
transferring findings to Simulator. This is hypothesis generation for a broadly
applicable native-code change, not macOS results masquerading as mobile acceptance.
All original PRD, SunPad UI, performance/audio, stability, gameplay/progression and
physical-device goals remain unchanged; no performance gain claimed.
