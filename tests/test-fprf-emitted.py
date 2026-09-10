"""Execute actual emitted entry/availability/cycle paths with deferred FPRF.

Isolated experiment: no reference source or generated module is modified.
"""
from pathlib import Path
import importlib.util
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
vendor = root/'ref/ModernGekko/vendor/dolphin'
src = vendor/'DolRecomp/src'
core = vendor/'GXRuntime/src/core'
spec = importlib.util.spec_from_file_location('regions', root/'scripts/audit-fprf-regions.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

def extract(text, signature):
    start = text.index(signature)
    brace = text.index('{', start)
    end, depth = brace + 1, 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]

helpers = []
floats = (core/'cpu_interpreter_float.c').read_text()
for op in ('add', 'sub', 'mul'):
    signature = 'void ppc_ps_' + op + '_op('
    body = extract(floats, signature)
    write = '    set_fprf(cpu, classify_f32(ps0));'
    assert body.count(write) == 1
    helpers.append(body.replace(signature, 'static void deferred_' + op + '(').replace(write, ''))
raise_fp = extract((core/'cpu.c').read_text(), 'bool ppc_fp_raise_unavailable(')

driver = r'''
#include "backend/emitter.h"
int main(void) {
    PPCInst inst[5]={0};
    for(unsigned i=0;i<5;i++) inst[i].address=0x80001000+4*i;
    inst[0]=ppc_decode(0x60000000,0x80001000);
    inst[1].op=PPC_OP_PS_ADD;inst[1].rD=0;inst[1].rA=1;inst[1].rB=2;
    inst[2].op=PPC_OP_PS_SUB;inst[2].rD=1;inst[2].rA=0;inst[2].rB=2;
    inst[3].op=PPC_OP_PS_MUL;inst[3].rD=2;inst[3].rA=1;inst[3].rC=0;
    inst[4].op=PPC_OP_MFFS;inst[4].rD=3;
    return !emit_function(stdout,inst,5,0x80001000);
}
'''
runner = r'''
static u64 random_bits(u64* seed) {
    *seed ^= *seed << 13; *seed ^= *seed >> 7; *seed ^= *seed << 17;
    return *seed;
}
int main(void) {
    const int modes[]={FE_TONEAREST,FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO};
    u64 seed=0x352794621ull;unsigned count=0;
    for(unsigned mode=0;mode<4;mode++) {
      assert(fesetround(modes[mode])==0);
      for(unsigned entry=0;entry<5;entry++)
      for(unsigned lazy=0;lazy<2;lazy++) for(unsigned enabled=0;enabled<2;enabled++)
      for(unsigned i=0;i<1000;i++) {
        CPUState a={0};a.pc=0x80001000+4*entry;
        a.msr=enabled?PPC_MSR_FP:0;a.fpscr=(u32)random_bits(&seed);
        a.downcount=(i&1)?-5000:100;
        for(unsigned r=0;r<4;r++) {
          a.fpr[r]=f64_value(random_bits(&seed));a.ps1[r]=f64_value(random_bits(&seed));
        }
        CPUState b=a;g_ppc_lazy_fp_enabled=lazy;
        feclearexcept(FE_ALL_EXCEPT);func_80001000(&a);
        int flags=fetestexcept(FE_ALL_EXCEPT);
        feclearexcept(FE_ALL_EXCEPT);candidate_80001000(&b);
        assert(flags==fetestexcept(FE_ALL_EXCEPT));
        assert(!memcmp(&a,&b,sizeof a));
        if(lazy&&!enabled) {
          assert(a.exception&PPC_EXC_FP_UNAVAILABLE);
          assert(a.srr0==0x80001000+4*(entry?entry:1));
        } else {
          assert(a.pc==0x80001014);
          assert(f64_bits(a.fpr[3])==(0xFFF8000000000000ull|a.fpscr));
        }
        count++;
      }
    }
    printf("%u emitted entry/FP-availability/downcount/observer comparisons passed\n",count);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-fprf-emitted-') as directory:
    temp = Path(directory)
    (temp/'driver.c').write_text(driver)
    subprocess.run(['clang','-O1','-fsanitize=address,undefined','-I',str(src),
                    str(temp/'driver.c'),str(src/'backend/emitter.c'),
                    str(src/'backend/c_cfg.c'),str(src/'frontend/decoder.c'),
                    '-o',str(temp/'driver')],check=True)
    emitted = subprocess.check_output([str(temp/'driver')],text=True)
    eligible = audit.regions('\n'+emitted)
    assert eligible == [0x80001004,0x80001008], eligible
    candidate = emitted.replace('func_80001000', 'candidate_80001000')
    for address in eligible:
        marker = f'label_{address:08X}:\n'
        start = candidate.index(marker)
        end = candidate.find('\nlabel_',start)
        body = candidate[start:end]
        body, n = re.subn(r'ppc_ps_(add|sub|mul)_op\(', r'deferred_\1(', body)
        assert n == 1
        candidate = candidate[:start]+body+candidate[end:]
    prefix = '''#pragma STDC FENV_ACCESS ON
#include "cpu_interpreter_float.c"
#include "cpu_exception.c"
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
bool g_ppc_lazy_fp_enabled=false;
static f64 dolrecomp_f64_from_bits(u64 bits) {return f64_value(bits);}
'''
    (temp/'probe.c').write_text(prefix+raise_fp+'\n'+'\n'.join(helpers)+'\n'+emitted+candidate+runner)
    subprocess.run(['clang','-O2','-std=c11','-ffp-contract=off','-fno-fast-math',
                    '-fsanitize=address,undefined','-ffunction-sections','-fdata-sections',
                    '-Wl,-dead_strip','-I',str(core),'-I',str(vendor/'GXRuntime/include'),
                    str(temp/'probe.c'),'-o',str(temp/'probe')],check=True)
    subprocess.run([str(temp/'probe')],check=True)
