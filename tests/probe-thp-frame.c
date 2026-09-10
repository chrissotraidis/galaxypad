/* Private offline execution probe. Not a runtime hook or a pixel-parity claim.
 * Build: clang -O2 -Iref/ModernGekko/include tests/probe-thp-frame.c -o generated/probe-thp-frame
 * Run only with audited exact module/DOL and local PrologueA.thp. */
#include "moderngekko/module_abi.h"
#include <assert.h>
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef THP_NATIVE_INNER
#include "GalaxyPadTHPDecoder.h"
#include "GalaxyPadTHPGuest.h"
static GalaxyPadTHPDecoder *native_decoder;
static unsigned native_bytes,native_calls;
#endif

static uint8_t lc[16384];
static uint32_t dmau, dmal, dma_bytes;
static uint8_t coverage[640*368*3/2];
static int track_output;
static unsigned block_entries;
static uint64_t generated_cycles;
static uint64_t inner_start_cycles;
static uint32_t inner_return,inner_info,inner_gqr[8],inner_fpscr;
static unsigned inner_active;
static const unsigned plane_start[3]={0x1200000,0x1300000,0x1400000};
static const unsigned plane_size[3]={640*368,320*184,320*184};
static uint32_t be32(const uint8_t *p) {
    return (uint32_t)p[0]<<24 | (uint32_t)p[1]<<16 | (uint32_t)p[2]<<8 | p[3];
}
static void unsupported(CPUState *s, uint32_t value, uint32_t pc) {
    unsigned spr=((value>>16)&31)|((value>>6)&992);
    if(value>>26==31 && ((value>>1)&1023)==467 && (spr==922 || spr==923)) {
        uint32_t v=s->gpr[(value>>21)&31];
        if(spr==922) dmau=v;
        else {
            dmal=v;
            if(v&2) {
                unsigned blocks=((dmau&31)<<2)|((v>>2)&3);
                unsigned bytes=(blocks ? blocks : 128)*32;
                uint32_t mem=(dmau&~31u)&0x3fffffff, cache=(v&~31u)&0x3ffff;
                assert((uint64_t)mem+bytes<=s->ram_size && cache+bytes<=sizeof lc);
                if(v&16) memcpy(lc+cache,s->ram+mem,bytes);
                else {
                    if(track_output) {
                        unsigned base=0,found=0;
                        for(unsigned p=0;p<3;p++) {
                            if(mem>=plane_start[p] && (uint64_t)mem+bytes<=plane_start[p]+plane_size[p]) {
                                for(unsigned i=0;i<bytes;i++) assert(++coverage[base+mem-plane_start[p]+i]==1);
                                found=1;break;
                            }
                            base+=plane_size[p];
                        }
                        assert(found);
                    }
                    memcpy(s->ram+mem,lc+cache,bytes);
                }
                dma_bytes+=bytes; dmal&=~2u;
            }
        }
        s->pc=pc+4; return;
    }
    fprintf(stderr,"unsupported instruction %08x at %08x\n",value,pc); exit(2);
}
static uint64_t read_external(CPUState *s, uint32_t a, uint8_t n) {
    if (a < 0xe0000000u || (uint64_t)a+n > 0xe0004000ull) {
        fprintf(stderr,"external read %08x at %08x\n",a,s->pc); exit(2);
    }
    uint64_t v=0; for(unsigned i=0;i<n;i++) v=v<<8|lc[a-0xe0000000u+i];
    return v;
}
static void write_external(CPUState *s,uint32_t a,uint64_t v,uint8_t n) {
    if(a>=0x80000000u && (uint64_t)(a-0x80000000u)+n<=s->ram_size) {
        for(unsigned i=0;i<n;i++)s->ram[a-0x80000000u+i]=(uint8_t)(v>>(8*(n-i-1)));
        return;
    }
    if (a < 0xe0000000u || (uint64_t)a+n > 0xe0004000ull) {
        fprintf(stderr,"external write %08x at %08x\n",a,s->pc); exit(2);
    }
    for(unsigned i=0;i<n;i++) lc[a-0xe0000000u+i]=(uint8_t)(v>>(8*(n-i-1)));
}
static void invoke(const ModernGekkoModuleDesc *m,CPUState *s,uint32_t pc) {
    s->pc=pc; s->lr=0x80000004; s->exception=0;
    for(unsigned i=0;i<1000000;i++) {
        /* Offline environment only: do not register SDK version with OS/EXI.
         * Decoder/init instructions still execute; this is not an OS-state oracle. */
        if(s->pc==0x804a1df8 && pc==0x80454820) {
            fprintf(stderr,"offline: omitting OSRegisterVersion side effects\n");
            s->pc=s->lr; continue;
        }
        if(s->pc==0x80000004) {
            printf("returned entry=%08x r3=%u dispatches=%u\n",pc,s->gpr[3],i); return;
        }
        s->downcount=100000;
        if(s->pc==0x80452398) {
            inner_active=1;inner_return=s->lr;inner_start_cycles=generated_cycles;
            inner_info=be32(s->ram+((s->gpr[13]-9084)&0x3fffffff))&0x3fffffff;
            assert((uint64_t)inner_info+1724<=s->ram_size);
            memcpy(inner_gqr,s->gqr,sizeof inner_gqr);inner_fpscr=s->fpscr;
        } else if(inner_active && s->pc==inner_return) {
            fprintf(stderr,"inner generated cycles=%llu gqr_preserved=%d fpscr_before=%08x after=%08x info=%08x\n",
                (unsigned long long)(generated_cycles-inner_start_cycles),
                !memcmp(inner_gqr,s->gqr,sizeof inner_gqr),inner_fpscr,s->fpscr,inner_info);
            fprintf(stderr,"inner info tail=");
            for(unsigned i=1668;i<1724;i+=4)fprintf(stderr," %u:%08x",i,be32(s->ram+inner_info+i));
            fputc('\n',stderr);inner_active=0;
        }
#ifdef THP_NATIVE_INNER
        if(s->pc==0x80452398) {
#ifdef THP_REAL_PATCH
            assert(GalaxyPadTHPDispatchInner(s,
#ifdef THP_NATIVE_REJECT
                                           NULL
#else
                                           native_decoder
#endif
                                           ));
            if(s->pc==s->lr)native_calls++;
            generated_cycles+=(uint64_t)(100000-s->downcount);
            continue;
#else
            uint8_t *planes[3];size_t sizes[3]={640*368,320*184,320*184};
            for(unsigned p=0;p<3;p++) {
                uint32_t a=s->gpr[3+p]&0x3fffffff;
                assert((uint64_t)a+sizes[p]<=s->ram_size);
                planes[p]=s->ram+a;
            }
            const uint8_t *packet=s->ram+0x1000000;size_t length=native_bytes;
#ifdef THP_PLAYER_WRAPPER
            GalaxyPadTHPGuestFrame frame;
            assert(GalaxyPadTHPResolveGuestFrame(s,&frame));
            packet=frame.packet;length=frame.bytes;
            assert(frame.width==640 && frame.height==368);
            for(unsigned p=0;p<3;p++) {assert(planes[p]==frame.planes[p]);assert(sizes[p]==frame.sizes[p]);}
#ifdef THP_NATIVE_REJECT
            length=3;
#endif
#endif
            if(GalaxyPadTHPDecode(native_decoder,packet,length,640,368,planes,sizes)) {
                native_calls++;s->pc=s->lr;continue;
            }
            // Failed native decode has not changed guest CPU or destinations.
#endif
        }
#endif
        if(s->pc==0x804526e8 || s->pc==0x80452b74) {
#ifdef THP_SPARSE_INPUT
            /* Isolated diagnostic input, never enabled in normal frame oracle. */
            if(block_entries==0) {
                uint32_t a=s->gpr[3]&0x3fffffff;
                assert((uint64_t)a+128<=s->ram_size);
                memset(s->ram+a,0,128);
                s->ram[a+3]=16; /* natural-order AC(1,0)=16, all other coefficients zero */
            }
#endif
            if(block_entries<6) {
                uint32_t q=be32(s->ram+((s->gpr[13]-9056)&0x3fffffff))&0x3fffffff;
                assert((uint64_t)q+256<=s->ram_size);
                fprintf(stderr,"quant %u bits=",block_entries);
                for(unsigned j=0;j<64;j++)fprintf(stderr,"%s%08x",j?",":"",be32(s->ram+q+4*j));
                fputc('\n',stderr);
            }
            if(block_entries<5520) {
                uint32_t a=s->gpr[3]&0x3fffffff;
                assert((uint64_t)a+128<=s->ram_size);
                fprintf(stderr,"block %u pc=%08x coefficients=",block_entries,s->pc);
                for(unsigned j=0;j<64;j++) {
                    uint8_t *b=s->ram+a+2*j;
                    fprintf(stderr,"%s%d",j?",":"",(int16_t)((unsigned)b[0]*256+b[1]));
                }
                fputc('\n',stderr);
            }
            block_entries++;
        }
        if(!m->dispatch(s,s->pc) || s->exception) {
            fprintf(stderr,"dispatch stop pc=%08x exception=%x srr0=%08x program=%x\n",
                    s->pc,s->exception,s->srr0,s->program_exception); exit(2);
        }
        assert(s->downcount<=100000);
        generated_cycles+=(uint64_t)(100000-s->downcount);
    }
    fprintf(stderr,"dispatch budget exhausted pc=%08x\n",s->pc); exit(2);
}
int main(int argc,char **argv) {
    assert(argc>=4 && argc<=6);
    void *handle=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);
    if(!handle) {fprintf(stderr,"%s\n",dlerror());return 2;}
    ModernGekkoGetModuleFn get=(ModernGekkoGetModuleFn)dlsym(handle,MODERNGEKKO_GET_MODULE_SYMBOL);
    assert(get); const ModernGekkoModuleDesc *m=get();
    assert(m->abi_version==3 && m->cpu_abi_version==3 && m->cpu_state_size==sizeof(CPUState));
    assert(!strcmp(m->game_id,"RMGE01"));
    CPUState s={0}; s.ram_size=24*1024*1024; s.ram=calloc(1,s.ram_size); assert(s.ram);
    FILE *f=fopen(argv[2],"rb"); assert(f); uint8_t header[256];
    assert(fread(header,1,256,f)==256);
    for(unsigned i=0;i<18;i++) {
        uint32_t off=be32(header+4*i), addr=be32(header+72+4*i), size=be32(header+144+4*i);
        if(!size)continue;
        assert(addr>=0x80000000 && (uint64_t)addr+size<=0x81800000);
        assert(!fseek(f,off,SEEK_SET)); assert(fread(s.ram+addr-0x80000000,1,size,f)==size);
    }
    fclose(f);
    s.gpr[1]=0x817f0000; s.gpr[2]=0x806ab280; s.gpr[13]=0x806a4ca0;
    s.hid2=0xb0000000; /* LSQE | PSE | LCE, matching paired/locked-cache prerequisites. */
    s.msr=0x2000; /* MSR[FP]: decoder uses paired floating point. */
    s.instruction_fallback=unsupported;
    s.external_read=read_external; s.external_write=write_external;
    invoke(m,&s,0x80454820); /* original THPInit */
    assert(s.gpr[3]==1);
    f=fopen(argv[3],"rb"); assert(f); uint8_t thp[48],frame[16];
    assert(fread(thp,1,48,f)==48 && !memcmp(thp,"THP\0",4));
    unsigned index=argc==6 ? (unsigned)strtoul(argv[5],NULL,10) : 0;
    assert(index<be32(thp+20));
    uint32_t offset=be32(thp+40), total=be32(thp+24);
    for(unsigned i=0;i<=index;i++) {
        assert(!fseek(f,offset,SEEK_SET)); assert(fread(frame,1,16,f)==16);
        if(i==index)break;
        assert(total>=16 && (uint64_t)offset+total<=0xffffffff);
        offset+=total; total=be32(frame);
    }
    uint32_t bytes=be32(frame+8); assert(bytes>0 && bytes<1024*1024);
    assert(fread(s.ram+0x1000000,1,bytes,f)==bytes); fclose(f);
