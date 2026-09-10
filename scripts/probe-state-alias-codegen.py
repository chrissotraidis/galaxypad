#!/usr/bin/env python3
"""Compile-only state-alias headroom probe. NEVER execute or package its output.

Restrict is a hypothetical stronger contract, not valid for arbitrary current
callbacks/CPUState-as-RAM. Static instruction counts are not runtime speed.
"""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
import re
import shlex
import subprocess

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
args = p.parse_args()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
module = root/'generated/modules-scale-r387/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-c4cbfba1bd04990b'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(module/'gRMGE01_recomp.dylib') == 'c0021b9f2fad3acc3746b6a582b46935e2f7b60bc38434ad7d485564957c7939'
assert sha(root/'generated/pgo/rmge01.profdata') == 'f39a3cedeb6c49f35c411356893c619dc347eb1b0bb5986687f25cf81e7d460d'
graph = (module/'module-build/build.ninja').read_text()
chunks = ['chunk_1102_text1_804520A0.c', 'chunk_1191_text1_804AB0A0.c',
          'chunk_1202_text1_804B60A0.c']
report = {'boundary': 'COMPILE ONLY; hypothetical alias contract; NOT safe to execute or ship; static counts not latency or FPS',
          'module_sha256': sha(module/'gRMGE01_recomp.dylib'), 'chunks': {}}
for chunk in chunks:
    original = module/'dolrecomp-output/RMGE01_generated/chunks'/chunk
    text = original.read_text()
    matches = []
    for header, body in re.findall(r'^build ([^\n]+)\n((?:  [^\n]*\n)*)', graph, re.M):
        if ': C_COMPILER_' in header and header.split(' || ')[0].endswith(' '+str(original)):
            matches.append(dict(re.findall(r'^  (\w+) = (.*)$', body, re.M)))
    assert len(matches) == 1
    fields = matches[0]
    flags = shlex.split(fields['DEFINES']+' '+fields['INCLUDES']+' '+fields['FLAGS'])
    assert [f for f in flags if re.fullmatch('-O[0-3sz]', f)][-1] == '-O2'
    assert all(f in flags for f in ['-flto=thin', '-ffp-contract=off', '-fno-fast-math'])
    changed, replacements = re.subn(r'(\b(?:func|loop)_[0-9A-Fa-f]+\(CPUState\*) ctx\)', r'\1 __restrict ctx)', text)
    assert replacements > 0
    row = {'source_sha256': sha(original), 'restricted_definitions': replacements, 'variants': {}}
    chunk_root = out/chunk.removesuffix('.c')
    chunk_root.mkdir()
    (chunk_root/'RMGE01.h').symlink_to(original.parent.parent/'RMGE01.h')
    for variant, source in [('control', text), ('hypothetical_restrict', changed)]:
        directory = out/chunk.removesuffix('.c')/variant
        directory.mkdir(parents=True)
        path = directory/chunk
        path.write_text(source)
        obj, dylib = directory/'chunk.o', directory/'DO-NOT-RUN.dylib'
        compile_cmd = ['xcrun', 'clang', *flags, '-c', str(path), '-o', str(obj)]
        link_cmd = ['xcrun', 'clang', '-arch', 'arm64', '-mmacosx-version-min=14.0',
                    '-flto=thin', '-dynamiclib', '-Wl,-undefined,dynamic_lookup',
                    '-Wl,-install_name,@rpath/DO-NOT-RUN.dylib',
                    '-Wl,-u,_func_'+chunk.removesuffix('.c').split('_')[-1],
                    str(obj), '-o', str(dylib)]
        with (directory/'build.log').open('w') as log:
            subprocess.run(compile_cmd, stdout=log, stderr=subprocess.STDOUT, check=True)
            subprocess.run(link_cmd, stdout=log, stderr=subprocess.STDOUT, check=True)
        asm = subprocess.check_output(['xcrun', 'llvm-objdump', '-d', str(dylib)], text=True)
        (directory/'chunk.asm').write_text(asm)
        counts = Counter(re.findall(r'^\s*[0-9a-f]+:\s+[0-9a-f]{8}\s+(\S+)', asm, re.M))
        assert counts
        row['variants'][variant] = {'source_sha256': sha(path), 'binary_sha256': sha(dylib),
            'compile_command': compile_cmd, 'link_command': link_cmd,
            'instructions': sum(counts.values()), 'loads': sum(n for op,n in counts.items() if op.startswith('ld')),
            'stores': sum(n for op,n in counts.items() if op.startswith('st')), 'opcodes': dict(counts)}
    report['chunks'][chunk] = row
    print(chunk, {k:{a:b for a,b in v.items() if a in ('instructions','loads','stores')} for k,v in row['variants'].items()}, flush=True)
(out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
