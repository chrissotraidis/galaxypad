"""Compile completed decoder fixtures with accepted PGO; no app/module build."""
import argparse
import hashlib
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
import importlib.util

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--benchmark', action='store_true')
parser.add_argument('--thinlto', action='store_true', help='Retain optimized IR and ThinLTO; keep harness native to prevent fixture specialization')
parser.add_argument('--cached-reads', action='store_true', help='Compare read-loop mapping cache instead of DCBZ policy')
parser.add_argument('--fused-tail', action='store_true', help='Compare isolated normal coefficient-tail fusion')
parser.add_argument('--tail-coverage', action='store_true', help='Assert fused-path hits in correctness runs only')
parser.add_argument('--identity-control', action='store_true', help='Use unchanged source for both linked variants')
parser.add_argument('--drop-chunk-profile', action='store_true', help='Unchanged candidate source without PGO, to isolate profile effects')
parser.add_argument('--loop-coverage', action='store_true', help='Count cached-loop reads in correctness fixtures, not timing')
parser.add_argument('--long-codes', action='store_true', help='Use valid long-code tables with independently expected coefficients')
parser.add_argument('--long-run-budget', action='store_true', help='Give long-code fixtures enough guest cycles to run without forced yield re-entry')
parser.add_argument('--runtime-charge-reset', action='store_true', help='Reset module charge per dispatch like the host; preserve aggregate charge for oracle')
args = parser.parse_args()
assert not (args.fused_tail and args.cached_reads)
assert not args.identity_control or not (args.fused_tail or args.cached_reads or args.tail_coverage or args.loop_coverage)
assert not args.drop_chunk_profile or not (args.fused_tail or args.cached_reads or args.identity_control or args.tail_coverage or args.loop_coverage)
assert not args.tail_coverage or (args.fused_tail and not args.benchmark)
assert not args.loop_coverage or (args.cached_reads and not args.benchmark)
assert not args.long_run_budget or args.long_codes
assert not (args.long_run_budget and args.runtime_charge_reset)
root = Path(__file__).resolve().parents[1]
module = Path((root/'generated/modules/RMGE01/active-module.txt').read_text().strip())
assert hashlib.sha256(module.read_bytes()).hexdigest() == '1180447313459c4c153ca74e5215811e88a9b69a00d15feff940f062148fc631'
source = module.parent/'dolrecomp-output/RMGE01_generated/chunks/chunk_1103_text1_804530A0.c'
original = source.read_text()
assert hashlib.sha256(original.encode()).hexdigest() == 'e6aa915816ee2a89534f75c4d59dd0c145f7a5d0162c3e1a15b2ebe33b996dcc'
original = original.replace('#include "../RMGE01.h"', '#include "'+str(source.parent.parent/'RMGE01.h')+'"')
helper = (root/'patches/experiments/dcbz-ram-loop.inc').read_text()
assert hashlib.sha256(helper.encode()).hexdigest() == 'ed743fdeb1b32af89dfd1fbfefa671a63b2a36ed7c2c59b684f105275783a421'
anchor = 'for (u32 i = 0; i < 32; i += 4) mem_write32(ctx, ea + i, 0);'
assert original.count(anchor)==8
candidate = original.replace(anchor, 'u8* line = galaxypad_dcbz_prepare(ctx, ea);\n        for (u32 i = 0; i < 32; i += 4) galaxypad_dcbz_store(ctx, ea, line, i);')
candidate = candidate.replace('void func_804530A0(CPUState* ctx) {', '#include <string.h>\n'+helper+'\nvoid func_804530A0(CPUState* ctx) {')
if args.cached_reads:
    spec = importlib.util.spec_from_file_location('cached', root/'scripts/cache-huffman-loop-reads.py')
    cached = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cached)
    candidate = cached.transform(original)
    if args.loop_coverage:
        candidate = candidate.replace('typedef struct { u8 *ram, *exram;', 'unsigned long galaxy_loop_reads;\ntypedef struct { u8 *ram, *exram;')
        candidate = candidate.replace('const u32 masked = addr', '++galaxy_loop_reads;\n    const u32 masked = addr')
if args.fused_tail:
    spec = importlib.util.spec_from_file_location('tail', root/'scripts/fuse_huffman_tail.py')
    tail = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tail)
    candidate = tail.transform(original)
    if args.tail_coverage:
        signature = 'static inline bool galaxy_huffman_tail(CPUState* ctx) {'
        assert candidate.count(signature) == 1
        report = '''#include <assert.h>
#include <stdio.h>
static unsigned long galaxy_tail_hits;
__attribute__((destructor)) static void galaxy_report_tail(void) {
    assert(galaxy_tail_hits > 0);
    fprintf(stderr, "fused_tail_hits=%lu\\n", galaxy_tail_hits);
}
'''
        candidate = candidate.replace(signature, report+signature+'\n++galaxy_tail_hits;', 1)
