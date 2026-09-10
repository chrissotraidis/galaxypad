"""Actual quantizer parity, host FP/errno behavior, and optional CPU timing."""
from pathlib import Path
import argparse
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'scripts'))
from psq_scale import transform, reference_source, OLD, NEW

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--benchmark', action='store_true')
args = parser.parse_args()
source = reference_source((root / 'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core/cpu.c').read_text())
changed = transform(source)
assert reference_source(changed) == source
assert changed.replace(NEW, OLD, 1) == source
for invalid in (source + '\n', changed):
    try:
        transform(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError('Unknown/reapplied source accepted')
try:
    reference_source(changed + '\n')
except ValueError:
    pass
else:
    raise AssertionError('Unknown candidate accepted')

def quant(text, name):
    body = 'static s64 psq_quantize_int(' + text.split('static s64 psq_quantize_int(', 1)[1].split('\nstatic void psq_store_value', 1)[0]
    return body.replace('static s64 psq_quantize_int(', '__attribute__((noinline)) s64 ' + name + '(', 1)

program = r'''
#include "core/types.h"
#include <assert.h>
#include <errno.h>
#include <fenv.h>
#include <math.h>
#include <stdio.h>
#include <time.h>
#pragma STDC FENV_ACCESS ON
QUANTIZERS
static u64 rng = 0x3426719abcde9876ull;
static u64 next(void) { rng = rng * 6364136223846793005ull + 1; return rng; }
static volatile s64 sink;
static double now(void) {
    struct timespec t; assert(clock_gettime(CLOCK_THREAD_CPUTIME_ID, &t) == 0);
    return t.tv_sec + t.tv_nsec * 1e-9;
}
static void check(f64 value, s32 scale, s64 lo, s64 hi, int preflags) {
    feclearexcept(FE_ALL_EXCEPT); feraiseexcept(preflags); errno = EDOM;
    s64 a = reference(value, lo, hi, scale);
    int af = fetestexcept(FE_ALL_EXCEPT), ae = errno;
    feclearexcept(FE_ALL_EXCEPT); feraiseexcept(preflags); errno = EDOM;
    s64 b = candidate(value, lo, hi, scale);
    assert(a == b && af == fetestexcept(FE_ALL_EXCEPT) && ae == errno);
}
int main(void) {
#ifdef BENCHMARK
    f64 values[4096];
    for (unsigned i=0;i<4096;++i) values[i] = (s32)(next() >> 32) / 1048576.0;
    for (unsigned pass=0;pass<4;++pass) {
        s64 (*volatile fn)(f64,s64,s64,s32) = (pass==0 || pass==3) ? reference : candidate;
        double start=now(); s64 result=0;
        for (unsigned i=0;i<10000000;++i)
            result += fn(values[i&4095],0,255,-3);
        sink=result;
        printf("%s seconds=%.9f digest=%lld\n", (pass==0 || pass==3)?"control":"candidate",now()-start,(long long)result);
    }
#else
    const int modes[]={FE_TONEAREST,FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO};
    const s64 lows[]={0,0,-128,-32768}, highs[]={255,65535,127,32767};
    const u64 special[]={0,0x8000000000000000ull,1,0x8000000000000001ull,
        0x7ff0000000000000ull,0xfff0000000000000ull,0x7ff0000000000001ull,
        0x7ff8000000000001ull,0xfff0000000000001ull,0x7fefffffffffffffull,
        0x0010000000000000ull,0x3ff0000000000000ull};
    unsigned cases=0;
    for(unsigned mode=0;mode<4;++mode) {
        assert(fesetround(modes[mode])==0);
        // Extend outside the GQR range to exercise unchanged libm fallback.
        for(s32 scale=-160;scale<=160;++scale) {
            for(unsigned type=0;type<4;++type) {
                for(unsigned i=0;i<128;++i) {
                    f64 value=i<sizeof(special)/sizeof(*special)?f64_value(special[i]):f64_value(next());
                    check(value,scale,lows[type],highs[type],i&1?FE_DIVBYZERO:0); ++cases;
                }
                // Values immediately surrounding saturation and integer boundaries.
                for(int edge=-1;edge<=1;++edge) {
                    f64 value=ldexp((f64)highs[type]+edge,-scale);
                    check(value,scale,lows[type],highs[type],0); ++cases;
                }
            }
        }
    }
    printf("quantizer parity cases=%u rounding_modes=4 scales=321 types=4\n",cases);
#endif
    return 0;
}
'''.replace('QUANTIZERS', quant(source, 'reference') + quant(changed, 'candidate'))

with tempfile.TemporaryDirectory(prefix='galaxypad-psq-scale-') as directory:
    folder = Path(directory)
    c = folder / 'probe.c'
    c.write_text(program)
    for name, flags in ([('benchmark', ['-O2', '-DBENCHMARK'])] if args.benchmark else
                        [('sanitized', ['-O1', '-fsanitize=address,undefined']), ('optimized', ['-O2'])]):
        binary = folder / name
        subprocess.run(['clang', *flags, '-ffp-contract=off', '-fno-fast-math',
                        '-I', str(root / 'ref/ModernGekko/vendor/dolphin/GXRuntime/include'),
                        str(c), '-o', str(binary)], check=True)
        print(name, flush=True)
        subprocess.run([str(binary)], check=True)
