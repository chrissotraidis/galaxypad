#!/usr/bin/env python3
"""Isolated actual-source three-register restore range prototype; never installs."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
module = Path((root / 'generated/modules/RMGE01/active-module.txt').read_text().strip())
source = module.parent / 'dolrecomp-output/RMGE01_generated/chunks/chunk_1299_text1_805170A0.c'
text = source.read_text()
assert hashlib.sha256(text.encode()).hexdigest() == '9b221ad3e1b417287e425640cc318e30fc5a6378e2956bf65a929be455acfd94'
blocks = []
for pc, reg, offset in [(0x80517584, 29, -12), (0x80517588, 30, -8), (0x8051758c, 31, -4)]:
    body = text.split(f'label_{pc:08X}:', 1)[1].split(f'label_{pc+4:08X}:', 1)[0]
    assert f'ctx->gpr[{reg}] = mem_read32(ctx, ea);' in body
    assert f'ctx->gpr[11] + (u32)(s32)({offset})' in body
    blocks.append(body)
original = '\n'.join(blocks)
candidate = r'''
u32 base = ctx->gpr[11] - 12u;
u32 masked = base & ~0x40000000u;
u8 *ptr = NULL;
// Select precisely one existing mapping, rejecting underflow/wrap/boundaries.
if (ctx->exram && ctx->exram_size >= 12 &&
    masked - 0x90000000u <= ctx->exram_size - 12)
    ptr = ctx->exram + (masked - 0x90000000u);
else if (ctx->ram && ctx->ram_size >= 12 &&
         masked - 0x80000000u <= ctx->ram_size - 12)
    ptr = ctx->ram + (masked - 0x80000000u);
// Product CPUState and RAM are separate allocations. Still reject overlap here.
if (ptr && !((uintptr_t)ptr + 12 <= (uintptr_t)ctx ||
             (uintptr_t)ptr >= (uintptr_t)ctx + sizeof(*ctx))) ptr = NULL;
if (!ptr) { reference(ctx); return; }
ctx->pc = 0x80517584u; ctx->gpr[29] = read_be32(ptr);
ctx->pc = 0x80517588u; ctx->gpr[30] = read_be32(ptr + 4);
ctx->pc = 0x8051758Cu; ctx->gpr[31] = read_be32(ptr + 8);
'''
driver = r'''
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include "core/cpu.h"
PPCMemWriteJournal g_mem_write_journal;
void *g_mem_write_journal_user;
static u8 ram[256], exram[256];
static unsigned calls;
static u64 external(CPUState *c, u32 address, u8 size) {
    assert(size == 4); ++calls;
    // Force the remaining original loads to observe a changed mapping/base.
    c->gpr[11] = 0x80000040; c->ram = ram; c->ram_size = sizeof(ram);
    return address ^ 0x12345678;
}
static __attribute__((noinline)) void reference(CPUState *ctx) { ORIGINAL }
static __attribute__((noinline)) void candidate(CPUState *ctx) { CANDIDATE }
int main(void) {
    for (unsigned i=0;i<256;i++) { ram[i]=i^37; exram[i]=i^91; }
    unsigned count=0;
    const u32 regions[]={0x80000000,0xc0000000,0x90000000,0xd0000000,
                         0,0xffffffff,0xcc000000};
    for (unsigned region=0;region<7;region++)
    for (unsigned offset=0;offset<272;offset++)
    for (unsigned mode=0;mode<4;mode++) {
        CPUState a={0}, b;
        a.ram=ram; a.ram_size=256;
        a.exram=(mode&1)?exram:NULL; a.exram_size=256;
        a.external_read=(mode&2)?external:NULL;
        a.gpr[11]=regions[region]+offset;
        a.downcount=-17; a.lr=0x1000; a.pc=0x80517584;
        b=a; calls=0; reference(&a); unsigned before=calls;
        calls=0; candidate(&b);
        assert(before==calls); assert(memcmp(&a,&b,sizeof(a))==0); ++count;
    }
    printf("%u complete-state and callback-count comparisons passed\n",count);
}
'''.replace('ORIGINAL', original).replace('CANDIDATE', candidate)
with tempfile.TemporaryDirectory(prefix='galaxypad-restore-range-') as tmp:
    path = Path(tmp) / 'test.c'
    path.write_text(driver)
    exe = Path(tmp) / 'test'
    subprocess.run(['clang', '-std=c11', '-O2', '-fsanitize=address,undefined',
                    '-I', str(root/'ref/ModernGekko/vendor/dolphin/GXRuntime/include'),
                    str(path), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
print('Source SHA256:', hashlib.sha256(text.encode()).hexdigest())
print('Boundary: three loads only; original entry-cycle/return dispatch untouched. '
      'No installed performance or complete-block acceptance.')