#ifdef THP_NATIVE_INNER
    native_decoder=GalaxyPadTHPDecoderCreate();assert(native_decoder);native_bytes=bytes;
#ifdef THP_NATIVE_REJECT
    native_bytes=3; // Diagnostic rejection: original guest packet remains intact.
#endif
#endif
    s.gpr[3]=0x81000000; s.gpr[4]=0x81200000; s.gpr[5]=0x81300000;
    s.gpr[6]=0x81400000; s.gpr[7]=0x81500000;
    for(unsigned p=0;p<3;p++) {
        memset(s.ram+plane_start[p]-32,0xa5,plane_size[p]+64);
    }
    track_output=1;
#ifdef THP_PLAYER_WRAPPER
    uint8_t *player=s.ram+0x1600000;
    memcpy(player+0x50,thp,48);player[0xb4]=1;
    player[0x83]=2;player[0x85]=1;
    player[0x94]=0;player[0x95]=0;player[0x96]=2;player[0x97]=128;
    player[0x98]=0;player[0x99]=0;player[0x9a]=1;player[0x9b]=112;
    const uint32_t fields[][2]={{0xb0,0x81500000},{0xe8,0x80fffff0},{0xec,42},{0xf0,1},
                              {0x1d8,0x81200000},{0x1dc,0x81300000},{0x1e0,0x81400000}};
    for(unsigned i=0;i<sizeof fields/sizeof fields[0];i++)
        for(unsigned j=0;j<4;j++)player[fields[i][0]+j]=fields[i][1]>>(24-j*8);
    memcpy(s.ram+0xfffff0,frame,16);
    s.gpr[3]=0x81600000;s.gpr[4]=0x81000000;
    invoke(m,&s,0x8038d2e4);
    int success=s.gpr[3]==1;
    assert(success && be32(player+0x1e4)==42);
    puts("original player wrapper returned1 and assigned frameNumber42");
