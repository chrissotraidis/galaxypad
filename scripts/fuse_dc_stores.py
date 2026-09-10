"""Offline exact-kernel DC-store run; original labels remain the fallback."""
import hashlib

SOURCE_SHA = '98d98621d4f744ea76977a63e44f3e2e3e731f50051e4a3a800a772e05a68991'
HELPER = r'''
static inline bool galaxy_dc_store_run(CPUState* cpu) {
    if (cpu->gpr[7] != 0 || cpu->exception || !(cpu->msr & PPC_MSR_FP) ||
        !(cpu->hid2 & PPC_HID2_LSQE) || (cpu->gqr[0] & 7u) != 0 ||
        g_mem_write_journal || !cpu->ram || cpu->ram_size < 24u ||
        cpu->ram_size > 0x10000000u ||
        (cpu->exram && (cpu->exram_size < 24u || cpu->exram_size > 0x10000000u)) ||
        cpu->downcount < INT64_MIN + 8) return false;
    const u32 ea = cpu->gpr[10] + 16u;
    u8* output = get_ram_ptr(cpu, ea, 24u, NULL);
    if (!output) return false;
    const uintptr_t begin = (uintptr_t)output, state = (uintptr_t)cpu;
    const uintptr_t journal = (uintptr_t)&g_mem_write_journal;
    const bool state_disjoint = begin >= state ? begin - state >= sizeof(*cpu) : state - begin >= 24u;
    const bool journal_disjoint = begin >= journal ? begin - journal >= sizeof(g_mem_write_journal) : journal - begin >= 24u;
    if (!state_disjoint || !journal_disjoint) return false;
    // No callback or alias can now change operands/mapping between the stores.
    const u32 first = convert_to_single_ftz(f64_bits(cpu->fpr[0]));
    const u32 second = convert_to_single_ftz(f64_bits(cpu->ps1[0]));
    for (u32 offset = 0; offset < 24u; offset += 8u) {
        clear_matching_reservation(cpu, ea + offset);
        write_be32(output + offset, first);
        clear_matching_reservation(cpu, ea + offset + 4u);
        write_be32(output + offset + 4u, second);
    }
    cpu->downcount -= 8;
    cpu->cr = (cpu->cr & 0x0fffffffu) | ((2u | ((cpu->xer >> 31) & 1u)) << 28);
    cpu->gpr[10] += 32u;
    cpu->pc = 0x80452798u;
    return true;
}
'''


def transform(source):
    if hashlib.sha256(source.encode()).hexdigest() != SOURCE_SHA:
        raise ValueError('Unexpected extracted kernel identity')
    signature = 'static __attribute__((noinline, flatten)) bool thp_kernel_0('
    label = '\nlabel_80452788:\n'
    assert source.count(label) == 2  # Original kernel plus outer trampoline.
    # Only the first occurrence is the actual kernel body; outer entries stay intact.
    changed = source.replace(label, label+'    if (galaxy_dc_store_run(ctx)) goto label_8045279C;\n', 1)
    return changed.replace(signature, HELPER+'\n'+signature, 1)
