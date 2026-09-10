"""Source-only checks for canonical THP ordering, identity and bootstrap wiring."""
from pathlib import Path
import hashlib

root = Path(__file__).resolve().parents[1]
policy = (root/'patches/experiments/thp-kernel-policy.inc').read_text()
assert (root/'ref/ModernGekko/tools/galaxypad_thp_policy.inc').read_text()==policy
port = (root/'ref/ModernGekko/tools/moderngekko_port.cpp').read_text()
assert '#include "galaxypad_thp_policy.inc"' in port
assert port.index('const std::string thp_policy = GalaxyThpPolicy(')<port.index('if (fs::is_regular_file(module))')
assert '"|thp_policy=" + thp_policy' in port
assert '"thp_policy=" << thp_policy' in port
assert port.index('!ApplyGalaxyFprf(generated)')<port.index('!ApplyGalaxyThp(generated)')<port.index('std::string configure =')
patch = root/'patches/ModernGekko/0016-rmge01-thp-kernels.patch'
digest = hashlib.sha256(patch.read_bytes()).hexdigest()
assert digest=='ef25620e8ec254b1c5eecf2bfa386ad60c06f085ac3cca0a1996cba611cf8f6f'
bootstrap = (root/'scripts/bootstrap-dependencies.sh').read_text()
assert digest in bootstrap
assert bootstrap.index('apply --reverse "$thp_policy_patch"')<bootstrap.index('apply --reverse "$fprf_policy_patch"')
assert bootstrap.index('apply "$fprf_policy_patch" || true')<bootstrap.index('apply "$thp_policy_patch" || true')
assert bootstrap.index('apply_patch_once "$ref/ModernGekko" "$fprf_policy_patch"')<bootstrap.index('apply_patch_once "$ref/ModernGekko" "$thp_policy_patch"')
print('THP source/cache/manifest/application order and bootstrap pin/recovery wiring pass')
