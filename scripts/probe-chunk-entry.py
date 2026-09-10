#!/usr/bin/env python3
"""Prepare/compile an isolated entry-split chunk. Never selects a module.

Original function remains intact as the interior-entry fallback. The normal
copy retains all code except initial cases that charge a nonleader suffix.
This is an assembly/code-size probe, not runtime correctness acceptance.
"""
from pathlib import Path
import hashlib
import argparse
import re
import shlex
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--no-profile', action='store_true')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
module = Path((root/'generated/modules/RMGE01/active-module.txt').read_text().strip())
generated = (module.parent/'dolrecomp-output').resolve()
source_path = generated/'RMGE01_generated/chunks/chunk_1103_text1_804530A0.c'
source = source_path.read_text()
assert hashlib.sha256(source.encode()).hexdigest() == 'e6aa915816ee2a89534f75c4d59dd0c145f7a5d0162c3e1a15b2ebe33b996dcc'
signature = 'void func_804530A0(CPUState* ctx) {'
prefix, body = source.split(signature)
switch_end = body.index('    default: return;')
entry, rest = body[:switch_end], body[switch_end:]
cases = re.findall(r'^    case[^\n]+\n', entry, re.M)
assert len(cases) == 1024
leaders = [line for line in cases if 'ctx->downcount -=' not in line]
assert all(re.fullmatch(r'    case 0x[0-9A-F]+u: goto label_[0-9A-F]+;\n', line) for line in leaders)
slow = 'static __attribute__((noinline)) void entry_suffix_804530A0(CPUState* ctx) {'+body
normal_entry = entry
for line in cases:
    if line not in leaders:
        normal_entry = normal_entry.replace(line, '')
normal_rest = rest.replace('    default: return;',
                          '    default: entry_suffix_804530A0(ctx); return;', 1)
candidate = prefix+slow+'\n'+signature+normal_entry+normal_rest
# Original fallback and post-switch normal instructions are byte-exact.
assert slow.split('{', 1)[1] == body
assert normal_rest.replace('    default: entry_suffix_804530A0(ctx); return;',
                           '    default: return;', 1) == rest
output = root/'generated/chunk-entry-r182'
output.mkdir(exist_ok=True)
include = '#include "../RMGE01.h"'
absolute = '#include "'+str(generated/'RMGE01_generated/RMGE01.h')+'"'
(output/'reference.c').write_text(source.replace(include, absolute))
(output/'candidate.c').write_text(candidate.replace(include, absolute))
graph = (generated.parent/'module-build/build.ninja').read_text()
block = re.search(r'^build [^\n]*: C_COMPILER[^\n]*'+re.escape(str(source_path))+r'[^\n]*\n((?:  [^\n]*\n)*)', graph, re.M)
assert block
fields = dict(re.findall(r'^  (\w+) = (.*)$', block[1], re.M))
flags = shlex.split(fields['DEFINES']+' '+fields['INCLUDES']+' '+fields['FLAGS'])
# -S with LTO emits IR; inspect pre-link ARM64 assembly using all other flags.
flags = [flag for flag in flags if not flag.startswith('-flto')]
if args.no_profile:
    flags = [flag for flag in flags if not flag.startswith('-fprofile-instr-use=')]
print('entries', len(cases), 'normal leaders', len(leaders), 'suffix routes', len(cases)-len(leaders), flush=True)
for name in ('reference', 'candidate'):
    suffix = '-no-profile' if args.no_profile else ''
    subprocess.run(['clang', *flags, '-S', str(output/(name+'.c')),
                    '-o', str(output/(name+suffix+'.s'))], check=True)
    asm = (output/(name+suffix+'.s')).read_text()
    functions = re.findall(r'^(_[A-Za-z0-9_]+):[^\n]*\n(.*?)(?=^\s*\.cfi_endproc)', asm, re.M|re.S)
    for symbol, text in functions:
        if symbol in ('_func_804530A0', '_entry_suffix_804530A0'):
            instructions = re.findall(r'^\t([a-z][a-z0-9]*)\b', text, re.M)
            print(name, symbol, 'static instructions', len(instructions),
                  'loads', sum(op.startswith('ld') for op in instructions),
                  'stores', sum(op.startswith('st') for op in instructions), flush=True)
