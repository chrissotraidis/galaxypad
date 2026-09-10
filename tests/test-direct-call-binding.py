"""Real dlopen/dlsym extension lifecycle test, not CPU-guard correctness proof."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = root / 'apple/experiments/guarded-direct-calls'
wrapper = r'''
#include "binding.h"
__attribute__((visibility("default")))
int probe_transfer(CPUState* state, uint32_t target) {
  return galaxypad_direct_call_boundary(state, target);
}
'''
driver = r'''
#include "binding.h"
#include <assert.h>
#include <dlfcn.h>
#include <stddef.h>
struct CPUState { unsigned calls; uint32_t target; int allow; };
static int boundary(CPUState* state, uint32_t target) {
  ++state->calls; state->target = target; return state->allow;
}
int main(int argc, char** argv) {
  assert(argc == 2);
  for (unsigned run=0; run<3; ++run) {
    void* library = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL); assert(library);
    int (*bind)(uint32_t, GalaxyPadDirectBoundary) = dlsym(library, "galaxypad_bind_direct_calls_v1");
    int (*transfer)(CPUState*, uint32_t) = dlsym(library, "probe_transfer");
    assert(bind && transfer);
    CPUState state = {0,0,1};
    assert(!transfer(&state,0x80001000) && state.calls==0);
    assert(bind(1,boundary));
    assert(!transfer(NULL,0x80001000) && state.calls==0);
    assert(transfer(&state,0x80002000));
    assert(state.calls==1 && state.target==0x80002000);
    state.allow=0;
    assert(!transfer(&state,0x80003000) && state.calls==2);
    assert(!bind(2,boundary)); // Unsupported ABI disables the stale callback.
    assert(!transfer(&state,0x80004000) && state.calls==2);
    assert(bind(1,boundary));
    assert(bind(1,NULL)); // Detach before host/core or module teardown.
    assert(!transfer(&state,0x80005000) && state.calls==2);
    assert(dlclose(library)==0);
  }
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-direct-binding-') as directory:
    stage = Path(directory)
    (stage / 'wrapper.c').write_text(wrapper)
    (stage / 'driver.c').write_text(driver)
    flags = ['clang', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined',
             '-I', str(source)]
    library = stage / 'binding.dylib'
    subprocess.run([*flags, '-dynamiclib', '-fvisibility=hidden', str(source / 'binding.c'),
                    str(stage / 'wrapper.c'), '-o', str(library)], check=True)
    binary = stage / 'driver'
    subprocess.run([*flags, str(stage / 'driver.c'), '-o', str(binary)], check=True)
    subprocess.run([str(binary), str(library)], check=True)
print('Direct-call binding: dlopen, version rejection, forwarding, detach/reload pass ASan/UBSan')
