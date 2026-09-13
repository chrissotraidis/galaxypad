"""Source-derived ordering contract for future paired-store optimization."""
from pathlib import Path
import json
import subprocess
import tempfile
import hashlib

root = Path(__file__).resolve().parents[1]
source = subprocess.check_output(['git', '-C', str(root/'ref/ModernGekko/vendor/dolphin'),
    'show', json.loads((root/'config/dependencies.lock.json').read_text())['repositories']['recompCore']['upstreamRevision'] + ':GXRuntime/src/core/cpu.c']).decode()
assert hashlib.sha256(source.encode()).hexdigest() == 'ec16e3a5bc42809220465528086dc88b00cd491053056649020e94e15e3b69c7'
body = source.split('bool ppc_psq_store(', 1)[1].split('\nvoid ppc_rfi(', 1)[0]
prefix = r'''
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
typedef uint8_t u8; typedef uint32_t u32; typedef int32_t s32;
typedef struct { u32 gqr[8]; double fpr[32], ps1[32]; } CPUState;
static bool enabled = true;
static unsigned count;
static u32 addresses[2]; static double values[2]; static u8 types[2];
static s32 scales[2];
static bool psq_check_enabled(CPUState* c, bool indexed, u32 cia) { return enabled; }
static s32 gqr_scale(u32 x) { x &= 63u; return x < 32 ? (s32)x : (s32)x - 64; }
static u32 psq_type_size(u8 type) {
    return type == 0 ? 4 : (type == 4 || type == 6) ? 1 :
           (type == 5 || type == 7) ? 2 : 0;
}
static void psq_store_value(CPUState* c, u32 ea, u8 type, s32 scale, double value) {
    assert(count < 2);
    addresses[count] = ea; values[count] = value;
    types[count] = type; scales[count] = scale;
    if (count++ == 0) { c->ps1[9] = 77; c->gqr[6] = 0; }
}
'''
test = r'''
int main(void) {
    CPUState c = {0}; c.fpr[9] = 12; c.ps1[9] = 34;
    c.gqr[6] = 0x3d04;
    assert(ppc_psq_store(&c, 9, UINT32_MAX, false, 6, false, 0x80452a2c));
    assert(count == 2 && addresses[0] == UINT32_MAX && addresses[1] == 0);
    assert(values[0] == 12 && values[1] == 77); /* lane read after callback */
    assert(types[0] == 4 && types[1] == 4); /* GQR sampled before callbacks */
    assert(scales[0] == -3 && scales[1] == -3);
    count = 0; c.gqr[6] = 4;
    assert(ppc_psq_store(&c, 9, 100, true, 6, false, 0));
    assert(count == 1);
    count = 0; c.gqr[6] = 1;
    assert(ppc_psq_store(&c, 9, 100, false, 6, false, 0));
    assert(count == 0);
    enabled = false; c.gqr[6] = 4;
    assert(!ppc_psq_store(&c, 9, 100, false, 6, false, 0));
    assert(count == 0);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-psq-order-') as directory:
    path = Path(directory)
    c = path / 'probe.c'
    c.write_text(prefix + 'bool ppc_psq_store(' + body + test)
    subprocess.run(['clang', '-O2', '-fsanitize=undefined', str(c), '-o', str(path/'probe')], check=True)
    subprocess.run([str(path/'probe')], check=True)
print('Paired-store callback ordering, wraparound, GQR snapshot and lane-count contract passed')
