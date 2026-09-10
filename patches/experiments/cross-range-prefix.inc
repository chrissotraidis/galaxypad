/* Private six-instruction entry span; original suffix and entries stay live. */
static inline u8* cross_input_range(CPUState* ctx, u32 address) {
    if (address > UINT32_MAX-11u || !ctx->ram || ctx->ram_size < 12u ||
        (ctx->exram && ctx->exram_size < 12u)) return NULL;
    u8* p = get_ram_ptr(ctx, address, 12u, NULL);
    uintptr_t begin=(uintptr_t)p, state=(uintptr_t)ctx;
    if (!p || begin>UINTPTR_MAX-12u || state>UINTPTR_MAX-sizeof(*ctx) ||
        (begin<state+sizeof(*ctx) && state<begin+12u)) return NULL;
    return p;
}
static __attribute__((noinline)) bool cross_range_prefix(CPUState* ctx) {
    if (!(ctx->msr&PPC_MSR_FP) || ctx->exception ||
        (ctx->fpscr&FPSCR_NI_BIT) || !(ctx->hid2&PPC_HID2_LSQE) ||
        ((ctx->gqr[0]>>16)&7u)) return false;
    const u8* input3=cross_input_range(ctx,ctx->gpr[3]);
    const u8* input4=cross_input_range(ctx,ctx->gpr[4]);
    if (!input3 || !input4) return false;
    /* GENERATED_PREFIX */
    return true;
}
