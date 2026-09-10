"""Audit and execute the exact isolated candidate's real decoder chains.

Requires prepared generated/fprf-r167 source artifacts; never runs the game.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
exp = root/'generated/fprf-r167'
# Keep the measured experiment's reference independent of current selection.
generated = (root/'generated/modules-midblock-r144/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-da63c951ce4d7349/dolrecomp-output').resolve()
core = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
name = 'chunk_1102_text1_804520A0.c'
original = (generated/'RMGE01_generated/chunks'/name).read_text()
assert hashlib.sha256(original.encode()).hexdigest() == '2dc3b915db7bd33c84a0481499fefd0ee91a201bc20cb6540248caf06729d539'
candidate = (exp/name).read_text()
spec = importlib.util.spec_from_file_location('audit',root/'scripts/audit-fprf-regions.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

def extract(text, signature):
    start = text.index(signature); brace = text.index('{',start)
    end, depth = brace+1, 1
    while depth:
        depth += (text[end]=='{')-(text[end]=='}');end += 1
    return text[start:end]

floats = (core/'cpu_interpreter_float.c').read_text()
canonical_helpers = '\nvoid galaxypad_deferred_add(' in floats
if canonical_helpers:
    floats = floats.split('\nvoid galaxypad_deferred_add(', 1)[0]
new_float = (exp/'cpu_interpreter_float.c').read_text()
assert new_float.startswith(floats+'\n')
helpers = []
declarations = []
for op in ('add','sub','mul','madd'):
    helper = extract(new_float,'void galaxypad_deferred_'+op+'(')
    expected = extract(floats,'void ppc_ps_'+op+'_op(').replace(
        'ppc_ps_'+op+'_op(', 'galaxypad_deferred_'+op+'(').replace(
        '    set_fprf(cpu, classify_f32(ps0));','')
    assert helper == expected
    helpers.append(helper)
    declarations.append(helper.split('{',1)[0].strip()+';')
assert new_float == floats+'\n'+'\n'.join(helpers)+'\n'
prefix = '#include "'+str(generated/'RMGE01_generated/RMGE01.h')+'"\n'+'\n'.join(declarations)
assert candidate.count(prefix) == 1
restored = candidate.replace(prefix,'#include "../RMGE01.h"')
restored = re.sub(r'galaxypad_deferred_(add|sub|mul|madd)\(',r'ppc_ps_\1_op(',restored)
assert restored == original
eligible = set(audit.regions(original))
assert len(eligible) == 119
assert eligible == set(json.loads((exp/'build-provenance.json').read_text())['sites'])

def blocks(text):
    labels = list(audit.LABEL.finditer(text))
    return {int(label[1],16): text[label.end():labels[i+1].start()]
            for i,label in enumerate(labels[:-1])}

old, new = blocks(original), blocks(candidate)
chains = []
for start in sorted(eligible):
    if start-4 in eligible:
        continue
    end = start
    while end in eligible:
        end += 4
    assert audit.BODY.fullmatch(old[end])
    chains.append(list(range(start,end+1,4)))

functions = []
pairs = []
for chain in chains:
    # Also execute every suffix, corresponding to external entry at each label.
    for offset in range(len(chain)):
        addresses = chain[offset:]
        index = len(pairs)
        for kind, source in [('reference',old),('candidate',new)]:
            functions.append('static void '+kind+str(index)+'(CPUState* ctx) {\n'+
                             ''.join(source[pc] for pc in addresses)+'}\n')
        pairs.append('{reference'+str(index)+',candidate'+str(index)+'}')

program = r'''
#pragma STDC FENV_ACCESS ON
#include "cpu_interpreter_float.c"
#include "cpu_exception.c"
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
bool g_ppc_lazy_fp_enabled=false;
RAISE
HELPERS
FUNCTIONS
typedef void (*Run)(CPUState*);
static Run pairs[][2]={PAIRS};
static u64 random_bits(u64* seed) {
 *seed^=*seed<<13;*seed^=*seed>>7;*seed^=*seed<<17;return *seed;
}
int main(void) {
 const int modes[]={FE_TONEAREST,FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO};
 const u64 special[]={0,0x8000000000000000ull,1,0x000fffffffffffffull,
  0x0010000000000000ull,0x7fefffffffffffffull,0x7ff0000000000000ull,
  0xfff0000000000000ull,0x7ff0000000000001ull,0x7ff8000000000123ull};
 u64 seed=0x12467731ull;unsigned count=0;
 for(unsigned m=0;m<4;m++) {
  assert(fesetround(modes[m])==0);
  for(unsigned p=0;p<sizeof(pairs)/sizeof(pairs[0]);p++)
  for(unsigned i=0;i<100;i++) {
   CPUState a={0};a.fpscr=random_bits(&seed);
   g_ppc_lazy_fp_enabled=(i%3)!=0;a.msr=(i%3==1)?0:PPC_MSR_FP;
   for(unsigned r=0;r<32;r++) {
    a.fpr[r]=f64_value(i<30?special[(i+r)%10]:random_bits(&seed));
    a.ps1[r]=f64_value(i<30?special[(i*3+r)%10]:random_bits(&seed));
   }
   CPUState b=a;
   feclearexcept(FE_ALL_EXCEPT);pairs[p][0](&a);int flags=fetestexcept(FE_ALL_EXCEPT);
   feclearexcept(FE_ALL_EXCEPT);pairs[p][1](&b);
   assert(flags==fetestexcept(FE_ALL_EXCEPT));assert(!memcmp(&a,&b,sizeof a));count++;
  }
 }
 printf("%u exact candidate decoder-chain/suffix full-state+host-flag comparisons passed\n",count);
}
'''.replace('RAISE',extract((core/'cpu.c').read_text(),'bool ppc_fp_raise_unavailable('))
program = program.replace('HELPERS','' if canonical_helpers else '\n'.join(helpers)).replace('FUNCTIONS','\n'.join(functions)).replace('PAIRS',','.join(pairs))
with tempfile.TemporaryDirectory(prefix='galaxypad-fprf-source-') as directory:
    temp = Path(directory)
    (temp/'probe.c').write_text(program)
    subprocess.run(['clang','-O1','-std=c11','-ffp-contract=off','-fno-fast-math',
                    '-fsanitize=address,undefined','-ffunction-sections','-fdata-sections',
                    '-Wl,-dead_strip','-I',str(core),'-I',str(core.parent.parent/'include'),
                    str(temp/'probe.c'),'-o',str(temp/'probe')],check=True)
    subprocess.run([str(temp/'probe')],check=True)
print(f'Exact source delta verified: 119 sites, {len(chains)} maximal chains, {len(pairs)} suffixes')
