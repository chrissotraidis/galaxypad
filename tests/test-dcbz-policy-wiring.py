"""Check candidate-only identity, application order and pinned bootstrap recovery."""
from pathlib import Path
import hashlib
root=Path(__file__).resolve().parents[1]
policy=(root/'patches/experiments/dcbz-loop-policy.inc').read_text()
assert (root/'ref/ModernGekko/tools/galaxypad_dcbz_policy.inc').read_text()==policy
port=(root/'ref/ModernGekko/tools/moderngekko_port.cpp').read_text()
assert '#include "galaxypad_dcbz_policy.inc"' in port
assert port.index('const std::string dcbz_policy = GalaxyDcbzPolicy(')<port.index('if (fs::is_regular_file(module))')
assert '(dcbz_policy == "none" ? "" : "|dcbz_policy=" + dcbz_policy)' in port
assert '"dcbz_policy=" << dcbz_policy' in port
assert port.index('!ApplyGalaxyThp(generated)')<port.index('!ApplyGalaxyDcbz(generated)')<port.index('std::string configure =')
patch=root/'patches/ModernGekko/0021-dcbz-loop-policy.patch'
digest=hashlib.sha256(patch.read_bytes()).hexdigest()
assert digest=='ef5ce417866cd67f6fd314f8585a6ea7716e50bcf824a044c4b8d4020c3c0e3b'
bootstrap=(root/'scripts/bootstrap-dependencies.sh').read_text()
assert digest in bootstrap
assert bootstrap.index('apply --reverse "$dcbz_policy_patch"')<bootstrap.index('apply --reverse "$thp_policy_patch"')
assert bootstrap.index('apply "$thp_policy_patch" || true')<bootstrap.index('apply "$dcbz_policy_patch" || true')
assert bootstrap.index('apply_patch_once "$ref/ModernGekko" "$thp_policy_patch"')<bootstrap.index('apply_patch_once "$ref/ModernGekko" "$dcbz_policy_patch"')
print('Dcbz candidate cache identity, manifest, source parity and bootstrap wiring passed')
