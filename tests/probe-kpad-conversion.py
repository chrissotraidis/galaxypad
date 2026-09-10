#!/usr/bin/env python3
"""Run the accepted generated retail coordinate block against a scalar oracle.

Finite-input arithmetic doubles only: not FPSCR, filtering, KPAD tracking or
full emulator equivalence. No generated files or runtime configuration changed.
"""
from pathlib import Path
import hashlib
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
module=Path((root/'generated/modules/RMGE01/active-module.txt').read_text().strip())
source=(module.parent/'dolrecomp-output/RMGE01_generated/chunks/chunk_1099_text1_8044F0A0.c').read_text()
body='label_8044FA6C:'+source.split('label_8044FA6C:',1)[1].split('label_8044FB30:',1)[0]
print('generated_source_sha256='+hashlib.sha256(source.encode()).hexdigest(),flush=True)
preamble=r'''
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>
#include <assert.h>
#include <stdio.h>
typedef uint32_t u32; typedef int32_t s32; typedef int8_t s8; typedef double f64;
typedef struct {u32 gpr[32],pc,cr,xer; int64_t downcount; double fpr[32],ps1[32];} CPUState;
static uint8_t memory[65536];
static u32 mem_read32(CPUState*c,u32 a){(void)c;assert(a+4<=sizeof(memory));return (u32)memory[a]<<24|(u32)memory[a+1]<<16|(u32)memory[a+2]<<8|memory[a+3];}
static uint8_t mem_read8(CPUState*c,u32 a){(void)c;assert(a<sizeof(memory));return memory[a];}
static void mem_write32(CPUState*c,u32 a,u32 v){(void)c;assert(a+4<=sizeof(memory));for(unsigned i=0;i<4;i++)memory[a+i]=v>>(24-i*8);}
static double dolrecomp_f32_from_bits(u32 u){float f;memcpy(&f,&u,4);return f;}
static u32 dolrecomp_f32_to_bits(double d){float f=d;u32 u;memcpy(&u,&f,4);return u;}
static uint64_t dolrecomp_f64_to_bits(double d){uint64_t u;memcpy(&u,&d,8);return u;}
static double dolrecomp_f64_from_bits(uint64_t u){double d;memcpy(&d,&u,8);return d;}
static bool ppc_fp_available_inline(CPUState*c,u32 a){(void)c;(void)a;return true;}
static void ppc_fmuls(CPUState*c,unsigned d,unsigned a,unsigned b){c->fpr[d]=(float)(c->fpr[a]*c->fpr[b]);}
static void ppc_fadds(CPUState*c,unsigned d,unsigned a,unsigned b){c->fpr[d]=(float)(c->fpr[a]+c->fpr[b]);}
static void ppc_fsubs(CPUState*c,unsigned d,unsigned a,unsigned b){c->fpr[d]=(float)(c->fpr[a]-c->fpr[b]);}
static void run(CPUState*ctx){
'''
checks=r'''
}
static void set(u32 a,float f){mem_write32(0,a,dolrecomp_f32_to_bits(f));}
int main(){
 for(int i=0;i<1000;i++){
  CPUState c={0};c.gpr[30]=0x1000;c.gpr[1]=0x8000;c.gpr[2]=0xa000;
  float t=i*.013f, sx=cosf(t),sy=sinf(t),hx=cosf(t*.7f),hy=sinf(t*.7f);
  float ax=cosf(t*.3f),ay=sinf(t*.3f),mx=sinf(t)*.8f,my=cosf(t)*.6f;
  float cx=.1f*cosf(t),cy=-.2f,scale=1+(i%13)*.2f;
  set(0x1000+7000,sy);set(0x1000+6996,sx);set(0x10b0,hx);set(0x10b4,hy);
  set(0x10a8,ax);set(0x10ac,ay);set(0x10f4,mx-.1f);set(0x1100,mx+.1f);
  set(0x10f8,my);set(0x1104,my);set(0x10b8,cx);set(0x10bc,cy);set(0x10c0,scale);
  set(0xa000+0x206c,.5f);
  run(&c);
  float dot=sx*hx+sy*hy,cross=-sy*hx+sx*hy;
  float vx=(cx-(dot*mx-cross*my))*scale,vy=(cy-(cross*mx+dot*my))*scale;
  float ox=-ay*vx+ax*vy,oy=-ax*vx-ay*vy;
  double rx=dolrecomp_f32_from_bits(mem_read32(&c,0x8010));
  double ry=dolrecomp_f32_from_bits(mem_read32(&c,0x8014));
  assert(fabs(rx-ox)<2e-6 && fabs(ry-oy)<2e-6);
  assert(c.pc==0x8044fb2c);
 }
 puts("Retail generated midpoint/rotation/scale block: 1000 finite cases agree; tracking/filtering/FPSCR excluded");
}
'''
if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='galaxypad-kpad-') as temp:
        path=Path(temp)
        (path/'probe.c').write_text(preamble+body+checks)
        subprocess.run(['xcrun','clang','-std=c11','-fsanitize=address,undefined',
                        str(path/'probe.c'),'-o',str(path/'probe')],check=True)
        subprocess.run([str(path/'probe')],check=True)
