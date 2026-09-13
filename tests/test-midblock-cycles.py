#!/usr/bin/env python3
"""Compile the candidate in isolation; execute its actual generated C."""
import pathlib
import shutil
import json
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
VENDOR = ROOT / 'ref/ModernGekko/vendor/dolphin/DolRecomp'

DRIVER = r'''
#include <assert.h>
#include "backend/emitter.h"
#include "backend/c_cfg.h"
void original_destroy(CFunctionCFG*);
bool original_can_loop(const CFunctionCFG*, const PPCInst*, u32, u32);
#define c_function_cfg_build original_build
#define c_function_cfg_destroy original_destroy
#define c_function_cfg_contains original_contains
#define c_function_cfg_can_loop_directly original_can_loop
#include "original_cfg.c"
#undef c_function_cfg_build
#undef c_function_cfg_destroy
#undef c_function_cfg_contains
#undef c_function_cfg_can_loop_directly
static void differential(void) {
    u32 seed=17;
    const u32 raws[]={0x38630001,0x4e800020,0x7c001bac,0x48000008,
                      0x4200fff8,0x1c640003,0x60000000};
    for (unsigned t=0;t<10000;t++) {
        PPCInst inst[32];
        for (u32 i=0;i<32;i++) {
            seed=seed*1664525u+1013904223u;
            inst[i]=ppc_decode(raws[seed%7],0x1000+4*i);
            inst[i].embedded_data=(seed%11==0);
        }
        CFunctionCFG old,now;
        assert(original_build(&old,inst,32,0x1000));
        assert(c_function_cfg_build(&now,inst,32,0x1000));
        for(u32 i=0;i<32;i++) {
            assert(old.leaders[i]==now.leaders[i]);
            assert(old.loop_ends[i]==now.loop_ends[i]);
            if(old.leaders[i]) assert(old.block_cycles[i]==now.block_cycles[i]);
            u32 suffix=0;
            for(u32 j=i;j<32;j++) {
                suffix+=instruction_cycles(&inst[j]);
                if(instruction_ends_block(&inst[j]) || j==31 || old.leaders[j+1]) break;
            }
            assert(now.block_cycles[i]==suffix);
        }
        original_destroy(&old); c_function_cfg_destroy(&now);
    }
}
static void generate(u32 base, const u32 *raw, u32 n) {
    PPCInst inst[32];
    for (u32 i=0;i<n;i++) inst[i]=ppc_decode(raw[i],base+4*i);
    CFunctionCFG cfg;
    assert(c_function_cfg_build(&cfg,inst,n,base));
    assert(emit_function(stdout,inst,n,base));
    c_function_cfg_destroy(&cfg);
}
int main(void) {
    differential();
    emit_header(stdout);
    u32 helper[19];
    for (int i=0;i<18;i++) helper[i]=0x38630001; // addi r3,r3,1
    helper[18]=0x4e800020; // blr
    generate(0x80001000,helper,19);
    const u32 loop[]={0x38630001,0x38840001,0x4200fff8,0x4e800020};
    generate(0x80002000,loop,4); // two adds, bdnz, return
    const u32 branch[]={0x38630001,0x48000008,0x38630001,0x38840001,0x4e800020};
    generate(0x80003000,branch,5);
    // A linked branch makes +4 a local return target; returning from +16
    // must charge that leader but never repeat the external-entry suffix.
    const u32 returns[]={0x48000011,0x38630001,0x48000ff8,
                         0x60000000,0x38840001,0x4e800020};
    generate(0x80004000,returns,6);
    PPCInst data[]={ppc_decode(0x38630001,0x80006000),
                   ppc_decode(0x38630001,0x80006004),
                   ppc_decode(0x38630001,0x80006008),
                   ppc_decode(0x4e800020,0x8000600c)};
    data[1].embedded_data=true;
    assert(emit_function(stdout,data,4,0x80006000));
    // Fallback remains host-charged, and terminates the preceding suffix.
    PPCInst f[]={ppc_decode(0x38630001,0x4000),ppc_decode(0x7c001bac,0x4004),
                 ppc_decode(0x38630001,0x4008),ppc_decode(0x4e800020,0x400c)};
    CFunctionCFG cfg;
    assert(c_function_cfg_build(&cfg,f,4,0x4000));
    assert(cfg.block_cycles[0]==1 && cfg.block_cycles[1]==0);
    assert(cfg.block_cycles[2]==2 && cfg.block_cycles[3]==1);
    c_function_cfg_destroy(&cfg);
    assert(c_function_cfg_build(&cfg,f,0,0x4000));
    c_function_cfg_destroy(&cfg);
    emit_footer(stdout);
}
'''

