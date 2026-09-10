/* Preserve the generated loop for profile matching; specialize its stores. */
static inline u8* galaxypad_dcbz_prepare(CPUState* cpu, u32 ea) {
    if (!g_mem_write_journal && cpu->ram &&
        cpu->ram_size >= 32u && cpu->ram_size <= 0x10000000u &&
        (!cpu->exram || (cpu->exram_size >= 32u && cpu->exram_size <= 0x10000000u))) {
        u8* line = get_ram_ptr(cpu, ea, 32u, NULL);
        if (line) {
            const uintptr_t begin = (uintptr_t)line;
            const uintptr_t state = (uintptr_t)cpu;
            const uintptr_t journal = (uintptr_t)&g_mem_write_journal;
            const bool state_disjoint = begin >= state ?
                begin - state >= sizeof(*cpu) : state - begin >= 32u;
            const bool journal_disjoint = begin >= journal ?
                begin - journal >= sizeof(g_mem_write_journal) : journal - begin >= 32u;
            if (state_disjoint && journal_disjoint) {
                clear_matching_reservation(cpu, ea);
                return line;
            }
        }
    }
    return NULL;
}
static inline void galaxypad_dcbz_store(CPUState* cpu, u32 ea, u8* line, u32 i) {
    if (line) write_be32(line + i, 0);
    else mem_write32(cpu, ea + i, 0);
}
static inline void galaxypad_dcbz_ram_line(CPUState* cpu, u32 address) {
    const u32 ea = address & ~31u;
    u8* line = galaxypad_dcbz_prepare(cpu, ea);
    for (u32 i = 0; i < 32; i += 4)
        galaxypad_dcbz_store(cpu, ea, line, i);
}
