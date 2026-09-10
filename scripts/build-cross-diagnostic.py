#!/usr/bin/env python3
"""Private Simulator diagnostic; verify unchanged relink before changing one object.

Never runs Ninja, changes source inputs, normal selection, apps or saves.
"""
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--ni',action='store_true',help='Build distinct NI-capable diagnostic using the verified R804 control')
parser.add_argument('--uninstrumented',action='store_true',help='Build private R809 NI candidate without eligibility counters')
args=parser.parse_args()
if args.uninstrumented and not args.ni:
    parser.error('--uninstrumented requires --ni')

root=Path(__file__).resolve().parents[1]
build=root/'generated/build/ios-simulator-module'
work=root/('generated/candidates/cross-diagnostic-r807' if args.ni else 'generated/candidates/cross-diagnostic-r804')
if args.uninstrumented:work=root/'generated/candidates/cross-uninstrumented-r809'
baseline=build/'gRMGE01_recomp.dylib'
expected='3acdcddcd47812c2e2a67b8cec0cf06c17009cf1ad7f2e9dc9abd83158a1bac0'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(baseline)==expected
assert not work.exists(), 'Do not overwrite an existing experiment'
helper=(root/'patches/experiments/cross-island-vector.inc').read_text()
original_helper=helper
helper_sha=('2186c80040d479474785b8c193e494f068b6e518cc37dc7dc5882048ab0fbd4d' if args.ni else
            '94d089540f41667a053415ba105b86fc2072a6ebbbf61aef8bb4ca1c6ecd280c')
assert hashlib.sha256(helper.encode()).hexdigest()==helper_sha
rows=[]
for header,variables in re.findall(r'^build ([^\n]+)\n((?:  [^\n]*\n)*)',(build/'build.ninja').read_text(),re.M):
    target,rest=header.split(': ',1);rule,_,inputs=rest.partition(' ')
    rows.append((target,rule,inputs,dict(re.findall(r'^  (\w+) = (.*)$',variables,re.M))))
selected=[row for row in rows if row[1].startswith('C_COMPILER_') and
          row[2].split(' || ')[0].endswith('/chunk_1202_text1_804B60A0.c')]
assert len(selected)==1
target,_,input_path,compile_fields=selected[0]
flags=shlex.split(compile_fields['DEFINES']+' '+compile_fields['FLAGS']+' '+compile_fields['INCLUDES'])
source_path=Path(input_path.split(' || ')[0]);source=source_path.read_text()
assert sha(source_path)=='38d5085e7e8eceece0521f5566c012a5c15fa5a7be7c2c1fe915985d28c376ac'
links=[row for row in rows if row[0]=='gRMGE01_recomp.dylib'];assert len(links)==1
_,_,inputs,fields=links[0]
objects=shlex.split(inputs.split(' | ')[0])
assert len(objects)==1329 and target in objects
assert fields['PRE_LINK']==fields['POST_BUILD']==':'
identities={}
for name in objects:
    path=build/name
    assert path.is_file() and path.stat().st_mtime_ns<=baseline.stat().st_mtime_ns
    identities[name]=sha(path)
work.mkdir(parents=True)
def link(output,replacement=None):
    response=work/(output.stem+'.rsp')
    response.write_text('\n'.join(shlex.quote(str(replacement if name==target and replacement else build/name))
                                  for name in objects)+'\n'+fields['LINK_LIBRARIES']+'\n')
    command=['/usr/bin/clang',*shlex.split(fields['LANGUAGE_COMPILE_FLAGS']+' '+fields['ARCH_FLAGS']+' '+fields['LINK_FLAGS']),
             '-o',str(output),fields['SONAME_FLAG'],fields['INSTALLNAME_DIR']+fields['SONAME'],'@'+str(response)]
    print('Link '+output.name,flush=True)
    subprocess.run(command,cwd=build,check=True)
    return command
provenance=dict(baseline_sha256=expected,objects=identities,selected=False,ni_capable=args.ni,helper_sha256=helper_sha)
provenance['instrumented']=not args.uninstrumented
(work/'provenance.json').write_text(json.dumps(provenance,indent=2))
control=work/'control.dylib'
if args.ni:
    prior_dir=root/'generated/candidates/cross-diagnostic-r804'
    prior=json.loads((prior_dir/'provenance.json').read_text())
    control=prior_dir/'control.dylib'
    assert prior['baseline_sha256']==prior['control_sha256']==expected
    assert prior['objects']==identities
    assert prior['compile_command'][1:-5]==flags
    previous_link=prior['control_command']
    expected_link_prefix=['/usr/bin/clang',*shlex.split(fields['LANGUAGE_COMPILE_FLAGS']+' '+fields['ARCH_FLAGS']+' '+fields['LINK_FLAGS'])]
    assert previous_link[:previous_link.index('-o')]==expected_link_prefix
    assert previous_link[-3:-1]==[fields['SONAME_FLAG'],fields['INSTALLNAME_DIR']+fields['SONAME']]
    expected_response='\n'.join(shlex.quote(str(build/name)) for name in objects)+'\n'+fields['LINK_LIBRARIES']+'\n'
    assert Path(previous_link[-1][1:]).read_text()==expected_response
    provenance.update(control_command=previous_link,reused_control=str(control))
    print('Verified prior control, all1329 object hashes, compile/link flags and response inputs',flush=True)
