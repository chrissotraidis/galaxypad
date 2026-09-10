"""Isolated exact-source transform; refresh mapping after every slow read."""
import hashlib
import re

HELPER = r'''
typedef struct { u8 *ram, *exram; u32 ram_size, exram_size; } GalaxyReadMap;
static inline GalaxyReadMap galaxy_read_map(CPUState* cpu) {
    return (GalaxyReadMap){cpu->ram, cpu->exram, cpu->ram_size, cpu->exram_size};
}
static inline u32 galaxy_loop_read(CPUState* cpu, GalaxyReadMap* map, u32 addr) {
    const u32 masked = addr & ~0x40000000u;
    const u32 exoffset = masked - 0x90000000u;
    if (map->exram && exoffset <= map->exram_size - 4u)
        return read_be32(map->exram + exoffset);
    const u32 offset = masked - 0x80000000u;
    if (offset <= map->ram_size - 4u)
        return read_be32(map->ram + offset);
    u32 value = mem_read32(cpu, addr);
    *map = galaxy_read_map(cpu);
    return value;
}
'''


def transform(source):
    # Permit only relocation of the include by the existing private test driver.
    normalized = re.sub(r'^#include ".*RMGE01.h"$', '#include "../RMGE01.h"', source, flags=re.M)
    assert hashlib.sha256(normalized.encode()).hexdigest() == 'e6aa915816ee2a89534f75c4d59dd0c145f7a5d0162c3e1a15b2ebe33b996dcc'
    prefix, rest = source.split('void func_804530A0(CPUState* ctx) {', 1)
    signatures = re.findall(r'static void loop_[0-9A-F]+\(CPUState\* ctx\) \{', prefix)
    assert len(signatures) == 15 and prefix.count('mem_read32(ctx, ea)') == 15
    # The pinned loops write only registers/control state. No memory writes,
    # mapping mutation, or other call can invalidate a snapshot on the fast path.
    assert set(re.findall(r'ctx->(\w+)', prefix)) <= {'gpr', 'pc', 'downcount', 'cr', 'xer'}
    changed = prefix.replace('mem_read32(ctx, ea)', 'galaxy_loop_read(ctx, &map, ea)')
    for signature in signatures:
        changed = changed.replace(signature, signature+'\n    GalaxyReadMap map = galaxy_read_map(ctx);')
    return changed.replace(signatures[0], HELPER+'\n'+signatures[0], 1)+'void func_804530A0(CPUState* ctx) {'+rest
