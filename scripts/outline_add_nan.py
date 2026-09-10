"""Offline source-pinned ni_add NaN-path outline; no runtime selection."""
import hashlib

SOURCE_SHA = '554149a2e7d08783402af38e5a2b898aff476370b0e3a6af0ed4bd411aab934f'


def transform(source):
    if hashlib.sha256(source.encode()).hexdigest() != SOURCE_SHA:
        raise ValueError('Unexpected float source identity')
    start = source.index('FPRes ni_add(')
    begin = source.index('    if (isnan(result.value)) {', start)
    brace = source.index('{', begin)
    end, depth = brace + 1, 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    body = source[brace + 1:end - 1]
    helper = ('__attribute__((noinline,cold)) static FPRes galaxypad_add_nan('
              'CPUState* cpu, f64 a, f64 b, FPRes result) {' + body + '\n}\n\n')
    call = ('    if (isnan(result.value)) {\n'
            '        return galaxypad_add_nan(cpu, a, b, result);\n    }')
    return source[:start] + helper + source[start:begin] + call + source[end:]
