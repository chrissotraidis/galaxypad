# R834: private Simulator diagnostic host built

Previous turn progress: recorder/isolated VI overlay and focused tests pass.
This turn builds the private host only, reusing existing guest module and every
other host object. No game or Simulator launched, no installed app replaced.

`scripts/build-thread-work-host.py --output generated/candidates/thread-work-r834b`
completes (session62102 exit0). Provenance JSON retains exact original/core/object
hashes and all compile/link commands. It does not invoke the normal build graph
or mutate existing object/archive/app outputs. A fresh runtime compilation using
original source/flags matches the archived dolphin_runtime.cpp.o byte for byte.

## Unchanged control check

First output thread-work-r834/session73283 stopped at unsigned-binary comparison,
before candidate compilation. Comparison showed identical size20,225,968 and
UUID E886101A-75F4-3E5F-B000-722DE8B82781, with exactly two differing bytes.
They are in parsed LC_SEGMENT_64 __LINKEDIT vmsize at offset3152: original0x480000,
relink0x498000. codesign removal retains this virtual reservation. Both segments
are read-only, have no sections, are16KiB aligned and cover identical file size.
Every other byte is identical. This is not strict whole-file identity; no code,
data, UUID, file content or other load-command differences were disregarded.

Second run uses the explicit parsed-field comparison, preserving the failed
first attempt. tests/test-host-linkedit-comparison.py passes allowed reservation
differences, content inequality and malformed/writable/sectioned rejection.

## Candidate

Private Clang VFS overlay redirects the original quoted VI header, so original
sibling include precedence cannot accidentally select the unmodified recorder.
Only the runtime translation unit gets GALAXYPAD_PRIVATE_THREAD_WORK=1. Its
object contains thread_selfcounts; ordinary archived object is reproduced by
the control. Candidate replaces exactly one uniquely named archive member in a
copy, then relinks a copied app. Original archive/app hashes still match.
Ad-hoc signing and deep/strict verification succeed. vtool reports IOSSIMULATOR,
minOS16.0, SDK26.5, linker1267.0.

Private app:
`generated/candidates/thread-work-r834b/candidate/GalaxyPad.app`

Binary SHA24002e5004ae4c1e24a081fb68951984aeeadd32a6c2190ecc75a9c526c5fb0b.
Runtime object SHAe5f8a01f0215e756a026c7a3030fd4129f110891648024f3c76e52e6baf8427d.
Unchanged guest module SHA3acdcddcd47812c2e2a67b8cec0cf06c17009cf1ad7f2e9dc9abd83158a1bac0.
Original app SHA85ffc10065d375062a0c445d87d0a501d4fc91e236986d6d55d74f0b8333dbcc.

## Next

Implement/test strict sidecar analysis for query uncertainty, complete window,
per-level topology, raw counter resets/errors and Mach units. Then install/run
this private host in the sole iPad Simulator, using R831 scene/options/module,
both GALAXYPAD_VI_TIMING and GALAXYPAD_THREAD_WORK_TIMING to fresh paths. Preserve
save and original app for restoration; collect level names in run manifest.
Capture actual CPU-thread work/core-class time in neutral plaza, inspect scene,
stop via menu to export, and restore original installed app after experiment.
Do not claim a performance gain or physical-device behavior from this build.
No further host/module build is needed unless a specific failure requires it.
Full original PRD/SunPad/audio/stability/device goal remains open.
