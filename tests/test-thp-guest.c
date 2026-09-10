#include "GalaxyPadTHPGuest.h"
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
static void put(uint8_t *p,uint32_t v){p[0]=v>>24;p[1]=v>>16;p[2]=v>>8;p[3]=v;}
int main(void){
    CPUState s={0};s.ram_size=8*1024*1024;s.ram=calloc(1,s.ram_size);assert(s.ram);
    s.pc=0x80452398;s.lr=0x80451750;s.gpr[1]=0x80000100;s.gpr[26]=0x80001010;
    uint8_t *stack=s.ram+0x100,*p=s.ram+0x200,*b=s.ram+0x1000;
    put(stack+36,0x8038d310);put(stack+28,0x80000200);
    memcpy(p+0x50,"THP\0",4);put(p+0x54,0x11000);put(p+0x58,4096);
    p[0xb4]=1;put(p+0x80,2);p[0x85]=1;put(p+0x94,640);put(p+0x98,368);
    s.gpr[13]=0x806a4ca0;put(s.ram+0x6a4ca0-9084,0x800f0000);put(p+0xb0,0x800f0000);
    uint8_t *info=s.ram+0xf0000;info[1682]=2;info[1683]=128;info[1684]=1;info[1685]=112;
    put(info+1692,0x80001030);
    put(p+0xe8,0x80001000);put(p+0xf0,1);put(b+8,1024);put(b+12,128);b[16]=0xff;b[17]=0xd8;
    for(unsigned i=0;i<3;i++){s.gpr[3+i]=0x80010000+i*0x40000;put(p+0x1d8+i*4,s.gpr[3+i]);}
    CPUState before=s;GalaxyPadTHPGuestFrame f;
    assert(GalaxyPadTHPResolveGuestFrame(&s,&f));assert(f.packet==b+16 && f.bytes==1024);
    assert(!memcmp(&before,&s,sizeof s));
    s.lr++;assert(!GalaxyPadTHPResolveGuestFrame(&s,&f));s.lr--;
    put(p+0xc8,20);assert(!GalaxyPadTHPResolveGuestFrame(&s,&f));put(p+0xc8,0);
    put(b+8,4096);assert(!GalaxyPadTHPResolveGuestFrame(&s,&f));put(b+8,1024);
    put(p+0xf0,0);assert(!GalaxyPadTHPResolveGuestFrame(&s,&f));put(p+0xf0,1);
    s.gpr[26]++;assert(!GalaxyPadTHPResolveGuestFrame(&s,&f));s.gpr[26]--;
    s.gpr[3]=0xe0000000;put(p+0x1d8,s.gpr[3]);assert(!GalaxyPadTHPResolveGuestFrame(&s,&f));
    free(s.ram);puts("guest eligibility positive/caller/index/span/validity/pointer/MMIO rejection checks passed");
}
