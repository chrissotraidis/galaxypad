"""Source-pinned offline experiment; preserve the exact FMA tie correction."""
import hashlib

SOURCE_SHA = '554149a2e7d08783402af38e5a2b898aff476370b0e3a6af0ed4bd411aab934f'


def transform(source):
    if hashlib.sha256(source.encode()).hexdigest() != SOURCE_SHA:
        raise ValueError('Unexpected float source identity')
    signature = 'FPRes ni_madd_msub('
    start = source.index(signature)
    guard = '        if ((result_bits & D_MASK) == EVEN_TIE) {'
    begin = source.index(guard, start)
    brace = source.index('{', begin)
    depth, end = 1, brace + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    body = source[brace + 1:end - 1]
    helper = ('__attribute__((noinline,cold)) static f64 galaxypad_madd_tie('
              'f64 a, f64 c_round, f64 b_sign, f64 value, u64 result_bits) {\n'
              + body.replace('result.value', 'value') + '\n    return value;\n}\n\n')
    call = (guard + '\n            result.value = galaxypad_madd_tie('
            'a, c_round, b_sign, result.value, result_bits);\n        }')
    return source[:start] + helper + source[start:begin] + call + source[end:]
