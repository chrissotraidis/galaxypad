#!/usr/bin/env python3
"""Build one private Simulator candidate from a passing whole-chunk fixture.

Reuse the byte-verified R804 unchanged control and unchanged object graph.
No normal selection, installation, runtime, or save changes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--test',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
build=root/'generated/build/ios-simulator-module'
work=args.output.resolve()
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
baseline=build/'gRMGE01_recomp.dylib'
expected='3acdcddcd47812c2e2a67b8cec0cf06c17009cf1ad7f2e9dc9abd83158a1bac0'
assert sha(baseline)==expected
test=args.test.resolve();report=json.loads((test/'report.json').read_text())
assert report['exit_code']==0 and report['normalization_vector']
tested=test/'candidate/whole.c'
assert report['inputs'][str(tested)]==sha(tested)
helper=root/'patches/experiments/normalization-vector.inc'
assert report['inputs'][str(helper)]==sha(helper)
assert re.search(r'normalization vector accepted calls: [1-9][0-9]*', (test/'result.log').read_text())
rows=[]
for header,variables in re.findall(r'^build ([^\n]+)\n((?:  [^\n]*\n)*)',(build/'build.ninja').read_text(),re.M):
    target,rest=header.split(': ',1);rule,_,inputs=rest.partition(' ')
    rows.append((target,rule,inputs,dict(re.findall(r'^  (\w+) = (.*)$',variables,re.M))))
selected=[r for r in rows if r[1].startswith('C_COMPILER_') and r[2].split(' || ')[0].endswith('/chunk_1202_text1_804B60A0.c')]
assert len(selected)==1
target,_,source_name,compile_fields=selected[0]
source_path=Path(source_name.split(' || ')[0])
assert sha(source_path)==report['source_sha256']
flags=shlex.split(compile_fields['DEFINES']+' '+compile_fields['FLAGS']+' '+compile_fields['INCLUDES'])
links=[r for r in rows if r[0]=='gRMGE01_recomp.dylib'];assert len(links)==1
_,_,link_inputs,fields=links[0]
objects=shlex.split(link_inputs.split(' | ')[0]);assert len(objects)==1329 and target in objects
identities={name:sha(build/name) for name in objects}
prior_dir=root/'generated/candidates/cross-diagnostic-r804'
prior=json.loads((prior_dir/'provenance.json').read_text())
assert prior['objects']==identities and prior['baseline_sha256']==prior['control_sha256']==expected
assert sha(prior_dir/'control.dylib')==expected
assert prior['compile_command'][1:-5]==flags
prefix=['/usr/bin/clang',*shlex.split(fields['LANGUAGE_COMPILE_FLAGS']+' '+fields['ARCH_FLAGS']+' '+fields['LINK_FLAGS'])]
old_link=prior['control_command']
assert old_link[:old_link.index('-o')]==prefix
original_response='\n'.join(shlex.quote(str(build/name)) for name in objects)+'\n'+fields['LINK_LIBRARIES']+'\n'
assert Path(old_link[-1][1:]).read_text()==original_response
assert fields['PRE_LINK']==fields['POST_BUILD']==':'
assert not work.exists();work.mkdir(parents=True)
text=tested.read_text()
shim='\n__attribute__((visibility("default")))\nvoid probe_configure('
assert text.count(shim)==1
text=text.split(shim)[0]
visible='__attribute__((visibility("default"))) void func_804B60A0(CPUState* ctx) {'
assert text.count(visible)==1
text=text.replace(visible,'void func_804B60A0(CPUState* ctx) {')
assert helper.read_text() in text
text+='''
__attribute__((visibility("default"))) unsigned long probe_vector_fast(void) {return norm_vector_fast;}
__attribute__((visibility("default"))) unsigned long probe_vector_attempts(void) {return norm_vector_fast+norm_vector_rejected;}
'''
candidate=work/'candidate.c';candidate.write_text(text)
obj=work/'candidate.o';output=work/'gRMGE01_recomp.dylib'
core=root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
command=['/usr/bin/clang',*flags,'-I'+str(core),'-c',str(candidate),'-o',str(obj)]
provenance=dict(baseline_sha256=expected,objects=identities,selected=False,
    test_report_sha256=sha(test/'report.json'),tested_source_sha256=sha(tested),
    helper_sha256=sha(helper),source_sha256=sha(candidate),compile_command=command,
    control_reused=str(prior_dir/'control.dylib'),instrumented=True)
(work/'provenance.json').write_text(json.dumps(provenance,indent=2))
print('Verified original control and all1329 object hashes; compile private normalization chunk',flush=True)
subprocess.run(command,cwd=build,check=True)
response=work/'candidate.rsp'
response.write_text('\n'.join(shlex.quote(str(obj if name==target else build/name)) for name in objects)+'\n'+fields['LINK_LIBRARIES']+'\n')
link=[*prefix,'-o',str(output),fields['SONAME_FLAG'],fields['INSTALLNAME_DIR']+fields['SONAME'],'@'+str(response)]
provenance['link_command']=link
(work/'provenance.json').write_text(json.dumps(provenance,indent=2))
print('Link private Simulator candidate; do not restart this build on silence',flush=True)
subprocess.run(link,cwd=build,check=True)
assert sha(baseline)==expected and identities=={name:sha(build/name) for name in objects}
provenance['candidate_sha256']=sha(output)
(work/'provenance.json').write_text(json.dumps(provenance,indent=2))
subprocess.run(['xcrun','vtool','-show-build',str(output)],check=True)
subprocess.run(['codesign','--verify','--verbose=2',str(output)],check=True)
print('Private Simulator module ready: '+str(output),flush=True)
