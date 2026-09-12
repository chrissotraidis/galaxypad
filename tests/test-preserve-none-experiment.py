#!/usr/bin/env python3
"""ABI/differential screen for an unselected generated calling convention.

Compiles the complete real sampled chunk twice. Exercises every integer ABI
save/restore suffix against actual GXRuntime memory/FP/exception helpers. This
is host correctness and compiler-shape evidence, never gameplay acceptance.
"""
import importlib.util
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('experiment', root/'scripts/create-preserve-none-experiment.py')
experiment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(experiment)
source = root/'generated/aot/device-fresh/RMGE01_generated'
runtime = root/'ref/ModernGekko/vendor/dolphin/GXRuntime'
chunk = source/'chunks/chunk_1299_text1_805170A0.c'
header_text = (source/'RMGE01.h').read_text()
chunk_text = chunk.read_text()
assert 'case 0x80517538u: ctx->downcount -= 4; goto label_80517538;' in chunk_text
assert 'case 0x80517584u: ctx->downcount -= 4; goto label_80517584;' in chunk_text
assert len(experiment.PROTOTYPE.findall(header_text)) == 1322
assert experiment.DEFINITION.findall(chunk_text) == ['func_805170A0']
changed = experiment.transform_header(header_text)
assert changed.count(experiment.ATTRIBUTE) == 1323
assert experiment.transform_chunk(chunk_text).count(experiment.ATTRIBUTE) == 1
for invalid in (changed, 'typedef void (*Wrong)(CPUState* ctx);'):
    try:
        experiment.transform_header(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError('must reject partial/repeated transforms')

program = r'''
#include "core/cpu.h"
#include <assert.h>
#include <stdlib.h>
#include <string.h>
void reference_chunk(CPUState*);
__attribute__((preserve_none)) void candidate_chunk(CPUState*);
typedef void (*Reference)(CPUState*);
typedef __attribute__((preserve_none)) void (*Candidate)(CPUState*);
static Reference volatile reference_pointer = reference_chunk;
static Candidate volatile candidate_pointer = candidate_chunk;
static __attribute__((preserve_none,noinline)) void candidate_forward(CPUState* c) {
    candidate_chunk(c); // Direct generated-to-generated call uses the same ABI.
}
static unsigned callbacks;
static unsigned long long trace;
static unsigned rng = 0x513826;
static unsigned random32(void) { rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; return rng; }
static void observe(CPUState* c, u32 a, u64 v, u8 n) {
    ++callbacks;
    trace = trace * 131 + a + v + n + c->pc + c->downcount;
    c->gpr[11] += 4; // A normal-ABI callback can change later effective addresses.
    c->gpr[30] ^= (unsigned)v;
    c->reserve_valid = !c->reserve_valid;
}
static u64 external_read(CPUState* c, u32 a, u8 n) {
    observe(c, a, 0x12345678, n);
    return a ^ 0xa5a5;
}
static void external_write(CPUState* c, u32 a, u64 v, u8 n) { observe(c,a,v,n); }
static void journal(u32 a, u32 n, void* user) {
    (void)user; ++callbacks; trace = trace*131+a+n;
}
static void check_state(CPUState* a, CPUState* b) {
    // Separate buffers are deliberate. Every other byte, including padding,
    // PC, cycle charge, reservations and mutable callback state must match.
    b->ram=a->ram; b->exram=a->exram;
    assert(memcmp(a,b,sizeof(*a))==0);
}
int main(void) {
    u8 *ar=malloc(4096), *br=malloc(4096), *ae=malloc(4096), *be=malloc(4096);
    assert(ar && br && ae && be);
    unsigned cases=0;
    for(unsigned mode=0;mode<8;++mode) for(unsigned restore=0;restore<2;++restore)
    for(unsigned reg=14;reg<=31;++reg) for(unsigned repeat=0;repeat<80;++repeat) {
        CPUState a={0},b;
        for(unsigned i=0;i<32;++i) a.gpr[i]=random32();
        for(unsigned i=0;i<4096;++i) ar[i]=ae[i]=(u8)random32();
        memcpy(br,ar,4096);memcpy(be,ae,4096);
        a.ram=ar;a.ram_size=4096;a.exram=ae;a.exram_size=4096;
        a.external_read=external_read;a.external_write=external_write;
        a.pc=(restore?0x80517548u:0x805174fcu)+(reg-14)*4;
        a.lr=0x7fff0103u; a.downcount=1000-(int)(random32()%2000);
        a.cr=random32();a.xer=random32();a.reserve_valid=repeat&1;
        const u32 bases[]={0x80000800,0xc0000800,0x90000800,0xd0000800,
                           0x00000800,0xcc000800,0x80000028,0x90001010};
        a.gpr[11]=bases[mode];a.reserve_addr=a.gpr[11]-32;
        b=a;b.ram=br;b.exram=be;
        g_mem_write_journal=repeat%3==0?journal:NULL;
        callbacks=0;trace=0;reference_pointer(&a);
        unsigned reference_callbacks=callbacks;unsigned long long reference_trace=trace;
        callbacks=0;trace=0;
        if(repeat&1) candidate_forward(&b); else candidate_pointer(&b);
        if(callbacks!=reference_callbacks || trace!=reference_trace) {
            fprintf(stderr,"mode=%u restore=%u reg=%u repeat=%u callback=%u/%u trace=%llx/%llx pc=%x/%x cycles=%lld/%lld\n",
                    mode,restore,reg,repeat,reference_callbacks,callbacks,reference_trace,trace,a.pc,b.pc,
                    (long long)a.downcount,(long long)b.downcount);
            abort();
        }
        assert(memcmp(ar,br,4096)==0 && memcmp(ae,be,4096)==0);
        check_state(&a,&b);++cases;
    }
    free(ar);free(br);free(ae);free(be);
    printf("preserve_none: %u complete-chunk save/restore entry comparisons pass\n",cases);
}
'''

with tempfile.TemporaryDirectory(prefix='galaxypad-preserve-none-') as temporary:
    folder = Path(temporary)
    for name, body, header in [('reference',chunk_text,header_text),
                               ('candidate',experiment.transform_chunk(chunk_text),changed)]:
        target=folder/name
        (target/'chunks').mkdir(parents=True)
        (target/'RMGE01.h').write_text(header.replace('func_805170A0',name+'_chunk'))
        (target/'chunks/chunk.c').write_text(body.replace('func_805170A0',name+'_chunk'))
    test=folder/'test.c'; test.write_text(program)
    common=['clang','-std=gnu11','-ffp-contract=off','-fno-fast-math',
            '-Werror=attributes','-Werror=incompatible-function-pointer-types',
            '-I'+str(runtime/'include')]
    implementations=[runtime/'src/core'/name for name in
                     ['cpu.c','cpu_exception.c','cpu_interpreter.c',
                      'cpu_interpreter_integer.c','cpu_interpreter_float.c','cpu_interpreter_table.c']]
    # Apple's ASan keeps a dynamic stack base in x19 across preserve_none
    # calls. A separate minimal compiler reproducer shows that register is
    # legally clobbered by the callee. UBSan avoids that toolchain limitation;
    # do not interpret this screen as ASan support or module promotion.
    for name, flags in [('optimized',['-O2']),('undefined',['-O1','-fsanitize=undefined'])]:
        binary=folder/name
        subprocess.run(common+flags+[str(folder/'reference/chunks/chunk.c'),
                                      str(folder/'candidate/chunks/chunk.c'),str(test),
                                      *map(str,implementations),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
    # Both supported Apple product targets must honor the attribute and typed
    # call. Feature-test availability alone does not prove target support.
    for sdk,target in [('iphonesimulator','arm64-apple-ios16.0-simulator'),
                       ('iphoneos','arm64-apple-ios16.0')]:
        sdkpath=subprocess.check_output(['xcrun','--sdk',sdk,'--show-sdk-path'],text=True).strip()
        subprocess.run(common+['-O2','-target',target,'-isysroot',sdkpath,
                               '-c',str(folder/'candidate/chunks/chunk.c'),
                               '-o',str(folder/(sdk+'.o'))],check=True)
        subprocess.run(common+['-O2','-target',target,'-isysroot',sdkpath,
                               '-fsyntax-only',str(test)],check=True)
print('preserve_none transform, whole-state/memory/callback parity, typed indirect calls and Apple target checks pass')
