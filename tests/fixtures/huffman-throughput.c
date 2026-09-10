/* Synthetic canonical two-code tables: 0=zero/EOB, 1=nonzero category.
 * No game data. Completed Y blocks only; not full movie acceptance. */
#include "core/cpu.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
void reference_chunk(CPUState*);
void candidate_chunk(CPUState*);
PPCMemWriteJournal g_mem_write_journal;
void* g_mem_write_journal_user;
unsigned dolrecomp_call_depth;
static u8 memory[0x600000], expected[0x600000];
static CPUState initial;
static unsigned active_category;
static const u32 patterns[]={0,0xffffffffu,0xaaaaaaaau,0x55555555u};
/* Model only per-dispatch accumulator reset, not Dolphin scheduling/events.
 * Restore total charge at return so the oracle still compares exact charges. */
static void fixture_dispatch(void(*fn)(CPUState*),CPUState* cpu,s64* charge) {
#ifdef RUNTIME_CHARGE_RESET
    cpu->downcount=0;
#endif
    fn(cpu);
#ifdef RUNTIME_CHARGE_RESET
    *charge+=cpu->downcount;
#else
    (void)charge;
#endif
}
static u64 bad_read(CPUState* c,u32 ea,u8 size) {
    fprintf(stderr,"unexpected read pc=%08x ea=%08x size=%u\n",c->pc,ea,size);assert(0);return 0;
}
static void bad_write(CPUState* c,u32 ea,u64 value,u8 size) {
    (void)value;(void)c;(void)ea;(void)size;assert(0);
}
static void setup(unsigned pattern,unsigned category,unsigned count) {
    active_category=category;
    memset(memory,0,sizeof memory);memset(&initial,0,sizeof initial);
    initial.ram=memory;initial.ram_size=sizeof memory;
    initial.gpr[1]=0x8000e000;initial.gpr[3]=0x80001000;
    initial.gpr[4]=0x80004000;initial.gpr[13]=0x80008000;
    initial.pc=0x804534b4;initial.lr=0x90001000;
    initial.external_read=bad_read;initial.external_write=bad_write;
    initial.reserve_valid=true;initial.reserve_addr=0xc0004000;
    write_be32(memory+0x8000-8800,0x80002000);
    write_be32(memory+0x8000-8896,0x80003000);
    for(unsigned i=0;i<32;i++) {
        memory[0x2000+i]=memory[0x3000+i]=i<16?0:category;
        memory[0x2020+i]=memory[0x3020+i]=1;
    }
    for(unsigned i=0;i<64;i++) memory[0x547df8+i]=(u8)i;
    for(unsigned i=0;i<1024;i+=4) write_be32(memory+0x6000+i,patterns[pattern]);
    write_be32(memory+0x1000+1692,0x80006000);
    write_be32(memory+0x1000+1696,patterns[pattern]);
    write_be32(memory+0x1000+1700,count);
}
static CPUState decode(void(*fn)(CPUState*),unsigned pattern,unsigned count,bool verify) {
    CPUState cpu=initial;
    memset(memory+0x4000,0xa5,128);
    write_be16(memory+0x1000+1668,7);
    write_be32(memory+0x1000+1692,0x80006000);
    write_be32(memory+0x1000+1696,patterns[pattern]);
    write_be32(memory+0x1000+1700,count);
    unsigned calls=0;
    s64 charge=0;
    do {fixture_dispatch(fn,&cpu,&charge);assert(++calls<64);} while(cpu.pc!=initial.lr);
#ifdef RUNTIME_CHARGE_RESET
    cpu.downcount=charge;
#endif
    assert(cpu.gpr[1]==initial.gpr[1] && !cpu.reserve_valid);
    if(verify && pattern==0) {
        assert(read_be16(memory+0x4000)==7);
        for(unsigned i=2;i<128;i++) assert(memory[0x4000+i]==0);
    }
    if(verify && pattern==1) {
        unsigned coefficient=(1u<<active_category)-1u;
        assert(read_be16(memory+0x4000)==7+coefficient);
        for(unsigned i=2;i<128;i+=2) assert(read_be16(memory+0x4000+i)==coefficient);
    }
    return cpu;
}
static u64 now(void) {
    struct timespec t;assert(clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t)==0);
    return (u64)t.tv_sec*1000000000ull+t.tv_nsec;
}
int main(void) {
    const unsigned counts[]={1,27,29,32};unsigned cases=0;
    for(unsigned p=0;p<4;p++)for(unsigned category=1;category<=2;category++)
    for(unsigned c=0;c<4;c++) {
        setup(p,category,counts[c]);CPUState a=decode(reference_chunk,p,counts[c],true);
        memcpy(expected,memory,sizeof memory);
        setup(p,category,counts[c]);CPUState b=decode(candidate_chunk,p,counts[c],true);
        assert(memcmp(&a,&b,sizeof a)==0 && memcmp(memory,expected,sizeof memory)==0);++cases;
#ifdef BENCHMARK
        const unsigned repeats=100000;
        for(unsigned step=0;step<4;step++) {
            unsigned variant=(step==1||step==2);
            void(*fn)(CPUState*)=variant?candidate_chunk:reference_chunk;
            setup(p,category,counts[c]);
            for(unsigned i=0;i<1000;i++) decode(fn,p,counts[c],false);
            u64 begin=now();
            for(unsigned i=0;i<repeats;i++) {CPUState result=decode(fn,p,counts[c],false);assert(result.pc==initial.lr);}
            printf("p=%u category=%u count=%u step=%u variant=%u ns=%.3f\n",p,category,counts[c],step,variant,(double)(now()-begin)/repeats);
            fflush(stdout);
        }
#endif
    }
    printf("completed synthetic Y decoder cases=%u: state/memory parity passed\n",cases);
    return 0;
}
