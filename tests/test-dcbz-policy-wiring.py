"""Check candidate-only identity, application order and pinned fork integration."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
policy=(root/'patches/experiments/dcbz-loop-policy.inc').read_text()
assert (root/'ref/ModernGekko/tools/galaxypad_dcbz_policy.inc').read_text()==policy
port=(root/'ref/ModernGekko/tools/moderngekko_port.cpp').read_text()
assert '#include "galaxypad_dcbz_policy.inc"' in port
assert port.index('const std::string dcbz_policy = GalaxyDcbzPolicy(')<port.index('if (fs::is_regular_file(module))')
assert '(dcbz_policy == "none" ? "" : "|dcbz_policy=" + dcbz_policy)' in port
assert '"dcbz_policy=" << dcbz_policy' in port
assert port.index('!ApplyGalaxyThp(generated)')<port.index('!ApplyGalaxyDcbz(generated)')<port.index('std::string configure =')
print('Dcbz candidate cache identity, manifest, source parity and fork source wiring passed')
