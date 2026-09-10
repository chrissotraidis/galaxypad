"""Isolated actual-decoder block entry experiment, not a generator change.

Requires the accepted private generated source. No game launch or selection.
"""
from pathlib import Path
import hashlib
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
module = Path((root/'generated/modules/RMGE01/active-module.txt').read_text().strip())
source = (module.parent/'dolrecomp-output/RMGE01_generated/chunks/chunk_1103_text1_804530A0.c').read_text()
assert hashlib.sha256(source.encode()).hexdigest() == 'e6aa915816ee2a89534f75c4d59dd0c145f7a5d0162c3e1a15b2ebe33b996dcc'
addresses = ['80453AAC', '80453AB0', '80453AB4', '80453AB8']
cases = '\n'.join(re.search(r'case 0x'+pc+r'u: [^\n]+', source)[0] for pc in addresses)
body = 'label_80453AAC:'+source.split('label_80453AAC:', 1)[1].split('label_80453ABC:', 1)[0]
assert body.count('goto ') == 1
body = body.replace('goto label_80453AC8;', 'return 0x80453AC8u;')+'return 0x80453ABCu;\n'
normal = re.sub(r'label_[0-9A-F]+:', '', body)
program = '''
#include "core/cpu.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
__attribute__((noinline)) u32 reference(CPUState* ctx) {
 switch(ctx->pc) { CASES default: return 0; }
 BODY
}
__attribute__((noinline)) u32 normal_entry(CPUState* ctx) { NORMAL }
__attribute__((noinline)) u32 separated(CPUState* ctx) {
 if (ctx->pc == 0x80453AACu) return normal_entry(ctx);
 return reference(ctx);
}
static u32 random_word(u32* s) { *s ^= *s<<13; *s ^= *s>>17; *s ^= *s<<5; return *s; }
int main(void) {
 u32 seed=0x198321af, addresses[]={0x80453AAC,0x80453AB0,0x80453AB4,0x80453AB8};
 for(unsigned i=0;i<100000;i++) for(unsigned entry=0;entry<4;entry++) {
  CPUState a={0};
  for(unsigned r=0;r<32;r++) a.gpr[r]=random_word(&seed);
  a.cr=random_word(&seed);a.xer=random_word(&seed);a.pc=addresses[entry];
  a.downcount=(int)(i%100)-50;
  if(i<64) a.gpr[31]=i<32? (1u<<i):0;
  CPUState b=a; u32 left=reference(&a),right=separated(&b);
  assert(left==right); assert(!memcmp(&a,&b,sizeof a));
  assert(a.downcount==(int)(i%100)-50-(int)(4-entry));
 }
 puts("400000 full-state/branch-target/all-entry/cycle comparisons passed");
}
'''.replace('CASES', cases).replace('BODY', body).replace('NORMAL', normal)
includes = ['-I', str(root/'ref/ModernGekko/vendor/dolphin/GXRuntime/include')]
with tempfile.TemporaryDirectory(prefix='galaxypad-block-entry-') as directory:
    temp = Path(directory)
    path = temp/'probe.c'
    path.write_text(program)
    subprocess.run(['clang', '-O1', '-std=c11', '-fsanitize=address,undefined',
                    *includes, str(path), '-o', str(temp/'probe')], check=True)
    subprocess.run([str(temp/'probe')], check=True)
    subprocess.run(['clang', '-O2', '-std=c11', '-S', *includes, str(path),
                    '-o', str(temp/'probe.s')], check=True)
    asm = (temp/'probe.s').read_text()
    for name in ('reference', 'normal_entry', 'separated'):
        function = asm.split('_'+name+':', 1)[1].split('.cfi_endproc', 1)[0]
        instructions = re.findall(r'^\s+([a-z][a-z0-9]*)\s', function, re.M)
        print(name, 'instructions', len(instructions), 'loads',
              sum(op.startswith('ld') for op in instructions), 'stores',
              sum(op.startswith('st') for op in instructions))
        print(function)
