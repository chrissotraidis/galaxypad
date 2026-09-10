/* Isolated ARM64 experiment; not applied to generated or shipping code.
 * Requires cpu_interpreter_float.c and arm_neon.h in the test translation unit.
 * Retains scalar fallback for every nonfinite operand and the original
 * rounding, result classification, destination aliasing and state writes.
 */
static void vector_addsub(CPUState* cpu, u8 d, u8 a, u8 b, bool subtract) {
    const f64 a0 = cpu->fpr[a], a1 = cpu->ps1[a];
    const f64 b0 = cpu->fpr[b], b1 = cpu->ps1[b];
    const u64 exponent = 0x7ff0000000000000ull;
    if ((f64_bits(a0) & exponent) == exponent ||
        (f64_bits(a1) & exponent) == exponent ||
        (f64_bits(b0) & exponent) == exponent ||
        (f64_bits(b1) & exponent) == exponent) {
        if (subtract) ppc_ps_sub_op(cpu, d, a, b);
        else ppc_ps_add_op(cpu, d, a, b);
        return;
    }
    const float64x2_t av = {a0, a1}, bv = {b0, b1};
    const float64x2_t result = subtract ? vsubq_f64(av, bv) : vaddq_f64(av, bv);
    const f32 ps0 = force_single(cpu, vgetq_lane_f64(result, 0));
    const f32 ps1 = force_single(cpu, vgetq_lane_f64(result, 1));
    ps_write_both(cpu, d, ps0, ps1);
    set_fprf(cpu, classify_f32(ps0));
}
