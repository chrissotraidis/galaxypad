"""Offline exact-generated THP transforms; compare O1 sanitized and O2 execution.

Private source is extracted only into a temporary directory. No runtime hooks.
This is an oracle preparation check, not a candidate or decoder accuracy proof.
"""
from pathlib import Path
import hashlib
import re
import subprocess
import tempfile
import argparse
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from psq_scale import reference_source

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--merge-fprf', action='store_true', help='Test isolated FPRF elimination across paired merges')
parser.add_argument('--benchmark', action='store_true', help='Time optimized reference/candidate ABBA, without hashing or setup')
parser.add_argument('--identity-c', action='store_true', help='Test exact already-rounded C-operand shortcut')
parser.add_argument('--flatten', action='store_true', help='Compare same-TU transform-local flattening with the same-TU control')
parser.add_argument('--flatten-lto', action='store_true', help='Compare separate-TU ThinLTO transform-local flattening')
parser.add_argument('--kernels', action='store_true', help='Compare complete reference/candidate chunks with extracted kernels')
parser.add_argument('--fp-routing', action='store_true', help='With --kernels, test checked-entry FP fallthrough routing')
parser.add_argument('--pair-load', action='store_true', help='With --kernels, compare the identical extracted chunk using the RAM paired-load header')
parser.add_argument('--hardware-widen', action='store_true', help='With --kernels, compare normal-finite hardware float widening')
parser.add_argument('--cpu-time', action='store_true', help='Benchmark thread CPU time instead of elapsed wall time')
parser.add_argument('--inline-add-sub', action='store_true', help='With --kernels, inline exact ni_add/ni_sub bodies in the float translation unit')
parser.add_argument('--vector-add-sub', action='store_true', help='With --kernels, test guarded two-lane NEON add/sub helpers')
parser.add_argument('--outline-madd-tie', action='store_true', help='With --kernels, outline the unchanged FMA tie-correction body')
parser.add_argument('--outline-add-nan', action='store_true', help='With --kernels, outline only the exact ni_add NaN branch')
parser.add_argument('--cached-kernel-reads', action='store_true', help='With --kernels, cache read maps only until a store or slow read')
parser.add_argument('--dc-store-run', action='store_true', help='With --kernels, fuse the guarded three-pair DC store run')
parser.add_argument('--zero-column', action='store_true', help='With --kernels, test a guarded whole zero-coefficient column')
parser.add_argument('--nonzero-dc', action='store_true', help='With --zero-column, permit any signed16 DC coefficient with zero AC')
parser.add_argument('--both-dc-kernels', action='store_true', help='With --nonzero-dc, test both transform kernels')
parser.add_argument('--normal-kernel-entry', action='store_true', help='Separate exact normal entries from original transform resumes')
parser.add_argument('--local-columns', action='store_true', help='Guarded local-state first-pass columns, original fallback')
parser.add_argument('--s16-load', action='store_true', help='Specialize signed16 scale-zero coefficient loads only')
parser.add_argument('--s16-pair', action='store_true', help='With --s16-load, share a checked four-byte mapping; original fallback')
parser.add_argument('--dead-pc', action='store_true', help='Avoid unobserved arithmetic PC writes; preserve unavailable-FP path')
parser.add_argument('--psq-scale', action='store_true', help='Exact normal power-of-two factor in quantized stores')
parser.add_argument('--module-pgo', action='store_true', help='Use pinned saved module profile for both supported variants')
args = parser.parse_args()
assert not args.s16_pair or args.s16_load
assert not args.module_pgo or args.normal_kernel_entry or args.outline_add_nan or args.local_columns or args.s16_load or args.dead_pc or args.psq_scale
assert not args.psq_scale or (args.kernels and not any((args.fp_routing,args.pair_load,args.hardware_widen,args.inline_add_sub,args.outline_madd_tie,args.outline_add_nan,args.cached_kernel_reads,args.dc_store_run,args.zero_column,args.normal_kernel_entry,args.local_columns,args.s16_load,args.dead_pc)))
assert not args.dead_pc or (args.kernels and not any((args.fp_routing,args.pair_load,args.hardware_widen,args.inline_add_sub,args.outline_madd_tie,args.outline_add_nan,args.cached_kernel_reads,args.dc_store_run,args.zero_column,args.normal_kernel_entry,args.local_columns,args.s16_load)))
assert not args.s16_load or (args.kernels and not any((args.fp_routing,args.pair_load,args.hardware_widen,args.inline_add_sub,args.outline_madd_tie,args.outline_add_nan,args.cached_kernel_reads,args.dc_store_run,args.zero_column,args.normal_kernel_entry,args.local_columns)))
assert not args.local_columns or (args.kernels and not any((args.fp_routing,args.pair_load,args.hardware_widen,args.inline_add_sub,args.outline_madd_tie,args.outline_add_nan,args.cached_kernel_reads,args.dc_store_run,args.zero_column,args.normal_kernel_entry)))
assert not args.outline_add_nan or (args.kernels and not any((args.fp_routing,args.pair_load,args.hardware_widen,args.inline_add_sub,args.outline_madd_tie,args.cached_kernel_reads,args.dc_store_run,args.zero_column,args.normal_kernel_entry)))
assert not args.fp_routing or args.kernels
assert not args.pair_load or (args.kernels and not args.fp_routing)
assert not args.hardware_widen or (args.kernels and not args.fp_routing and not args.pair_load)
assert not args.cpu_time or args.benchmark
if args.vector_add_sub:
    assert args.kernels
    assert not any(value for name,value in vars(args).items()
                   if name not in ('vector_add_sub','kernels','benchmark','cpu_time'))
