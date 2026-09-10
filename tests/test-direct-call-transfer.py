"""Compile actual experimental transfer glue; not full generated-module proof."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = root / 'apple/experiments/guarded-direct-calls'
driver = r'''
#include "binding.h"
#include <assert.h>
#include <stddef.h>
struct CPUState { uint32_t pc; };
static unsigned depth, limit=24, calls, checks, replacements, mode;
static unsigned events[8], count;
static int dolrecomp_call_enter(void) {
  if (depth>=limit) return 0;
  ++depth; return 1;
}
static void dolrecomp_call_leave(void) { assert(depth); --depth; }
static int dolrecomp_dispatch_replacement(CPUState* ctx, uint32_t address) {
  events[count++]=address==100 ? 2 : 5;
  if ((mode==3 && address==100) || (mode==4 && address==104)) {
    ++replacements; ctx->pc=address==100 ? 104 : 900; return 1;
  }
  return 0;
}
#include "transfer.h"
static int boundary(CPUState* ctx, uint32_t target) {
  assert(ctx->pc==target);
  events[count++]=target==100 ? 1 : 4; ++checks;
  return !((mode==1 && target==100) || (mode==2 && target==104));
}
static void callee(CPUState* ctx) {
  events[count++]=3; ++calls; ctx->pc=mode==5 ? 800 : 104;
}
int main(void) {
  for (mode=0; mode<8; ++mode) {
    CPUState ctx={100}; depth=calls=checks=replacements=count=0;
    limit=mode==6 ? 0 : 24;
    galaxypad_bind_direct_calls_v1(1,mode==7 ? NULL : boundary);
    int resume=galaxypad_direct_transfer(&ctx,100,104,callee);
    assert(depth==0);
    assert(resume==(mode==0 || mode==3));
    if (mode==0) {
      assert(calls==1 && checks==2 && count==5);
      for (unsigned i=0;i<5;++i) assert(events[i]==i+1);
    }
    if (mode==1) assert(!calls && checks==1 && ctx.pc==100);
    if (mode==2) assert(calls==1 && checks==2 && count==4 && ctx.pc==104);
    if (mode==3) assert(!calls && replacements==1 && checks==2 && ctx.pc==104);
    if (mode==4) assert(calls==1 && replacements==1 && ctx.pc==900);
    if (mode==5) assert(calls==1 && checks==1 && ctx.pc==800);
    if (mode>=6) assert(!calls && !checks && !count && ctx.pc==100);
  }
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-direct-transfer-') as directory:
    stage = Path(directory)
    (stage / 'driver.c').write_text(driver)
    binary = stage / 'driver'
    subprocess.run(['clang', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', '-I', str(source),
                    str(stage / 'driver.c'), str(source / 'binding.c'),
                    '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print('Direct transfer: boundary/replacement ordering, early return and balanced depth pass ASan/UBSan')
