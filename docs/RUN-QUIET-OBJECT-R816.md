# R816: full actual-policy quiet-loop objects

Previous turn was progress: R815 added an extracted complete-burst differential
and resolved optional-configuration write sites. This turn moves that exact
specialization into a private copy of the complete actual Run translation unit.

`scripts/build-quiet-run-probe.py --output generated/quiet-run-r816` completed
successfully. It uses the current ios-simulator-core compile_commands entry:
Apple c++, -O3 -DNDEBUG, C++23, ARM64, Simulator SDK 26.5/minimum 16,
-march=armv8-a+crc, -fno-strict-aliasing, -fno-exceptions, original visibility
and remaining warning/include flags. It does not substitute game-module
ThinLTO/PGO policy for the host policy; this host entry has neither option.

Both complete Run objects compile. Candidate selection occurs once per native
burst after SyncIn, with the exact existing inner loop instantiated for quiet
or general operation. Entry checks trace, lockstep, sampling, REL presence and
direct binding. Dynamic eligibility, cycles, timebase, exceptions and hook checks
are retained. No reference runtime source was edited.

Object __text grows from 6,672 to 7,216 bytes (+544). Run starts at object offset
0x188 in both; the following symbol starts at 0xf00 control versus 0x1120
candidate. Thus the growth is in Run, and the emitted variants are inlined into
Run rather than separate outlined template functions. This is code-size evidence,
not executed instruction counts or CPU-time savings. Object relocations are not
resolved executable call destinations.

`tests/test-run-quiet-specialization.py --candidate-source
generated/quiet-run-r816/candidate.cpp` now checks the entire candidate source,
including the entry gate, against the exact tested transformation. All 5,376
stub-service differential cases pass in ASan/UBSan and -O2. The test does not
execute the actual compiled Dolphin object; keep this distinction explicit.

Artifacts: generated/quiet-run-r816/report.json contains full compiler commands,
source/object SHA256s and unchanged source/cached-object/compile-database hashes.
control.asm, candidate.asm and *.size.txt preserve machine-code evidence.
No link, app install, Simulator, gameplay run or measured speed benefit occurred.
No normal app/module/save/disc changes. The full original goal remains active.

## Exact next action

Complete the runtime cost screen, which is still pending. Use separate-TU opaque
callback/configuration boundaries and the same host optimization policy (document
any target adaptation if run as a macOS process), short and long bursts, varied
guest work, and hook/exception exits. Include entry selection and retain the
exact candidate identity. Do not interpret this object build or the -O2 stub
correctness executable as a cost result. Material repeatable savings are required
before a private app rebuild; this lane must not become another prolonged series
of tiny flag variants. The original PRD, SunPad UI, performance/audio, stability
and device acceptance requirements remain unchanged.
