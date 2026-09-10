#!/usr/bin/env python3
"""Execute generated retail position-filter branches with finite FP/sqrt doubles."""
from pathlib import Path
import runpy
import re
import subprocess
import tempfile

shared=runpy.run_path(str(Path(__file__).with_name('probe-kpad-conversion.py')))
source=shared['source']
body='label_8044FB60:'+source.split('label_8044FB60:',1)[1].split('label_8044FCA0:',1)[0]
prefix=shared['preamble'].split('static void run(CPUState*ctx){')[0].replace('gpr[32],pc,cr,xer','gpr[32],pc,cr,xer,lr')
prefix+=r'''
static void ppc_fdivs(CPUState*c,unsigned d,unsigned a,unsigned b){c->fpr[d]=(float)(c->fpr[a]/c->fpr[b]);}
static void ppc_frsp(CPUState*c,unsigned d,unsigned a){c->fpr[d]=(float)c->fpr[a];}
static void ppc_fcmp(CPUState*c,unsigned field,double a,double b,bool ordered){
 (void)ordered;u32 bits=a<b?8:a>b?4:2;unsigned shift=28-field*4;
 c->cr=(c->cr&~(15u<<shift))|(bits<<shift);
}
static void run(CPUState*ctx){switch(ctx->pc){
'''
for pc in ['8044FB60','8044FB88','8044FBEC','8044FC5C']:
    prefix+=re.search(r'case 0x'+pc+r'u: [^\n]+',source)[0]+'\n'
prefix+='default:assert(false);}\n'
suffix=r'''
label_8044FCA0:ctx->pc=0x8044fca0;
}
static void set(u32 a,float f){mem_write32(0,a,dolrecomp_f32_to_bits(f));}
static float get(u32 a){return dolrecomp_f32_from_bits(mem_read32(0,a));}
int main(){
 float radii[]={0,.03f},distances[]={0,.001f,.015f,.03f,.031f,.1f,1},sensitivities[]={0,.5f,1};
 unsigned count=0;
 for(unsigned mode=0;mode<2;mode++)for(unsigned r=0;r<2;r++)
 for(unsigned d=0;d<7;d++)for(unsigned s=0;s<3;s++){
  memset(memory,0,sizeof(memory));CPUState c={0};c.gpr[30]=0x1000;c.gpr[1]=0x8000;
  c.gpr[2]=0xa000;c.gpr[13]=0x6000;c.pc=0x8044fb60;
  float radius=radii[r],sensitivity=sensitivities[s];
  set(0x1020,.2f);set(0x1024,-.3f);set(0x1084,radius);set(0x1088,sensitivity);
  mem_write32(&c,0x1000+7144,mode);set(0xa000+0x207c,1);
  c.fpr[3]=(float)(.2f+distances[d]*.6f);c.fpr[2]=(float)(-.3f+distances[d]*.8f);
  float dx=(float)c.fpr[3]-.2f,dy=(float)c.fpr[2]+.3f;
  float length=sqrtf(dx*dx+dy*dy),factor;
  if(!mode){factor=length>=radius?1:powf(length/radius,4);factor*=sensitivity;}
  else factor=length>radius?(length-radius)/length*sensitivity:0;
  unsigned calls=0;
  while(c.pc!=0x8044fca0){
   assert(calls++<8);run(&c);
   if(c.pc==0x80527078){c.fpr[1]=sqrt(c.fpr[1]);c.pc=c.lr;}
  }
  assert(fabsf(get(0x1020)-(.2f+dx*factor))<1e-6f);
  assert(fabsf(get(0x1024)-(-.3f+dy*factor))<1e-6f);
  assert(fabsf(get(0x1028)-dx*factor)<1e-6f && fabsf(get(0x102c)-dy*factor)<1e-6f);
  count++;
 }
 printf("Retail generated filter: %u finite cases pass both modes, radius boundaries and sensitivities; FPSCR/tracking excluded\n",count);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-filter-') as temp:
    path=Path(temp)
    (path/'probe.c').write_text(prefix+body+suffix)
    subprocess.run(['xcrun','clang','-std=c11','-fsanitize=address,undefined',
                    str(path/'probe.c'),'-o',str(path/'probe')],check=True)
    subprocess.run([str(path/'probe')],check=True)
