# R798: direct RAM loads pass correctness, fail the local cost screen

The private offline exporter can now lower normal MEM1/MEM2 word loads without
a helper call. It masks mirrors, checks MEM2 before MEM1, preserves the existing
unsigned bounds expression, reverses byte order, and falls back to the original
helper for other addresses. It writes canonical PC before reading memory and
flushes pending GPRs. Stores still use the original journal-aware helper.
This does not alter the app, selected module, or mobile runtime policy.

## Verification

- Mixed direct-load run 61842 exited 0: 152,320 complete-state/RAM/callback
  comparisons plus 2,880 CPUState-as-RAM comparisons.
- Mixed helper-only regression 11069 exited 0 with the same counts.
- Restore direct-load regression 6989 exited 0: 60,928 matrix comparisons plus
  1,152 CPUState-as-RAM comparisons.
- All three stderr files are empty. Unsupported opcodes and invalid suffix
  entries still reject. C++ driver/helpers use ASan/UBSan; assembly does not.
- Alias tests reuse the same CPU object address across reset reference/candidate
  runs, exposing either its GPR array or PC field as RAM. No pointer-byte
  normalization hides differences. This is bounded alias coverage, not proof
  for every possible malformed map or alias.

Evidence: generated/arm64-load-r798-final.json, arm64-helper-r798.json,
arm64-restore-load-r798.json and corresponding .err files.

## Cost result and decision

Added optional `--benchmark`: a separate unsanitized -O2 macOS executable runs
eight alternating-order reference/candidate pairs, one million calls per half.
The actual generated-C source oracle is noinline; the candidate uses its static
assembly entry. Both reset the same input registers/cycles and use ordinary RAM
without callbacks. Checksums match. Timings include the small input-reset loop.

In the final four direct-load pairs, reference cost is 7.365–7.649 ns/block,
candidate 9.713–9.976 ns/block. Helper-only final pairs are 7.161–7.417 versus
9.464–9.487 ns/block. Earlier samples are substantially slower, demonstrating
warmup/host-frequency sensitivity. These separate runs do not establish a
precise direct-load-versus-helper delta. Neither demonstrates an improvement
over the reference. This is not an actual-policy ThinLTO/PGO module benchmark,
nor a representative scene workload, CPU-share measurement, or FPS result.

Do not promote this candidate or start a full app/module build from this result.
The exporter currently saves/restores X19–X30 for each tiny block, flushes at
every memory operation, and calls helpers for stores and return. The actual
reference allocator is present, but values rarely remain resident for long.
That is a structural difference from a sustained native execution backend;
direct word-load emission alone has not overcome it here.

Next qualify a materially larger, observed hot region and its state-observation
boundaries before extending the compiler. Estimate remaining call/spill work
against compiled C and use actual-policy cost evidence before promotion. Avoid
another series of tweaks to this ten-instruction fixture. Broader FP/CR,
interrupt/SMC contracts, full-module execution, gameplay performance, stability,
SunPad UI, audio and physical-device requirements remain open.

Reproduce with `python3 tests/probe-arm64-restore-block.py --direct-cpu --mixed
--fast-load --benchmark` (on one shell line). Omit --fast-load for helper-only;
omit --mixed and --benchmark for the restore correctness regression.
