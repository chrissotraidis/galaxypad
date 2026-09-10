#!/usr/bin/env python3
"""Inspect isolated decoder assembly with accepted flags, without a module build."""
import hashlib
import argparse
from pathlib import Path
import re
import shlex
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--no-profile', action='store_true', help='Separate extraction shape from stale-profile effects')
parser.add_argument('--dcbz', action='store_true', help='Inspect guarded line clears, not extraction')
parser.add_argument('--dcbz-loop', action='store_true', help='Preserve original loop shape for PGO')
args = parser.parse_args()
if args.dcbz_loop:
    args.dcbz = True
root = Path(__file__).resolve().parents[1]
module = Path((root/'generated/modules/RMGE01/active-module.txt').read_text().strip())
assert hashlib.sha256(module.read_bytes()).hexdigest() == '1180447313459c4c153ca74e5215811e88a9b69a00d15feff940f062148fc631'
source = module.parent/'dolrecomp-output/RMGE01_generated/chunks/chunk_1103_text1_804530A0.c'
graph = (module.parent/'module-build/build.ninja').read_text()
block = re.search(r'^build [^\n]*: C_COMPILER[^\n]*' + re.escape(str(source)) +
                  r'[^\n]*\n((?:  [^\n]*\n)*)', graph, re.M)
assert block
fields = dict(re.findall(r'^  (\w+) = (.*)$', block[1], re.M))
flags = shlex.split(fields['DEFINES']+' '+fields['INCLUDES']+' '+fields['FLAGS'])
assert '-O2' in flags and '-flto=thin' in flags and '-fno-fast-math' in flags
# LTO -S emits IR, not ARM64 assembly. This is deliberately pre-link evidence.
flags = [flag for flag in flags if not flag.startswith('-flto')]
if args.no_profile:
    flags = [flag for flag in flags if not flag.startswith('-fprofile-instr-use=')]
output = root/'generated/huffman-y-r263'
if args.dcbz:
    output = root/('generated/dcbz-loop-assembly-r277' if args.dcbz_loop else 'generated/dcbz-assembly-r277')
    output.mkdir(exist_ok=True)
    original = source.read_text()
    assert hashlib.sha256(original.encode()).hexdigest() == 'e6aa915816ee2a89534f75c4d59dd0c145f7a5d0162c3e1a15b2ebe33b996dcc'
    original = original.replace('#include "../RMGE01.h"', '#include "'+str(source.parent.parent/'RMGE01.h')+'"')
    anchor = 'for (u32 i = 0; i < 32; i += 4) mem_write32(ctx, ea + i, 0);'
    assert original.count(anchor) == 8
    helper = (root/('patches/experiments/dcbz-ram-loop.inc' if args.dcbz_loop else 'patches/experiments/dcbz-ram-line.inc')).read_text()
    expected_helper = 'ed743fdeb1b32af89dfd1fbfefa671a63b2a36ed7c2c59b684f105275783a421' if args.dcbz_loop else '6f576f6719cb6a60a4a9fc1363b5da1be701b16c712ec85a85da2514f7b49711'
    assert hashlib.sha256(helper.encode()).hexdigest() == expected_helper
    replacement = ('u8* line = galaxypad_dcbz_prepare(ctx, ea);\n'
        '        for (u32 i = 0; i < 32; i += 4) galaxypad_dcbz_store(ctx, ea, line, i);') if args.dcbz_loop else 'galaxypad_dcbz_ram_line(ctx, ea);'
    candidate = original.replace(anchor, replacement)
    candidate = candidate.replace('void func_804530A0(CPUState* ctx) {',
        '#include <string.h>\n'+helper+'\nvoid func_804530A0(CPUState* ctx) {')
    (output/'reference.c').write_text(original)
    (output/'candidate.c').write_text(candidate)
for name, expected in (
    ('reference', 'f1be7297ea3f8176e5be440a5fa596deb1c706a1885cb91e084f8fede5f423ca'),
    ('candidate', '76fdb33cad574c96f4aa2affd392e892f6a2a6e9837e851fe0aeb0fcd5b1405b'),
):
    candidate = output/(name+'.c')
    if not args.dcbz:
        assert hashlib.sha256(candidate.read_bytes()).hexdigest() == expected
    assembly = output/(name+('-no-profile' if args.no_profile else '')+'.s')
    subprocess.run(['clang', *flags, '-S', str(candidate), '-o', str(assembly)], check=True)
    functions = re.findall(r'^(_[A-Za-z0-9_]+):[^\n]*\n(.*?)(?=^\s*\.cfi_endproc)',
                           assembly.read_text(), re.M | re.S)
    for symbol, body in functions:
        if symbol not in ('_func_804530A0', '_huffman_y') and not symbol.startswith('_galaxypad_dcbz'):
            continue
        ops = re.findall(r'^\t([a-z][a-z0-9]*)\b', body, re.M)
        print(name, symbol, 'instructions', len(ops), 'loads',
              sum(op.startswith('ld') for op in ops), 'stores',
              sum(op.startswith('st') for op in ops), flush=True)