if args.identity_control or args.drop_chunk_profile:
    candidate = original
graph = (module.parent/'module-build/build.ninja').read_text()
block = re.search(r'^build [^\n]*: C_COMPILER[^\n]*'+re.escape(str(source))+r'[^\n]*\n((?:  [^\n]*\n)*)',graph,re.M)
fields = dict(re.findall(r'^  (\w+) = (.*)$',block[1],re.M))
flags = shlex.split(fields['DEFINES']+' '+fields['INCLUDES']+' '+fields['FLAGS'])
assert '-O2' in flags and '-flto=thin' in flags and '-fno-fast-math' in flags
# Native assembly permits symbol renaming after PGO has been applied, without
# changing profile lookup names. This is pre-link evidence, not a ThinLTO app.
if not args.thinlto:
    flags=[flag for flag in flags if not flag.startswith('-flto')]
if not args.benchmark:flags+=['-fsanitize=address,undefined']
with tempfile.TemporaryDirectory(prefix='galaxypad-huffman-throughput-') as directory:
    temp = Path(directory)
    objects=[]
    for name,text in [('reference',original),('candidate',candidate)]:
        path=temp/(name+'.c');path.write_text(text);obj=temp/(name+'.o')
        assembly=temp/(name+'.s')
        compile_flags = flags
        if args.drop_chunk_profile and name == 'candidate':
            compile_flags = [flag for flag in flags if not flag.startswith('-fprofile-instr-use=')]
            assert len(compile_flags) == len(flags)-1
        if args.thinlto:
            ir=temp/(name+'.ll')
            subprocess.run(['clang',*compile_flags,'-S','-emit-llvm',str(path),'-o',str(ir)],check=True)
            text=ir.read_text()
            assert re.search(r'define .*@func_804530A0\(',text)
            text=text.replace('func_804530A0',name+'_chunk')
            ir.write_text(text)
            # Assemble already-optimized IR without running another optimizer.
            subprocess.run(['clang','-cc1','-triple','arm64-apple-macosx14.0.0',
                            '-emit-llvm-bc','-flto=thin','-disable-llvm-passes',
                            '-x','ir',str(ir),'-o',str(obj)],check=True)
            assert obj.read_bytes()[:4] in (b'BC\xc0\xde',b'\xde\xc0\x17\x0b')
        else:
            subprocess.run(['clang',*compile_flags,'-S',str(path),'-o',str(assembly)],check=True)
            assembly.write_text(assembly.read_text().replace('_func_804530A0','_'+name+'_chunk'))
            subprocess.run(['clang','-c',str(assembly),'-o',str(obj)],check=True)
        objects.append(str(obj))
    if not args.thinlto:
        subprocess.run(['size', *objects], check=True)
    harness_flags=['-O2','-flto=thin','-I'+str(root/'ref/ModernGekko/vendor/dolphin/GXRuntime/include')]
    if args.runtime_charge_reset:
        harness_flags += ['-DRUNTIME_CHARGE_RESET']
    if args.benchmark:harness_flags+=['-DBENCHMARK']
    else:harness_flags+=['-fsanitize=address,undefined']
    harness = root/'tests/fixtures/huffman-throughput.c'
    if args.long_codes:
        harness = root/'tests/fixtures/huffman-long-throughput.c'
        if args.long_run_budget:
            harness_flags += ['-DLONG_RUN_BUDGET']
        if args.loop_coverage:
            harness_flags += ['-DLOOP_COVERAGE']
    elif args.loop_coverage:
        harness_text = harness.read_text().replace('int main(void) {', 'extern unsigned long galaxy_loop_reads;\nint main(void) {')
        harness_text = harness_text.replace('printf("completed synthetic', 'printf("cached_loop_reads=%lu\\n",galaxy_loop_reads);\n    printf("completed synthetic')
        harness = temp/'coverage.c'
        harness.write_text(harness_text)
    if args.thinlto:
        harness_object=temp/'harness.o'
        subprocess.run(['clang',*[f for f in harness_flags if not f.startswith('-flto')],
                        '-c',str(harness),'-o',str(harness_object)],check=True)
        subprocess.run(['clang',*harness_flags,str(harness_object),*objects,
                        '-Wl,-exported_symbol,_reference_chunk',
                        '-Wl,-exported_symbol,_candidate_chunk','-o',str(temp/'test')],check=True)
        subprocess.run(['size',str(temp/'test')],check=True)
    else:
        subprocess.run(['clang',*harness_flags,str(harness),*objects,'-o',str(temp/'test')],check=True)
    subprocess.run([str(temp/'test')],check=True,timeout=90)
