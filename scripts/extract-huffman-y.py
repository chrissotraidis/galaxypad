#!/usr/bin/env python3
"""Prepare one private decoder extraction; never build or select a module."""
import hashlib
import json
from pathlib import Path
import re

EXPECTED = 'e6aa915816ee2a89534f75c4d59dd0c145f7a5d0162c3e1a15b2ebe33b996dcc'
START, END = 0x804534B4, 0x80453B10


def extract(source):
    assert hashlib.sha256(source.encode()).hexdigest() == EXPECTED
    signature = 'void func_804530A0(CPUState* ctx) {'
    prefix, outer = source.split(signature)
    entry = outer[:outer.index('    default: return;')]
    begin, end = (outer.index(f'\nlabel_{pc:08X}:') for pc in (START, END))
    body = outer[begin:end]
    labels = re.findall(r'^label_([0-9A-F]{8}):', body, re.M)
    assert [int(pc, 16) for pc in labels] == list(range(START, END, 4))
    cases = re.findall(r'^    case 0x([0-9A-F]{8})u: (.*)$', entry, re.M)
    selected = [(pc, action) for pc, action in cases if START <= int(pc, 16) < END]
    assert [pc for pc, _ in selected] == labels
    helper_cases = []
    for pc, action in selected:
        # External suffix charges remain solely in the unchanged outer switch.
        action = re.sub(r'^ctx->downcount -= \d+; ', '', action)
        assert action == f'goto label_{pc};'
        helper_cases.append(f'    case 0x{pc}u: {action}')
    assert set(re.findall(r'goto (\w+);', body)) - {
        'label_' + pc for pc in labels} == {'return_dispatch_804530A0'}
    helper = ('static __attribute__((noinline, flatten)) bool huffman_y(CPUState* ctx) {\n'
              '    switch (ctx->pc) {\n' + '\n'.join(helper_cases) +
              '\n    default: return false;\n    }\n' +
              body.replace('return;', 'return false;') +
              '\nreturn_dispatch_804530A0: return true;\n}\n')
    trampolines = ''.join(f'\nlabel_{pc}:\n    ctx->pc = 0x{pc}u;\n'
                          '    goto invoke_huffman_y;\n' for pc in labels)
    trampolines += ('\ninvoke_huffman_y:\n    if (!huffman_y(ctx)) return;\n'
                    '    goto return_dispatch_804530A0;\n')
    changed = outer[:begin] + trampolines + outer[end:]
    assert changed.replace(trampolines, body, 1) == outer
    assert changed[:changed.index('    default: return;')] == entry
    return prefix + helper + '\n' + signature + changed


def main():
    root = Path(__file__).resolve().parents[1]
    module = Path((root/'generated/modules/RMGE01/active-module.txt').read_text().strip())
    generated = module.parent/'dolrecomp-output/RMGE01_generated'
    source = (generated/'chunks/chunk_1103_text1_804530A0.c').read_text()
    candidate = extract(source)
    include = '#include "' + str(generated/'RMGE01.h') + '"'
    output = root/'generated/huffman-y-r263'
    output.mkdir(exist_ok=False)
    manifest = dict(original_sha256=EXPECTED, instruction_entries=407, selected=False)
    for name, text in (('reference', source), ('candidate', candidate)):
        text = text.replace('#include "../RMGE01.h"', include)
        (output/(name+'.c')).write_text(text)
        manifest[name+'_sha256'] = hashlib.sha256(text.encode()).hexdigest()
    (output/'provenance.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