#else
    invoke(m,&s,0x804514ec);
    int success=s.gpr[3]==0;
#endif
    if(success) {
#ifndef THP_NATIVE_INNER
        for(unsigned i=0;i<sizeof coverage;i++) assert(coverage[i]==1);
#endif
        for(unsigned p=0;p<3;p++) for(unsigned i=0;i<32;i++) {
            assert(s.ram[plane_start[p]-32+i]==0xa5);
            assert(s.ram[plane_start[p]+plane_size[p]+i]==0xa5);
        }
        puts("32-byte boundary guards intact (original path also checks exact-once DMA coverage)");
    }
    printf("decoder result=%u DMA bytes=%u; output validation still required\n",s.gpr[3],dma_bytes);
    printf("observed inverse-transform entries=%u\n",block_entries);
    if(argc>=5 && success) {
        /* PrologueA geometry only; GX I8 planes, not a linear rawvideo image. */
#ifndef THP_NATIVE_INNER
        assert(dma_bytes==640*368*3/2);
#endif
        FILE *out=fopen(argv[4],"wbx"); assert(out);
        assert(fwrite(s.ram+0x1200000,1,640*368,out)==640*368);
        assert(fwrite(s.ram+0x1300000,1,320*184,out)==320*184);
        assert(fwrite(s.ram+0x1400000,1,320*184,out)==320*184);
        assert(!fclose(out));
    }
#ifdef THP_NATIVE_INNER
    printf("native inner calls=%u; guest cycle/work-state equivalence not established\n",native_calls);
#ifdef THP_NATIVE_REJECT
    assert(native_calls==0);
#else
    assert(native_calls==1);
#endif
    GalaxyPadTHPDecoderDestroy(native_decoder);
#endif
    free(s.ram); dlclose(handle); return success ? 0 : 2;
}