assert not args.inline_add_sub or (args.kernels and not args.fp_routing and not args.pair_load and not args.hardware_widen)
assert not args.outline_madd_tie or (args.kernels and not args.fp_routing and not args.pair_load and not args.hardware_widen and not args.inline_add_sub)
assert not args.cached_kernel_reads or (args.kernels and not args.fp_routing and not args.pair_load and not args.hardware_widen and not args.inline_add_sub and not args.outline_madd_tie)
assert not args.dc_store_run or (args.kernels and not any((args.fp_routing, args.pair_load, args.hardware_widen, args.inline_add_sub, args.outline_madd_tie, args.cached_kernel_reads)))
assert not args.zero_column or (args.kernels and not any((args.fp_routing, args.pair_load, args.hardware_widen, args.inline_add_sub, args.outline_madd_tie, args.cached_kernel_reads, args.dc_store_run)))
assert not args.nonzero_dc or args.zero_column
assert not args.both_dc_kernels or args.nonzero_dc
assert not args.normal_kernel_entry or (args.kernels and not any((args.fp_routing,args.pair_load,args.hardware_widen,args.inline_add_sub,args.outline_madd_tie,args.cached_kernel_reads,args.dc_store_run,args.zero_column)))
assert sum((args.identity_c,args.merge_fprf,args.flatten,args.flatten_lto,args.kernels))<=1
assert not args.benchmark or args.merge_fprf or args.identity_c or args.flatten or args.flatten_lto or args.kernels

root = Path(__file__).resolve().parents[1]
module_profile=root/'generated/pgo/rmge01.profdata'
if args.module_pgo:
    assert hashlib.sha256(module_profile.read_bytes()).hexdigest()=='f39a3cedeb6c49f35c411356893c619dc347eb1b0bb5986687f25cf81e7d460d'
generated = root/'generated/modules-fprf-r174/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-27fc425ac63117e7/dolrecomp-output/RMGE01_generated'
source = (generated/'chunks/chunk_1102_text1_804520A0.c').read_text()
assert hashlib.sha256(source.encode()).hexdigest() == 'f2d6911016e8e1c9f46caf5ee97dece58689f5b5f51397860bb868383c34bd61'
core = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
cpu_reference = reference_source((core/'cpu.c').read_text())
if args.s16_pair:
    # Compare both sides with the currently accepted quantized-store helper.
    cpu_reference = (core/'cpu.c').read_text()
    assert hashlib.sha256(cpu_reference.encode()).hexdigest()=='05e221c01bead6801c51217f84398bd10f22e1b810f6d06977e04d8a801436ea'
