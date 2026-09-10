#!/usr/bin/env python3
"""Print Apple's compiler ABI for real pinned CPU helper declarations.

Read-only diagnostic: success is not LLVM-backend compatibility acceptance.
No game input, generated module, dependency mutation or linking is involved.
"""
import argparse
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--clang', default='/usr/bin/clang')
args = parser.parse_args()
source = r'''
#include "cpu/cpu.h"
u32 audit_spr(CPUState* cpu, u16 spr, u32 pc) {
  return ppc_mfspr(cpu, spr, pc);
}
void audit_lswx(CPUState* cpu, u8 d, u8 a, u8 b, u32 pc) {
  ppc_lswx(cpu, d, a, b, pc);
}
'''
includes = ROOT / 'ref/ModernGekko/vendor/dolphin/DolRecomp/src'
print(subprocess.check_output([args.clang, '--version'], text=True).splitlines()[0])
for target in ('arm64-apple-macos14', 'arm64-apple-ios17.0-simulator'):
    result = subprocess.run(
        [args.clang, '-target', target, '-S', '-emit-llvm', '-O1',
         '-I', str(includes), '-x', 'c', '-', '-o', '-'],
        input=source, text=True, capture_output=True, check=True)
    print(target)
    for helper, expected in (('ppc_mfspr', 1), ('ppc_lswx', 3)):
        declaration = next(line for line in result.stdout.splitlines()
                           if line.startswith('declare ') and '@' + helper + '(' in line)
        if len(re.findall(r'\bzeroext\b', declaration)) != expected:
            raise SystemExit('Unexpected ABI; inspect compiler output: ' + declaration)
        print(declaration)
print('Compiler ABI observed; hand-written backend call sites require a separate audit.')