else:
    provenance['control_command']=link(control)
provenance['control_sha256']=sha(control)
(work/'provenance.json').write_text(json.dumps(provenance,indent=2))
assert sha(control)==expected, 'Unchanged relink differs; inspect before compiling a candidate'

stats=r'''
#include <stdio.h>
static unsigned long long cross_calls,cross_fast,cross_mode,cross_range,cross_ties;
static void cross_report(void) {
  if((cross_calls&4095)!=0) return;
  u64 flags;__asm__ volatile("mrs %0, fpsr":"=r"(flags)::"memory");
  fprintf(stderr,"[cross-island-r804] calls=%llu fast=%llu mode=%llu range=%llu ties=%llu\n",
          cross_calls,cross_fast,cross_mode,cross_range,cross_ties);
  __asm__ volatile("msr fpsr, %0"::"r"(flags):"memory");
}
'''
if args.ni:stats=stats.replace('[cross-island-r804]','[cross-island-r807]')
condition='cpu->fpscr&FPSCR_RN_MASK' if args.ni else 'cpu->fpscr&(FPSCR_NI_BIT|FPSCR_RN_MASK)'
anchor=f'if({condition}) return false;'
assert helper.count(anchor)==1
helper=helper.replace(anchor,f'++cross_calls; if({condition}) {{++cross_mode;return false;}}')
anchor='''      return false;
    }
  }
  u64 saved_status;'''
assert helper.count(anchor)==1
helper=helper.replace(anchor,anchor.replace('return false;','++cross_range;return false;'))
anchor='''    return false;
  }
  const float64x2_t out5'''
assert helper.count(anchor)==1
helper=helper.replace(anchor,anchor.replace('return false;','++cross_ties;return false;'))
helper=helper.replace('  return true;','  ++cross_fast;return true;')
if args.uninstrumented:
    helper=original_helper
    stats=''
header=source_path.parent.parent/'RMGE01.h'
changed=source.replace('#include "../RMGE01.h"',f'#include "{header}"')
start,end='label_804B6CCC:','label_804B6CD0:'
body=start+changed.split(start,1)[1].split(end,1)[0]
call='ppc_ps_mul_op(ctx, 4, 1, 2);'
assert body.count(call)==1 and 'if (!ppc_fp_available_inline(ctx, 0x804B6CCCu)) return;' in body
replacement='''{ bool accepted=cross_island_try(ctx); cross_report();
      if(accepted) {ctx->pc=0x804B6CE0u;goto label_804B6CE4;} }
    '''+call
if args.uninstrumented:
    replacement='''if(cross_island_try(ctx)) {ctx->pc=0x804B6CE0u;goto label_804B6CE4;}
    '''+call
changed=changed.replace(body,body.replace(call,replacement),1)
changed=f'#include "{header}"\n#include "cpu_interpreter_private.h"\n#include <arm_neon.h>\n'+stats+helper+'\n'+changed
if args.uninstrumented:
    assert all(name not in changed for name in ['cross_report','cross_calls','cross_fast','cross_mode','cross_range','cross_ties'])
candidate_source=work/'candidate.c';candidate_source.write_text(changed)
obj=work/'candidate.o'
core=root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
command=['/usr/bin/clang',*flags,'-I'+str(core),'-c',str(candidate_source),'-o',str(obj)]
print('Compile diagnostic chunk',flush=True);subprocess.run(command,cwd=build,check=True)
subprocess.run(['python3',str(root/'tests/test-cross-island-vector.py'),
                '--uninstrumented-source' if args.uninstrumented else '--diagnostic-source',str(candidate_source),
                *(['--require-ni-fast'] if args.ni else [])],check=True)
provenance.update(source_sha256=sha(candidate_source),compile_command=command)
(work/'provenance.json').write_text(json.dumps(provenance,indent=2))
output=work/'gRMGE01_recomp.dylib'
provenance.update(source_sha256=sha(candidate_source),compile_command=command,link_command=link(output,obj),
                  candidate_sha256=sha(output))
assert sha(baseline)==expected
(work/'provenance.json').write_text(json.dumps(provenance,indent=2))
subprocess.run(['xcrun','vtool','-show-build',str(output)],check=True)
subprocess.run(['codesign','--verify','--verbose=2',str(output)],check=True)
print('Private diagnostic ready: '+str(output),flush=True)
