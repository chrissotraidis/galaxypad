/* Private experiment: included after actual float helpers, not installed. */
static inline bool checked_single_bits(u64 bits) {
    return ((bits >> 52) & 2047u) != 2047u &&
           convert_to_double(convert_to_single(bits)) == bits;
}

static inline void checked_ps_multiply(CPUState* cpu, u8 d, u8 a, u8 c) {
    if ((cpu->fpscr & FPSCR_NI_BIT) ||
        !checked_single_bits(f64_bits(cpu->fpr[a])) ||
        !checked_single_bits(f64_bits(cpu->ps1[a])) ||
        !checked_single_bits(f64_bits(cpu->fpr[c])) ||
        !checked_single_bits(f64_bits(cpu->ps1[c]))) {
        ppc_ps_mul_op(cpu, d, a, c);
        return;
    }
    const float32x2_t left = {(f32)cpu->fpr[a], (f32)cpu->ps1[a]};
    const float32x2_t right = {(f32)cpu->fpr[c], (f32)cpu->ps1[c]};
    const float32x2_t result = vmul_f32(left, right);
    const f32 r0 = vget_lane_f32(result, 0), r1 = vget_lane_f32(result, 1);
    ps_write_both(cpu, d, r0, r1);
    set_fprf(cpu, classify_f32(r0));
}
