# R832: self-thread work counters available on both hosts

Previous turn: progress, complete R831 matched plaza measurement. Current step
tests counter feasibility and time units, not game performance. No game build,
app launch, guest-module change or save access.

## Interface and private scope

Apple XNU's [resource_private.h](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/resource_private.h)
declares thread_selfcounts and THSC_TIME_CPI(3)/PER_PERF_LEVEL(4). Its
[implementation](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/kern/sys_recount.c)
reads the current thread and returns instructions, cycles, user/system Mach
ticks. Perf-level array indices follow hw.perflevelN. These are SPI, not public
shipping-app APIs. Local scripts/probe-thread-work.c resolves the wrapper with
dlsym; missing wrapper or unsupported query returns2, no syscall workaround,
entitlement/policy change, task-port request or profiler attachment.

Probe does20M volatile integer iterations between counter and CPU-clock
snapshots; checks nondecreasing counters, positive work and converted CPU time
within10% of CLOCK_THREAD_CPUTIME_ID. Reports1000-query overhead and labels
perf levels from sysctl. This is a feasibility test, not a stable benchmark or
proof that the game CPU thread has the same policy or core residency.

## Executed results

| Metric | Native | Simulator standalone process |
| --- | ---: | ---: |
| Mach timebase |125/3|125/3|
| Thread-clock CPU ns |42,429,125|86,872,208|
| Converted counter CPU ns |42,431,208|86,876,792|
| Counter/clock ratio |1.000049|1.000053|
| Instructions |100,616,566|103,955,107|
| Cycles |127,202,227|154,420,274|
| Performance-level CPU ns |42,424,292|32,123,250|
| Efficiency-level CPU ns |6,167|54,751,708|
| Mean perf-level query wall ns |177|377|

Both pass. Different snapshot boundaries account for small total/per-level
differences. Simulator probe wall time713,773,584ns greatly exceeds CPU time;
it ran soon after boot under a simctl-spawned process, not UIKit/game-thread
conditions. Do NOT interpret these values as the source of R831 game slowdown,
a frequency measurement or an optimization/QoS result. No raw Mach ticks were
treated as nanoseconds. Historical process-work user/system fields are raw
values and were not used in R830/R831 reported per-VI CPU-time calculations.

## Reproduction and identity

```
xcrun clang -O2 -Wall -Wextra -Werror scripts/probe-thread-work.c -o generated/thread-work-native-r832
generated/thread-work-native-r832
xcrun clang -target arm64-apple-ios16.0-simulator -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator.sdk -O2 -Wall -Wextra -Werror scripts/probe-thread-work.c -o generated/thread-work-simulator-r832
xcrun simctl spawn DE8E956F-6B29-4FF3-AF4A-77034CE8588A "$PWD/generated/thread-work-simulator-r832"
```

Source SHA a73181d2287da610a9487b5b6d7c1a2a1570568d3a461734b6f72cd181540d18.
Native SHA09799ed5657e682dd3a8d717a3d77279023368323d47739209f28cd5e7af27e6.
Simulator SHA6e643ed23d6aad3a1c9638fd92ac8c167dc09bdb55fbecc6f443945d6f1a09d9.
Native compile/run and Simulator compile exit0. Boot27680 finishes; probe and
shutdown51817 finish0. Only one Simulator booted, now shut down. No game ran.

## Next bounded step

Add compile-time-private AND opt-in collection to the existing in-memory VI
diagnostic recorder: CPU-thread total/per-level work and Mach time, resolved
before writer start, query errors explicit, zero reads/allocation when disabled.
Do not add the SPI to ordinary release targets or per-instruction hot paths.
Use injected-counter tests for reset/missing/disabled/buffer semantics before
a private host-only build (reuse unchanged guest module). Then measure actual
neutral-plaza CPU-thread instructions/cycles/core-class time, retaining R831
whole-process and VI boundaries. This answers a new question; it does not
authorize another unchanged aggregate capture or repeat the closed QoS trial.
Full original PRD/SunPad/audio/stability/device gates remain open.
