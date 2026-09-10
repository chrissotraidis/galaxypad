/* Test actual offline harness transfer callback without game/module inputs. */
#define main thp_probe_main
#include "probe-thp-frame.c"
#undef main

static void mtspr(CPUState *s,unsigned spr,unsigned v) {
    s->gpr[6]=v;
    uint32_t op=(31u<<26)|(6u<<21)|((spr&31)<<16)|((spr>>5)<<11)|(467u<<1);
    unsupported(s,op,0x80001000);
    assert(s->pc==0x80001004);
}
int main(void) {
    CPUState s={0};s.ram_size=16384;s.ram=malloc(s.ram_size);assert(s.ram);
    for(unsigned load=0;load<2;load++) for(unsigned blocks=1;blocks<=128;blocks++) {
        unsigned length=blocks*32,encoded=blocks==128?0:blocks;
        memset(s.ram,0xa5,s.ram_size);memset(lc,0x5a,sizeof lc);
        uint8_t *src=load?s.ram+256:lc+128,*dst=load?lc+128:s.ram+256;
        for(unsigned i=0;i<length;i++)src[i]=(uint8_t)(i*31+blocks);
        dmau=dmal=dma_bytes=0;
        mtspr(&s,922,0x80000100|(encoded>>2));
        /* Without DMA_T, register write must not transfer. */
        mtspr(&s,923,0xe0000080|((encoded&3)<<2)|(load<<4));
        assert(dma_bytes==0 && dst[0]==(load?0x5a:0xa5));
        mtspr(&s,923,0xe0000080|((encoded&3)<<2)|(load<<4)|2);
        assert(dma_bytes==length && !(dmal&2));
        assert(!memcmp(src,dst,length));
        assert(dst[-1]==(load?0x5a:0xa5) && dst[length]==(load?0x5a:0xa5));
    }
    free(s.ram);puts("256 DMA length/direction cases passed, including zero-encoded128 blocks");
}
