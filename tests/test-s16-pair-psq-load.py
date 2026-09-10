"""Four-byte mapped signed16 pair against the actual original helper."""
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
from s16_pair_psq_load import HELPER,transform
source=(root/'generated/thp-kernels-r198-exits/candidate.c').read_text()
changed=transform(source)
marker='static __attribute__((noinline, flatten)) bool thp_kernel_0('
assert changed.split(marker,1)[1].replace('galaxy_s16_pair_load(', 'ppc_psq_load_inline(')==source.split(marker,1)[1]
assert changed.count('galaxy_s16_pair_load(ctx,')==16
try:
    transform(source+'\n')
except ValueError:
    pass
else:
    raise AssertionError('Unpinned source accepted')
core=root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
header=(core.parent.parent/'include/core/cpu.h').read_bytes()
assert hashlib.sha256(header).hexdigest()=='7fc1448116c581afc53f2c41c6e3b3d11b3a580c5e71147cb52fca493e0d4657'
cpu_reference=(core/'cpu.c').read_text()
assert hashlib.sha256(cpu_reference.encode()).hexdigest()=='05e221c01bead6801c51217f84398bd10f22e1b810f6d06977e04d8a801436ea'
program=r'''
#pragma STDC FENV_ACCESS ON
#include "cpu.c"
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
static unsigned mapped_pairs;
HELPER
static u8 ram[256],exram[256],replacement[256];
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
 c->ram=replacement;c->ram_size=256;c->exram=NULL;c->exram_size=0;
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
 bool actual=galaxy_s16_pair_load(&cpu,10,ea,w,5,indexed,0x80452750u);
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
 // Independent mapping boundaries, mirrors and undersized mappings; backing
 // arrays are intentionally larger than declared sizes for safe legacy cases.
 const u32 bases[]={0x80000000u,0xc0000000u,0x90000000u,0xd0000000u};
 const u32 sizes[]={1,2,3,4,5,63,64,65};
 const u32 offsets[]={0,1,2,3,4,61,62,63,64,65,255,256};
 for(unsigned i=0;i<256;i++) {
  ram[i]=(u8)(i*31u);exram[i]=(u8)(i*47u);replacement[i]=(u8)(i*71u);
 }
 for(unsigned memory=0;memory<4;memory++)
  for(unsigned size=0;size<8;size++) for(unsigned offset=0;offset<12;offset++) {
   // For size1 the legacy size-2 expression underflows. Only safe backed
   // offsets are sampled; never dereference its giant synthetic range.
   if(sizes[size]<2 && offsets[offset]>4)continue;
   CPUState c={0};c.ram=ram;c.ram_size=sizes[size];
   c.exram=memory>=2?exram:NULL;c.exram_size=sizes[size];
   c.hid2=PPC_HID2_LSQE;c.gqr[5]=0x70000u;c.external_read=callback;
   compare(c,bases[memory]+offsets[offset],false,false);cases++;
  }
 // Oversized declarations must retain original lookup precedence. Restrict
 // addresses to actually backed bytes, not an invented giant allocation.
 for(unsigned memory=0;memory<2;memory++) for(unsigned offset=0;offset<4;offset++) {
  CPUState c={0};c.ram=ram;c.ram_size=memory?64:0xffffffffu;
  c.exram=memory?exram:NULL;c.exram_size=0xffffffffu;
  c.hid2=PPC_HID2_LSQE;c.gqr[5]=0x70000u;c.external_read=callback;
  compare(c,(memory?0x90000000u:0x80000000u)+offset,false,false);cases++;
 }
 // Pointer metadata and lane values remain observable in CPUState aliases.
 // compare() uses the same global CPU address for both executions.
 for(unsigned memory=0;memory<2;memory++) for(int delta=-2;delta<=4;delta++) {
  CPUState c={0};c.ram=memory?ram:(u8*)&cpu;c.ram_size=memory?256:sizeof cpu;
  c.exram=memory?(u8*)&cpu:NULL;c.exram_size=sizeof cpu;
  c.hid2=PPC_HID2_LSQE;c.gqr[5]=0x70000u;c.fpr[10]=17.25;c.ps1[10]=-3.5;
  u32 ea=(memory?0x90000000u:0x80000000u)+(u32)offsetof(CPUState,fpr)+10u*8u+delta;
  compare(c,ea,false,false);cases++;
 }
 assert(mapped_pairs>=4u*65536u);
 printf("%u signed16 pair/state/flags/boundary/remap/alias cases pass; mapped=%u\n",cases,mapped_pairs);
}
'''.replace('HELPER',HELPER.replace('   cpu->fpr[frD]=','   ++mapped_pairs; cpu->fpr[frD]='))
with tempfile.TemporaryDirectory(prefix='galaxypad-s16-pair-') as temporary:
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
