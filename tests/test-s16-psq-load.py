"""Exhaustive exact signed16 loads plus fallback/callback ordering."""
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
from s16_psq_load import HELPER,transform
from psq_scale import reference_source
source=(root/'generated/thp-kernels-r198-exits/candidate.c').read_text()
changed=transform(source)
marker='static __attribute__((noinline, flatten)) bool thp_kernel_0('
assert changed.split(marker,1)[1].replace('galaxy_s16_load(', 'ppc_psq_load_inline(')==source.split(marker,1)[1]
assert changed.count('galaxy_s16_load(ctx,')==16
try:
    transform(source+'\n')
except ValueError:
    pass
else:
    raise AssertionError('Unpinned source accepted')
core=root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
cpu_reference=reference_source((core/'cpu.c').read_text())
program=r'''
#pragma STDC FENV_ACCESS ON
#include "cpu.c"
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
HELPER
static u8 ram[64];
static CPUState cpu;
static unsigned callbacks;
static u64 digest;
static u64 callback(CPUState* c,u32 address,u8 size) {
 assert(c==&cpu); callbacks++;
 const u8* p=(const u8*)c;
 for(size_t i=0;i<sizeof(*c);i++)digest=(digest^p[i])*1099511628211ull;
 digest=(digest^address)*1099511628211ull;digest=(digest^size)*1099511628211ull;
 // First read changes the fields the original helper snapshots before reading.
 c->gqr[5]=0x1f040000u;c->hid2=0;
 c->fpscr^=0x12345678u;c->fpr[10]=-11;c->ps1[10]=-12;
 return 0x8001u+callbacks;
}
static void compare(CPUState initial,u32 ea,bool w,bool indexed) {
 cpu=initial;callbacks=0;digest=14695981039346656037ull;
 assert(feclearexcept(FE_ALL_EXCEPT)==0);
 bool expected=ppc_psq_load_inline(&cpu,10,ea,w,5,indexed,0x80452750u);
 CPUState state=cpu;unsigned reads=callbacks;u64 trace=digest;
 int flags=fetestexcept(FE_ALL_EXCEPT);
 cpu=initial;callbacks=0;digest=14695981039346656037ull;
 assert(feclearexcept(FE_ALL_EXCEPT)==0);
 bool actual=galaxy_s16_load(&cpu,10,ea,w,5,indexed,0x80452750u);
 assert(actual==expected&&!memcmp(&state,&cpu,sizeof cpu));
 assert(reads==callbacks&&trace==digest&&flags==fetestexcept(FE_ALL_EXCEPT));
}
int main(void) {
 const int modes[]={FE_TONEAREST,FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO};
 unsigned cases=0;
 for(unsigned mode=0;mode<4;mode++) {
  assert(fesetround(modes[mode])==0);
  CPUState c={0};c.ram=ram;c.ram_size=64;c.hid2=PPC_HID2_LSQE;
  c.gqr[5]=0xc0ffabcdu;c.external_read=callback;
  c.gqr[5]=(c.gqr[5]&~0x3f070000u)|0x00070000u;
  for(unsigned i=0;i<65536;i++) {
   write_be16(ram+1,(u16)i);write_be16(ram+3,(u16)~i);
   compare(c,0x80000001u,false,false);cases++;
  }
  for(unsigned type=0;type<8;type++)for(unsigned scale=0;scale<64;scale++)
   for(unsigned options=0;options<8;options++) {
    c.gqr[5]=(scale<<24)|(type<<16);c.hid2=(options&1)?PPC_HID2_LSQE:0;
    compare(c,0xfffffffEu,options&2,options&4);cases++;
   }
 }
 printf("%u exhaustive signed16 and fallback/callback state/flags cases pass\n",cases);
}
'''.replace('HELPER',HELPER)
with tempfile.TemporaryDirectory(prefix='galaxypad-s16-') as temporary:
    directory=Path(temporary)
    (directory/'cpu.c').write_text(cpu_reference)
    harness=directory/'probe.c';harness.write_text(program)
    for name,flags in [('sanitized',['-O1','-fsanitize=address,undefined']),('optimized',['-O2'])]:
        binary=directory/name
        subprocess.run(['clang','-std=c11',*flags,'-ffp-contract=off','-fno-fast-math',
                        '-ffunction-sections','-fdata-sections','-I',str(core),
                        '-I',str(core.parent.parent/'include'),str(harness),
                        str(core/'cpu_interpreter_float.c'),str(core/'cpu_exception.c'),
                        '-Wl,-dead_strip','-lm','-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
