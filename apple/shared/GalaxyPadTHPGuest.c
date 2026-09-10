#include "GalaxyPadTHPGuest.h"
#include <string.h>
static uint32_t read32(const uint8_t *p) {
    return (uint32_t)p[0]<<24|(uint32_t)p[1]<<16|(uint32_t)p[2]<<8|p[3];
}
static uint8_t *mapped(const CPUState *s,uint32_t a,size_t n) {
    if(a>=0x80000000u && a<0x81800000u && s->ram &&
       (uint64_t)a+n<=0x81800000ull &&
       (uint64_t)(a-0x80000000u)+n<=s->ram_size)return s->ram+(a-0x80000000u);
    if(a>=0x90000000u && a<0x94000000u && s->exram &&
       (uint64_t)a+n<=0x94000000ull &&
       (uint64_t)(a-0x90000000u)+n<=s->exram_size)return s->exram+(a-0x90000000u);
    return NULL;
}
int GalaxyPadTHPResolveGuestFrame(const CPUState *s,GalaxyPadTHPGuestFrame *out) {
    if(!s || !out || s->pc!=0x80452398 || s->lr!=0x80451750 || s->exception)return 0;
    const uint8_t *stack=mapped(s,s->gpr[1],40);
    if(!stack || read32(stack+36)!=0x8038d310)return 0;
    // THPVideoDecode saved the wrapper's r31 at stack+28 before using r31 locally.
    const uint8_t *player=mapped(s,read32(stack+28),0x1e8);
    if(!player || memcmp(player+0x50,"THP\0",4) || read32(player+0x54)!=0x11000 ||
       !player[0xb4] || read32(player+0x80)!=2 || player[0x84]!=0 || player[0x85]!=1)return 0;
    unsigned index=read32(player+0xc8),capacity=read32(player+0x58);
    if(index>=20 || capacity<16 || capacity>4*1024*1024)return 0;
    const uint8_t *entry=player+0xe8+index*12;
    if(read32(entry+8)!=1)return 0;
    uint32_t buffer_address=read32(entry);
    const uint8_t *buffer=mapped(s,buffer_address,capacity);
    if(!buffer || (uint64_t)buffer_address+16!=s->gpr[26])return 0;
    unsigned bytes=read32(buffer+8),audio=read32(buffer+12);
    if(bytes<4 || (uint64_t)16+bytes+audio>capacity || buffer[16]!=0xff || buffer[17]!=0xd8)return 0;
    GalaxyPadTHPGuestFrame f={0};
    f.width=read32(player+0x94);f.height=read32(player+0x98);
    if(!f.width || !f.height || f.width>640 || f.height>480 || f.width%16 || f.height%16)return 0;
    if(s->gpr[13]<9084)return 0;
    const uint8_t *global=mapped(s,s->gpr[13]-9084,4);
    uint32_t work=read32(player+0xb0);
    if(!global || work>UINT32_MAX-31 || read32(global)!=((work+31)&~31u))return 0;
    const uint8_t *info=mapped(s,read32(global),1724);
    if(!info || ((unsigned)info[1682]*256+info[1683])!=f.width ||
       ((unsigned)info[1684]*256+info[1685])!=f.height)return 0;
    uint32_t cursor=read32(info+1692);
    if(cursor<s->gpr[26] || (uint64_t)cursor>=(uint64_t)s->gpr[26]+bytes)return 0;
    // Active supported wrapper passes texture-set0 directly in this exact DOL.
    for(unsigned p=0;p<3;p++) {
        if(s->gpr[3+p]!=read32(player+0x1d8+4*p))return 0;
        f.sizes[p]=(size_t)f.width*f.height/(p?4:1);
        f.planes[p]=mapped(s,s->gpr[3+p],f.sizes[p]);
        if(!f.planes[p])return 0;
        const uint8_t *protected[]={stack,player,buffer,info};
        size_t protected_sizes[]={40,0x1e8,capacity,1724};
        uintptr_t a=(uintptr_t)f.planes[p];
        for(unsigned i=0;i<4;i++) {
            uintptr_t b=(uintptr_t)protected[i];
            if(a<b+protected_sizes[i] && b<a+f.sizes[p])return 0;
        }
    }
    f.packet=buffer+16;f.bytes=bytes;*out=f;return 1;
}
