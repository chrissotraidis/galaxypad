#include "GalaxyPadTHPDecoder.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned be32(const unsigned char *p) {return (unsigned)p[0]<<24|(unsigned)p[1]<<16|p[2]<<8|p[3];}
int main(int argc,char **argv) {
    assert(argc==3);
    FILE *f=fopen(argv[1],"rb");assert(f);unsigned char header[48],fh[16];
    assert(fread(header,1,48,f)==48);assert(!fseek(f,be32(header+40),SEEK_SET));
    assert(fread(fh,1,16,f)==16);size_t bytes=be32(fh+8);assert(bytes<4*1024*1024);
    unsigned char *packet=malloc(bytes);assert(packet && fread(packet,1,bytes,f)==bytes);fclose(f);
    size_t sizes[3]={640*368,320*184,320*184};
    unsigned char *storage[3],*planes[3];
    for(int p=0;p<3;p++){storage[p]=malloc(sizes[p]+64);assert(storage[p]);memset(storage[p],0xa5,sizes[p]+64);planes[p]=storage[p]+32;}
    unsigned char *expected=malloc(353280);assert(expected);
    f=fopen(argv[2],"rb");assert(f && fread(expected,1,353280,f)==353280);fclose(f);
    GalaxyPadTHPDecoder *d=GalaxyPadTHPDecoderCreate();assert(d);
    for(int attempt=0;attempt<16;attempt++) {
        assert(GalaxyPadTHPDecode(d,packet,bytes,640,368,planes,sizes));
        size_t offset=0;
        for(unsigned p=0;p<3;p++) {
            unsigned w=p?320:640,h=p?184:368;
            for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++)
                assert(planes[p][((y/4)*(w/8)+x/8)*32+(y%4)*8+x%8]==expected[offset+y*w+x]);
            for(unsigned i=0;i<32;i++)assert(storage[p][i]==0xa5 && planes[p][sizes[p]+i]==0xa5);
            offset+=sizes[p];
        }
        // Failure and recovery each iteration; rejection must preserve every byte.
        unsigned char *before=malloc(353280);assert(before);offset=0;
        for(unsigned p=0;p<3;p++){memcpy(before+offset,planes[p],sizes[p]);offset+=sizes[p];}
        size_t short_sizes[3]={sizes[0]-1,sizes[1],sizes[2]};
        unsigned char invalid[4]={0};
        assert(!GalaxyPadTHPDecode(d,packet,bytes,640,368,planes,short_sizes));
        assert(!GalaxyPadTHPDecode(d,invalid,4,640,368,planes,sizes));
        assert(!GalaxyPadTHPDecode(d,packet,bytes,624,368,planes,sizes));
        unsigned char *overlap[3]={planes[0],planes[0],planes[2]};
        assert(!GalaxyPadTHPDecode(d,packet,bytes,640,368,overlap,sizes));
        offset=0;for(unsigned p=0;p<3;p++){assert(!memcmp(before+offset,planes[p],sizes[p]));offset+=sizes[p];}
        free(before);
    }
    GalaxyPadTHPDecoderDestroy(d);for(int p=0;p<3;p++)free(storage[p]);free(packet);free(expected);
    puts("16 decode/reject/recovery iterations: exact prototype output, guarded writes, failure atomicity passed");
}
