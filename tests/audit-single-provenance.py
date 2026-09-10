"""Conservative, read-only precision scope audit of the R464 straight-line fixture.

No rewriting; every suffix starts with unknown registers. Unknown operations
fail closed. Memory accesses invalidate all facts because callbacks can mutate
CPUState. Scalar writes are treated as unknown because they may be gated.
"""
import hashlib
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
module = Path((root/'generated/modules/RMGE01/active-module.txt').read_text().strip())
sources = list((module.parent/'dolrecomp-output/RMGE01_generated/chunks').glob('*804B60A0.c'))
assert len(sources) == 1
source = sources[0].read_text()
source_sha = hashlib.sha256(source.encode()).hexdigest()
assert source_sha == '38d5085e7e8eceece0521f5566c012a5c15fa5a7be7c2c1fe915985d28c376ac'
body = source.split('label_804B6278:\n', 1)[1].split('label_804B6328:\n', 1)[0]
operations = re.findall(r'// ([0-9A-F]{8}):\s+(\w+)\s*(.*)', body)
assert len(operations) == 44
assert [int(pc,16) for pc,_,_ in operations] == list(range(0x804b6278,0x804b6328,4))
memory = {'psq_l','lfs','psq_st'}
paired = {'ps_mul','ps_madd','ps_sum0','ps_sum1','ps_muls0','ps_muls1'}
scalar = {'frsp','fadds','fsubs','fmuls','fnmsubs','fmadds','frsqrte'}
reports=[]
for start in range(44):
    known=set(); eligible=[]
    for pc,op,operands in operations[start:]:
        regs=[int(r) for r in re.findall(r'f(\d+)',operands)]
        if op in memory:
            known.clear()
        elif op in paired:
            if op in {'ps_muls0','ps_muls1'} and regs[2] in known:
                eligible.append(pc)
            known.add(regs[0])
        elif op in scalar or op == 'ps_neg':
            known.discard(regs[0])
        elif op == 'ps_merge00':
            if regs[1] in known and regs[2] in known:
                known.add(regs[0])
            else:
                known.discard(regs[0])
        elif op != 'blr':
            raise ValueError('Unreviewed operation: '+op)
    reports.append({'entry': operations[start][0], 'eligible_factor_rounding_sites': eligible})
# Regression expectations for this exact inspected fixture, not generic dataflow.
expected = ['804B62D4', '804B62D8', '804B62DC', '804B62F4']
assert reports[0]['eligible_factor_rounding_sites'] == expected
assert sorted({pc for row in reports for pc in row['eligible_factor_rounding_sites']}) == expected
for row in reports:
    # Direct external dispatch to a consumer never has the preceding producer fact.
    assert row['entry'] not in row['eligible_factor_rounding_sites']
assert all(not row['eligible_factor_rounding_sites'] for row in reports[23:])
installed = root/'generated/macos/GalaxyPad.app/Contents/MacOS/gRMGE01_recomp.dylib'
with installed.open('rb') as stream:
    module_sha = hashlib.file_digest(stream, 'sha256').hexdigest()
assert module_sha == '1fb635f71b8ca6afab01fccb1b06a0a5e2b6ddd5a1aec4bb8ef629af3201dc7a'
profile = json.loads((root/'generated/fprf-site-r423.json').read_text())
chunk_samples = sum(row['samples'] for row in profile['addresses']
                    if row['name'] == 'func_804B60A0')
assert chunk_samples == 1143 and profile['samples'] == 28822
print(json.dumps({'source_sha256': source_sha, 'module_sha256': module_sha,
    'reports':reports,
    'scope': {'eligible_static_sites': len(expected), 'chunk_guest_instructions':1024,
              'chunk_cpu_leaf_samples':chunk_samples, 'all_cpu_leaf_samples':profile['samples'],
              'whole_chunk_sample_percent':100*chunk_samples/profile['samples']},
    'decision':'No full-module build: only four path-local sites; whole chunk is 3.97% of retained CPU samples and eligible-site dynamic cost is unproven.',
    'boundary':'Whole-chunk sample share is not removable time or an FPS prediction. Path facts do not hold at shared external-entry labels. No code change or general precision-optimization rejection.'}, indent=2))
