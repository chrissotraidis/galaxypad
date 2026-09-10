// Experimental helper probe, not compiled into GalaxyPad or generated modules.
#pragma STDC FENV_ACCESS ON
#include "cpu_interpreter_float.c"
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
#include <time.h>

static void candidate(CPUState* cpu, u8 d, u8 a, u8 b, bool subtract) {
    const f64 a0=cpu->fpr[a], a1=cpu->ps1[a];
    const f64 b0=cpu->fpr[b], b1=cpu->ps1[b];
    if (!isfinite(a0) || !isfinite(a1) || !isfinite(b0) || !isfinite(b1)) {
        if (subtract) ppc_ps_sub_op(cpu,d,a,b);
        else ppc_ps_add_op(cpu,d,a,b);
        return;
    }
    const f32 r0=force_single(cpu, subtract ? a0-b0 : a0+b0);
    const f32 r1=force_single(cpu, subtract ? a1-b1 : a1+b1);
    ps_write_both(cpu,d,r0,r1);
    set_fprf(cpu,classify_f32(r0));
}

static u64 random_bits(u64* seed) {
    *seed ^= *seed << 13; *seed ^= *seed >> 7; *seed ^= *seed << 17;
    return *seed;
}

static void fast_add(CPUState* cpu,u8 d,u8 a,u8 b) { candidate(cpu,d,a,b,false); }
static double bench(void (*fn)(CPUState*,u8,u8,u8), CPUState* cpu) {
    void (*volatile call)(CPUState*,u8,u8,u8)=fn;
    const clock_t start=clock();
    for (unsigned i=0;i<5000000;++i) call(cpu,0,1,2);
    return (double)(clock()-start)/CLOCKS_PER_SEC;
}

int main(void) {
    static CPUState reference, fast;
    const u64 special[]={0,0x8000000000000000ull,1,0x000fffffffffffffull,
        0x0010000000000000ull,0x380fffffffffffffull,0x3810000000000000ull,
        0x7fefffffffffffffull,0x7ff0000000000000ull,0xfff0000000000000ull,
        0x7ff0000000000001ull,0x7ff8000000000123ull,0xfff8000000000123ull};
    const int modes[]={FE_TONEAREST,FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO};
    u64 seed=0x91a22f13ull;
    for (unsigned mode=0;mode<4;++mode) {
        assert(fesetround(modes[mode])==0);
        for (unsigned i=0;i<250000;++i) {
            memset(&reference,0,sizeof(reference));
            reference.fpscr=(u32)random_bits(&seed);
            u64 operands[4];
            for (unsigned j=0;j<4;++j)
                operands[j]=(i<169) ? special[((j<2 ? i/13 : i%13)+(j&1)*5)%13] : random_bits(&seed);
            reference.fpr[1]=f64_value(operands[0]); reference.ps1[1]=f64_value(operands[1]);
            reference.fpr[2]=f64_value(operands[2]); reference.ps1[2]=f64_value(operands[3]);
            fast=reference;
            u8 d=i%3; // Includes destination/source aliasing.
            assert(feclearexcept(FE_ALL_EXCEPT)==0);
            if (i&1) ppc_ps_sub_op(&reference,d,1,2);
            else ppc_ps_add_op(&reference,d,1,2);
            const int reference_flags=fetestexcept(FE_ALL_EXCEPT);
            assert(feclearexcept(FE_ALL_EXCEPT)==0);
            candidate(&fast,d,1,2,(i&1)!=0);
            assert(fetestexcept(FE_ALL_EXCEPT)==reference_flags);
            assert(memcmp(&reference,&fast,sizeof(reference))==0);
        }
    }
    assert(fesetround(FE_TONEAREST)==0);
    puts("One million finite-path/reference state comparisons passed");
    memset(&fast,0,sizeof(fast));
    fast.fpr[1]=1.25; fast.ps1[1]=-2.5; fast.fpr[2]=3.75; fast.ps1[2]=4.25;
    for (unsigned repeat=0;repeat<4;++repeat) {
        double old_time, new_time;
        if (repeat&1) { new_time=bench(fast_add,&fast); old_time=bench(ppc_ps_add_op,&fast); }
        else { old_time=bench(ppc_ps_add_op,&fast); new_time=bench(fast_add,&fast); }
        printf("normal add %u: reference=%.6f candidate=%.6f ratio=%.3f\n",
               repeat,old_time,new_time,new_time/old_time);
    }
    return 0;
}
