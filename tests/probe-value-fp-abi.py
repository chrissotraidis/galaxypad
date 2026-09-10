"""Isolated paired-FP value ABI; exact arithmetic, no module/runtime mutation."""
from pathlib import Path
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
core = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
source = (core/'cpu_interpreter_float.c').read_text()
helpers = ['typedef struct { f64 first, second; } Pair;',
           'typedef struct { u32 fpscr; } FPStatus;']
# Transitive status-only callees: refuse any newly introduced CPUState field.
status_helpers = ['ppc_fpscr_updated', 'set_fp_exception', 'clear_fifr', 'set_fprf',
                  'force_single', 'ni_add', 'ni_sub', 'ni_mul']
def rename_status(text):
    for name in status_helpers:
        text = re.sub(r'\b'+name+r'\b', 'value_status_'+name, text)
    return text
for name in status_helpers:
    body = re.search(r'^\w+ '+name+r'\(.*?^}', source, re.M|re.S)[0]
    assert set(re.findall(r'cpu->(\w+)', body)) <= {'fpscr'}
    cpu_calls = set(re.findall(r'\b(\w+)\(cpu\s*[,)]', body)) - {name}
    assert cpu_calls <= set(status_helpers), (name, cpu_calls)
    helpers.append('static __attribute__((always_inline)) inline '+
                   rename_status(body.replace('CPUState', 'FPStatus')))
for operation, right in [('add', 'b'), ('sub', 'b'), ('mul', 'c')]:
    match = re.search(r'void ppc_ps_'+operation+r'_op\(.*?\n}', source, re.S)
    assert match
    body = match[0].split('{', 1)[1].rsplit('}', 1)[0]
    for register, arg in [('a', 'a'), (right, 'b')]:
        body = body.replace('cpu->fpr['+register+']', arg+'0')
        body = body.replace('cpu->ps1['+register+']', arg+'1')
    body = body.replace('ps_write_both(cpu, d, ps0, ps1);',
                        'f64 result0 = (f64)ps0; f64 result1 = (f64)ps1;')
    helpers.append('''
__attribute__((noinline)) Pair value_OP(u32* fpscr, f64 a0, f64 a1, f64 b0, f64 b1) {
    FPStatus local = {*fpscr};
    FPStatus* cpu = &local;
BODY
    *fpscr = local.fpscr;
    return (Pair){result0, result1};
}
static __attribute__((always_inline)) inline void candidate_OP(CPUState* cpu,u8 d,u8 a,u8 b) {
    Pair result = value_OP(&cpu->fpscr,cpu->fpr[a],cpu->ps1[a],cpu->fpr[b],cpu->ps1[b]);
    cpu->fpr[d]=result.first; cpu->ps1[d]=result.second;
}
'''.replace('OP',operation).replace('BODY',rename_status(body)))

matched_source = source
for name in status_helpers:
    matched_source, count = re.subn(r'^(\w+ '+name+r'\()',
        r'__attribute__((always_inline)) \1', matched_source, flags=re.M)
    assert count == 1
