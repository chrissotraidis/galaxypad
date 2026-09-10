"""Prove memory metadata cannot be blindly hoisted across callbacks."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
include = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/include'
source = r'''
#include <assert.h>
#include <stddef.h>
#include "core/cpu.h"
PPCMemWriteJournal g_mem_write_journal;
void* g_mem_write_journal_user;
static unsigned char old_ram[64], new_ram[64];
static u64 remap(CPUState* cpu, u32 address, u8 size) {
    assert(address == 0xe0000000u && size == 4);
    cpu->ram = new_ram;
    cpu->msr ^= 0x2000;
    return 17;
}
static void journal(u32 offset, u32 size, void* user) {
    assert(offset == 0 && size == 4);
    ((CPUState*)user)->ram = new_ram;
}
int main(void) {
    CPUState cpu = {0};
    cpu.ram = old_ram; cpu.ram_size = sizeof(old_ram);
    write_be32(old_ram, 11); write_be32(new_ram, 22);
    cpu.external_read = remap;
    assert(mem_read32(&cpu, 0x80000000u) == 11);
    assert(mem_read32(&cpu, 0xe0000000u) == 17);
    assert(mem_read32(&cpu, 0x80000000u) == 22);
    assert(cpu.msr == 0x2000);
    cpu.ram = old_ram;
    cpu.reserve_valid = true; cpu.reserve_addr = 0x80000000u;
    g_mem_write_journal = journal; g_mem_write_journal_user = &cpu;
    mem_write32(&cpu, 0x80000000u, 33);
    // Current store retains the pointer acquired before the callback.
    assert(read_be32(old_ram) == 33 && read_be32(new_ram) == 22);
    assert(!cpu.reserve_valid);
    g_mem_write_journal = NULL;
    mem_write32(&cpu, 0x80000000u, 44);
    assert(read_be32(new_ram) == 44);
    assert(offsetof(CPUState, msr) == 0x298);
    assert(offsetof(CPUState, exception) == 0x320);
    assert(offsetof(CPUState, reserve_valid) == 0x344);
    // Exact traced ARM64 module's x19-relative accesses (x19 retains CPUState*).
    assert(offsetof(CPUState, ram) == 0xd80);
    assert(offsetof(CPUState, ram_size) == 0xd88);
    assert(offsetof(CPUState, downcount) == 0xd98);
    assert(offsetof(CPUState, exram) == 0xda0);
    assert(offsetof(CPUState, exram_size) == 0xda8);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-mapping-contract-') as directory:
    temp = Path(directory)
    (temp/'test.c').write_text(source)
    subprocess.run(['clang', '-O2', '-fsanitize=address,undefined', '-I', str(include),
                    str(temp/'test.c'), '-o', str(temp/'test')], check=True)
    subprocess.run([str(temp/'test')], check=True)
print('Callback remapping, journal pointer ordering, reservation and field offsets pass')
