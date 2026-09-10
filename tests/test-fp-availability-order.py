"""Exact helper/exception differential test and isolated check-order assembly."""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
runtime = root/'ref/ModernGekko/vendor/dolphin/GXRuntime'
header = (runtime/'include/core/cpu.h').read_text()
start = header.index('static inline bool ppc_fp_available_inline(')
end = header.index('\n}',start)+2
original = header[start:end]
old = '!g_ppc_lazy_fp_enabled || (cpu->msr & PPC_MSR_FP)'
new = '(cpu->msr & PPC_MSR_FP) || !g_ppc_lazy_fp_enabled'
assert original.count(old) == 1
reference = original.replace('static inline bool ppc_fp_available_inline',
    '__attribute__((noinline)) bool reference_check')
candidate = reference.replace('reference_check','candidate_check').replace(old,new)
out = root/'generated/fp-availability-order-r472'
out.mkdir(exist_ok=False)
program = r'''
#include "core/cpu.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
bool g_ppc_lazy_fp_enabled;
unsigned exception_calls;
bool ppc_fp_raise_unavailable(CPUState* cpu,u32 cia) {
    ++exception_calls;
    ppc_take_exception(cpu,PPC_EXC_FP_UNAVAILABLE,PPC_VECTOR_FP_UNAVAILABLE,cia,0);
    return false;
}
REFERENCE
CANDIDATE
int main(void) {
    unsigned cases=0; u32 seed=0x4722026;
    for(unsigned i=0;i<200000;++i) {
        CPUState initial={0};
        seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;
        initial.msr=seed; initial.pc=seed^0xabcdef; initial.srr0=~seed;
        initial.srr1=seed>>3; initial.exception=seed & 0x7f;
        initial.downcount=-(s64)seed; initial.fpscr=seed>>8;
        for(unsigned flag=0;flag<2;++flag) for(unsigned fp=0;fp<2;++fp) {
            initial.msr=(initial.msr & ~PPC_MSR_FP)|(fp?PPC_MSR_FP:0);
            CPUState a=initial,b=initial;
            g_ppc_lazy_fp_enabled=flag;
            exception_calls=0;bool ra=reference_check(&a,seed);unsigned ca=exception_calls;
            exception_calls=0;bool rb=candidate_check(&b,seed);
            assert(ra==rb && ca==exception_calls && memcmp(&a,&b,sizeof(a))==0);
            assert(ra==(!flag||fp)); assert(ca==(flag&&!fp));
            ++cases;
        }
    }
    printf("%u full-state availability/exception comparisons pass\n",cases);
}
'''.replace('REFERENCE',reference).replace('CANDIDATE',candidate)
src = out/'probe.c'; src.write_text(program)
common = ['clang','-std=c11','-I'+str(runtime/'include'),str(src),
          str(runtime/'src/core/cpu_exception.c')]
for name, flags in [('sanitized',['-O1','-fsanitize=address,undefined']),('optimized',['-O2'])]:
    binary = out/name
    subprocess.run([*common,*flags,'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
subprocess.run(['clang','-std=c11','-O2','-I'+str(runtime/'include'),'-S',str(src),
                '-o',str(out/'probe.s')],check=True)
print('Assembly retained; no runtime header or module modified')
