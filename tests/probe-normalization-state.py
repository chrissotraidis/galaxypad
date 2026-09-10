#!/usr/bin/env python3
"""Private real normalization region: local FP-state differential, not promotion."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import importlib.util

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--optimized', action='store_true', help='O2/ThinLTO correctness run without sanitizers; not a performance benchmark')
p.add_argument('--compact', action='store_true', help='Use the exact compact FP helper closure instead of full CPUState scratch')
p.add_argument('--production-fenv', action='store_true', help='Omit oracle FENV_ACCESS pragma to investigate production-context differences')
args = p.parse_args()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
core = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
source = root/'generated/modules-scale-r387/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-c4cbfba1bd04990b/dolrecomp-output/RMGE01_generated/chunks/chunk_1202_text1_804B60A0.c'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(source) == '38d5085e7e8eceece0521f5566c012a5c15fa5a7be7c2c1fe915985d28c376ac'
text = source.read_text()
addresses = list(range(0x804B6BE0, 0x804B6C04, 4))
body = text[text.index('label_804B6BE0:'):text.index('label_804B6C04:')]
assert not any(token in body for token in ('mem_read', 'mem_write', 'downcount', 'goto '))
cases = []
for a in addresses:
    match = re.search(rf'    case 0x{a:08X}u: (ctx->downcount -= \d+; )?goto label_{a:08X};', text)
    assert match
    charge = match[1] or ''
    cases.append(f'case 0x{a:08X}u: '+(f'if (external) {{ {charge} }} ' if charge else '')+f'goto label_{a:08X};')
switch = 'switch(ctx->pc) {\n'+'\n'.join(cases)+'\ndefault: return;\n}\n'
reference = 'static __attribute__((noinline)) void original(CPUState* ctx, bool external) {\n'+switch+body+'}\n'
local, n = re.subn(r'    ctx->pc = 0x[0-9A-F]+u;\n', '', body)
assert n == 9
local, n = re.subn(r'    if \(!ppc_fp_available_inline\(ctx, 0x[0-9A-F]+u\)\) return;\n', '', local)
assert n == 9
charge_switch = re.sub(r'goto label_[0-9A-F]+;', 'break;', switch)
entry_switch = 'switch(entry) {\n'+''.join(f'case 0x{a:08X}u: goto label_{a:08X};\n' for a in addresses)+'default: __builtin_unreachable();\n}\n'
candidate = '''static __attribute__((noinline,flatten)) void local_state(CPUState* cpu, bool external) {
 CPUState* ctx=cpu;
'''+charge_switch+'''
 const u32 entry=cpu->pc;
 if (!ppc_fp_available_inline(cpu,entry)) return;
 CPUState scratch={0};
 memcpy(scratch.fpr,cpu->fpr,7*sizeof(f64));
 memcpy(scratch.ps1,cpu->ps1,7*sizeof(f64));
 scratch.fpscr=cpu->fpscr;
 ctx=&scratch;
'''+entry_switch+local+'''
 memcpy(cpu->fpr,scratch.fpr,7*sizeof(f64));
 memcpy(cpu->ps1,scratch.ps1,7*sizeof(f64));
 cpu->fpscr=scratch.fpscr;
 cpu->pc=0x804B6C00u;
}
'''
compact_manifest = None
if args.compact:
    spec=importlib.util.spec_from_file_location('compact',root/'scripts/compact_fp_state.py')
    compact=importlib.util.module_from_spec(spec);spec.loader.exec_module(compact)
    helpers,names,compact_manifest=compact.build((core/'cpu_interpreter_float.c').read_text())
    candidate=candidate.replace('CPUState scratch={0};','CompactFPState scratch={0};')
    candidate=candidate.replace('ctx=&scratch;','CompactFPState* fp=&scratch;')
    compact_local=re.sub(r'\b(?:'+'|'.join(names)+r')\b',lambda m:names[m[0]],local)
    compact_local=compact_local.replace('ctx','fp')
    assert candidate.count(local)==1
    candidate=candidate.replace(local,compact_local)
    candidate=helpers+candidate
cpu = (core/'cpu.c').read_text()
start = cpu.index('bool ppc_fp_raise_unavailable(')
raise_fp = cpu[start:cpu.index('\n}',start)+2]
prefix = '''#pragma STDC FENV_ACCESS ON
#include "cpu_interpreter_float.c"
#include "cpu_interpreter_table.c"
#include "cpu_exception.c"
#include <assert.h>
#include <stdio.h>
bool g_ppc_lazy_fp_enabled=false;
'''+raise_fp+'\n'
if args.production_fenv:
    prefix=prefix.replace('#pragma STDC FENV_ACCESS ON\n','',1)
driver = r'''
static u64 rng=826;
static u64 bits(void){rng^=rng<<13;rng^=rng>>7;rng^=rng<<17;return rng;}
int main(void) {
 u64 saved_mode,saved_flags;
 __asm__ volatile("mrs %0, fpcr":"=r"(saved_mode));
 __asm__ volatile("mrs %0, fpsr":"=r"(saved_flags));
 const u64 edge[]={0,0x8000000000000000ull,1,0x000fffffffffffffull,
  0x0010000000000000ull,0x3ff0000000000000ull,0x7fefffffffffffffull,
  0x7ff0000000000000ull,0xfff0000000000000ull,0x7ff0000000000001ull,
  0x7ff8000000001234ull};
 unsigned cases=0,unavailable=0;
 for(unsigned rn=0;rn<4;rn++)for(unsigned ni=0;ni<2;ni++)
 for(unsigned lazy=0;lazy<2;lazy++)for(unsigned enabled=0;enabled<2;enabled++)
 for(unsigned entry=0;entry<9;entry++)for(unsigned external=0;external<2;external++)
 for(unsigned i=0;i<512;i++) {
  CPUState a={0};
  for(unsigned r=0;r<32;r++) {
   a.gpr[r]=bits();
   a.fpr[r]=f64_value(i<121?edge[(i+r)%11]:bits());
   a.ps1[r]=f64_value(i<121?edge[(i/11+r)%11]:bits());
   if(i%3==0){a.fpr[r]=(double)(int)(bits()%200-100)/16.;a.ps1[r]=a.fpr[r]*.5;}
  }
  a.fpscr=((u32)bits()&~(FPSCR_NI_BIT|3u))|rn|(ni?FPSCR_NI_BIT:0);
  a.msr=((u32)bits()&~PPC_MSR_FP)|(enabled?PPC_MSR_FP:0);
  a.cr=bits();a.lr=bits();a.pc=0x804B6BE0+entry*4;
  a.downcount=(i&1)?-1024:4096;a.exception=i&1;
  CPUState b=a;g_ppc_lazy_fp_enabled=lazy;
  const u64 flags=i&0x9f;
  ppc_fpscr_control_updated(&a);
  __asm__ volatile("msr fpsr, %0"::"r"(flags));
  original(&a,external);
  u64 expected,actual;__asm__ volatile("mrs %0, fpsr":"=r"(expected));
  ppc_fpscr_control_updated(&b);
  __asm__ volatile("msr fpsr, %0"::"r"(flags));
  local_state(&b,external);
  __asm__ volatile("mrs %0, fpsr":"=r"(actual));
  if(memcmp(&a,&b,sizeof a)||expected!=actual) {
   fprintf(stderr,"Mismatch rn%u ni%u lazy%u enabled%u entry%u external%u i%u\n",rn,ni,lazy,enabled,entry,external,i);
   fprintf(stderr,"statecmp=%d FPSR=%llx/%llx FPSCR=%08x/%08x\n",memcmp(&a,&b,sizeof a),
      (unsigned long long)expected,(unsigned long long)actual,a.fpscr,b.fpscr);
   return 1;
  }
  if(lazy&&!enabled){assert(a.srr0==0x804B6BE0+entry*4);unavailable++;}
  cases++;
 }
 __asm__ volatile("msr fpcr, %0"::"r"(saved_mode));
 __asm__ volatile("msr fpsr, %0"::"r"(saved_flags));
 printf("%u whole CPUState/FPSR comparisons pass; %u FP-unavailable cases; 9 suffixes, internal/external entries\n",cases,unavailable);
}
'''
(out/'region.inc').write_text(reference+candidate)
(out/'probe.c').write_text(prefix+reference+candidate+driver)
command=['clang','-O2','-std=c11','-ffp-contract=off','-fno-fast-math',
 *(['-flto=thin'] if args.optimized else ['-fsanitize=address,undefined']),
 '-Wl,-dead_strip','-I',str(core),
 '-I',str(core.parents[1]/'include'),str(out/'probe.c'),'-o',str(out/'probe')]
with (out/'build.log').open('w') as log:
 subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
result=subprocess.run([str(out/'probe')],text=True,capture_output=True)
(out/'result.log').write_text(result.stdout+result.stderr)
print(result.stdout+result.stderr,flush=True)
(out/'report.json').write_text(json.dumps({'source_sha256':sha(source),'command':command,
 'compact_manifest':compact_manifest,
 'helper_source_sha256':{name:sha(core/name) for name in ('cpu_interpreter_float.c',
 'cpu_interpreter_private.h','cpu_interpreter_table.c','cpu_exception.c','cpu.c')},
 'region_sha256':sha(out/'region.inc'),'exit_code':result.returncode,
 'boundary':'Private arithmetic-region differential; no callbacks, full chunk, runtime or performance acceptance'},indent=2)+'\n')
result.check_returncode()
