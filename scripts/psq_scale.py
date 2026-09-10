"""Isolated exact-power-of-two store-scale experiment; never edits the checkout."""
import hashlib

SOURCE_SHA = '1350d1196b38b147477890ef0dc59d5d9e389a55a169d51913fc033be34edb69'
CANDIDATE_SHA = '05e221c01bead6801c51217f84398bd10f22e1b810f6d06977e04d8a801436ea'
OLD = '    f32 conv = (f32)value * ldexpf(1.0f, scale);'
NEW = '''    // GQR scales are signed six-bit integers. These powers are normal,
    // exactly representable floats; keep libm for any other caller range.
    f32 factor = (scale >= -32 && scale <= 31)
        ? f32_value((u32)(scale + 127) << 23) : ldexpf(1.0f, scale);
    f32 conv = (f32)value * factor;'''


def transform(source):
    if hashlib.sha256(source.encode()).hexdigest() != SOURCE_SHA:
        raise ValueError('Unexpected CPU source; scale experiment refused')
    if source.count(OLD) != 1:
        raise ValueError('Expected exactly one quantization expression')
    return source.replace(OLD, NEW, 1)


def reference_source(source):
    """Recover the exact historical oracle from either audited source identity."""
    digest = hashlib.sha256(source.encode()).hexdigest()
    if digest == CANDIDATE_SHA:
        source = source.replace(NEW, OLD, 1)
    if hashlib.sha256(source.encode()).hexdigest() != SOURCE_SHA:
        raise ValueError('Unknown CPU source; reference recovery refused')
    return source
