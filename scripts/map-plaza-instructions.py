"""Stream exact baseline module disassembly; retain sampled PCs and nearby context.

No app launch/build. Families are opcode attribution, not removable CPU cost or
proof that a memory operand accesses guest CPU state. Sampling skid remains.
"""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import importlib.util
import json
import re
import subprocess

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--profile', type=Path,
                    default=root/'generated/runtime/plaza-profile-r821/summary-r822.json',
                    help='CPU summary from this exact module; caller verifies trace UUID/load base')
args = parser.parse_args()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
module = root/'generated/modules-scale-r387/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-c4cbfba1bd04990b/gRMGE01_recomp.dylib'
profile = args.profile.resolve()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(module) == 'c0021b9f2fad3acc3746b6a582b46935e2f7b60bc38434ad7d485564957c7939'
summary = json.loads(profile.read_text())
assert summary['address_binary'] == 'gRMGE01_recomp.dylib'
names = sorted({r['name'] for r in summary['addresses'] if re.fullmatch('func_[0-9A-Fa-f]{8}',r['name'])})
selected = [r for r in summary['addresses'] if r['name'] in set(names)]
assert selected and all('cycles' in r for r in selected)
wanted = {((int(r['raw_offset'],16)&~3)+delta) for r in selected for delta in range(-16,24,4)}
command = ['xcrun','llvm-objdump','--disassemble-symbols='+','.join('_'+n for n in names),str(module)]
print(f'Disassembling {len(names)} sampled chunks; retaining {len(wanted)} context PCs',flush=True)
with (out/'context.asm').open('x') as output:
    process = subprocess.Popen(command,stdout=subprocess.PIPE,text=True)
    for line in process.stdout:
        match = re.match(r'^\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+',line)
        if match and int(match[1],16) in wanted:
            output.write(line)
    if process.wait()!=0:
        raise RuntimeError('Disassembly failed')
spec = importlib.util.spec_from_file_location('classifier',root/'scripts/classify-cpu-instructions.py')
classifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classifier)
assembly = (out/'context.asm').read_text()
instructions = {}
for line in assembly.splitlines():
    match = re.match(r'^\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+(\S+)\s*(.*)',line)
    if match:
        instructions[int(match[1],16)] = (match[2],match[3])
symbol_text = subprocess.check_output(['xcrun','nm','-n',str(module)],text=True)
globals_by_address = {}
for line in symbol_text.splitlines():
    match = re.fullmatch(r'([0-9a-f]+) \S (_g_ppc_lazy_fp_enabled|_g_mem_write_journal)',line)
    if match:
        globals_by_address[int(match[1],16)] = match[2]
counts = classifier.classify(summary,assembly,names,details=True)
weights = classifier.classify(summary,assembly,names,details=True,weight_field='cycles')
families, cycles = Counter(),Counter()
load_bases, load_opcodes = Counter(),Counter()
load_origins = Counter()
for name in names:
    families.update(counts[name]['families'])
    cycles.update(weights[name]['families'])
    for site in weights[name]['instructions']:
        if classifier.family(site['opcode']) == 'load':
            base = re.search(r'\[([^,\]]+)', site['operands'])
            load_bases[base[1] if base else 'literal_or_unrecognized'] += site['cycles']
            load_opcodes[site['opcode']] += site['cycles']
            origin = classifier.load_origin(instructions,int(site['offset'],16),globals_by_address)
            load_origins[origin] += site['cycles']
assert sum(families.values())==sum(r['samples'] for r in selected)
assert sum(cycles.values())==sum(r['cycles'] for r in selected)
assert sum(load_origins.values()) == cycles['load']
assert sum(load_bases.values()) == cycles['load']
assert sum(load_opcodes.values()) == cycles['load']
report = dict(module_sha256=sha(module),profile_sha256=sha(profile),command=command,
              cpu_samples=summary['samples'],cpu_cycle_weights=summary['cycles'],
              chunk_count=len(names),chunk_samples=sum(families.values()),
              chunk_cycle_weights=sum(cycles.values()),families_samples=dict(families),
              families_cycle_weights=dict(cycles),chunks_samples=counts,chunks_cycles=weights,
              load_base_register_cycle_weights=dict(load_bases.most_common()),
              load_opcode_cycle_weights=dict(load_opcodes.most_common()),
              proven_local_load_origins_cycle_weights=dict(load_origins.most_common()),
              recognized_globals={hex(a):n for a,n in globals_by_address.items()},
              boundary='Sampled-PC opcode families, not instruction latency, state provenance or predicted FPS')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('command','chunks_samples','chunks_cycles')},indent=2))
