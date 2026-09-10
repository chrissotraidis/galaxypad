"""Offline, exact-kernel read-map cache; stores and slow calls invalidate it."""
import hashlib
import re

SOURCE_SHA = '98d98621d4f744ea76977a63e44f3e2e3e731f50051e4a3a800a772e05a68991'
HELPERS = r'''
typedef struct {
    u8 *ram, *exram;
    u32 ram_size, exram_size;
    bool valid;
} GalaxyKernelMap;
static inline u64 galaxy_kernel_read(CPUState* cpu, GalaxyKernelMap* map,
                                    u32 address, u32 size) {
    if (!map->valid) {
        map->ram = cpu->ram; map->ram_size = cpu->ram_size;
        map->exram = cpu->exram; map->exram_size = cpu->exram_size;
        map->valid = true;
    }
    u32 masked = address & ~0x40000000u;
    u32 offset = masked - 0x90000000u;
    u8* ptr = NULL;
    if (map->exram && offset <= map->exram_size - size)
        ptr = map->exram + offset;
    else {
        offset = masked - 0x80000000u;
        if (offset <= map->ram_size - size) ptr = map->ram + offset;
    }
    if (ptr) {
        if (size == 1) return *ptr;
        if (size == 2) return read_be16(ptr);
        if (size == 4) return read_be32(ptr);
        return read_be64(ptr);
    }
    // The callback may remap any field. Do not reuse this snapshot afterward.
    map->valid = false;
    if (cpu->external_read) return cpu->external_read(cpu, address, (u8)size);
    return 0;
}
static inline bool galaxy_kernel_psq_load(CPUState* cpu, GalaxyKernelMap* map,
    u8 frD, u32 ea, bool w, u8 gqr_index, bool indexed, u32 cia) {
    const u32 gqr = cpu->gqr[gqr_index & 7u];
    if (((gqr >> 16) & 7u) == 0u && (indexed || (cpu->hid2 & PPC_HID2_LSQE) != 0u)) {
        cpu->fpr[frD] = f64_value(convert_to_double((u32)galaxy_kernel_read(cpu, map, ea, 4)));
        cpu->ps1[frD] = w ? 1.0 : f64_value(convert_to_double((u32)galaxy_kernel_read(cpu, map, ea + 4u, 4)));
        return true;
    }
    map->valid = false;
    return ppc_psq_load(cpu, frD, ea, w, gqr_index, indexed, cia);
}
'''


def transform(source):
    if hashlib.sha256(source.encode()).hexdigest() != SOURCE_SHA:
        raise ValueError('Unexpected extracted kernel identity')
    start = source.index('static __attribute__((noinline, flatten)) bool thp_kernel_0(')
    end = source.index('void func_804520A0(CPUState* ctx) {', start)
    body = source[start:end]
    # No unknown call may silently bypass invalidation. Inspect new source first.
    calls = set(re.findall(r'\b(\w+)\(ctx\b', body))
    allowed = {'ppc_fp_available_inline', 'ppc_psq_load_inline', 'ppc_psq_store_inline',
               'dolrecomp_f64_to_bits', 'dolrecomp_rotl32'}
    allowed |= {'mem_' + op + str(bits) for op in ('read', 'write') for bits in (8, 16, 32, 64)}
    allowed |= {'ppc_ps_' + op + '_op' for op in ('add', 'sub', 'mul', 'madd')}
    allowed |= {'galaxypad_deferred_' + op for op in ('add', 'sub', 'mul', 'madd')}
    assert calls <= allowed, calls - allowed
    for index in range(2):
        signature = f'bool thp_kernel_{index}(CPUState* ctx) {{'
        assert body.count(signature) == 1
        body = body.replace(signature, signature + '\n    GalaxyKernelMap map = {0};')
    for bits in (8, 16, 32, 64):
        # Preserve narrowing of external reads exactly as in each original helper.
        body = re.sub(rf'mem_read{bits}\(ctx, ([^()]+)\)',
                      rf'((u{bits})galaxy_kernel_read(ctx, &map, \1, {bits // 8}))', body)
    assert not re.search(r'mem_read\d+\(ctx', body)
    body = body.replace('ppc_psq_load_inline(ctx, ', 'galaxy_kernel_psq_load(ctx, &map, ')
    body, stores = re.subn(r'(?m)^(\s*)((?:mem_write\d+|ppc_psq_store_inline)\(ctx,)',
                          r'\1map.valid = false;\n\1\2', body)
    assert stores > 0
    return source[:start] + HELPERS + '\n' + body + source[end:]
