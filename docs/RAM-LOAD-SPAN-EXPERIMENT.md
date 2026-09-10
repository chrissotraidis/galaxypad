# R783: shared RAM range across actual generated loads

Previous turn: progress, pure-GPR census rejected another callback-free batch.
This test crosses memory instructions but does not cache mappings persistently.
No emitter, installed runtime, CPU ABI or settings changed.

tests/test-ram-load-span.py extracts four actual lwz instructions at804B66A0–AC
from the current R387 chunk804B60A0. Candidate normal entry checks the whole
twenty-byte source range once, rejects wrapping address arithmetic and CPU-state
overlap, then reads four words in original order. Other entries and rejected
ranges execute original bodies. No callback is elided unless the entire range
is direct RAM. No instruction charges occur inside this extracted span; this
test is not proof of full-function entry/exit cycle accounting.

generated/ram-load-span-r783.log, command exits0 with ASan/UBSan:120000 complete
CPU-state and ordered callback-address/PC comparisons,17145 shared-range calls.
MEM1/MEM2/mirrors, unaligned/boundary/unmapped/wrapping addresses, absent EXRAM,
all four entries, callback base-register mutation and explicit CPU/RAM alias
covered. Original callbacks see original per-instruction PC. Alias case rejects
fast path and retains sequential reads. No speed benchmark or module integration.
Experimental generated-fixture dependency means this is separate from the
repository suite, like the existing full-transform probe.

Initial read-only exact-body scan:68974 matching lwz bodies;1853 instructions
in same-base contiguous spans of at least4. Break at gaps, base changes or a
destination overwriting the base. Counts exclude unfamiliar bodies, cycles,
other memory widths and mixed operations. This is textual coverage, not proof
of mapping eligibility, loop frequency or total CPU opportunity. Preserve the
result as a prerequisite only; no full module build justified from these counts.

Next: dynamic coverage/full-context cost qualification before promoting range
fusion. Do not broaden into speculative caches, omit callback effects, or call
these tests improved FPS. Wider memory-state dataflow remains unproven. Full
PRD, movie/audio, SunPad, gameplay, stability and physical-device gates remain.
