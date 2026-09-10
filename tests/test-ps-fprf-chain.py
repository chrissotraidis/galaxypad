"""Isolated proof for dead intermediate FPRF writes; never changes runtime.

Only consecutive non-recording arithmetic operations with no observer between
them are in scope. This is not permission to omit flags at a block exit, Rc
instruction, memory callback, exception boundary, or external entry.
"""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
core = root / 'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
source = (core / 'cpu_interpreter_float.c').read_text()
parts = []
for op in ('add', 'sub', 'mul', 'madd'):
    signature = 'void ppc_ps_' + op + '_op('
    start = source.index(signature)
    brace = source.index('{', start)
    depth, end = 1, brace + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    body = source[start:end]
    write = '    set_fprf(cpu, classify_f32(ps0));'
    assert body.count(write) == 1
    parts.append(body.replace(signature, 'static void deferred_' + op + '(')
                 .replace(write, ''))

program = r'''
#pragma STDC FENV_ACCESS ON
#include "cpu_interpreter_float.c"
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
DEFERRED_HELPERS
static u64 random_bits(u64* seed) {
    *seed ^= *seed << 13; *seed ^= *seed >> 7; *seed ^= *seed << 17;
    return *seed;
}
static void operation(CPUState* c, unsigned op, bool deferred, unsigned d,
                      unsigned a, unsigned b, unsigned k, unsigned variant) {
    switch(op) {
    case 0: if(deferred) deferred_add(c,d,a,b); else ppc_ps_add_op(c,d,a,b); break;
    case 1: if(deferred) deferred_sub(c,d,a,b); else ppc_ps_sub_op(c,d,a,b); break;
    case 2: if(deferred) deferred_mul(c,d,a,k); else ppc_ps_mul_op(c,d,a,k); break;
    case 3: if(deferred) deferred_madd(c,d,a,k,b,variant&1,variant&2);
            else ppc_ps_madd_op(c,d,a,k,b,variant&1,variant&2); break;
    }
}
int main(void) {
    const int modes[]={FE_TONEAREST,FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO};
    const u64 special[]={0,0x8000000000000000ull,1,0x000fffffffffffffull,
      0x0010000000000000ull,0x380fffffffffffffull,0x3810000000000000ull,
      0x7fefffffffffffffull,0x7ff0000000000000ull,0xfff0000000000000ull,
      0x7ff0000000000001ull,0x7ff8000000000123ull,0xfff8000000000123ull};
    u64 seed=0x76ca34121ull;
    unsigned count=0, different=0;
    for(unsigned mode=0;mode<4;mode++) {
      assert(fesetround(modes[mode])==0);
      for(unsigned first=0;first<4;first++) for(unsigned last=0;last<4;last++)
      for(unsigned i=0;i<4000;i++) {
        CPUState a={0};a.fpscr=(u32)random_bits(&seed);
        for(unsigned r=0;r<4;r++) {
          a.fpr[r]=f64_value(i<169?special[(i/13+r)%13]:random_bits(&seed));
          a.ps1[r]=f64_value(i<169?special[(i%13+r)%13]:random_bits(&seed));
        }
        CPUState b=a;
        assert(feclearexcept(FE_ALL_EXCEPT)==0);
        operation(&a,first,false,i%4,0,1,2,i);
        int flags=fetestexcept(FE_ALL_EXCEPT);
        assert(feclearexcept(FE_ALL_EXCEPT)==0);
        operation(&b,first,true,i%4,0,1,2,i);
        assert(flags==fetestexcept(FE_ALL_EXCEPT));
        different += ((a.fpscr^b.fpscr)&(0x1fu<<12))!=0;
        CPUState masked=a;
        masked.fpscr=(masked.fpscr&~(0x1fu<<12))|(b.fpscr&(0x1fu<<12));
        assert(!memcmp(&masked,&b,sizeof a));
        // The next writer consumes the previous result as an operand.
        assert(feclearexcept(FE_ALL_EXCEPT)==0);
        operation(&a,last,false,(i+1)%4,i%4,2,3,i>>2);
        flags=fetestexcept(FE_ALL_EXCEPT);
        assert(feclearexcept(FE_ALL_EXCEPT)==0);
        operation(&b,last,false,(i+1)%4,i%4,2,3,i>>2);
        assert(flags==fetestexcept(FE_ALL_EXCEPT));
        assert(!memcmp(&a,&b,sizeof a));
        count++;
      }
    }
    assert(different>0); // An intermediate observer would see different state.
    printf("%u chains agree in full final state/host flags; %u intermediate FPRF differences\n",count,different);
}
'''.replace('DEFERRED_HELPERS', '\n'.join(parts))
with tempfile.TemporaryDirectory(prefix='galaxypad-fprf-chain-') as directory:
    temp = Path(directory)
    (temp / 'probe.c').write_text(program)
    subprocess.run(['clang', '-O2', '-std=c11', '-ffp-contract=off',
                    '-fno-fast-math', '-fsanitize=undefined',
                    '-ffunction-sections', '-fdata-sections', '-Wl,-dead_strip',
                    '-I', str(core), '-I', str(core.parent.parent / 'include'),
                    str(temp / 'probe.c'), '-o', str(temp / 'probe')], check=True)
    subprocess.run([str(temp / 'probe')], check=True)
