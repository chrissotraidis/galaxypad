"""Source/cache/bootstrap ordering checks supplement compiled policy parity."""
from pathlib import Path
import hashlib

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
patch=root/'patches/ModernGekko/0025-rmge01-two-range-policy.patch'
digest=hashlib.sha256(patch.read_bytes()).hexdigest()
assert digest=='1a8378b059fc3ef9ff00285c23d491200ed404a2245ac789e90d8413c4d169bc'
bootstrap=(root/'scripts/bootstrap-dependencies.sh').read_text()
assert bootstrap.count(digest)==2
scope=bootstrap.split('verify_patch_scope "$ref/ModernGekko" vendor/dolphin',1)[1].split('lc_pair_runtime_patch=',1)[0]
assert '"$two_range_policy_patch"' in scope
assert bootstrap.index('apply --reverse "$two_range_policy_patch"')<bootstrap.index('apply --reverse "$dcbz_policy_patch"')
assert bootstrap.index('apply "$dcbz_policy_patch" || true')<bootstrap.index('apply "$two_range_policy_patch" || true')
assert bootstrap.index('apply_patch_once "$ref/ModernGekko" "$dcbz_policy_patch"')<bootstrap.index('apply_patch_once "$ref/ModernGekko" "$two_range_policy_patch"')
print('Two-range policy eligibility/cache/manifest/header-copy and bootstrap pin/order checks pass')
