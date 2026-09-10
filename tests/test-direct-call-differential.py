"""Execute transformed generated-shaped fixtures against original dispatch.

Uses actual transformer, binding and transfer helper. Guest bodies/runtime are
explicit fixtures, not a claim of real module or full runtime equivalence.
"""
import importlib.util
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prepare', root / 'scripts/prepare-direct-call-chunk.py')
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)

def caller(name, start, target, prefix, suffix, finish):
    continuation = start + 4
    return f'''
static void {name}(CPUState* ctx) {{
    switch(ctx->pc) {{
    case 0x{start:08X}u: goto label_{start:08X};
    case 0x{continuation:08X}u: ctx->downcount -= {suffix}; goto label_{continuation:08X};
    default: assert(0);
    }}
label_{start:08X}:
    ctx->downcount -= {prefix};
    ctx->value += 3;
    if (0x{start:08X}u == 0x80002000u) ctx->saved_lr=ctx->lr;
    // {start:08X}: bl      0x{target:08X}
    {{
            ctx->lr = 0x{continuation:08X}u;
            ctx->pc = 0x{target:08X}u;
            return;
    }}
label_{continuation:08X}:
    ctx->pc = 0x{continuation:08X}u;
    ctx->value ^= 0x1234;
    {finish}
}}
'''

original = caller('outer', 0x80001000, 0x80002000, 5, 7, 'ctx->pc=0;')
original += caller('inner', 0x80002000, 0x80003000, 11, 13,
                   'ctx->lr=ctx->saved_lr; ctx->pc=ctx->lr;')
transformed, count = prepare.transform(original, lambda target: {'80002000':'inner', '80003000':'leaf'}[target])
assert count == 2
driver = r'''
#include "binding.h"
#include <assert.h>
#include <string.h>
struct CPUState { uint32_t pc,lr,saved_lr,value; int64_t downcount; };
static unsigned depth,limit,deny,checks,n;
static int committed,latched;
static uint64_t cycles;
struct Event { uint32_t pc,lr,value; uint64_t cycles; };
static struct Event events[16];
static void flush(CPUState* c) {
  if (committed && c->downcount==0) return;
  cycles+=c->downcount<0 ? (uint64_t)-c->downcount : 1;
  c->downcount=0;committed=1;
  assert(n<16);
  events[n++]=(struct Event){c->pc,c->lr,c->value,cycles};
}
static int boundary(CPUState* c,uint32_t target) {
  assert(c->pc==target);
  if(latched)return 0;
  flush(c);
  if(++checks==deny){latched=1;return 0;}
  committed=0;return 1;
}
static int dolrecomp_call_enter(void){if(depth>=limit)return 0;++depth;return 1;}
static void dolrecomp_call_leave(void){assert(depth);--depth;}
static int dolrecomp_dispatch_replacement(CPUState* c,uint32_t a){(void)c;(void)a;return 0;}
#include "transfer.h"
static void inner(CPUState*);
static void leaf(CPUState* ctx){ctx->downcount-=17;ctx->value*=2;ctx->pc=ctx->lr;}
FIXTURE
static CPUState run(unsigned cap,unsigned reject,int enabled){
  CPUState c={.pc=0x80001000,.value=9};
  depth=checks=n=0;limit=cap;deny=reject;cycles=0;committed=latched=0;
  memset(events,0,sizeof(events));
  galaxypad_bind_direct_calls_v1(1,enabled?boundary:0);
  unsigned dispatches=0;
  while(c.pc){
    assert(++dispatches<16);committed=latched=0;
    if(c.pc==0x80001000 || c.pc==0x80001004)outer(&c);
    else if(c.pc==0x80002000 || c.pc==0x80002004)inner(&c);
    else {assert(c.pc==0x80003000);leaf(&c);}
    flush(&c);assert(depth==0);
  }
  return c;
}
int main(void){
  CPUState reference=run(0,0,0);
  assert(cycles==53 && n==5);
  struct Event expected[16];memcpy(expected,events,sizeof(events));
  for(unsigned cap=0;cap<3;++cap)
    for(unsigned reject=0;reject<6;++reject)
      for(int enabled=0;enabled<2;++enabled){
        CPUState c=run(cap==2?24:cap,reject,enabled);
        assert(c.pc==reference.pc && c.lr==reference.lr && c.value==reference.value);
        assert(c.saved_lr==reference.saved_lr && c.downcount==0);
        assert(cycles==53 && n==5);
        for(unsigned i=0;i<n;++i){
          assert(events[i].pc==expected[i].pc && events[i].lr==expected[i].lr);
          assert(events[i].value==expected[i].value && events[i].cycles==expected[i].cycles);
        }
      }
}
'''
extension = root / 'apple/experiments/guarded-direct-calls'
with tempfile.TemporaryDirectory(prefix='galaxypad-direct-differential-') as directory:
    stage = Path(directory)
    for name, fixture in [('original', original), ('transformed', transformed)]:
        path = stage / f'{name}.c'
        path.write_text(driver.replace('FIXTURE', fixture))
        binary = stage / name
        subprocess.run(['clang', '-std=c11', '-Wall', '-Wextra',
                        '-fsanitize=address,undefined', '-I', str(extension),
                        str(path), str(extension / 'binding.c'), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
print('Original/transformed nested fixtures: 36 modes each match all five boundary states and charges under ASan/UBSan')
