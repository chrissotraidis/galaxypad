// Private complete 6BE0..6C00 candidate. No guest writes until acceptance.
#include <arm_neon.h>
static unsigned long norm_vector_fast,norm_vector_rejected;
static bool norm_vector_input(f64 v) {
    const u64 bits=f64_bits(v),mag=bits&0x7fffffffffffffffull;
    return !mag || (((mag>>52)-1013u)<=20u && !(bits&0x1fffffffull));
}
static bool norm_vector_range(f64 v) {
    const u64 mag=f64_bits(v)&0x7fffffffffffffffull;
    return !mag || ((mag>>52)-963u)<=120u;
}
static bool norm_vector_tie(f64 v) {
    return (f64_bits(v)&0x1fffffffull)==0x10000000ull;
}
static float64x2_t norm_vector_pair(f64 lo,f64 hi) {
    const f64 values[]={lo,hi};return vld1q_f64(values);
}
static float64x2_t norm_vector_round(float64x2_t v) {
    return vcvt_f64_f32(vcvt_f32_f64(v));
}
static bool norm_vector_try(CPUState* cpu) {
#pragma STDC FENV_ACCESS ON
    if(cpu->fpscr&FPSCR_RN_MASK) {++norm_vector_rejected;return false;}
    const f64 input[]={cpu->fpr[0],cpu->fpr[1],cpu->fpr[2],cpu->ps1[2],
                       cpu->fpr[3],cpu->ps1[3],cpu->fpr[5],cpu->ps1[5]};
    for(unsigned i=0;i<8;++i) if(!norm_vector_input(input[i])) {
        ++norm_vector_rejected;return false;
    }
    u64 status;__asm__ volatile("mrs %0, fpsr":"=r"(status)::"memory");
    const float64x2_t in2=norm_vector_pair(input[2],input[3]);
    const float64x2_t in3=norm_vector_pair(input[4],input[5]);
    const float64x2_t in5=norm_vector_pair(input[6],input[7]);
    const float64x2_t madd=vfmaq_f64(in5,in3,in3);
    if(norm_vector_tie(vgetq_lane_f64(madd,0)) || norm_vector_tie(vgetq_lane_f64(madd,1))) goto reject;
    const float64x2_t pair4=norm_vector_round(madd);
    // Upper madd output is overwritten, but its rounding effects must execute.
    __asm__ volatile(""::"w"(pair4):"memory");
    const f64 sum=vgetq_lane_f64(pair4,0)+input[7];
    if(!norm_vector_range(sum) || !(sum>0.0)) goto reject;
    const f64 out4=(f64)(f32)sum;
    const f64 estimate=ppc_approx_rsqrt(out4);
    const f64 square=estimate*force_25bit_c(estimate);
    const f64 half=estimate*input[0];
    if(!norm_vector_range(square) || !norm_vector_range(half)) goto reject;
    const f64 squared=(f64)(f32)square, out0=(f64)(f32)half;
    const f64 correction=fma(squared,out4,-input[1]);
    if(!norm_vector_range(correction) || norm_vector_tie(correction)) goto reject;
    const f64 out6=-(f64)(f32)correction;
    const f64 scaled=out6*out0;
    if(!norm_vector_range(scaled)) goto reject;
    const f64 out5=(f64)(f32)scaled;
    const float64x2_t product2=vmulq_n_f64(in2,out5),product3=vmulq_n_f64(in3,out5);
    if(!norm_vector_range(vgetq_lane_f64(product2,0)) || !norm_vector_range(vgetq_lane_f64(product2,1)) ||
       !norm_vector_range(vgetq_lane_f64(product3,0)) || !norm_vector_range(vgetq_lane_f64(product3,1))) goto reject;
    const float64x2_t out2=norm_vector_round(product2),out3=norm_vector_round(product3);
    __asm__ volatile(""::"w"(out2),"w"(out3):"memory");
    cpu->fpr[0]=cpu->ps1[0]=out0;
    cpu->fpr[2]=vgetq_lane_f64(out2,0);cpu->ps1[2]=vgetq_lane_f64(out2,1);
    cpu->fpr[3]=vgetq_lane_f64(out3,0);cpu->ps1[3]=vgetq_lane_f64(out3,1);
    cpu->fpr[4]=out4;cpu->ps1[4]=input[5];
    cpu->fpr[5]=cpu->ps1[5]=out5;cpu->fpr[6]=cpu->ps1[6]=out6;
    cpu->fpscr&=~(FPSCR_FI_BIT|FPSCR_FR_BIT);
    set_fprf(cpu,classify_f32((f32)cpu->fpr[3]));
    cpu->pc=0x804B6C00u;++norm_vector_fast;return true;
reject:
    __asm__ volatile("msr fpsr, %0"::"r"(status):"memory");
    ++norm_vector_rejected;return false;
}