for path, expected in (
    (core/'cpu_interpreter_float.c','554149a2e7d08783402af38e5a2b898aff476370b0e3a6af0ed4bd411aab934f'),
    (core.parent.parent/'include/core/cpu.h','7fc1448116c581afc53f2c41c6e3b3d11b3a580c5e71147cb52fca493e0d4657'),
):
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, path
functions = []
candidate_functions = []
changed_sites = []
for index, (start, end) in enumerate(((0x804526e8,0x80452b74),(0x80452b74,0x80453008))):
    body = source[source.index(f'\nlabel_{start:08X}:'):source.index(f'\nlabel_{end:08X}:')]
    cases = [line for line in source.splitlines() if re.match(r'    case 0x[0-9A-F]+u:', line)
             and start <= int(line.split('0x')[1].split('u')[0],16) < end]
    assert len(cases) == (end-start)//4
    targets = set(re.findall(r'goto (\w+);',body))
    labels = set(re.findall(r'^(\w+):',body,re.M))
    assert targets-labels == {'return_dispatch_804520A0'}
    # Sentinel LR is outside the chunk. Its real return dispatch would return.
    functions.append(f'void transform{index}(CPUState* ctx) {{\n switch(ctx->pc) {{\n'+
                     '\n'.join(cases)+'\n default: abort();\n }\n'+body+
                     '\nreturn_dispatch_804520A0: return;\n}\n')
    candidate = functions[-1]
    matches = list(re.finditer(r'^label_([0-9A-F]{8}):\n', body, re.M))
    blocks = [body[m.end():matches[i+1].start() if i+1<len(matches) else len(body)]
              for i,m in enumerate(matches)]
    writer = re.compile(r'ppc_ps_(add|sub|mul|madd)_op\(ctx, [0-9, truefals]+\);')
    deferred = re.compile(r'galaxypad_deferred_(add|sub|mul|madd)\(ctx, [0-9, truefals]+\);')
    def simple(block, operation):
        # Only one FP operation with its PC/availability guard, no other effects.
        stripped = re.sub(r'    ctx->pc = 0x[0-9A-F]+u;\n|    //[^\n]*\n|    if \(!ppc_fp_available_inline\(ctx, 0x[0-9A-F]+u\)\) return;\n', '', block)
        return bool(operation.fullmatch(stripped.strip()))
    def merge(block):
        # Exact generated ps_merge shape. No calls other than FP availability,
        # no control flow or memory, and no FPSCR/MSR changes.
        return bool(re.fullmatch(
            r'    ctx->pc = 0x[0-9A-F]+u;\n    // [0-9A-F]+: ps_merge[01]{2}  [^\n]+\n'
            r'    if \(!ppc_fp_available_inline\(ctx, 0x[0-9A-F]+u\)\) return;\n'
            r'    \{\n        f64 ps0 = ctx->(?:fpr|ps1)\[\d+\];\n'
            r'        f64 ps1 = ctx->(?:fpr|ps1)\[\d+\];\n'
            r'        ctx->fpr\[\d+\] = ps0;\n        ctx->ps1\[\d+\] = ps1;\n    \}\n\s*', block))
    for i, block in enumerate(blocks):
        if not simple(block, writer):
            continue
        crossed_merge = False
        for following in blocks[i+1:]:
            if merge(following):
                crossed_merge = True
            elif simple(following, deferred):
                continue
            elif simple(following, writer):
                if crossed_merge:
                    replacement = writer.sub(lambda m:'galaxypad_deferred_'+m[1]+m[0].split('_op',1)[1], block)
                    assert candidate.count(block)==1
                    candidate = candidate.replace(block,replacement,1)
                    changed_sites.append(matches[i][1])
                break
            else:
                break
    candidate_functions.append(candidate)
