/* Synthetic singleton canonical codes of lengths 6, 8, 12, 16.
 * Offset layout verified against exact RMGE01 loads and THPHuffmanTab.
 * A zero-valued symbol ends AC immediately; category 1 fills all coefficients.
 * Incomplete but valid prefix tables: the only assigned code is all zeros. */
#define main short_fixture_main
#include "huffman-throughput.c"
#undef main

static void long_setup(unsigned length, unsigned dense, unsigned count) {
    setup(0,1,count);
    for(unsigned table=0x2000;table<=0x3000;table+=0x1000) {
        memset(memory+table,255,32); /* no 5-bit quick code */
        memset(memory+table+32,0,32);
        write_be32(memory+table+64,0x80000000+table+224);
        for(unsigned i=0;i<18;i++) {
            write_be32(memory+table+68+4*i,i==length?0:i==17?0xfffff:0xffffffff);
            write_be32(memory+table+140+4*i,i==length?0:0xffffffff);
        }
        memory[table+224]=(u8)dense;
    }
    memset(memory+0x6000,0,1024);
    unsigned bit=count-1;
    for(unsigned symbol=0;symbol<(dense?64u:2u);symbol++) {
        bit+=length;
        if(dense) {
            assert(bit<8192);
            memory[0x6000+bit/8]|=(u8)(1u<<(7-bit%8));
            bit++;
        }
    }
}
static CPUState long_decode(void(*fn)(CPUState*),unsigned dense,unsigned count,bool verify) {
    CPUState cpu=initial;
#ifdef LONG_RUN_BUDGET
    cpu.downcount=1000000;
#endif
    memset(memory+0x4000,0xa5,128);
    write_be16(memory+0x1000+1668,7);
    write_be32(memory+0x1000+1692,0x80006000);
    write_be32(memory+0x1000+1696,read_be32(memory+0x6000));
    write_be32(memory+0x1000+1700,count);
    unsigned calls=0;
    s64 charge=0;
    do {fixture_dispatch(fn,&cpu,&charge);assert(++calls<4096);} while(cpu.pc!=initial.lr);
#ifdef RUNTIME_CHARGE_RESET
    cpu.downcount=charge;
#endif
    assert(cpu.gpr[1]==initial.gpr[1] && !cpu.reserve_valid);
    if(verify) {
        assert(read_be16(memory+0x4000)==7+dense);
        for(unsigned i=2;i<128;i+=2) assert(read_be16(memory+0x4000+i)==dense);
    }
    return cpu;
}
#ifdef LOOP_COVERAGE
extern unsigned long galaxy_loop_reads;
#endif
int main(void) {
    const unsigned lengths[]={6,8,12,16},counts[]={1,27,29,32};
    unsigned cases=0;
    for(unsigned l=0;l<4;l++)for(unsigned dense=0;dense<2;dense++)for(unsigned c=0;c<4;c++) {
#ifndef BENCHMARK
        printf("checking length=%u dense=%u count=%u\n",lengths[l],dense,counts[c]);fflush(stdout);
#endif
        long_setup(lengths[l],dense,counts[c]);
        CPUState a=long_decode(reference_chunk,dense,counts[c],true);
        memcpy(expected,memory,sizeof memory);
        long_setup(lengths[l],dense,counts[c]);
        CPUState b=long_decode(candidate_chunk,dense,counts[c],true);
        assert(memcmp(&a,&b,sizeof a)==0 && memcmp(memory,expected,sizeof memory)==0);
        cases++;
#ifdef BENCHMARK
        for(unsigned step=0;step<4;step++) {
            unsigned variant=step==1||step==2;
            void(*fn)(CPUState*)=variant?candidate_chunk:reference_chunk;
            long_setup(lengths[l],dense,counts[c]);
            for(unsigned i=0;i<1000;i++) long_decode(fn,dense,counts[c],false);
            u64 begin=now();
            for(unsigned i=0;i<10000;i++) long_decode(fn,dense,counts[c],false);
            printf("length=%u dense=%u count=%u variant=%u ns=%.3f\n",lengths[l],dense,counts[c],variant,(double)(now()-begin)/10000);
            fflush(stdout);
        }
#endif
    }
#ifdef LOOP_COVERAGE
    assert(galaxy_loop_reads>0);
    printf("cached_loop_reads=%lu\n",galaxy_loop_reads);
#endif
    printf("completed long-code cases=%u: expected coefficients/state/memory passed\n",cases);
}