RUNNER = r'''
#include <assert.h>
#include <stdio.h>
int main(void) {
  for(unsigned i=0;i<19;i++) {
    CPUState ctx={0}; ctx.pc=0x80001000+4*i; ctx.lr=0x90000000;
    func_80001000(&ctx);
    assert(ctx.gpr[3]==18-i && ctx.downcount==-(s64)(19-i));
    assert(ctx.pc==ctx.lr);
  }
  // First partial iteration followed by full iterations must charge once each.
  for(unsigned i=0;i<3;i++) {
    CPUState ctx={0}; ctx.pc=0x80002000+4*i; ctx.lr=0x90000000; ctx.ctr=3;
    func_80002000(&ctx);
    assert(ctx.gpr[3]==(i==0?3:2));
    assert(ctx.gpr[4]==(i<2?3:2));
    assert(ctx.downcount==-(s64)(10-i) && ctx.pc==ctx.lr);
  }
  for(unsigned i=0;i<5;i++) {
    CPUState ctx={0}; ctx.pc=0x80003000+4*i; ctx.lr=0x90000000;
    func_80003000(&ctx);
    const int charges[]={4,3,3,2,1};
    assert(ctx.downcount==-charges[i] && ctx.pc==ctx.lr);
    assert(ctx.gpr[3]==(i==0 || i==2));
    assert(ctx.gpr[4]==(i<4));
  }
  for(unsigned i=4;i<6;i++) {
    CPUState ctx={0}; ctx.pc=0x80004000+4*i; ctx.lr=0x80004004;
    func_80004000(&ctx);
    assert(ctx.pc==0x80005000 && ctx.downcount==-(s64)(8-i));
    assert(ctx.gpr[3]==1 && ctx.gpr[4]==(i==4));
  }
  for(unsigned i=0;i<4;i++) {
    CPUState ctx={0}; ctx.pc=0x80006000+4*i; ctx.lr=0x90000000;
    func_80006000(&ctx);
    const int adds[]={2,1,1,0};
    assert(ctx.pc==ctx.lr && ctx.gpr[3]==adds[i]);
    assert(ctx.downcount==-(adds[i]+1));
  }
  puts("midblock emitted execution: entries, fallthrough, branches, loops, local returns, embedded data passed");
}
'''

with tempfile.TemporaryDirectory(prefix='galaxypad-midblock-') as temporary:
    base = pathlib.Path(temporary)
    shutil.copytree(VENDOR / 'src', base / 'src')
    original = subprocess.check_output(['git', '-C', str(VENDOR), 'show',
        json.loads((ROOT / 'config/dependencies.lock.json').read_text())['repositories']['dolRecomp']['upstreamRevision'] + ':src/backend/c_cfg.c'], text=True)
    (base / 'original_cfg.c').write_text(original)
    (base / 'driver.c').write_text(DRIVER)
    flags = ['clang', '-O1', '-g', '-fsanitize=address,undefined', '-I', str(base / 'src')]
    subprocess.run(flags + [str(base / 'driver.c'), str(base / 'src/backend/emitter.c'),
                           str(base / 'src/backend/c_cfg.c'), str(base / 'src/frontend/decoder.c'),
                           '-o', str(base / 'driver')], check=True)
    emitted = subprocess.check_output([str(base / 'driver')], text=True)
    assert 'case 0x8000103Cu: ctx->downcount -= 4;' in emitted
    (base / 'emitted.c').write_text(emitted + RUNNER)
    subprocess.run(flags + [str(base / 'emitted.c'), str(base / 'src/cpu/cpu.c'),
                           '-o', str(base / 'test')], check=True)
    subprocess.run([str(base / 'test')], check=True)
