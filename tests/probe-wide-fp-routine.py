#!/usr/bin/env python3
"""Verify a complete extracted routine against its original generated chunk.

Private oracle only: no optimized implementation or module selection.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import importlib.util
import os

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--candidate', action='store_true')
parser.add_argument('--benchmark', action='store_true')
parser.add_argument('--fp-guard-chains', action='store_true',
                    help='Private availability-chain correctness probe; no memory candidate')
parser.add_argument('--whole-fp-guards', action='store_true',
                    help='Compare independent full-chunk libraries, retaining original entry dispatch')
parser.add_argument('--resident-merges', action='store_true',
                    help='Correctness-only static ARM64 merge region in original whole chunk')
parser.add_argument('--resident-multiply', action='store_true')
parser.add_argument('--resident-fma', action='store_true')
parser.add_argument('--resident-lanes', action='store_true')
parser.add_argument('--resident-long', action='store_true')
parser.add_argument('--random-inputs', action='store_true')
parser.add_argument('--fma-ties', action='store_true')
parser.add_argument('--normalization-vector', action='store_true')
parser.add_argument('--routine', choices=('wide','normalize','cross'),default='wide')
args = parser.parse_args()
if sum((args.resident_multiply,args.resident_fma,args.resident_lanes,args.resident_long))>1:
    parser.error('Select one resident arithmetic region')
if args.resident_multiply or args.resident_fma or args.resident_lanes or args.resident_long:
    args.resident_merges=True
whole_mode = args.whole_fp_guards or args.resident_merges or args.normalization_vector
if args.normalization_vector and (args.routine!='normalize' or args.candidate or args.resident_merges or args.whole_fp_guards or args.fp_guard_chains):
    parser.error('Normalization vector requires its own normalize whole-chunk comparison')
if args.resident_merges and (args.whole_fp_guards or args.candidate or args.fp_guard_chains or (args.benchmark and not args.resident_long) or args.routine != 'wide'):
    parser.error('Resident integration is wide-only; only the long region permits a cost gate')
if args.whole_fp_guards and (args.candidate or args.fp_guard_chains):
    parser.error('Whole-chunk guards cannot combine with other candidates')
if args.fp_guard_chains and (args.candidate or args.benchmark):
    parser.error('Guard-chain probe is correctness-only; actual whole-chunk cost gate is separate')
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
vendor = root/'ref/ModernGekko/vendor/dolphin'
core = vendor/'GXRuntime/src/core'
configured_chunk = os.environ.get('GALAXYPAD_WIDE_FP_CHUNK')
if configured_chunk:
    chunks = [Path(configured_chunk).resolve()]
else:
    chunks = list((root/'generated/modules-scale-r387/RMGE01').glob(
        '*/dolrecomp-output/RMGE01_generated/chunks/*804B60A0.c'))
    if not chunks:
        chunks = list((root/'generated/aot/device-fresh/RMGE01_generated/chunks').glob(
            '*804B60A0.c'))
assert len(chunks) == 1
chunk = chunks[0]
raw = chunk.read_bytes()
assert hashlib.sha256(raw).hexdigest() == '38d5085e7e8eceece0521f5566c012a5c15fa5a7be7c2c1fe915985d28c376ac'
source = raw.decode()
begin,end,constant_offset={'wide':(0x804B64A4,0x804B6548,9392),
                         'normalize':(0x804B6BCC,0x804B6C10,9448),
                         'cross':(0x804B6CB8,0x804B6CF4,0)}[args.routine]
body = source[source.index(f'label_{begin:08X}:'):source.index(f'label_{end:08X}:')]
addresses = list(range(begin,end,4))
assert len(re.findall(r'^label_', body, re.M)) == len(addresses)
assert body.count('goto ') == body.count('goto return_dispatch_804B60A0;') == 1
cases = []
for pc in addresses:
    match = re.search(rf'^    case 0x{pc:08X}u: (.*?)goto label_{pc:08X};$', source, re.M)
    assert match, hex(pc)
    assert re.fullmatch(r'(?:ctx->downcount -= \d+; )?', match[1])
    cases.append(f'case 0x{pc:08X}u: {match[1]}goto label_{pc:08X};')
oracle = ('__attribute__((noinline)) void extracted(CPUState* ctx) {\n'
          'switch(ctx->pc) {\n'+'\n'.join(cases)+'\ndefault: return;\n}\n'+
          body.replace('goto return_dispatch_804B60A0;', 'return;')+'\n}\n')
guard_sites = []
if args.fp_guard_chains:
    spec = importlib.util.spec_from_file_location('guard_chains', root/'scripts/fp_guard_chains.py')
    chain_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(chain_module)
    chain_module.verify_helpers()
    oracle, guard_sites = chain_module.transform(oracle)
    assert guard_sites, 'No guard-chain transformation exercised'
    print('FP guard sites relocated:', [hex(pc) for pc in guard_sites], flush=True)
(out/'routine.inc').write_text(oracle)
header = chunk.parent.parent/'RMGE01.h'
unit = source.replace('#include "../RMGE01.h"', f'#include "{header}"')
unit += '\n'+oracle+'\n__attribute__((noinline)) void original(CPUState* ctx) { func_804B60A0(ctx); }\n'
if args.candidate:
    spec=importlib.util.spec_from_file_location('wide',root/'scripts/wide_fp_candidate.py')
    wide=importlib.util.module_from_spec(spec);spec.loader.exec_module(wide)
    unit=unit.replace('void extracted(CPUState* ctx)', 'void slow_extracted(CPUState* ctx)',1)
    unit+='\n'+wide.build(body)+'''
static unsigned long wide_accepted;
unsigned long probe_accepted(void) { return wide_accepted; }
__attribute__((noinline)) void extracted(CPUState* ctx) {
    u8 *input,*output,*constant;
    if(wide_eligible(ctx,&input,&output,&constant)) {
        ++wide_accepted;wide_fast(ctx,input,output,constant);
    } else slow_extracted(ctx);
}
'''
else:
    unit+='\nunsigned long probe_accepted(void) { return 0; }\n'
(out/'routine.c').write_text(unit)
configured_graph = os.environ.get('GALAXYPAD_WIDE_FP_GRAPH')
graph_path = Path(configured_graph).resolve() if configured_graph else chunk.parents[3]/'module-build/build.ninja'
graph = graph_path.read_text()
stanza = re.search(r'^build [^\n]+: C_COMPILER_[^\n]+ '+re.escape(str(chunk))+r'[^\n]*\n((?:  [^\n]*\n)*)', graph, re.M)
assert stanza
fields = dict(re.findall(r'^  (\w+) = (.*)$', stanza[1], re.M))
flags = shlex.split(fields['DEFINES']+' '+fields['FLAGS']+' '+fields['INCLUDES'])
assert all(f in flags for f in ('-flto=thin', '-DNDEBUG', '-ffp-contract=off', '-fno-fast-math'))
host_flags = []
skip_next = False
for flag in flags:
    if skip_next:
        skip_next = False
        continue
    if flag in ('-isysroot',) or flag.startswith('-mios-'):
        skip_next = flag == '-isysroot'
        continue
    host_flags.append(flag)
commands = []
objects = []
inputs = {str(driver_path): hashlib.sha256(driver_path.read_bytes()).hexdigest()
          for driver_path in [root/'tests/wide-fp-routine-driver.c', header,
                              root/'scripts/wide_fp_candidate.py',
                              root/'scripts/fp_guard_chains.py',
                              *sorted(core.glob('cpu*.c'))]}
for path in [*([] if whole_mode else [out/'routine.c']), *sorted(core.glob('cpu*.c'))]:
    obj = out/(path.stem+'.o')
    command = ['clang', *host_flags, '-I'+str(core), '-c', str(path), '-o', str(obj)]
    commands.append(command)
    subprocess.run(command, check=True)
    objects.append(str(obj))
libraries=[]
resident_metadata=None
candidate_objects=[]
if whole_mode:
    if args.normalization_vector:
        vector_path=root/'patches/experiments/normalization-vector.inc'
        helper=vector_path.read_text()
        assert hashlib.sha256((core/'cpu_interpreter_float.c').read_bytes()).hexdigest()=='554149a2e7d08783402af38e5a2b898aff476370b0e3a6af0ed4bd411aab934f'
        entry='    if (!ppc_fp_available_inline(ctx, 0x804B6BE0u)) return;'
        assert source.count(entry)==1
        candidate_source=source.replace(entry,entry+'\n    if (norm_vector_try(ctx)) goto label_804B6C04;')
        candidate_source=candidate_source.replace('void func_804B60A0(CPUState* ctx) {',
            '#include "cpu_interpreter_private.h"\n'+helper+'\nvoid func_804B60A0(CPUState* ctx) {',1)
        inputs[str(vector_path)]=hashlib.sha256(vector_path.read_bytes()).hexdigest()
    elif args.resident_merges:
        spec=importlib.util.spec_from_file_location('resident',root/'scripts/stage_resident_merges.py')
        resident=importlib.util.module_from_spec(spec);spec.loader.exec_module(resident)
        candidate_source,region_object,resident_metadata=resident.build(source,out/'resident',args.resident_multiply,args.resident_fma,args.resident_lanes,args.resident_long)
        candidate_objects=[str(region_object)]
        commands.extend(resident_metadata['commands'])
        for path in [root/'scripts/stage_resident_merges.py',root/'tests/export-resident-merge-region.cpp',
                     root/'tests/aot-paired-merge.h',root/'tests/aot-paired-multiply.h',root/'tests/adapt-arm64-fpr-cache.py',
                     root/'tests/aot-cpu-fpr-layout.h',
                     *sorted((root/'tests/aot-support').rglob('*.h')),
                     vendor/'Source/Core/Common/Arm64Emitter.cpp',
                     vendor/'Source/Core/Core/PowerPC/JitArm64/JitArm64_RegCache.cpp',
                     out/'resident/cache.cpp',out/'resident/region.S',region_object]:
            inputs[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
    else:
        spec=importlib.util.spec_from_file_location('whole_guards',root/'scripts/fp_guard_chains.py')
        guards=importlib.util.module_from_spec(spec);spec.loader.exec_module(guards)
        guards.verify_helpers()
        candidate_source,guard_sites=guards.transform(source)
        assert guard_sites
        print('Whole-chunk relocated guard count:',len(guard_sites),flush=True)
    shim='''
__attribute__((visibility("default")))
void probe_configure(bool lazy,PPCMemWriteJournal journal,void* user) {
    g_ppc_lazy_fp_enabled=lazy;g_mem_write_journal=journal;g_mem_write_journal_user=user;
}
'''
    for variant,text in [('control',source),('candidate',candidate_source)]:
        directory=out/variant;directory.mkdir()
        text=text.replace('#include "../RMGE01.h"',f'#include "{header}"')
        assert text.count('void func_804B60A0(CPUState* ctx) {')==1
        text=text.replace('void func_804B60A0(CPUState* ctx) {',
                          '__attribute__((visibility("default"))) void func_804B60A0(CPUState* ctx) {')
        path=directory/'whole.c';path.write_text(text+shim)
        if args.normalization_vector:
            counts='return norm_vector_fast;' if variant=='candidate' else 'return 0;'
            path.write_text(text+shim+'\n__attribute__((visibility("default"))) unsigned long probe_vector_fast(void) {'+counts+'}\n')
        obj=directory/'whole.o';library=directory/'whole.dylib'
        command=['clang',*host_flags,'-I'+str(core),'-c',str(path),'-o',str(obj)]
        commands.append(command);subprocess.run(command,check=True)
        command=['clang','-arch','arm64','-mmacosx-version-min=14.0','-flto=thin',
                 '-dynamiclib','-Wl,-dead_strip','-Wl,-install_name,@rpath/whole.dylib',
                 '-Wl,-exported_symbol,_func_804B60A0','-Wl,-exported_symbol,_probe_configure',
                 *(['-Wl,-exported_symbol,_probe_vector_fast'] if args.normalization_vector else []),
                 str(obj),*objects,*(candidate_objects if variant=='candidate' else []),'-o',str(library)]
        commands.append(command);subprocess.run(command,check=True)
        libraries.append(str(library))
        (directory/'size.txt').write_text(subprocess.check_output(['xcrun','size','-m',str(library)],text=True))
        inputs[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
        inputs[str(library)]=hashlib.sha256(library.read_bytes()).hexdigest()
driver = root/'tests/wide-fp-routine-driver.c'
command = ['clang', '-O2', '-std=c11', '-ffp-contract=off', '-fno-fast-math',
           f'-DROUTINE_START=0x{begin:X}u',f'-DROUTINE_LENGTH={len(addresses)}',
           f'-DCONSTANT_OFFSET={constant_offset}',
           *(['-DWIDE_BENCHMARK'] if args.benchmark else []),
           *(['-DWIDE_DYNAMIC'] if whole_mode else []),
           *(['-DWIDE_RANDOM_INPUTS'] if args.random_inputs else []),
           *(['-DWIDE_FMA_TIES'] if args.fma_ties else []),
           *(['-DWIDE_VECTOR_COUNTS'] if args.normalization_vector else []),
           '-I'+str(core), '-I'+str(vendor/'GXRuntime/include'),
           str(driver), *objects, '-flto=thin', '-Wl,-dead_strip', '-o', str(out/'probe')]
commands.append(command)
subprocess.run(command, check=True)
result = subprocess.run([str(out/'probe'),*libraries], capture_output=True, text=True)
(out/'result.log').write_text(result.stdout+result.stderr)
(out/'report.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(raw).hexdigest(),
    inputs=inputs, candidate=args.candidate, whole_fp_guards=args.whole_fp_guards,
    resident_merges=resident_metadata,
    random_inputs=args.random_inputs,
    fma_ties=args.fma_ties,
    normalization_vector=args.normalization_vector,
    guard_sites=guard_sites, addresses=addresses, commands=commands, exit_code=result.returncode,
    boundary='Private routine comparison only; not game performance or promotion'), indent=2))
print(result.stdout+result.stderr, flush=True)
result.check_returncode()
if args.candidate:
    accepted=re.search(r'fast-path accepted calls: (\d+)',result.stdout)
    assert accepted and int(accepted[1])>0, 'Candidate was never exercised'
