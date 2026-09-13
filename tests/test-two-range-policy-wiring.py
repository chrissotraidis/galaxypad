"""Source/cache ordering checks supplement compiled policy parity."""
from pathlib import Path

root=Path(__file__).resolve().parents[1]
policy=(root/'patches/experiments/two-range-policy.inc').read_text()
assert (root/'ref/ModernGekko/tools/galaxypad_two_range_policy.inc').read_text()==policy
port=(root/'ref/ModernGekko/tools/moderngekko_port.cpp').read_text()
assert '#include "galaxypad_two_range_policy.inc"' in port
assert port.index('const std::string two_range_policy = GalaxyTwoRangePolicy(')<port.index('if (fs::is_regular_file(module))')
assert 'options.backend, options.c_chunk_instructions, options.dispatch_lookup);' in port
assert '"|two_range_policy=" + two_range_policy' in port
assert '"two_range_policy=" << two_range_policy' in port
assert port.index('!ApplyGalaxyDcbz(generated)')<port.index('!ApplyGalaxyTwoRange(generated)')<port.index('fs::copy_file(emitted_header, generated / "generated.h"')
print('Two-range policy eligibility/cache/manifest/header-copy and fork source checks pass')
