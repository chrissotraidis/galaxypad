"""Prove the integrated fork source reproduces the tested candidate exactly."""
from pathlib import Path
import hashlib
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root/'scripts'))
from psq_scale import transform, reference_source

source = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core/cpu.c'
checkout = source.read_text()
original = reference_source(checkout)
expected = transform(original)
assert hashlib.sha256(expected.encode()).hexdigest() == '05e221c01bead6801c51217f84398bd10f22e1b810f6d06977e04d8a801436ea'
assert checkout == expected
assert "f32 factor = (scale >= -32 && scale <= 31)" in checkout

assert source.read_text() == checkout
print('Fork scale implementation matches the tested candidate; checkout unchanged')
