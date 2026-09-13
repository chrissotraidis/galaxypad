"""Source-only checks for canonical THP ordering, identity and fork source wiring."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
policy = (root/'patches/experiments/thp-kernel-policy.inc').read_text()
assert (root/'ref/ModernGekko/tools/galaxypad_thp_policy.inc').read_text()==policy
port = (root/'ref/ModernGekko/tools/moderngekko_port.cpp').read_text()
assert '#include "galaxypad_thp_policy.inc"' in port
assert port.index('const std::string thp_policy = GalaxyThpPolicy(')<port.index('if (fs::is_regular_file(module))')
assert '"|thp_policy=" + thp_policy' in port
assert '"thp_policy=" << thp_policy' in port
assert port.index('!ApplyGalaxyFprf(generated)')<port.index('!ApplyGalaxyThp(generated)')<port.index('std::string configure =')
print('THP source/cache/manifest/application order and fork source wiring pass')
