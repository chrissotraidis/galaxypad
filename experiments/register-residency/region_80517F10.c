static void loop_80517F10(CPUState* ctx) {
    /* Register-resident form: guest values live in C locals; ctx is written
       only at exits and before the out-of-line MMIO path, then reloaded. */
    GP_MM_DECL(ctx);
    u32 r0 = ctx->gpr[0], r5 = ctx->gpr[5], r6 = ctx->gpr[6], r7 = ctx->gpr[7];
    u32 cr = ctx->cr;
    s64 dc = ctx->downcount;
    for (;;) {
        dc -= 2;
        r6 = r6 + 4u;
        r7 = r7 + 1u;
        {
            u8* p = gp_fast_ptr(&gp_mm, r6);
            if (!p && (gp_mm.exram == NULL || ((r6 & ~0x40000000u) - 0x90000000u) > gp_mm.exram_lim + 8u)) p = gp_fast_ptr1(&gp_mm, r6);
            if (__builtin_expect(p != NULL, 1)) {
                r0 = read_be32(p);
            } else {
                ctx->gpr[0] = r0; ctx->gpr[5] = r5; ctx->gpr[6] = r6; ctx->gpr[7] = r7;
                ctx->cr = cr; ctx->downcount = dc; ctx->pc = 0x80517F18u;
                u32 v = gp_slow_read32(ctx, r6);
                ctx->gpr[0] = v;
                r0 = v; r5 = ctx->gpr[5]; r6 = ctx->gpr[6]; r7 = ctx->gpr[7]; cr = ctx->cr; dc = ctx->downcount;
            }
        }
        {
            u32 cr_bits = 0;
            if (r5 < r0) cr_bits |= 0x8u;
            if (r5 > r0) cr_bits |= 0x4u;
            if (r5 == r0) cr_bits |= 0x2u;
            cr_bits |= (ctx->xer >> 31) & 1u;
            cr = (cr & ~(0xFu << 28)) | (cr_bits << 28);
        }
        if ((cr & 0x40000000u) != 0) {
            if (dc <= -(s64)DOLRECOMP_C_LOOP_CYCLE_BUDGET) {
                ctx->gpr[0] = r0; ctx->gpr[6] = r6; ctx->gpr[7] = r7; ctx->cr = cr; ctx->downcount = dc;
                ctx->pc = 0x80517F10u;
                return;
            }
            continue;
        }
        break;
    }
    ctx->gpr[0] = r0; ctx->gpr[6] = r6; ctx->gpr[7] = r7; ctx->cr = cr; ctx->downcount = dc;
    ctx->pc = 0x80517F24u;
}