program = r'''
#define DOLRECOMP_CPU_HEADER "core/cpu.h"
#include "GENERATED_HEADER"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define DOLRECOMP_C_LOOP_CYCLE_BUDGET 256
void galaxypad_deferred_add(CPUState*,u8,u8,u8);
void galaxypad_deferred_sub(CPUState*,u8,u8,u8);
void galaxypad_deferred_mul(CPUState*,u8,u8,u8);
void galaxypad_deferred_madd(CPUState*,u8,u8,u8,u8,bool,bool);
FUNCTIONS
static u8 ram[8*1024*1024],lc[16384];
static u64 digest=14695981039346656037ull;
static unsigned output_bytes,events,journals,inject,caller;
static void hash(const void* p,size_t n) {
#ifdef THP_BENCH
 return;
#endif
 const u8* b=p;while(n--) {digest^=*b++;digest*=1099511628211ull;}
}
static void state(CPUState* c) {
#ifdef THP_BENCH
 return;
#endif
 CPUState normalized=*c;
 normalized.ram=NULL;normalized.external_read=NULL;normalized.external_write=NULL;
 hash(&normalized,sizeof normalized);
}
static void event(CPUState* c,u32 ea,u64 value,u8 size) {
 state(c);hash(&ea,sizeof ea);hash(&value,sizeof value);hash(&size,sizeof size);events++;
}
static void journal(u32 offset,u32 size,void* user) {
 assert((u64)offset+size<=sizeof ram);
 state((CPUState*)user);hash(&offset,sizeof offset);hash(&size,sizeof size);
 hash(ram+offset,size);journals++;
 if(caller && output_bytes==64 && ((CPUState*)user)->pc==0x804526e8)
  ((CPUState*)user)->exception|=1;
}
static u64 read_lc(CPUState* c,u32 ea,u8 size) {
 assert(ea>=0xe0000000 && (u64)ea+size<=0xe0000000ull+sizeof lc);
 u64 value=0;for(unsigned i=0;i<size;i++) value=(value<<8)|lc[ea-0xe0000000+i];
 event(c,ea,value,size);return value;
}
static void write_lc(CPUState* c,u32 ea,u64 value,u8 size) {
 assert(ea>=0xe0000000 && (u64)ea+size<=0xe0000000ull+sizeof lc);
 event(c,ea,value,size);output_bytes+=size;
 for(unsigned i=0;i<size;i++) lc[ea-0xe0000000+i]=(u8)(value>>(8*(size-i-1)));
 if(inject && output_bytes==1) {c->exception|=1;if(inject==2)c->pc=0x80452558;}
}
static void put32(u32 ea,u32 value) {
 assert((ea&0x7fffffff)+4<=sizeof ram);
 for(unsigned i=0;i<4;i++) ram[(ea&0x7fffffff)+i]=(u8)(value>>(24-8*i));
}
static void putfloat(u32 ea,float value) {u32 bits;memcpy(&bits,&value,4);put32(ea,bits);}
int main(void) {
 unsigned cases=0,yields=0,faults=0,illegal=0,reservations=0,interrupted=0,caller_returns=0;
#ifdef THP_KERNEL_CALLERS
 unsigned observer_modes=5;
#else
 unsigned observer_modes=3;
#endif
 for(unsigned which=0;which<2;which++) for(unsigned pattern=0;pattern<6;pattern++)
 for(unsigned x=0;x<2;x++) for(unsigned budget=0;budget<2;budget++)
 for(unsigned fp=0;fp<3;fp++) for(unsigned quant=0;quant<2;quant++)
 for(unsigned observed=0;observed<observer_modes;observed++) {
#ifdef THP_BENCH
  if(fp!=1 || observed!=0 || quant!=0 || budget!=0 || x!=0) continue;
#endif
  memset(ram,0,sizeof ram);memset(lc,0x55,sizeof lc);output_bytes=0;
  inject=observed==2?1:observed==3?2:0;caller=observed==4;
  CPUState c={0};c.ram=ram;c.ram_size=sizeof ram;
  c.external_read=read_lc;c.external_write=write_lc;
  c.pc=which?0x80452b74:0x804526e8;c.lr=0x90001000;
  c.gpr[1]=0x80030000;c.gpr[2]=0x80010000;c.gpr[13]=0x80020000;
  c.gpr[3]=0x80040000;c.gpr[4]=x*8;c.msr=fp?PPC_MSR_FP:0;
  c.hid2=fp==2?0:PPC_HID2_LSQE;
  c.gqr[5]=0x00070007;c.gqr[6]=0x3d043d04;c.downcount=budget?-257:0;
  if(quant) {c.gqr[5]=0x01070007;c.gqr[6]=0x3e043e04;}
  c.reserve_valid=true;c.reserve_addr=0x8002ff80;
  g_mem_write_journal=observed?journal:NULL;g_mem_write_journal_user=&c;
  g_ppc_lazy_fp_enabled=true;
  for(unsigned r=0;r<32;r++) {c.fpr[r]=r+0.25;c.ps1[r]=r+0.5;}
  put32(c.gpr[13]-9056,0x80041000);put32(c.gpr[13]-9024,512);put32(c.gpr[13]-8992,0xe0000000);
  if(inject==2) c.downcount=10000; // Ensure a mistaken return dispatch is not hidden by a yield.
  if(caller) {
   c.lr=0x80452558;c.gpr[27]=0x80050000;c.gpr[24]=0;
   put32(0x80050004,0x80040000);
  }
  const float constants[]={1.414213562f,1.847759065f,1.082392200f,-2.613125930f,1024.f};
  for(unsigned i=0;i<5;i++) putfloat(c.gpr[2]+8408+4*i,constants[i]);
  for(unsigned i=0;i<64;i++) {
   int value=pattern==0?0:pattern==1?(i==0?64:0):pattern==2?(i%8==0?16:0):
             pattern==3?(i%5==0?-31:0):pattern==4?(int)(i*37%511)-255:(i%2?32767:-32768);
   ram[0x40000+i*2]=(u16)value>>8;ram[0x40001+i*2]=(u8)value;
   putfloat(0x80041000+i*4,1.f+(i%4));
  }
  CPUState initial=c;
  unsigned repeats=1;
#ifdef THP_BENCH
  repeats=20000;
  struct timespec begin,end;clock_gettime(CLOCK_MONOTONIC,&begin);
#endif
  for(unsigned repeat=0;repeat<repeats;repeat++) {
  c=initial;output_bytes=0;
  unsigned slices=0;
  do {
   if(which) transform1(&c);else transform0(&c);
   state(&c);
   assert(++slices<100);
   if((!caller && c.pc==c.lr) || c.exception) break;
   assert(c.downcount<=-256);c.downcount=0;yields++;
  } while(1);
  }
#ifdef THP_BENCH
  clock_gettime(CLOCK_MONOTONIC,&end);
  printf("%u %u %.3f\n",which,pattern,((end.tv_sec-begin.tv_sec)*1e9+end.tv_nsec-begin.tv_nsec)/repeats);
#endif
  assert(!c.reserve_valid);reservations++;
  if(fp==1 && caller) {
   assert(c.exception && output_bytes==64 && c.lr==0x80452564);caller_returns++;
  } else if(fp==1 && inject) {
   assert(c.exception && output_bytes>0 && output_bytes<64 && c.pc!=c.lr);
   interrupted++;
  } else if(fp==1) {
   if(c.exception || c.pc!=c.lr || c.gpr[1]!=0x80030000 || output_bytes!=64)
    fprintf(stderr,"which=%u pattern=%u x=%u budget=%u pc=%08x exception=%u sp=%08x output=%u\n",which,pattern,x,budget,c.pc,c.exception,c.gpr[1],output_bytes);
   assert(!c.exception && c.pc==c.lr && c.gpr[1]==0x80030000 && output_bytes==64);
   for(unsigned r=25;r<32;r++) assert(c.fpr[r]==r+0.25 && c.ps1[r]==r+0.5);
   if(pattern==0) {unsigned pixels=0;unsigned neutral=quant?255:128;for(unsigned i=0;i<sizeof lc;i++) {assert(lc[i]==0x55||lc[i]==neutral);pixels+=lc[i]==neutral;}assert(pixels==64);}
  } else {assert(c.exception && output_bytes==0);if(fp==0) {assert(c.pc==0x800);faults++;}else {assert(c.pc==0x700);illegal++;}}
  state(&c);hash(ram,sizeof ram);hash(lc,sizeof lc);cases++;
 }
#ifndef THP_BENCH
 assert(journals>0);
 printf("cases=%u yields=%u fp_faults=%u illegal=%u interrupted=%u caller_returns=%u callbacks=%u journals=%u reservations=%u digest=%016llx\n",cases,yields,faults,illegal,interrupted,caller_returns,events,journals,reservations,(unsigned long long)digest);
#endif
}
'''.replace('FUNCTIONS','\n'.join(functions)).replace('GENERATED_HEADER',str(generated/'RMGE01.h'))
with tempfile.TemporaryDirectory(prefix='galaxypad-thp-oracle-') as directory:
    temp = Path(directory)
    (temp/'cpu.c').write_text(cpu_reference)
    if args.psq_scale:
        import sys
        sys.path.insert(0, str(root/'scripts'))
        from psq_scale import transform as scale_transform
        (temp/'scale-cpu.c').write_text(scale_transform(cpu_reference))
    if args.hardware_widen:
        include = core.parent.parent/'include/core'
        types = (include/'types.h').read_text()
        assert hashlib.sha256(types.encode()).hexdigest() == '824490a35e968e645067711189a67156536ddd127ade063418ddcb59787f58bf'
        snippet = (root/'patches/experiments/f32-hardware-widen.inc').read_text()
        assert hashlib.sha256(snippet.encode()).hexdigest() == 'bb191ac81e691ea661d5af075ec4800863d3f019cca51bdb60a3cd582ad7bb4f'
        anchor = 'static inline u64 convert_to_double(u32 value) {\n'
        assert types.count(anchor) == 1
        altered = types.replace(anchor, anchor+snippet)
        assert altered.replace(anchor+snippet, anchor) == types
        (temp/'include/core').mkdir(parents=True)
        (temp/'include/core/types.h').write_text(altered)
        # cpu.h includes types.h relative to itself: copy it unchanged so the
        # generated chunk and actual helper sources both use the overridden types.
        (temp/'include/core/cpu.h').write_text((include/'cpu.h').read_text())
    if args.pair_load:
        header_path = core.parent.parent/'include/core/cpu.h'
        header = header_path.read_text()
        snippet = (root/'patches/experiments/psq-ram-pair-load.inc').read_text()
        assert hashlib.sha256(snippet.encode()).hexdigest() == '4e41c47f814bf6b79783f37bb98b1a1bea7e568f6790f4285d89d7559c58de3d'
        anchor = '        cpu->fpr[frD] = f64_value(convert_to_double(mem_read32(cpu, ea)));'
        assert header.count(anchor) == 1
        altered = header.replace(anchor, snippet+'\n'+anchor)
        assert altered.replace(snippet+'\n'+anchor, anchor) == header
        altered = altered.replace('#include "types.h"', '#include "'+str(header_path.parent/'types.h')+'"')
        (temp/'include/core').mkdir(parents=True)
        (temp/'include/core/cpu.h').write_text(altered)
    float_source = (core/'cpu_interpreter_float.c').read_text()
    if args.vector_add_sub:
        altered_float = float_source
        snippet = (root/'patches/experiments/ps-vector-addsub.inc').read_text()
        for operation in ('add','sub'):
            name = f'ppc_ps_{operation}_op'
            signature = 'void '+name+'('
            assert altered_float.count(signature) == 1
            altered_float = altered_float.replace(signature,'void reference_'+name+'(')
            snippet = snippet.replace(name+'(', 'reference_'+name+'(')
        altered_float += '\n#include <arm_neon.h>\n'+snippet
        for operation in ('add','sub'):
            altered_float += (f'\nvoid ppc_ps_{operation}_op(CPUState* c,u8 d,u8 a,u8 b) '
                              '{ vector_addsub(c,d,a,b,'+('true' if operation=='sub' else 'false')+'); }\n')
        (temp/'vector-add-sub.c').write_text(altered_float)
    if args.outline_add_nan:
        import sys
        sys.path.insert(0, str(root/'scripts'))
        from outline_add_nan import transform as outline_nan
        (temp/'outlined-add-nan.c').write_text(outline_nan(float_source))
    if args.outline_madd_tie:
        import sys
        sys.path.insert(0, str(root/'scripts'))
        from outline_madd_tie import transform as outline_tie
        (temp/'outlined-tie-float.c').write_text(outline_tie(float_source))
    if args.inline_add_sub:
        altered_float = float_source
        for operation in ('add', 'sub'):
            signature = f'FPRes ni_{operation}(CPUState* cpu, f64 a, f64 b) {{'
            assert altered_float.count(signature) == 1
            altered_float = altered_float.replace(signature, '__attribute__((always_inline)) '+signature)
        assert altered_float.replace('__attribute__((always_inline)) ', '') == float_source
        (temp/'inline-add-sub.c').write_text(altered_float)
    needle = 'f64 force_25bit_c(f64 d) {\n    u64 integral = f64_bits(d);'
    assert float_source.count(needle)==1
    (temp/'identity-float.c').write_text(float_source.replace(needle,needle+
        '\n    if ((integral & 0x0fffffffull) == 0) return d;',1))
    (temp/'probe.c').write_text(program)
    outputs = []
    builds = [('sanitized',['-O1','-fsanitize=address,undefined']),('optimized',['-O2'])]
    if args.merge_fprf:
        assert changed_sites, 'No eligible merge-crossing FPRF sites'
        print('Candidate sites:', ','.join(changed_sites),flush=True)
        builds += [('candidate-sanitized',['-O1','-fsanitize=address,undefined']),('candidate-optimized',['-O2'])]
    if args.identity_c:
        builds += [('identity-sanitized',['-O1','-fsanitize=address,undefined']),('identity-optimized',['-O2'])]
    if args.flatten or args.flatten_lto:
        builds += [('flatten-sanitized',['-O1','-fsanitize=address,undefined']),('flatten-optimized',['-O2'])]
    if args.flatten_lto:
        builds = [(name,flags+['-flto=thin']) for name,flags in builds]
    if args.kernels:
        builds += [('kernels-sanitized',['-O1','-fsanitize=address,undefined']),('kernels-optimized',['-O2','-flto=thin'])]
        if args.benchmark:
            builds = [(name,flags if '-flto=thin' in flags else flags+['-flto=thin']) for name,flags in builds]
    if args.benchmark:
        builds = [(name,flags+['-DTHP_BENCH']) for name,flags in builds if name.endswith('optimized')]
    for name, flags in builds:
        if args.module_pgo:
            flags=flags+['-fprofile-instr-use='+str(module_profile),'-arch','arm64','-mmacosx-version-min=14.0']
        selected = program.replace('\n'.join(functions),'\n'.join(candidate_functions)) if name.startswith('candidate') else program
        if (args.pair_load or args.hardware_widen or args.outline_madd_tie or args.outline_add_nan or args.cached_kernel_reads or args.dc_store_run or args.zero_column or args.normal_kernel_entry or args.local_columns or args.s16_load or args.dead_pc or args.psq_scale) and args.benchmark:
            # Longer samples for a small whole-kernel effect; same reset/dispatch work.
            assert selected.count('repeats=20000;') == 1
            selected = selected.replace('repeats=20000;', 'repeats=200000;')
        if args.cpu_time:
            assert selected.count('clock_gettime(CLOCK_MONOTONIC,') == 2
            selected = selected.replace('clock_gettime(CLOCK_MONOTONIC,', 'clock_gettime(CLOCK_THREAD_CPUTIME_ID,')
        sources = [str(temp/'cpu.c'),str(temp/'identity-float.c' if name.startswith('identity') else core/'cpu_interpreter_float.c'),str(core/'cpu_exception.c')]
        if args.psq_scale and name.startswith('kernels'):
            sources[0] = str(temp/'scale-cpu.c')
        if args.outline_madd_tie and name.startswith('kernels'):
            sources[1] = str(temp/'outlined-tie-float.c')
        if args.outline_add_nan and name.startswith('kernels'):
            sources[1] = str(temp/'outlined-add-nan.c')
        if args.inline_add_sub and name.startswith('kernels'):
            sources[1] = str(temp/'inline-add-sub.c')
        if args.vector_add_sub and name.startswith('kernels'):
            sources[1] = str(temp/'vector-add-sub.c')
        if args.kernels:
            directory = root/'generated/thp-kernels-r198-exits'
            chunk = directory/('candidate.c' if name.startswith('kernels') else 'reference.c')
            expected = '98d98621d4f744ea76977a63e44f3e2e3e731f50051e4a3a800a772e05a68991' if name.startswith('kernels') else 'f288241d6699aa3344ed7470bab69edd1b5f54fdae392010038bc786f721327f'
            if args.vector_add_sub or args.pair_load or args.hardware_widen or args.inline_add_sub or args.outline_madd_tie or args.outline_add_nan or args.cached_kernel_reads or args.dc_store_run or args.zero_column or args.normal_kernel_entry or args.local_columns or args.s16_load or args.dead_pc or args.psq_scale:
                # Compare header change only, not kernel extraction versus old chunk.
                chunk = directory/'candidate.c'
                expected = '98d98621d4f744ea76977a63e44f3e2e3e731f50051e4a3a800a772e05a68991'
            if args.fp_routing:
                directory = root/'generated/fp-check-routing-r219'
                chunk = directory/('candidate.c' if name.startswith('kernels') else 'reference.c')
                expected = 'ad83b55033d700b1ce5f57db07dfb66bda2e66bc8bdb839ca3cf407004a28918' if name.startswith('kernels') else 'fa455a7ae795c5428ce66c56d745416d2c5d9815ac32db14da571428b3661bae'
            assert hashlib.sha256(chunk.read_bytes()).hexdigest()==expected
            if args.dead_pc and name.startswith('kernels'):
                import sys
                sys.path.insert(0,str(root/'scripts'))
                from thp_dead_pc import transform as dead_pc
                changed=dead_pc(chunk.read_text())
                chunk=temp/(name+'-dead-pc.c')
                chunk.write_text(changed)
            if args.s16_load and name.startswith('kernels'):
                import sys
                sys.path.insert(0,str(root/'scripts'))
                from s16_psq_load import transform as s16_load
                if args.s16_pair:
                    from s16_pair_psq_load import transform as s16_load
                changed=s16_load(chunk.read_text(),coverage=not args.benchmark)
                chunk=temp/(name+'-s16-load.c')
                chunk.write_text(changed)
            if args.local_columns and name.startswith('kernels'):
                import sys
                sys.path.insert(0,str(root/'scripts'))
                from local_thp_columns import transform as local_columns
                changed=local_columns(chunk.read_text(),coverage=not args.benchmark)
                chunk=temp/(name+'-local-columns.c')
                chunk.write_text(changed)
            if args.normal_kernel_entry and name.startswith('kernels'):
                import sys
                sys.path.insert(0,str(root/'scripts'))
                from normal_kernel_entry import transform as normal_entry
                changed=normal_entry(chunk.read_text())
                if not args.benchmark:
                    probe=('#include <assert.h>\n#include <stdio.h>\nstatic unsigned long normal_hits[2];\n'
                           '__attribute__((destructor)) static void normal_coverage(void) {\n'
                           'assert(normal_hits[0] && normal_hits[1]);\n'
                           'fprintf(stderr,"normal_kernel_hits=%lu,%lu\\n",normal_hits[0],normal_hits[1]);\n}\n')
                    changed=probe+changed
                    for i in range(2):
                        marker=f'bool thp_normal_{i}(CPUState* ctx) {{'
                        assert changed.count(marker)==1
                        changed=changed.replace(marker,marker+f'\n++normal_hits[{i}];',1)
                chunk=temp/(name+'-normal-entry.c')
                chunk.write_text(changed)
            if args.zero_column and name.startswith('kernels'):
                import sys
                sys.path.insert(0,str(root/'scripts'))
                from zero_dc_column import transform as zero_column
                fused=zero_column(chunk.read_text(),nonzero_dc=args.nonzero_dc,both_kernels=args.both_dc_kernels)
                if not args.benchmark:
                    marker='static inline bool galaxy_zero_column(CPUState* cpu) {'
                    probe=('#include <assert.h>\nstatic unsigned long zero_hits;\n'
                           '__attribute__((destructor)) static void zero_coverage(void) {\n'
                           'assert(zero_hits>0); fprintf(stderr,"Zero-column hits=%lu\\n",zero_hits);\n}\n')
                    fused=fused.replace(marker,probe+marker,1)
                    fused=fused.replace('cpu->downcount-=14;', 'cpu->downcount-=14; ++zero_hits;',1)
                    if args.both_dc_kernels:
                        marker='static inline bool galaxy_second_column(CPUState* cpu) {'
                        probe=('static unsigned long second_hits;\n'
                               '__attribute__((destructor)) static void second_coverage(void) {\n'
                               'assert(second_hits>0); fprintf(stderr,"Second-column hits=%lu\\n",second_hits);\n}\n')
                        fused=fused.replace(marker,probe+marker,1)
                        fused=fused.replace('cpu->pc=0x80452C24u;cpu->downcount-=14;',
                                            'cpu->pc=0x80452C24u;cpu->downcount-=14; ++second_hits;',1)
                chunk=temp/(name+'-zero-column.c')
                chunk.write_text(fused)
            if args.dc_store_run and name.startswith('kernels'):
                import sys
                sys.path.insert(0, str(root/'scripts'))
                from fuse_dc_stores import transform as fuse_dc_stores
                fused = fuse_dc_stores(chunk.read_text())
                if not args.benchmark:
                    # Coverage only in correctness executables, never timed runs.
                    marker = 'static inline bool galaxy_dc_store_run(CPUState* cpu) {'
                    probe = ('#include <assert.h>\nstatic unsigned long dc_hits;\n'
                             '__attribute__((destructor)) static void dc_coverage(void) {\n'
                             'assert(dc_hits > 0); fprintf(stderr, "DC fast-path hits=%lu\\n", dc_hits);\n}\n')
                    fused = fused.replace(marker, probe+marker, 1)
                    assert fused.count('cpu->downcount -= 8;') == 1
                    fused = fused.replace('cpu->downcount -= 8;', '++dc_hits; cpu->downcount -= 8;', 1)
                chunk = temp/(name+'-dc-store-chunk.c')
                chunk.write_text(fused)
            if args.cached_kernel_reads and name.startswith('kernels'):
                import sys
                sys.path.insert(0, str(root/'scripts'))
                from cache_kernel_reads import transform as cache_kernel_reads
                cached = cache_kernel_reads(chunk.read_text())
                chunk = temp/(name+'-cached-chunk.c')
                chunk.write_text(cached)
            if args.fp_routing:
                text = chunk.read_text()
                assert text.count('#include "../RMGE01.h"') == 1
                chunk = temp/(name+'-chunk.c')
                chunk.write_text(text.replace('#include "../RMGE01.h"', '#include "'+str(generated/'RMGE01.h')+'"'))
                if not args.benchmark:
                    entries = re.findall(r'^fp_ready_([0-9A-F]{8}):', (directory/'candidate.c').read_text(), re.M)
                    assert len(entries) == len(set(entries)) == 119
                    extra = '''
 const u32 direct_entries[]={ENTRIES};
 g_ppc_lazy_fp_enabled=true;
 for(unsigned entry=0;entry<119;entry++) for(unsigned budget=0;budget<3;budget++) {
  CPUState c={0}; c.ram=ram;c.ram_size=sizeof ram;
  c.pc=direct_entries[entry];c.downcount=budget==0?0:budget==1?-257:10000;
  transform0(&c);
  assert(c.pc==0x800 && c.srr0==direct_entries[entry] && c.exception);
  state(&c);
 }
 printf("direct_fp_faults=357\\n");
'''.replace('ENTRIES', ','.join('0x'+pc+'u' for pc in entries))
                    anchor = ' unsigned cases=0,yields=0,faults=0,illegal=0,reservations=0,interrupted=0,caller_returns=0;'
                    assert selected.count(anchor)==1
                    selected = selected.replace(anchor,anchor+extra)
            callees = set(re.findall(r'\b(func_[0-9A-F]+)\(ctx\)',chunk.read_text()))-{'func_804520A0'}
            wrappers = 'void func_804520A0(CPUState*);\n'+''.join(
                f'void {callee}(CPUState* ctx) {{ (void)ctx; abort(); }}\n' for callee in sorted(callees))
            wrappers += '\n'.join(f'void transform{i}(CPUState* ctx) {{ func_804520A0(ctx); }}' for i in range(2))
            selected = selected.replace('\n'.join(functions),wrappers)
            sources.append(str(chunk))
            flags = flags+['-DDOLRECOMP_CPU_HEADER="core/cpu.h"','-DTHP_KERNEL_CALLERS']
        if args.flatten:
            selected = '\n'.join('#include "'+path+'"' for path in sources)+'\n'+selected
            sources = []
        if name.startswith('flatten'):
            for index in range(2):
                signature = f'void transform{index}(CPUState* ctx)'
                assert selected.count(signature)==1
                selected = selected.replace(signature,'__attribute__((flatten)) '+signature)
        (temp/'probe.c').write_text(selected)
        if (args.pair_load or args.hardware_widen) and name.startswith('kernels'):
            flags = flags+['-I', str(temp/'include')]
        subprocess.run(['clang',*flags,'-std=c11','-ffp-contract=off','-fno-fast-math',
                        '-ffunction-sections','-fdata-sections','-Wl,-dead_strip',
                        '-I',str(core.parent.parent/'include'),'-I',str(core),str(temp/'probe.c'),
                        *sources,
                        '-o',str(temp/name)],check=True)
        if args.benchmark:
            print(name,subprocess.check_output(['size',str(temp/name)],text=True).strip(),flush=True)
        if not args.benchmark:
            output = subprocess.check_output([str(temp/name)],text=True)
            print(name,output.strip(),flush=True);outputs.append(output)
    if args.benchmark:
        candidate_name = 'kernels-optimized' if args.kernels else 'flatten-optimized' if args.flatten or args.flatten_lto else 'identity-optimized' if args.identity_c else 'candidate-optimized'
        for name in ('optimized',candidate_name,candidate_name,'optimized'):
            output = subprocess.check_output([str(temp/name)],text=True)
            rows = [line.split() for line in output.splitlines()]
            assert len(rows)==12
            print(json.dumps(dict(variant=name,unit=('thread CPU ' if args.cpu_time else 'wall ')+
                                  'ns/transform including CPU reset and yield dispatch',
                                  rows=rows,total=sum(float(row[2]) for row in rows))),flush=True)
    else:
        assert all(output==outputs[0] for output in outputs), 'Oracle state/memory/exit digest differs'
