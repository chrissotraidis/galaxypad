"""Private source-pinned FP helper closure with a compact state ABI.

Only type and symbol names change; arithmetic/status bodies remain original.
Not a general C parser or shipping transform.
"""
import hashlib
import re

SOURCE_SHA = '554149a2e7d08783402af38e5a2b898aff476370b0e3a6af0ed4bd411aab934f'
ROOTS = ('ppc_ps_madd_op', 'ppc_ps_sum0', 'ppc_frsqrte', 'ppc_fmuls',
         'ppc_fma', 'ppc_ps_muls0')

def build(source):
    assert hashlib.sha256(source.encode()).hexdigest() == SOURCE_SHA
    functions = {}
    pattern = r'^((?:static )?(?:inline )?\w+(?:\s*\*)?)\s+(\w+)\(([^;{}]*?)\)\s*\{'
    for match in re.finditer(pattern, source, re.M):
        end, depth = match.end(), 1
        while depth:
            depth += (source[end] == '{') - (source[end] == '}')
            end += 1
        name = match[2]
        assert name not in functions
        functions[name] = (match[1], match[3], source[match.end()-1:end])
    selected = set(ROOTS)
    while True:
        required = set(selected)
        for name in selected:
            assert name in functions, name
            required.update(set(re.findall(r'\b(\w+)\s*\(', functions[name][2])) & functions.keys())
        if required == selected:
            break
        selected = required
    names = {name: 'compact_'+name for name in sorted(selected)}
    def rename(text):
        return re.sub(r'\b(?:CPUState|'+'|'.join(names)+r')\b',
                      lambda m: 'CompactFPState' if m[0]=='CPUState' else names[m[0]], text)
    fields, external = set(), set()
    declarations, definitions = [], []
    for name in sorted(selected):
        result, params, body = functions[name]
        fields.update(re.findall(r'cpu->(\w+)', body))
        external.update(set(re.findall(r'\b(\w+)\s*\(', body))-selected)
        signature = 'static inline '+re.sub(r'^(?:static |inline )+', '', result)+' '+names[name]+'('+rename(params)+')'
        declarations.append(signature+';')
        transformed = rename(body)
        # Exact reversible spelling transform, not an arithmetic rewrite.
        reverse = {v:k for k,v in names.items()} | {'CompactFPState':'CPUState'}
        restored = re.sub(r'\b(?:'+'|'.join(reverse)+r')\b', lambda m:reverse[m[0]], transformed)
        assert restored == body
        definitions.append(signature+' '+transformed)
    assert fields <= {'fpr', 'ps1', 'fpscr'}, fields
    # The selected closure must not introduce a CPU callback or memory access.
    allowed = {'if','while','for','switch','return','sizeof','defined','f64_bits','f64_value',
               'f32_bits','f32_value','isnan','isinf','fma','fmaf','signbit',
               '__builtin_clzll','memcpy'}
    assert external <= allowed, external-allowed
    code = 'typedef struct { f64 fpr[7], ps1[7]; u32 fpscr; } CompactFPState;\n'
    code += '\n'.join(declarations)+'\n'+'\n\n'.join(definitions)+'\n'
    return code, names, {'helpers': sorted(selected), 'fields':sorted(fields),
                         'external_calls':sorted(external), 'source_sha256':SOURCE_SHA}
