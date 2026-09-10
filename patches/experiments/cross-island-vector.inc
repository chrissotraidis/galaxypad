// Private whole-island experiment: 804B6CCC..804B6CE0. No observer may occur
// within this region. Caller owns original PC/FPU checks and cycle accounting.
static void cross_island_original(CPUState* cpu) {
  ppc_ps_mul_op(cpu,4,1,2);
  ppc_ps_muls0(cpu,7,1,0);
  ppc_ps_madd_op(cpu,5,0,3,4,true,false);
  ppc_ps_madd_op(cpu,8,0,6,7,true,false);
  cpu->fpr[9]=cpu->ps1[5];cpu->ps1[9]=cpu->ps1[5];
  cpu->fpr[10]=cpu->fpr[5];cpu->ps1[10]=cpu->ps1[8];
}
static bool cross_island_input(f64 value) {
  const u64 bits=f64_bits(value), magnitude=bits&0x7fffffffffffffffull;
  if(!magnitude) return true;
  const u32 exponent=(u32)(magnitude>>52);
  // Exact binary32 operands, magnitudes in[2^-30,2^31). Products and differences
  // stay away from binary32 overflow/subnormal handling. No precision assumption
  // is made about arbitrary doubles or data loaded by an external callback.
  return exponent-993u<=60u && !(bits&0x1fffffffull);
}
static float64x2_t cross_island_pair(CPUState* cpu,unsigned r) {
  const double lanes[]={cpu->fpr[r],cpu->ps1[r]};return vld1q_f64(lanes);
}
static bool cross_island_tie(float64x2_t value) {
  const uint64x2_t bits=vreinterpretq_u64_f64(value);
  return (vgetq_lane_u64(bits,0)&0x1fffffffull)==0x10000000ull ||
         (vgetq_lane_u64(bits,1)&0x1fffffffull)==0x10000000ull;
}
static void cross_island_write(CPUState* cpu,unsigned r,float64x2_t value) {
  cpu->fpr[r]=vgetq_lane_f64(value,0);cpu->ps1[r]=vgetq_lane_f64(value,1);
}
static bool cross_island_try(CPUState* cpu) {
#pragma STDC FENV_ACCESS ON
  // NI may be enabled: the following exact-single magnitude guard keeps every
  // nonzero arithmetic intermediate normal in binary32. No subnormal behavior
  // is bypassed. Other rounding modes still take the original path.
  if(cpu->fpscr&FPSCR_RN_MASK) return false;
  const unsigned inputs[]={0,1,2,3,6};
  for(unsigned i=0;i<5;++i) {
    unsigned r=inputs[i];
    if(!cross_island_input(cpu->fpr[r]) || !cross_island_input(cpu->ps1[r])) {
      return false;
    }
  }
  u64 saved_status;__asm__ volatile("mrs %0, fpsr":"=r"(saved_status)::"memory");
  const float64x2_t a=cross_island_pair(cpu,1),b=cross_island_pair(cpu,2);
  const float64x2_t c=cross_island_pair(cpu,0),d=cross_island_pair(cpu,3);
  const float64x2_t e=cross_island_pair(cpu,6);
  const float64x2_t p=vcvt_f64_f32(vcvt_f32_f64(vmulq_f64(a,b)));
  const float64x2_t q=vcvt_f64_f32(vcvt_f32_f64(vmulq_f64(a,vdupq_n_f64(cpu->fpr[0]))));
  const float64x2_t x=vfmaq_f64(vnegq_f64(p),c,d);
  const float64x2_t y=vfmaq_f64(vnegq_f64(q),c,e);
  // Reference ni_madd_msub corrects these ties using error-free arithmetic.
  // Restore status before fallback; no guest output has been committed yet.
  if(cross_island_tie(x)||cross_island_tie(y)) {
    __asm__ volatile("msr fpsr, %0"::"r"(saved_status):"memory");
    return false;
  }
  const float64x2_t out5=vcvt_f64_f32(vcvt_f32_f64(x));
  const float64x2_t out8=vcvt_f64_f32(vcvt_f32_f64(y));
  cross_island_write(cpu,4,p);cross_island_write(cpu,7,q);
  cross_island_write(cpu,5,out5);cross_island_write(cpu,8,out8);
  cpu->fpr[9]=cpu->ps1[5];cpu->ps1[9]=cpu->ps1[5];
  cpu->fpr[10]=cpu->fpr[5];cpu->ps1[10]=cpu->ps1[8];
  set_fprf(cpu,classify_f32((f32)cpu->fpr[8]));
  return true;
}
static void cross_island_vector(CPUState* cpu) {
  if(!cross_island_try(cpu)) cross_island_original(cpu);
}
