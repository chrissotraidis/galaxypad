"""Compare the integrated caller against the pinned upstream sequential oracle."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import hashlib

root = Path(__file__).resolve().parents[1]
source = subprocess.check_output(['git', '-C', str(root/'ref/ModernGekko/vendor/dolphin'),
    'show', json.loads((root/'config/dependencies.lock.json').read_text())['repositories']['recompCore']['upstreamRevision'] + ':GXRuntime/src/core/cpu.c']).decode()
assert hashlib.sha256(source.encode()).hexdigest() == 'ec16e3a5bc42809220465528086dc88b00cd491053056649020e94e15e3b69c7'
body = 'bool ppc_psq_store(' + source.split('bool ppc_psq_store(', 1)[1].split('\nvoid ppc_rfi(', 1)[0]
quant = 'static s64 psq_quantize_int(' + source.split('static s64 psq_quantize_int(', 1)[1].split('\nstatic void psq_store_value', 1)[0]
candidate = body.replace('ppc_psq_store(', 'candidate(', 1).replace(
    '    psq_store_value(cpu, ea, type, scale, cpu->fpr[frS]);',
    (root/'patches/experiments/lc-pair-store.inc').read_text() +
    '    psq_store_value(cpu, ea, type, scale, cpu->fpr[frS]);')
actual_path = Path(sys.argv[1]) if len(sys.argv) == 2 else root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core/cpu.c'
actual = actual_path.read_text()
actual = 'bool ppc_psq_store(' + actual.split('bool ppc_psq_store(', 1)[1].split('\nvoid ppc_rfi(', 1)[0]
assert actual.replace('ppc_psq_store(', 'candidate(', 1) == candidate
prefix = r'''
#include "core/types.h"
#include <math.h>
#include <assert.h>
#include <fenv.h>
typedef struct CPUState CPUState;
struct CPUState {
  u32 gqr[8]; f64 fpr[32], ps1[32];
  void* (*external_pointer)(CPUState*,u32,u32);
};
static bool g_mem_write_journal=false, grant=false, mutate=false;
static unsigned requests, stores;
static u8 bytes[2]; static u32 addresses[2];
static bool psq_check_enabled(CPUState* c,bool indexed,u32 cia) { return true; }
static s32 gqr_scale(u32 x) { x &= 63u; return x<32 ? (s32)x : (s32)x-64; }
static u32 psq_type_size(u8 t) { return t==0?4:(t==4||t==6)?1:(t==5||t==7)?2:0; }
static void* pointer(CPUState* c,u32 ea,u32 size) {
  ++requests; assert(size==0); return grant ? bytes : NULL;
}
'''
store = r'''
static void psq_store_value(CPUState* c,u32 ea,u8 type,s32 scale,f64 value) {
  assert(stores<2); addresses[stores]=ea;
  bytes[stores++]=(u8)psq_quantize_int(value,0,255,scale);
  if (mutate) { c->ps1[9]=77; c->gqr[6]=0; }
}
'''
test = r'''
int main(void) {
  CPUState c={0}; c.external_pointer=pointer;
  /* Rejected requests preserve callback order, wrapped address, live lane1. */
  for (unsigned journal=0;journal<2;++journal) {
    stores=requests=0; grant=false; mutate=true; g_mem_write_journal=journal;
    c.gqr[6]=4; c.fpr[9]=12; c.ps1[9]=34;
    assert(candidate(&c,9,UINT32_MAX,false,6,false,0));
    assert(stores==2 && requests==!journal);
    assert(addresses[0]==UINT32_MAX && addresses[1]==0);
    assert(bytes[0]==12 && bytes[1]==77);
  }
  g_mem_write_journal=false; mutate=false;
  u64 bits=0x1234567812345678ull;
  for (unsigned i=0;i<1000000;++i) {
    bits=bits*6364136223846793005ull+1; c.fpr[9]=f64_value(bits);
    bits=bits*6364136223846793005ull+1; c.ps1[9]=f64_value(bits);
    c.gqr[6]=4|((i&63u)<<8);
    stores=0; feclearexcept(FE_ALL_EXCEPT);
    ppc_psq_store(&c,9,0xe0000000,false,6,false,0);
    int flags=fetestexcept(FE_ALL_EXCEPT);
    u8 a=bytes[0],b=bytes[1]; stores=requests=0; grant=true;
    feclearexcept(FE_ALL_EXCEPT);
    candidate(&c,9,0xe0000000,false,6,false,0);
    assert(fetestexcept(FE_ALL_EXCEPT)==flags);
    assert(requests==1 && stores==0 && bytes[0]==a && bytes[1]==b);
  }
  for (u32 type=0;type<8;++type) {
    stores=requests=0; c.gqr[6]=type;
    candidate(&c,9,0xe0000000,true,6,false,0);
    assert(requests==0);
    stores=0;
    if(type!=4) { candidate(&c,9,0xe0000000,false,6,false,0); assert(requests==0); }
  }
}
'''
hooks = (root/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Hooks.cpp').read_text()
assert 'size != 0' in hooks.split('void* StaticRecompCore::HookExternalPointer',1)[1].split('\nu32 StaticRecompCore::HookSPRRead',1)[0]
with tempfile.TemporaryDirectory(prefix='galaxypad-pair-store-') as directory:
    path=Path(directory); c=path/'probe.c'
    c.write_text(prefix+quant+store+body+candidate+test)
    subprocess.run(['clang','-O2','-ffp-contract=off','-fno-fast-math','-fsanitize=undefined,address',
                    '-I',str(root/'ref/ModernGekko/vendor/dolphin/GXRuntime/include'),str(c),'-o',str(path/'probe')],check=True)
    subprocess.run([str(path/'probe')],check=True)
print('Optional pair-store quantization parity and rejected-request fallback passed')
