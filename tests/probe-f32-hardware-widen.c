#pragma STDC FENV_ACCESS ON
#include "core/types.h"
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
#include <time.h>

__attribute__((noinline)) static u64 reference(u32 value) {
    return convert_to_double(value);
}
__attribute__((noinline)) static u64 candidate(u32 value) {
#include "../patches/experiments/f32-hardware-widen.inc"
    return convert_to_double(value);
}
static u32 seed = 0x97531246;
static u32 random32(void) { seed=seed*1664525u+1013904223u; return seed; }
static unsigned checked;
#if defined(__aarch64__)
static u64 fpcr(void) { u64 value; __asm__ volatile("mrs %0, fpcr":"=r"(value));return value; }
static u64 fpsr(void) { u64 value; __asm__ volatile("mrs %0, fpsr":"=r"(value));return value; }
static void set_fpcr(u64 value) { __asm__ volatile("msr fpcr, %0"::"r"(value):"memory"); }
#endif
static void check(u32 value, int initial_flags) {
    feclearexcept(FE_ALL_EXCEPT);
    feraiseexcept(initial_flags);
    const u64 expected=reference(value);
    const int expected_flags=fetestexcept(FE_ALL_EXCEPT);
#if defined(__aarch64__)
    const u64 expected_status=fpsr(), expected_control=fpcr();
#endif
    feclearexcept(FE_ALL_EXCEPT);
    feraiseexcept(initial_flags);
    const u64 actual=candidate(value);
    assert(actual==expected && fetestexcept(FE_ALL_EXCEPT)==expected_flags);
#if defined(__aarch64__)
    assert(fpsr()==expected_status && fpcr()==expected_control);
#endif
    ++checked;
}
int main(void) {
    fenv_t saved;
    assert(fegetenv(&saved)==0);
    const int modes[]={FE_TONEAREST,FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO};
    const u32 fractions[]={0,1,0x3fffff,0x400000,0x7ffffe,0x7fffff};
    for(unsigned flush=0;flush<2;flush++) for(unsigned mode=0;mode<4;mode++) {
        assert(fesetround(modes[mode])==0);
#if defined(__aarch64__)
        // Match Common/ArmFPURoundMode.cpp: FZ=24, AH=1, FIZ=0.
        // Unsupported controls may read back cleared; this tests the actual host.
        set_fpcr((fpcr() & ~((1ull<<24)|3ull)) | (flush?((1ull<<24)|2ull):0));
#endif
        for(unsigned sign=0;sign<2;sign++) for(unsigned exponent=0;exponent<256;exponent++)
        for(unsigned fraction=0;fraction<6;fraction++) for(unsigned flags=0;flags<2;flags++)
            check((sign<<31)|(exponent<<23)|fractions[fraction],flags?FE_ALL_EXCEPT:0);
        for(unsigned i=0;i<100000;i++) check(random32(),i&1?FE_INEXACT:0);
    }
    assert(fesetenv(&saved)==0);
    printf("%u exact result/status comparisons across four rounding modes and both runtime flush modes passed\n",checked);
#ifndef SANITIZED
    u32 inputs[1024];
    volatile u64 sink=0;
    for(unsigned kind=0;kind<3;kind++) {
        for(unsigned i=0;i<1024;i++) {
            u32 bits=random32();
            inputs[i]=kind==0?((bits&0x807fffffu)|0x3f000000u):kind==1?0:bits;
        }
        for(unsigned trial=0;trial<6;trial++) {
            double times[2];u64 sums[2];
            for(unsigned step=0;step<2;step++) {
                unsigned which=step^(trial&1);u64 sum=0;
                u64(*volatile fn)(u32)=which?candidate:reference;
                clock_t start=clock();
                for(unsigned i=0;i<5000000;i++) sum+=fn(inputs[i&1023]);
                times[which]=(double)(clock()-start)/CLOCKS_PER_SEC;sums[which]=sum;
            }
            assert(sums[0]==sums[1]);sink=sums[0];
            printf("kind=%u trial=%u reference=%.6f candidate=%.6f ratio=%.4f\n",
                   kind,trial,times[0],times[1],times[1]/times[0]);
        }
    }
    (void)sink;
#endif
    assert(fesetenv(&saved)==0);
}
