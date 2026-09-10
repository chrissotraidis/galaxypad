#!/usr/bin/env python3
"""Isolated named-site emission experiment; does not alter production codegen.

Use the actual current emitter/CFG. Exercise callbacks after all native entry
paths, not a handwritten approximation of generated control flow.
"""
import pathlib
import shutil
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
VENDOR = ROOT / 'ref/ModernGekko/vendor/dolphin/DolRecomp'
DRIVER = r'''
#include "backend/emitter.h"
#include <assert.h>
int main(void) {
  emit_header(stdout);
  const u32 words[]={0x38630001,0x38840001,0x4200fff8,0x4e800020};
  PPCInst instructions[4];
  for(unsigned i=0;i<4;++i) instructions[i]=ppc_decode(words[i],0x80002000+4*i);
  assert(emit_function(stdout,instructions,4,0x80002000));
  const u32 calls[]={0x48000011,0x38630001,0x48000ff8,0x60000000,0x38840001,0x4e800020};
  PPCInst returning[6];
  for(unsigned i=0;i<6;++i) returning[i]=ppc_decode(calls[i],0x80004000+4*i);
  assert(emit_function(stdout,returning,6,0x80004000));
  emit_footer(stdout);
}
'''
RUNNER = r'''
#include <assert.h>
#include <stdio.h>
static unsigned observations;
static bool observe(CPUState* ctx,u32 address) {
  assert((address==0x80002004 || address==0x80004004) && ctx->pc==address);
  ++observations;
  return false;
}
int main(void) {
  for(unsigned start=0;start<4;++start) {
    CPUState ctx={0}; ctx.pc=0x80002000+4*start; ctx.lr=0x90000000; ctx.ctr=3;
    ctx.host_call=observe; observations=0;
    func_80002000(&ctx);
    unsigned expected=start<=1?3:start==2?2:0;
    assert(observations==expected);
    assert(ctx.gpr[3]==(start==0?3:start<=2?2:0));
    assert(ctx.gpr[4]==expected && ctx.pc==ctx.lr);
    assert(ctx.downcount==-(s64)(start<3?10-start:1));
    // Missing observer preserves instruction results and cycle charges.
    CPUState plain={0}; plain.pc=0x80002000+4*start; plain.lr=ctx.lr; plain.ctr=3;
    func_80002000(&plain);
    assert(plain.gpr[3]==ctx.gpr[3] && plain.gpr[4]==ctx.gpr[4]);
    assert(plain.pc==ctx.pc && plain.downcount==ctx.downcount);
  }
  for(unsigned start=4;start<6;++start) {
    CPUState ctx={0}; ctx.pc=0x80004000+4*start; ctx.lr=0x80004004;
    ctx.host_call=observe; observations=0;
    func_80004000(&ctx);
    assert(observations==1 && ctx.gpr[3]==1 && ctx.gpr[4]==(start==4));
    assert(ctx.pc==0x80005000 && ctx.downcount==-(s64)(8-start));
  }
  puts("Native observer prototype: entries, fallthrough, back-edges, local returns, null callback and cycles pass");
}
'''

with tempfile.TemporaryDirectory(prefix='galaxypad-observer-') as temporary:
    base = pathlib.Path(temporary)
    shutil.copytree(VENDOR / 'src', base / 'src')
    emitter = base / 'src/backend/emitter.c'
    source = emitter.read_text()
    # Prototype selected sites. Keep outlined counted loops from bypassing them;
    # ordinary generated branch paths retain the existing per-block accounting.
    needle = '    // DOLRECOMP_C_LOCAL_RETURNS=0 sends every blr back through the dispatcher'
    assert source.count(needle) == 1
    source = source.replace(needle, '''    if ((func_addr <= 0x80002004u && func_end > 0x80002004u) ||
        (func_addr <= 0x80004004u && func_end > 0x80004004u))
        for (u32 n = 0; n < count; ++n) cfg.loop_ends[n] = UINT32_MAX;
''' + needle)
    needle = '        fprintf(out, "label_%08X:\\n", insts[i].address);'
    assert source.count(needle) == 1
    source = source.replace(needle, needle + r'''
        if (insts[i].address == 0x80002004u || insts[i].address == 0x80004004u) {
            fprintf(out, "    if (ctx->host_call) { u32 observer_pc = ctx->pc; ctx->pc = 0x%08Xu; ppc_host_call(ctx, ctx->pc); ctx->pc = observer_pc; }\n", insts[i].address);
        }
''')
    emitter.write_text(source)
    (base / 'driver.c').write_text(DRIVER)
    flags = ['xcrun','clang','-O1','-g','-fsanitize=address,undefined','-I',str(base/'src')]
    subprocess.run(flags+[str(base/'driver.c'),str(emitter),str(base/'src/backend/c_cfg.c'),
                         str(base/'src/frontend/decoder.c'),'-o',str(base/'driver')],check=True)
    generated = subprocess.check_output([str(base/'driver')],text=True)
    assert generated.count('observer_pc = ctx->pc') == 2
    (base/'generated.c').write_text(generated+RUNNER)
    subprocess.run(flags+[str(base/'generated.c'),str(base/'src/cpu/cpu.c'),
                         '-o',str(base/'test')],check=True)
    subprocess.run([str(base/'test')],check=True)
