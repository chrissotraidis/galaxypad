// Private oracle driver; assertions remain enabled separately from module code.
#include "cpu_interpreter_private.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#ifdef WIDE_BENCHMARK
#include <libproc.h>
#include <sys/resource.h>
#include <unistd.h>
#include <time.h>
static double cpu_seconds(void) {
    struct timespec t;assert(!clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t));
    return t.tv_sec+t.tv_nsec*1e-9;
}
static u64 process_instructions(void) {
    struct rusage_info_v4 r={0};
    assert(!proc_pid_rusage(getpid(),RUSAGE_INFO_V4,(rusage_info_t*)&r));
    return r.ri_instructions;
}
#endif
void original(CPUState*);
void extracted(CPUState*);
unsigned long probe_accepted(void);
#ifdef WIDE_DYNAMIC
#include <dlfcn.h>
static void (*chunk_entry[2])(CPUState*);
static void (*configure_entry[2])(bool,PPCMemWriteJournal,void*);
#ifdef WIDE_VECTOR_COUNTS
static unsigned long (*vector_fast)(void);
#endif
void original(CPUState* cpu) {chunk_entry[0](cpu);}
void extracted(CPUState* cpu) {chunk_entry[1](cpu);}
unsigned long probe_accepted(void) {return 0;}
static void prepare(unsigned variant) {
    configure_entry[variant](g_ppc_lazy_fp_enabled,g_mem_write_journal,g_mem_write_journal_user);
}
#else
static void prepare(unsigned variant) {(void)variant;}
#endif
#ifndef ROUTINE_START
#define ROUTINE_START 0x804B64A4u
#define ROUTINE_LENGTH 41
#define CONSTANT_OFFSET 9392
#endif
static unsigned char ram[512], other[512], expected_ram[512], expected_other[512];
static u64 trace;
static unsigned callbacks;
static void observe(CPUState* cpu, u32 address, u64 value) {
    trace = trace*0x100000001b3ull ^ address ^ value ^ cpu->pc ^ cpu->fpscr ^ f64_bits(cpu->fpr[6]);
    callbacks++;
    cpu->gpr[3]=0x80000080;
    cpu->gpr[4]=0x80000040;
    cpu->gpr[5]=0x800000a0;
    cpu->fpr[5]=f64_value(0x3fe0000000000000ull);
    cpu->ps1[7]=f64_value(0x4000000000000000ull);
    cpu->ram=other;
    cpu->ram_size=sizeof other;
    cpu->downcount-=3;
}
static u64 read_external(CPUState* cpu,u32 address,u8 size) {
    observe(cpu,address,size);
    return 0x3f800000u;
}
static void write_external(CPUState* cpu,u32 address,u64 value,u8 size) {
    observe(cpu,address,value ^ size);
}
static void journal(u32 offset,u32 size,void* user) {
    observe(user,offset,size);
}
static void reset_memory(void) {
    for(unsigned i=0;i<512;i+=4) {
        write_be32(ram+i,0x3e800000u+(i<<12));
        write_be32(other+i,0x3f000000u+(i<<11));
    }
    trace=0;callbacks=0;
}
int main(int argc,char** argv) {
#ifdef WIDE_DYNAMIC
    assert(argc==3);
    for(unsigned i=0;i<2;i++) {
        void* library=dlopen(argv[i+1],RTLD_NOW|RTLD_LOCAL);
        if(!library) fprintf(stderr,"dlopen: %s\n",dlerror());
        assert(library);
        chunk_entry[i]=dlsym(library,"func_804B60A0");
        configure_entry[i]=dlsym(library,"probe_configure");
        assert(chunk_entry[i] && configure_entry[i]);
#ifdef WIDE_VECTOR_COUNTS
        if(i==1) {vector_fast=dlsym(library,"probe_vector_fast");assert(vector_fast);}
#endif
    }
#else
    (void)argc;(void)argv;
#endif
    u64 saved_mode,saved_flags;
    __asm__ volatile("mrs %0, fpcr":"=r"(saved_mode));
    __asm__ volatile("mrs %0, fpsr":"=r"(saved_flags));
    unsigned cases=0, observed=0;
#ifdef WIDE_RANDOM_INPUTS
    u64 random=0x905;
#endif
    const u64 values[]={0,0x8000000000000000ull,0x3ff0000000000000ull,
        0x7ff0000000000000ull,0x7ff0000000000001ull,0x7ff8000000000123ull,
        1,0x7fefffffffffffffull};
    for(unsigned lazy=0;lazy<2;lazy++)
    for(unsigned entry=0;entry<ROUTINE_LENGTH;entry++)for(unsigned mode=0;mode<5;mode++)
    for(unsigned rn=0;rn<4;rn++)for(unsigned ni=0;ni<2;ni++)
    for(unsigned type=0;type<8;type++)for(unsigned enabled=0;enabled<2;enabled++)
    for(unsigned overlap=0;overlap<3;overlap++)for(unsigned scale=0;scale<4;scale++) {
        CPUState initial={0};
        initial.pc=ROUTINE_START+entry*4;initial.lr=0x81234564;
        initial.downcount=entry&1 ? -100 : 1000;
        initial.msr=enabled?PPC_MSR_FP:0;
        initial.hid2=PPC_HID2_LSQE|PPC_HID2_PSE;
        initial.fpscr=rn|(ni?FPSCR_NI_BIT:0)|((entry&1)?FPSCR_VE_BIT:0);
        const unsigned scales[]={0,31,32,63};
        initial.gqr[0]=type|(type<<16)|(scales[scale]<<8)|(scales[scale]<<24);
        initial.ram=ram;initial.ram_size=sizeof ram;
        initial.gpr[2]=0x80000100u-CONSTANT_OFFSET;
        initial.gpr[3]=0x80000040+overlap*16;
        initial.gpr[4]=0x80000040;
        if(mode==1) initial.gpr[3]=initial.gpr[4]=0xcc000040;
        if(mode==3) {initial.gpr[3]=initial.gpr[4]=0x800001ff;}
        initial.gpr[5]=initial.gpr[3];
        initial.external_read=read_external;initial.external_write=write_external;
        initial.reserve_valid=true;
        initial.reserve_addr=initial.gpr[3]+(entry%3)*32;
        for(unsigned r=0;r<32;r++) {
            initial.fpr[r]=f64_value(values[(r+entry)%8]);
            initial.ps1[r]=f64_value(values[(r+entry+3)%8]);
#ifdef WIDE_RANDOM_INPUTS
            random^=random<<13;random^=random>>7;random^=random<<17;
            initial.fpr[r]=f64_value(random);
            random^=random<<13;random^=random>>7;random^=random<<17;
            initial.ps1[r]=f64_value(random);
#endif
        }
#ifdef WIDE_RANDOM_INPUTS
        initial.fpscr=(u32)(random & ~7ull)|rn|(ni?FPSCR_NI_BIT:0);
#endif
#ifdef WIDE_FMA_TIES
        if(initial.pc==0x804B650Cu) {
            // Exact products straddle an f32 halfway value by 2^-75, or tie.
            const f64 aa[]={0x1.0000000000001p0,0x1.ffffffffffffep-1,
                            -0x1.0000000000001p0,1.0};
            const f64 cc[]={0x1.000002p0,0x1.000002p0,0x1.000002p0,1.0};
            const f64 bb[]={0x1.0000001p-24,0x1.ffffffep-25,-0x1.0000001p-24,-0x1p-24};
            initial.fpr[8]=initial.ps1[8]=aa[scale];
            initial.fpr[3]=initial.ps1[3]=cc[scale];
            initial.fpr[1]=initial.ps1[1]=bb[scale];
        }
#endif
        CPUState a=initial,b=initial;
#ifdef WIDE_VECTOR_COUNTS
        if(initial.pc==0x804B6BE0u) {
            initial.fpr[0]=0.5;initial.fpr[1]=3.0;
            initial.fpr[2]=3.0;initial.ps1[2]=4.0;
            initial.fpr[3]=0.0;initial.ps1[3]=1.0;
            initial.fpr[5]=9.0;initial.ps1[5]=16.0;
            if(scale==1) {initial.fpr[3]=initial.fpr[5]=initial.ps1[5]=0.0;}
            if(scale==2) {initial.fpr[3]=1.0;initial.fpr[5]=0x1p-24;}
            if(scale==3) {
                // Exact binary32 values varying independently at the direct entry.
                for(unsigned r=0;r<6;++r) {
                    const unsigned seed=cases*1664525u+r*1013904223u;
                    initial.fpr[r]=((seed&0xffffu)+1)/256.0;
                    initial.ps1[r]=(((seed>>16)&0xffffu)+1)/256.0;
                }
            }
            a=initial;b=initial;
        }
#endif
        if(mode==4) {
            _Static_assert(offsetof(CPUState,ps1)==offsetof(CPUState,fpr)+sizeof(a.fpr),"paired bank layout");
            a.ram=(u8*)a.fpr;b.ram=(u8*)b.fpr;
        }
        g_ppc_lazy_fp_enabled=lazy!=0;
        reset_memory();g_mem_write_journal=mode==2?journal:NULL;g_mem_write_journal_user=&a;
        ppc_fpscr_control_updated(&a);
        u64 seed_flags=entry&0x9f;
        __asm__ volatile("msr fpsr, %0"::"r"(seed_flags));
        prepare(0);
        original(&a);
#ifdef WIDE_VECTOR_COUNTS
        if(initial.pc==0x804B6BE0u && scale==0 && mode==0 && rn==0 && enabled) {
            assert(fabs(a.fpr[2]-0.6)<0.000001 && fabs(a.ps1[2]-0.8)<0.000001);
            assert(a.fpr[3]==0.0);
        }
#endif
#ifdef WIDE_FMA_TIES
        if(initial.pc==0x804B650Cu && mode==0 && rn==0 && ni==0 && enabled) {
            const f64 expected[]={-0x1.000002p0,-1.0,0x1.000002p0,-1.0};
            assert(f64_bits(a.fpr[8])==f64_bits(expected[scale]));
            assert(f64_bits(a.ps1[8])==f64_bits(expected[scale]));
        }
#endif
        u64 aflags;__asm__ volatile("mrs %0, fpsr":"=r"(aflags));
        if(lazy && !enabled && entry<ROUTINE_LENGTH-1) assert(a.srr0==initial.pc);
        if(!callbacks && !a.exception) {
            assert(a.downcount==initial.downcount-(ROUTINE_LENGTH-entry));
            assert(a.pc==(initial.lr&~3u));
        }
        u64 expected_trace=trace;unsigned expected_callbacks=callbacks;
        memcpy(expected_ram,ram,sizeof ram);memcpy(expected_other,other,sizeof other);
        reset_memory();g_mem_write_journal_user=&b;
        ppc_fpscr_control_updated(&b);
        __asm__ volatile("msr fpsr, %0"::"r"(seed_flags));
        prepare(1);
#ifdef WIDE_VECTOR_COUNTS
        const unsigned long accepted_before=vector_fast();
#endif
        extracted(&b);
#ifdef WIDE_VECTOR_COUNTS
        if(initial.pc==0x804B6BE0u && rn==0 && enabled) {
            if(scale==0) assert(vector_fast()==accepted_before+1);
            if(scale==1 || scale==2) assert(vector_fast()==accepted_before);
        }
#endif
        u64 bflags;__asm__ volatile("mrs %0, fpsr":"=r"(bflags));
        // Normalize only the different addresses of equivalent self-aliases.
        if(a.ram==(u8*)a.fpr)a.ram=ram;
        if(b.ram==(u8*)b.fpr)b.ram=ram;
        if(memcmp(&a,&b,sizeof a)||aflags!=bflags||expected_trace!=trace||expected_callbacks!=callbacks||
           memcmp(expected_ram,ram,sizeof ram)||memcmp(expected_other,other,sizeof other)) {
            fprintf(stderr,"Mismatch entry=%u mode=%u rn=%u ni=%u type=%u fp=%u overlap=%u state=%d flags=%llx/%llx\n",
                entry,mode,rn,ni,type,enabled,overlap,memcmp(&a,&b,sizeof a),aflags,bflags);
            return 1;
        }
        observed+=callbacks>0;cases++;
    }
    g_mem_write_journal=NULL;g_mem_write_journal_user=NULL;
    __asm__ volatile("msr fpcr, %0"::"r"(saved_mode));
    __asm__ volatile("msr fpsr, %0"::"r"(saved_flags));
    printf("%u complete routine CPUState/memory/callback/FPSR comparisons pass; %u callback cases\n",cases,observed);
    printf("fast-path accepted calls: %lu\n",probe_accepted());
#ifdef WIDE_VECTOR_COUNTS
    printf("normalization vector accepted calls: %lu\n",vector_fast());
    assert(vector_fast()>0);
#endif
#ifdef WIDE_BENCHMARK
#ifdef WIDE_VECTOR_COUNTS
    for(unsigned workload=0;workload<8;++workload)
#else
    const unsigned workload=0;
#endif
    for(unsigned pair=0;pair<8;pair++) {
        CPUState results[2];unsigned char memory[2][512];u64 status[2];
        for(unsigned half=0;half<2;half++) {
            unsigned candidate=half^(pair&1);
            CPUState cpu={0};cpu.ram=ram;cpu.ram_size=sizeof ram;
            cpu.msr=PPC_MSR_FP;cpu.hid2=PPC_HID2_LSQE|PPC_HID2_PSE;
            cpu.gpr[2]=0x80000100u-CONSTANT_OFFSET;cpu.gpr[3]=0x80000000;cpu.gpr[4]=0x80000040;
            cpu.gpr[5]=0x800000c0;
            if(ROUTINE_START==0x804B6BCCu) {cpu.gpr[3]=0x80000040;cpu.gpr[4]=0x80000000;}
            cpu.lr=0x81234564;
            reset_memory();
#ifdef WIDE_VECTOR_COUNTS
            cpu.fpscr=workload>=4?FPSCR_NI_BIT:0;
#endif
            ppc_fpscr_control_updated(&cpu);
#ifdef WIDE_VECTOR_COUNTS
            const unsigned kind=workload&3;
            if(kind) {
                write_be32(ram+0x100,0x3f000000u);write_be32(ram+0x104,0x40400000u);
                write_be32(ram+0x40,kind==1?0x40400000u:kind==2?0x49800000u:0);
                write_be32(ram+0x44,kind==1?0x40800000u:0);
                write_be32(ram+0x48,0);
            }
#endif
            const u64 clear=0;__asm__ volatile("msr fpsr, %0"::"r"(clear));
            void (*run)(CPUState*)=candidate?extracted:original;
            prepare(candidate);
            const u64 instructions=process_instructions();const double start=cpu_seconds();
            for(unsigned i=0;i<1000000;i++) {
                cpu.pc=ROUTINE_START;cpu.downcount=1000;run(&cpu);
            }
            const double seconds=cpu_seconds()-start;
            const u64 count=process_instructions()-instructions;
            __asm__ volatile("mrs %0, fpsr":"=r"(status[candidate]));
            results[candidate]=cpu;memcpy(memory[candidate],ram,sizeof ram);
            printf("workload=%u pair=%u candidate=%u ns_per_call=%.3f instructions_per_call=%.3f\n",
                workload,pair,candidate,seconds*1000,count/1000000.);
        }
        assert(!memcmp(&results[0],&results[1],sizeof(CPUState)));
        assert(!memcmp(memory[0],memory[1],sizeof ram));assert(status[0]==status[1]);
    }
    __asm__ volatile("msr fpcr, %0"::"r"(saved_mode));
    __asm__ volatile("msr fpsr, %0"::"r"(saved_flags));
#endif
}
