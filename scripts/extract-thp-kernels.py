#!/usr/bin/env python3
"""Prepare a private two-kernel chunk overlay; never selects or builds a module."""
import hashlib
import json
from pathlib import Path
import re

EXPECTED = 'f2d6911016e8e1c9f46caf5ee97dece58689f5b5f51397860bb868383c34bd61'
REGIONS = ((0x804526e8,0x80452b74),(0x80452b74,0x80453008))


def extract(source):
    assert hashlib.sha256(source.encode()).hexdigest()==EXPECTED
    signature = 'void func_804520A0(CPUState* ctx) {'
    prefix, outer = source.split(signature)
    entry = outer[:outer.index('    default: return;')]
    kernels, replacements = [], []
    for index,(start,end) in enumerate(REGIONS):
        body = outer[outer.index(f'\nlabel_{start:08X}:'):outer.index(f'\nlabel_{end:08X}:')]
        labels = re.findall(r'^label_([0-9A-F]{8}):',body,re.M)
        assert [int(pc,16) for pc in labels]==list(range(start,end,4))
        cases = [line for line in entry.splitlines() if re.match(r'    case 0x[0-9A-F]+u:',line)
                 and start<=int(line.split('0x')[1].split('u')[0],16)<end]
        assert len(cases)==len(labels)
        # The original outer switch already charged external nonleader entries.
        kernel_cases = [re.sub(r'ctx->downcount -= \d+; ', '',line) for line in cases]
        assert all(re.fullmatch(r'    case 0x[0-9A-F]+u: goto label_[0-9A-F]+;',line) for line in kernel_cases)
        targets = set(re.findall(r'goto (\w+);',body))
        assert targets-set('label_'+pc for pc in labels)=={'return_dispatch_804520A0'}
        # Preserve the distinction between early helper/yield exits and guest blr.
        # An exception callback may even change PC to an outer return target.
        kernel_body = body.replace('return;', 'return false;')
        kernels.append(f'static __attribute__((noinline, flatten)) bool thp_kernel_{index}(CPUState* ctx) {{\n'
                       +'    switch (ctx->pc) {\n'+'\n'.join(kernel_cases)+'\n    default: return false;\n    }\n'
                       +kernel_body+'\nreturn_dispatch_804520A0: return true;\n}\n')
        trampolines = ''.join(f'\nlabel_{pc}:\n    ctx->pc = 0x{pc}u;\n    goto invoke_thp_{index};\n' for pc in labels)
        trampolines += f'\ninvoke_thp_{index}:\n    if (!thp_kernel_{index}(ctx)) return;\n    goto return_dispatch_804520A0;\n'
        assert outer.count(body)==1
        outer = outer.replace(body,trampolines,1)
        replacements.append((trampolines,body))
    restored = outer
    for trampolines,body in replacements:
        assert restored.count(trampolines)==1
        restored = restored.replace(trampolines,body,1)
    assert prefix+signature+restored==source, 'Unexpected changes outside the two regions'
    assert outer[:outer.index('    default: return;')]==entry
    return prefix+'\n'.join(kernels)+'\n'+signature+outer


def main():
    root = Path(__file__).resolve().parents[1]
    generated = root/'generated/modules-fprf-r174/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-27fc425ac63117e7/dolrecomp-output/RMGE01_generated'
    source = (generated/'chunks/chunk_1102_text1_804520A0.c').read_text()
    candidate = extract(source)
    include = '#include "'+str(generated/'RMGE01.h')+'"'
    reference = source.replace('#include "../RMGE01.h"',include)
    candidate = candidate.replace('#include "../RMGE01.h"',include)
    directory = root/'generated/thp-kernels-r198-exits'
    directory.mkdir(exist_ok=False)
    for name,text in (('reference.c',reference),('candidate.c',candidate)):
        (directory/name).write_text(text)
    manifest = dict(original_sha256=EXPECTED, instruction_entries=584,
                    reference_sha256=hashlib.sha256(reference.encode()).hexdigest(),
                    candidate_sha256=hashlib.sha256(candidate.encode()).hexdigest(),
                    selected=False, compiled=False)
    (directory/'provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':
    main()
