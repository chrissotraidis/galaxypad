"""Execute all exact changed sites against real FP/exception helpers."""
from pathlib import Path
import hashlib
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root/'scripts'))
from thp_dead_pc import PATTERN, transform
from psq_scale import reference_source

source = (root/'generated/thp-kernels-r198-exits/candidate.c').read_text()
changed = transform(source)
core = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
cpu_reference = reference_source((core/'cpu.c').read_text())
for name, expected in (
    ('cpu_interpreter_float.c', '554149a2e7d08783402af38e5a2b898aff476370b0e3a6af0ed4bd411aab934f'),
):
    assert hashlib.sha256((core/name).read_bytes()).hexdigest() == expected

cases = []
for match in PATTERN.finditer(source.split('\nvoid func_804520A0(', 1)[0]):
    pc, next_pc = match['pc'], match['next']
    assert int(next_pc, 16) == int(pc, 16)+4
    before = match[0].split(':\n', 1)[1]
    after = changed.split(f'\nlabel_{pc}:\n', 1)[1].split(f'\nlabel_{next_pc}:', 1)[0]
    assert after != before
    cases.append(f'''case {len(cases)}:
        if (candidate) {{ {after} }} else {{ {before} }}
        ctx->pc = 0x{next_pc}u;
        observe(ctx);
        return true;
''')
assert len(cases) == 95

program = r'''
#pragma STDC FENV_ACCESS ON
#include "core/cpu.h"
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
#include <string.h>
static CPUState observed;
static unsigned calls;
static void observe(CPUState* cpu) {
    observed=*cpu;calls++;
    cpu->pc ^= 0x543210;cpu->xer ^= 0x80000000;
}
static bool run(CPUState* ctx,unsigned site,bool candidate) {
    switch(site) { CASES default: assert(0); return false; }
}
static u64 seed=0x839c01f42;
static u64 random_bits(void) {seed^=seed<<13;seed^=seed>>7;seed^=seed<<17;return seed;}
int main(void) {
 const int modes[]={FE_TONEAREST,FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO};
 const u64 special[]={0,0x8000000000000000ull,1,0x000fffffffffffffull,
  0x0010000000000000ull,0x7fefffffffffffffull,0x7ff0000000000000ull,
  0xfff0000000000000ull,0x7ff0000000000001ull,0x7ff8000000000123ull};
 unsigned count=0,faults=0,observations=0;
 for(unsigned m=0;m<4;m++) for(unsigned site=0;site<95;site++)
 for(unsigned mode=0;mode<4;mode++) for(unsigned n=0;n<128;n++) {
  CPUState a={0};
  a.pc=(u32)random_bits();a.fpscr=(u32)random_bits();a.msr=(u32)random_bits();
  a.msr=(a.msr&~PPC_MSR_FP)|((mode&1)?PPC_MSR_FP:0);
  a.exception=(u32)random_bits();a.srr0=(u32)random_bits();a.srr1=(u32)random_bits();
  a.downcount=(s64)(n%7)-3;a.ctr=random_bits();a.lr=random_bits();
  for(unsigned r=0;r<32;r++) {
   a.gpr[r]=(u32)random_bits();
   u64 v=n<100?special[(n+r)%10]:random_bits();memcpy(&a.fpr[r],&v,8);
   v=n<100?special[(n/10+r)%10]:random_bits();memcpy(&a.ps1[r],&v,8);
  }
  CPUState b=a;g_ppc_lazy_fp_enabled=(mode&2)!=0;
  assert(fesetround(modes[m])==0);assert(feclearexcept(FE_ALL_EXCEPT)==0);
  calls=0;memset(&observed,0,sizeof observed);bool ar=run(&a,site,false);
  int flags=fetestexcept(FE_ALL_EXCEPT);CPUState ao=observed;unsigned ac=calls;
  assert(fesetround(modes[m])==0);assert(feclearexcept(FE_ALL_EXCEPT)==0);
  calls=0;memset(&observed,0,sizeof observed);bool br=run(&b,site,true);
  assert(ar==br && flags==fetestexcept(FE_ALL_EXCEPT));
  assert(ac==calls && !memcmp(&ao,&observed,sizeof ao));
  assert(!memcmp(&a,&b,sizeof a));
  assert(ar==!(mode==2));assert(calls==(ar?1u:0u));
  faults+=!ar;observations+=calls;count++;
 }
 printf("%u direct-entry cases over95sites: %u unavailable faults, %u next-PC observers; full state and host flags match\n",count,faults,observations);
}
'''.replace('CASES', '\n'.join(cases))
with tempfile.TemporaryDirectory(prefix='galaxypad-dead-pc-entries-') as directory:
    temp = Path(directory)
    (temp/'cpu.c').write_text(cpu_reference)
    (temp/'test.c').write_text(program)
    for flags in (['-O1', '-fsanitize=address,undefined'], ['-O2']):
        subprocess.run(['clang', '-std=c11', *flags, '-ffp-contract=off', '-fno-fast-math',
                        '-ffunction-sections', '-fdata-sections', '-Wl,-dead_strip',
                        '-I', str(core.parent.parent/'include'), str(temp/'test.c'),
                        str(temp/'cpu.c'), str(core/'cpu_interpreter_float.c'),
                        str(core/'cpu_exception.c'), '-o', str(temp/'test')], check=True)
        subprocess.run([str(temp/'test')], check=True)