driver = r'''
#pragma STDC FENV_ACCESS ON
#include "cpu_interpreter_float.c"
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
#include <time.h>
HELPERS
typedef void (*Operation)(CPUState*,u8,u8,u8);
__attribute__((noinline)) void original_chain(CPUState* cpu) {
    ppc_ps_add_op(cpu,0,1,2); ppc_ps_mul_op(cpu,3,0,4); ppc_ps_sub_op(cpu,5,3,1);
}
__attribute__((noinline)) void candidate_chain(CPUState* cpu) {
    candidate_add(cpu,0,1,2); candidate_mul(cpu,3,0,4); candidate_sub(cpu,5,3,1);
}
static double now(void) {
    struct timespec t; assert(!clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t));
    return t.tv_sec + t.tv_nsec*1e-9;
}
int main(void) {
    Operation originals[]={ppc_ps_add_op,ppc_ps_sub_op,ppc_ps_mul_op};
    Operation candidates[]={candidate_add,candidate_sub,candidate_mul};
    const u64 special[]={0,0x8000000000000000ull,1,0x000fffffffffffffull,
        0x0010000000000000ull,0x3ff0000000000000ull,0x7fefffffffffffffull,
        0x7ff0000000000000ull,0xfff0000000000000ull,0x7ff0000000000001ull,
        0x7ff8000000000123ull,0xfff8000000000123ull};
    const u8 aliases[][3]={{0,1,2},{1,1,2},{2,1,2},{1,1,1}};
    u64 random=766, saved; unsigned cases=0;
    __asm__ volatile("mrs %0, fpcr":"=r"(saved));
    for(unsigned rn=0;rn<4;++rn)for(unsigned ni=0;ni<2;++ni)
    for(unsigned op=0;op<3;++op)for(unsigned alias=0;alias<4;++alias)
    for(unsigned i=0;i<2000;++i) {
        CPUState a={0}; a.fpscr=(random & ~(FPSCR_NI_BIT|3u))|rn|(ni?FPSCR_NI_BIT:0);
        for(unsigned reg=0;reg<6;++reg) {
            random^=random<<13;random^=random>>7;random^=random<<17;
            a.fpr[reg]=f64_value(i<144?special[(i+reg)%12]:random);
            random^=random<<13;random^=random>>7;random^=random<<17;
            a.ps1[reg]=f64_value(i<144?special[(i/12+reg)%12]:random);
        }
        CPUState b=a;
        ppc_fpscr_control_updated(&a); feclearexcept(FE_ALL_EXCEPT);
        originals[op](&a,aliases[alias][0],aliases[alias][1],aliases[alias][2]);
        int af=fetestexcept(FE_ALL_EXCEPT);
        ppc_fpscr_control_updated(&b); feclearexcept(FE_ALL_EXCEPT);
        candidates[op](&b,aliases[alias][0],aliases[alias][1],aliases[alias][2]);
        int bf=fetestexcept(FE_ALL_EXCEPT);
        assert(!memcmp(&a,&b,sizeof a) && af==bf);
        ++cases;
    }
    __asm__ volatile("msr fpcr, %0"::"r"(saved));
    printf("%u full-CPU/host-flag paired ABI cases pass\n",cases);
    CPUState initial={0}; initial.fpscr=0; ppc_fpscr_control_updated(&initial);
    for(unsigned r=0;r<32;++r) {initial.fpr[r]=(r+1)/7.0;initial.ps1[r]=-(r+1)/9.0;}
    CPUState original=initial,candidate=initial;
    original_chain(&original); candidate_chain(&candidate);
    assert(!memcmp(&original,&candidate,sizeof original));
#ifndef CORRECTNESS_ONLY
    for(unsigned run=0;run<4;++run) {
        CPUState cpu=initial; int candidate_run=run==1||run==2;
        void (*fn)(CPUState*)=candidate_run?candidate_chain:original_chain;
        double start=now();
        for(unsigned i=0;i<1000000;++i) fn(&cpu);
        printf("chain candidate=%d ns/call=%.3f checksum=%llx\n",candidate_run,
            (now()-start)*1000,(unsigned long long)f64_bits(cpu.fpr[5]));
    }
#endif
    __asm__ volatile("msr fpcr, %0"::"r"(saved));
}
'''.replace('HELPERS','\n'.join(helpers)).replace('#include "cpu_interpreter_float.c"', matched_source)
with tempfile.TemporaryDirectory(prefix='galaxypad-value-abi-') as directory:
    stage=Path(directory); cpp=stage/'probe.c';cpp.write_text(driver)
    flags=['clang','-O2','-std=c11','-ffp-contract=off','-fno-fast-math',
           '-I'+str(core),'-I'+str(core.parent.parent/'include')]
    subprocess.run([*flags,'-DCORRECTNESS_ONLY','-fsanitize=undefined','-Wl,-dead_strip',str(cpp),
                    '-o',str(stage/'probe')],check=True)
    subprocess.run([str(stage/'probe')],check=True)
    subprocess.run([*flags,'-Wl,-dead_strip',str(cpp),'-o',str(stage/'release')],check=True)
    subprocess.run([str(stage/'release')],check=True)
    subprocess.run([*flags,'-S',str(cpp),'-o',str(stage/'probe.s')],check=True)
    assembly=(stage/'probe.s').read_text()
    for name in ['original_chain','candidate_chain','ppc_ps_add_op','ppc_ps_sub_op',
                 'ppc_ps_mul_op','value_add','value_sub','value_mul']:
        body=re.search(r'^_'+name+r':.*?\.cfi_endproc',assembly,re.M|re.S)[0]
        instructions=re.findall(r'^\t[a-z][a-z0-9.]*\s',body,re.M)
        calls=re.findall(r'^\tbl\s+([^\n]+)',body,re.M)
        print(name,'static_instructions=',len(instructions),'calls=',calls)
print('Isolated value ABI only: scratch FPSCR observer proof, installed-policy parity and gameplay unproven')
