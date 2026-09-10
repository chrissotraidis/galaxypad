"""Private whole-transform strict-FP inlining screen; never selects a module."""
from pathlib import Path
import hashlib
import re
import subprocess
import shlex
import sys
import tempfile
import importlib.util
from contextlib import nullcontext

root = Path(__file__).resolve().parents[1]
normalization = sys.argv[1:] == ['--normalization-square']
compact_normalization = sys.argv[1:] in [['--normalization-compact'], ['--normalization-compact-fenv'], ['--normalization-compact-audit']]
compact_fenv = sys.argv[1:] == ['--normalization-compact-fenv']
compact_audit = sys.argv[1:] == ['--normalization-compact-audit']
cross_range = sys.argv[1:] == ['--cross-range']
cross_island = sys.argv[1:] == ['--cross-island']
cross_product = sys.argv[1:] in [['--cross-checked'], ['--cross-range'], ['--cross-island']]
vendor = root/'ref/ModernGekko/vendor/dolphin'
core = vendor/'GXRuntime/src/core'
matches = list((root/'generated/modules-scale-r387/RMGE01').glob(
    '*/dolrecomp-output/RMGE01_generated/chunks/*804B60A0.c'))
assert len(matches) == 1
chunk = matches[0]
source = chunk.read_text()
body = 'label_804B6278:' + source.split('label_804B6278:', 1)[1].split('label_804B6328:', 1)[0]
assert len(re.findall(r'^label_', body, re.M)) == 44
assert body.count('goto ') == 1
body = body.replace('goto return_dispatch_804B60A0;', 'return;')
floats = (core/'cpu_interpreter_float.c').read_text()
definitions = re.findall(r'^(?:static )?\w+ (\w+)\([^;]*?\) \{', floats, re.M)
assert len(definitions) > 40 and len(set(definitions)) == len(definitions)
def rename(text):
    return re.sub(r'\b('+'|'.join(definitions)+r')\b', r'transform_inline_\1', text)
clones = rename(floats)
clones = re.sub(r'^((?:static )?\w+ transform_inline_\w+\()',
                r'__attribute__((always_inline)) \1', clones, flags=re.M)
prototypes = '\n'.join(m.group(0).rsplit('{', 1)[0]+';' for m in
    re.finditer(r'^(?:__attribute__\(\(always_inline\)\) )(?:static )?\w+ transform_inline_\w+\([^;]*?\) \{', clones, re.M))
cases = '\n'.join(f'case 0x{pc:08X}u: ctx->downcount -= {44-i}; goto label_{pc:08X};'
                   for i, pc in enumerate(range(0x804B6278, 0x804B6328, 4)))
# Match the emitted interior-entry charge; the first label already charges44.
cases = cases.replace('case 0x804B6278u: ctx->downcount -= 44;', 'case 0x804B6278u:')
functions = ''
for name, code in [('reference', body), ('candidate', rename(body))]:
    functions += f'__attribute__((noinline)) void {name}(CPUState* ctx) {{\nswitch(ctx->pc) {{ {cases} default: return; }}\n{code}\n}}\n'
driver = r'''
#include <assert.h>
#include <fenv.h>
#include <libproc.h>
#include <stdio.h>
#include <sys/resource.h>
#include <time.h>
#include <unistd.h>
static double now(void) { struct timespec t; assert(!clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t)); return t.tv_sec+t.tv_nsec*1e-9; }
static u64 random_word(u64* s) { *s^=*s<<13;*s^=*s>>7;*s^=*s<<17;return *s; }
static u64 instructions(void) {struct rusage_info_v4 r={0};assert(!proc_pid_rusage(getpid(),RUSAGE_INFO_V4,(rusage_info_t*)&r));return r.ri_instructions;}
int main(void) {
 unsigned char ram[256]={0}, expected[256];
 write_be32(ram+64,0x3f800000);write_be32(ram+68,0x40000000);
 write_be32(ram+72,0x40400000);write_be32(ram+128,0x3f000000);write_be32(ram+132,0x40400000);
 CPUState initial={0};initial.ram=ram;initial.ram_size=256;initial.msr=0x2000;
 initial.hid2=PPC_HID2_LSQE|PPC_HID2_PSE;initial.lr=0x81234564;
 initial.gpr[3]=0x80000000;initial.gpr[4]=0x80000040;initial.gpr[2]=0x80000080u-9400;
 for(unsigned r=0;r<32;r++){initial.fpr[r]=(r+1)/17.;initial.ps1[r]=-(r+1)/19.;}
 unsigned cases=0;u64 random=768;
 const u64 special[]={0,0x8000000000000000ull,1,0x0010000000000000ull,0x7fefffffffffffffull,
   0x7ff0000000000000ull,0xfff0000000000000ull,0x7ff0000000000001ull,0x7ff8000000000123ull};
 for(unsigned pattern=0;pattern<64;pattern++)for(unsigned rn=0;rn<4;rn++)for(unsigned ni=0;ni<2;ni++)for(unsigned entry=0;entry<44;entry++) {
   CPUState a=initial;a.fpscr=rn|(ni?FPSCR_NI_BIT:0);a.pc=0x804b6278+entry*4;a.downcount=10000;
   if(pattern==63)a.msr=0;
   if(pattern) {
     a.fpscr=((u32)random_word(&random)&~(FPSCR_NI_BIT|3u))|a.fpscr;
     for(unsigned r=0;r<32;r++) {
       a.fpr[r]=f64_value(pattern<10?special[(pattern+r)%9]:random_word(&random));
       a.ps1[r]=f64_value(pattern<10?special[(pattern+2*r)%9]:random_word(&random));
     }
   }
   CPUState b=a; unsigned char before[256];memcpy(before,ram,256);
   ppc_fpscr_control_updated(&a);feclearexcept(FE_ALL_EXCEPT);reference(&a);int flags=fetestexcept(FE_ALL_EXCEPT);
   memcpy(expected,ram,256);memcpy(ram,before,256);
   ppc_fpscr_control_updated(&b);feclearexcept(FE_ALL_EXCEPT);candidate(&b);
   assert(flags==fetestexcept(FE_ALL_EXCEPT));assert(!memcmp(&a,&b,sizeof a));assert(!memcmp(expected,ram,256));
   assert(a.downcount==10000-(44-entry));
   if(pattern==63 && entry!=43)assert(a.exception);
   else assert(a.pc==initial.lr && !a.exception);
   cases++;
 }
 printf("%u whole-transform interior-entry/RN/NI CPU, memory and host-flag comparisons pass\n",cases);
 ppc_fpscr_control_updated(&initial);
#ifndef CORRECTNESS_ONLY
 for(unsigned run=0;run<8;run++) {
   bool is_reference=run%4==0||run%4==3;
   void (*volatile fn)(CPUState*)=is_reference?reference:candidate;
   CPUState warm=initial;
   for(unsigned i=0;i<10000;i++){warm.pc=0x804b6278;warm.downcount=10000;warm.fpr[1]=.2;warm.fpr[2]=.8;fn(&warm);}
   CPUState state=initial;u64 before=instructions();double start=now();
   for(unsigned i=0;i<1000000;i++){state.pc=0x804b6278;state.downcount=10000;state.fpr[1]=.2;state.fpr[2]=.8;fn(&state);}
   double elapsed=now()-start;u64 after=instructions();
   printf("%s ns/transform=%.3f instructions/transform=%.3f pc=%08x\n",is_reference?"reference":"candidate",elapsed*1e9/1000000,(double)(after-before)/1000000,state.pc);
 }
#endif
}
'''
if normalization:
    # Use the hot seventeen-instruction routine, not the old cold transform.
    driver = driver.replace('0x804b6278', '0x804b6bcc').replace('entry<44', 'entry<17')
    driver = driver.replace('(44-entry)', '(17-entry)').replace('entry!=43', 'entry!=16')
    driver = driver.replace('initial.gpr[3]=0x80000000;initial.gpr[4]=0x80000040;',
                            'initial.gpr[3]=0x80000040;initial.gpr[4]=0x80000000;')
    driver = driver.replace('0x80000080u-9400', '0x80000080u-9448')
    driver = driver.replace('CPUState a=initial;a.fpscr=',
        'if(pattern) { for(unsigned j=0;j<3;j++) write_be32(ram+64+4*j,(u32)random_word(&random)); }\n   CPUState a=initial;a.fpscr=')
    driver = driver.replace(' ppc_fpscr_control_updated(&initial);',
        ' write_be32(ram+64,0x3f800000);write_be32(ram+68,0x40000000);write_be32(ram+72,0x40400000);\n ppc_fpscr_control_updated(&initial);')
if cross_product:
    driver = driver.replace('0x804b6278', '0x804b6cb8').replace('entry<44', 'entry<15')
    driver = driver.replace('(44-entry)', '(15-entry)').replace('entry!=43', 'entry!=14')
    driver = driver.replace('initial.gpr[3]=0x80000000;initial.gpr[4]=0x80000040;',
        'initial.gpr[3]=0x80000040;initial.gpr[4]=0x80000050;initial.gpr[5]=0x80000000;')
    driver = driver.replace('CPUState a=initial;a.fpscr=',
        'if(pattern) { for(unsigned j=0;j<7;j++) write_be32(ram+64+4*j,(u32)random_word(&random)); }\n   CPUState a=initial;a.fpscr=')
    driver = driver.replace(' ppc_fpscr_control_updated(&initial);',
        ' write_be32(ram+64,0x3f800000);write_be32(ram+68,0x40000000);write_be32(ram+72,0x40400000);\n'
        ' write_be32(ram+80,0x40800000);write_be32(ram+84,0x40a00000);write_be32(ram+88,0x40c00000);\n ppc_fpscr_control_updated(&initial);')
if cross_island:
    assert driver.count('#endif\n}')==1
    driver=driver.replace('#endif\n}',(root/'tests/cross-island-workloads.inc').read_text()+'\n#endif\n}')
header = chunk.parent.parent/'RMGE01.h'
program = '#pragma STDC FENV_ACCESS ON\n#define DOLRECOMP_CPU_HEADER "core/cpu.h"\n'
program += f'#include "{header}"\n#include "cpu_interpreter_float.c"\n'
program += prototypes+'\n'+clones+'\n'+functions+'\n'+driver
print('chunk_sha256='+hashlib.sha256(source.encode()).hexdigest(), flush=True)
print('float_sha256='+hashlib.sha256(floats.encode()).hexdigest(), flush=True)
if compact_normalization:
    # Cost screen calls the complete 17-instruction routine, including memory,
    # through independent whole-chunk libraries, not the nine-op oracle alone.
    driver=driver.replace('entry<44','entry<17').replace('0x804b6278','0x804b6bcc')
    driver=driver.replace('(44-entry)','(17-entry)').replace('entry!=43','entry!=16')
    driver=driver.replace('0x80000080u-9400','0x80000080u-9448')
    driver=driver.replace('CPUState initial={0};',
        'write_be32(ram,0x3f800000);write_be32(ram+4,0x40000000);write_be32(ram+8,0x40400000);\n CPUState initial={0};')
    driver=driver.replace('assert(flags==fetestexcept(FE_ALL_EXCEPT));', '''
   if(flags!=fetestexcept(FE_ALL_EXCEPT)) {
     fprintf(stderr,"Compact whole-chunk flags mismatch pattern=%u rn=%u ni=%u entry=%u expected=%x actual=%x statecmp=%d fpscr=%08x/%08x pc=%08x/%08x\\n",
       pattern,rn,ni,entry,flags,fetestexcept(FE_ALL_EXCEPT),memcmp(&a,&b,sizeof a),a.fpscr,b.fpscr,a.pc,b.pc);
     return 3;
   }
''')
    if compact_audit:
        driver=driver.replace('unsigned cases=0;u64 random=768;',
                              'unsigned cases=0,host_flag_failures=0;u64 random=768;')
        driver=driver.replace('fprintf(stderr,"Compact whole-chunk flags mismatch',
                              'if(host_flag_failures<8) fprintf(stderr,"Compact whole-chunk flags mismatch')
        driver=driver.replace('     return 3;', '     host_flag_failures++;')
        marker=' printf("%u whole-transform interior-entry/RN/NI CPU, memory and host-flag comparisons pass\\n",cases);'
        assert marker in driver
        driver=driver.replace(marker, '''
 printf("%u complete CPUState/memory comparisons pass; %u host-flag mismatches; audit only, no timing\\n",cases,host_flag_failures);
 return host_flag_failures?3:0;
''')
workspace = (nullcontext(tempfile.mkdtemp(prefix='normalization-compact-whole-r827-',dir=root/'generated'))
             if compact_normalization else tempfile.TemporaryDirectory(prefix='galaxypad-transform-inline-'))
with workspace as directory:
    if compact_normalization:
        print('retained_whole_chunk_artifacts='+str(directory),flush=True)
    temp=Path(directory); path=temp/'probe.c'; path.write_text(program)
    flags=['clang','-std=c11','-ffp-contract=off','-fno-fast-math','-I',str(core),
           '-I',str(vendor/'GXRuntime/include'),'-Wl,-dead_strip']
    if compact_normalization or sys.argv[1:] in [['--full-chunk'], ['--local-span'], ['--scalar-span'], ['--typed-span'], ['--normalization-square'], ['--cross-checked'], ['--cross-range'], ['--cross-island']]:
        local_span = sys.argv[1:] != ['--full-chunk']
        typed_span = sys.argv[1:] == ['--typed-span']
        scalar_span = sys.argv[1:] in [['--scalar-span'], ['--typed-span']]
        graph=(chunk.parents[3]/'module-build/build.ninja').read_text()
        stanza=re.search(r'^build [^\n]+: C_COMPILER_[^\n]+ '+re.escape(str(chunk))+r'[^\n]*\n((?:  [^\n]*\n)*)',graph,re.M)
        assert stanza
        fields=dict(re.findall(r'^  (\w+) = (.*)$',stanza[1],re.M))
        module_flags=shlex.split(fields['DEFINES']+' '+fields['FLAGS']+' '+fields['INCLUDES'])
        assert '-flto=thin' in module_flags and '-DNDEBUG' in module_flags
        assert '-ffp-contract=off' in module_flags and '-fno-fast-math' in module_flags
        print('actual_chunk_flags='+repr(module_flags),flush=True)
        objects=[]
        for unit in core.glob('cpu*.c'):
            obj=temp/(unit.stem+'.o')
            subprocess.run(['clang',*module_flags,'-I',str(core),'-c',str(unit),'-o',str(obj)],check=True)
            objects.append(str(obj))
        for variant in ['reference','candidate']:
            text=source.replace('#include "../RMGE01.h"',f'#include "{header}"')
            if variant=='candidate':
                if cross_island:
                    assert hashlib.sha256(source.encode()).hexdigest()=='38d5085e7e8eceece0521f5566c012a5c15fa5a7be7c2c1fe915985d28c376ac'
                    helper=(root/'patches/experiments/cross-island-vector.inc').read_text()
                    begin,end='label_804B6CCC:','label_804B6CD0:'
                    original=begin+text.split(begin,1)[1].split(end,1)[0]
                    call='ppc_ps_mul_op(ctx, 4, 1, 2);'
                    assert original.count(call)==1
                    assert 'if (!ppc_fp_available_inline(ctx, 0x804B6CCCu)) return;' in original
                    replacement='if(cross_island_try(ctx)) { ctx->pc=0x804B6CE0u; goto label_804B6CE4; }\n    '+call
                    text=text.replace(original,original.replace(call,replacement),1)
                    # All interior labels remain for the original suffix entries.
                    # No forced-inline clone of unrelated float helpers.
                    text=f'#include "{header}"\n#include "cpu_interpreter_private.h"\n#include <arm_neon.h>\n'+helper+'\n'+text
                elif compact_normalization:
                    oracle=root/'generated/normalization-compact-r827-optimized/region.inc'
                    assert hashlib.sha256(oracle.read_bytes()).hexdigest()=='caa541cb4c4e90021b6a462316b8c668741532b97d660bcd53e255376a4cd131'
                    region=oracle.read_text().split('typedef struct { f64 fpr[7], ps1[7]; u32 fpscr; } CompactFPState;',1)
                    assert len(region)==2
                    helper='typedef struct { f64 fpr[7], ps1[7]; u32 fpscr; } CompactFPState;'+region[1]
                    assert helper.count('void local_state(')==1
                    if compact_fenv:
                        # Preserve FP environment side effects inside the new
                        # closure; original generated chunk policy stays OFF.
                        helper='#pragma STDC FENV_ACCESS ON\n'+helper+'\n#pragma STDC FENV_ACCESS OFF\n'
                    marker='label_804B6BE0:\n'
                    assert text.count(marker)==1
                    text=text.replace(marker,marker+'''    if (ctx->msr & PPC_MSR_FP) {
        ctx->pc=0x804B6BE0u;
        local_state(ctx,false);
        goto label_804B6C04;
    }
''',1)
                    text=f'#include "{header}"\n#include "cpu_interpreter_private.h"\n'+helper+'\n'+text
                elif normalization or cross_product:
                    # Integer round-trip proves exact binary32 representation
                    # without changing host exception flags during eligibility.
                    helper = r'''
static inline void normalize_square(CPUState* ctx) {
 const u64 a=f64_bits(ctx->fpr[2]),b=f64_bits(ctx->ps1[2]);
 if((ctx->fpscr&FPSCR_NI_BIT) || ((a>>52)&2047)==2047 || ((b>>52)&2047)==2047 ||
    convert_to_double(convert_to_single(a))!=a || convert_to_double(convert_to_single(b))!=b) {
   ppc_ps_mul_op(ctx,5,2,2);return;
 }
 const float32x2_t v={(f32)ctx->fpr[2],(f32)ctx->ps1[2]};
 const float32x2_t result=vmul_f32(v,v);
 const f32 r0=vget_lane_f32(result,0),r1=vget_lane_f32(result,1);
 ps_write_both(ctx,5,r0,r1);set_fprf(ctx,classify_f32(r0));
}
'''
                    # Only this instruction is replaced; all memory operations,
                    # labels, cycles and unavailable-FPU checks remain original.
                    begin,end='label_804B6BD4:','label_804B6BD8:'
                    original_call, replacement='ppc_ps_mul_op(ctx, 5, 2, 2);','normalize_square(ctx);'
                    if cross_product:
                        helper=(root/'patches/experiments/checked-ps-multiply.inc').read_text()
                        begin,end='label_804B6CCC:','label_804B6CD0:'
                        original_call,replacement='ppc_ps_mul_op(ctx, 4, 1, 2);','checked_ps_multiply(ctx, 4, 1, 2);'
                    if cross_range:
                        span='label_804B6CB8:'+text.split('label_804B6CB8:',1)[1].split('label_804B6CD0:',1)[0]
                        assert span.count('ctx->downcount -= 15;')==1
                        span=re.sub(r'^label_[0-9A-F]+:\n','',span,flags=re.M)
                        span=span.replace('ctx->downcount -= 15;','')
                        # Only bounded direct loads are replaced. Original PC,
                        # conversion, lane writes and FP checks remain in order.
                        for reg,base,pc in [(1,4,'804B6CB8'),(0,3,'804B6CC0')]:
                            call=f'ppc_psq_load_inline(ctx, {reg}u, ea, false, 0u, false, 0x{pc}u);'
                            assert span.count(call)==1
                            span=span.replace(call,f'ctx->fpr[{reg}]=f64_value(convert_to_double(read_be32(input{base}))); ctx->ps1[{reg}]=f64_value(convert_to_double(read_be32(input{base}+4)));')
                        for base in [3,4]:
                            anchor=f'u32 ea = ctx->gpr[{base}] + (u32)(s32)(8);\n        f64 value = dolrecomp_f32_from_bits(mem_read32(ctx, ea));'
                            assert span.count(anchor)==1
                            span=span.replace(anchor,f'f64 value = dolrecomp_f32_from_bits(read_be32(input{base}+8));')
                        # Source loads prove precision here; preserve nonfinite
                        # fallback without repeating four integer round trips.
                        for operand in ['fpr[a]','ps1[a]','fpr[c]','ps1[c]']:
                            helper=helper.replace(f'!checked_single_bits(f64_bits(cpu->{operand}))',f'!isfinite(cpu->{operand})')
                        span=span.replace(original_call,replacement).replace('return;','return true;')
                        region=(root/'patches/experiments/cross-range-prefix.inc').read_text().replace('/* GENERATED_PREFIX */',span)
                        helper+='\n'+region
                        anchor='label_804B6CB8:\n    ctx->pc = 0x804B6CB8u;\n    ctx->downcount -= 15;'
                        assert text.count(anchor)==1
                        text=text.replace(anchor,anchor+'\n    if(cross_range_prefix(ctx)) goto label_804B6CD0;',1)
                        # All original arithmetic remains on rejected/interior paths.
                        replacement=original_call
                    original=begin+text.split(begin,1)[1].split(end,1)[0]
                    assert original.count(original_call)==1
                    text=text.replace(original,original.replace(original_call,replacement),1)
                    prefix=f'#include "{header}"\n#include "cpu_interpreter_private.h"\n#include <arm_neon.h>\n'
                    text=prefix+prototypes+'\n'+clones+'\n'+rename(helper)+'\n'+text
                elif not local_span:
                    text=f'#include "{header}"\n#include "cpu_interpreter_private.h"\n'+prototypes+'\n'+clones+'\n'+rename(text)
                else:
                    # This exact region contains no memory, control-flow or status
                    # observers. Preserve all original labels for interior entries.
                    start,end='label_804B62B0:','label_804B62FC:'
                    span=start+source.split(start,1)[1].split(end,1)[0]
                    assert span.count('ctx->downcount')==0 and 'goto ' not in span
                    assert set(re.findall(r'ctx->(\w+)',span))=={'pc','fpr','ps1'}
                    pure=re.sub(r'^label_[0-9A-F]+:\n|^    ctx->pc = 0x[0-9A-F]+u;\n|^    if \(!ppc_fp_available_inline\(ctx, 0x[0-9A-F]+u\)\) return;\n','',span,flags=re.M)
                    assert 'return' not in pure and 'ctx->pc' not in pure
                    if typed_span:
                        assert hashlib.sha256(source.encode()).hexdigest()=='38d5085e7e8eceece0521f5566c012a5c15fa5a7be7c2c1fe915985d28c376ac'
                        assert hashlib.sha256(floats.encode()).hexdigest()=='554149a2e7d08783402af38e5a2b898aff476370b0e3a6af0ed4bd411aab934f'
                        known=set();eligible=[]
                        for instruction in re.split(r'(?=// [0-9A-F]{8}:)',pure)[1:]:
                            annotation=re.match(r'// ([0-9A-F]{8}): (\w+)\s+f(\d+)',instruction)
                            assert annotation
                            pc,op,d=annotation.groups();d=int(d)
                            assert op in ['fmuls','fnmsubs','fmadds','ps_muls0','ps_muls1','ps_neg','ps_sum0']
                            call=re.search(r'ppc_ps_muls([01])\(ctx, (\d+), (\d+), (\d+)\);',instruction)
                            if call:
                                lane,dest,a,c=map(int,call.groups());assert dest==d
                                if a in known and c in known:
                                    code='''{
 const f64 typed_a0=ctx->fpr[A],typed_a1=ctx->ps1[A],typed_c=ctx->LANE[C];
 if(!isfinite(typed_a0)||!isfinite(typed_a1)||!isfinite(typed_c)) { ORIGINAL }
 else {
 const float32x2_t typed_left={(f32)typed_a0,(f32)typed_a1};
 const float32x2_t typed_result=vmul_f32(typed_left,vdup_n_f32((f32)typed_c));
 const f32 typed_r0=vget_lane_f32(typed_result,0),typed_r1=vget_lane_f32(typed_result,1);
 ps_write_both(ctx,D,typed_r0,typed_r1);set_fprf(ctx,classify_f32(typed_r0));
 }
}'''.replace('ORIGINAL',call[0]).replace('[A]',f'[{a}]').replace('[C]',f'[{c}]').replace('LANE','fpr' if lane==0 else 'ps1').replace('ctx,D,',f'ctx,{d},')
                                    # Duplicate operand spellings occur at distinct PCs;
                                    # replace only inside this exact annotated region.
                                    pure=pure.replace(instruction,instruction.replace(call[0],code,1),1)
                                    eligible.append(pc)
                            # Under the entry VE-clear guard these scalar writes
                            # succeed; every selected PS opcode writes both lanes.
                            known.add(d)
                        assert eligible==['804B62D4','804B62D8','804B62DC','804B62F4']
                        print('typed_sites='+repr(eligible)+' entry_requires=FP-on,VE-off,NI-off',flush=True)
                    bodies={}
                    for match in re.finditer(r'^(?:static )?\w+ (\w+)\([^;]*?\) \{',floats,re.M):
                        pos=match.end();depth=1
                        while depth:
                            depth+=(floats[pos]=='{')-(floats[pos]=='}');pos+=1
                        bodies[match[1]]=floats[match.start():pos]
                    if scalar_span:
                        # Expand only fixed-register leaf operations; preserve
                        # value-argument evaluation before destination writes.
                        expandable=['ppc_fmuls','ppc_ps_muls0','ppc_ps_muls1',
                                    'ppc_ps_sum0','ps_write_both','fp_write_single']
                        serial=0
                        while match:=re.search(r'\b('+'|'.join(expandable)+r')\(',pure):
                            pos=match.end();depth=1;begin=pos;arguments=[]
                            while depth:
                                char=pure[pos]
                                if char=='(':depth+=1
                                elif char==')':depth-=1
                                elif char==',' and depth==1:
                                    arguments.append(pure[begin:pos].strip());begin=pos+1
                                pos+=1
                            arguments.append(pure[begin:pos-1].strip())
                            assert pure[pos]==';'
                            definition=bodies[match[1]]
                            signature,expanded=definition.split('{',1)
                            params=signature.split('(',1)[1].rsplit(')',1)[0].split(',')
                            assert len(params)==len(arguments)
                            bindings={};prefix_args=''
                            for param,arg in zip(params,arguments):
                                ctype,name=param.strip().rsplit(' ',1)
                                if ctype in ['f32','f64']:
                                    temp_name=f'scalar_arg_{serial}_{name}'
                                    prefix_args+=f'{ctype} {temp_name} = {arg};\n'
                                    bindings[name]=temp_name
                                else:bindings[name]=arg
                            expanded=re.sub(r'(?<!->)(?<!\.)\b('+'|'.join(bindings)+r')\b',lambda m:bindings[m[0]],expanded.rsplit('}',1)[0])
                            pure=pure[:match.start()]+'{\n'+prefix_args+expanded+'\n}'+pure[pos+1:]
                            serial+=1
                            assert serial<100
                    needed=set(re.findall(r'\b(\w+)\(',pure)) & bodies.keys()
                    while True:
                        expanded=needed|set().union(*(set(re.findall(r'\b(\w+)\(',bodies[n])) & bodies.keys() for n in needed))
                        if expanded==needed:break
                        needed=expanded
                    helpers='\n'.join(bodies[n] for n in definitions if n in needed)
                    assert set(re.findall(r'cpu->(\w+)',helpers)) <= {'fpr','ps1','fpscr'}
                    assert 'CPUState' not in pure
                    local_protos='\n'.join(bodies[n].split('{',1)[0]+';' for n in definitions if n in needed)
                    local_helpers=rename(helpers).replace('CPUState','LocalFP')
                    local_helpers=re.sub(r'^((?:static )?\w+ transform_inline_\w+\()',r'__attribute__((always_inline)) \1',local_helpers,flags=re.M)
                    dirty=sorted(set(map(int,re.findall(r'// [0-9A-F]+: \w+\s+f(\d+)',span))))
                    assert len(re.findall(r'^label_',span,re.M))==19 and dirty==[0,2,3,4,5,6,7,8,9,10]
                    batch='static __attribute__((noinline)) void local_batch(CPUState* output) {\nLocalFP local; LocalFP* ctx=&local;\n'
                    batch+='memcpy(local.fpr,output->fpr,sizeof local.fpr);memcpy(local.ps1,output->ps1,sizeof local.ps1);local.fpscr=output->fpscr;\n'
                    batch+=rename(pure)+'\n'
                    for r in dirty:batch+=f'output->fpr[{r}]=local.fpr[{r}];output->ps1[{r}]=local.ps1[{r}];\n'
                    batch+='output->fpscr=local.fpscr;\n}\n'
                    prefix=f'#include "{header}"\n#include "cpu_interpreter_private.h"\ntypedef struct {{f64 fpr[32],ps1[32];u32 fpscr;}} LocalFP;\n'
                    prefix+=rename(local_protos).replace('CPUState','LocalFP')+'\n'+local_helpers+'\n'+batch
                    if scalar_span:
                        assert set(re.findall(r'cpu->(\w+)',helpers)) <= {'fpscr'}
                        lanes=sorted(set(re.findall(r'ctx->(fpr|ps1)\[(\d+)\]',pure)))
                        lowered=re.sub(r'ctx->(fpr|ps1)\[(\d+)\]',lambda m:f'lane_{m[1]}_{m[2]}',pure)
                        assert '[' not in lowered and set(re.findall(r'ctx->(\w+)',lowered)) <= {'fpscr'}, '\n'.join(line for line in lowered.splitlines() if '[' in line or 'ctx->' in line)
                        batch='static __attribute__((noinline)) void local_batch(CPUState* output) {\nLocalFP local={output->fpscr};LocalFP* ctx=&local;\n'
                        for lane,r in lanes:batch+=f'f64 lane_{lane}_{r}=output->{lane}[{r}];\n'
                        batch+=rename(lowered)+'\n'
                        for r in dirty:
                            for lane in ['fpr','ps1']:
                                assert (lane,str(r)) in lanes
                                batch+=f'output->{lane}[{r}]=lane_{lane}_{r};\n'
                        batch+='output->fpscr=local.fpscr;\n}\n'
                        prefix=f'#include "{header}"\n#include "cpu_interpreter_private.h"\ntypedef struct {{u32 fpscr;}} LocalFP;\n'
                        prefix+=rename(local_protos).replace('CPUState','LocalFP')+'\n'+local_helpers+'\n'+batch
                        print('scalar_lanes='+repr(lanes)+' expanded_calls='+str(serial),flush=True)
                    guard='(ctx->msr & PPC_MSR_FP)'
                    if typed_span:
                        guard+=' && !(ctx->fpscr & (FPSCR_VE_BIT | FPSCR_NI_BIT))'
                        prefix='#include <arm_neon.h>\n'+prefix
                    text=text.replace(start,start+'\n    if ('+guard+') { local_batch(ctx); goto label_804B62FC; }',1)
                    text=prefix+'\n'+text
                    print('local_span_ops=19 dirty='+repr(dirty)+' helper_closure='+repr(sorted(needed)),flush=True)
            text+='\n__attribute__((visibility("default"))) void probe_transform(CPUState* ctx) { func_804B60A0(ctx); }\n'
            if cross_island:
                text+='\n__attribute__((visibility("default"))) void probe_set_journal(PPCMemWriteJournal callback, void* user) { g_mem_write_journal=callback; g_mem_write_journal_user=user; }\n'
            unit=temp/(variant+'.c');unit.write_text(text);obj=temp/(variant+'.o')
            subprocess.run(['clang',*module_flags,'-I',str(core),'-c',str(unit),'-o',str(obj)],check=True)
            subprocess.run(['clang','-dynamiclib','-flto=thin','-O2','-arch','arm64','-mmacosx-version-min=14.0',str(obj),*objects,'-o',str(temp/(variant+'.dylib'))],check=True)
        # Driver keeps assertions and loads independent whole-chunk libraries.
        # Neither reference nor candidate product code is compiled with -UNDEBUG.
        load='''
 void* left=dlopen("LEFT",RTLD_NOW|RTLD_LOCAL);void* right=dlopen("RIGHT",RTLD_NOW|RTLD_LOCAL);
 if(!left||!right){fprintf(stderr,"%s\\n",dlerror());return 2;}
 reference=dlsym(left,"probe_transform");candidate=dlsym(right,"probe_transform");assert(reference&&candidate);
'''.replace('LEFT',str(temp/'reference.dylib')).replace('RIGHT',str(temp/'candidate.dylib'))
        new_driver=driver.replace('int main(void) {','int main(void) {'+load)
        if cross_island:
            checks=(root/'tests/cross-island-context-checks.inc').read_text()
            new_driver=checks+'\n'+new_driver.replace('assert(reference&&candidate);',
                'assert(reference&&candidate); cross_context_checks(left,right);')
        path.write_text('#include <dlfcn.h>\n#include "cpu_interpreter_float.c"\nstatic void (*reference)(CPUState*);static void (*candidate)(CPUState*);\n'+new_driver)
        subprocess.run([*flags,'-O2',str(path),str(core/'cpu_interpreter_table.c'),'-o',str(temp/'probe')],check=True)
        subprocess.run([str(temp/'probe')],check=True)
        sys.exit(0)
    assert not sys.argv[1:]
    for extra in [['-O1','-fsanitize=address,undefined','-DCORRECTNESS_ONLY'],['-O2']]:
        runtime = [str(core/name) for name in ['cpu.c', 'cpu_exception.c', 'cpu_interpreter_table.c']]
        subprocess.run([*flags,*extra,str(path),*runtime,'-o',str(temp/'probe')],check=True)
        subprocess.run([str(temp/'probe')],check=True)
    subprocess.run([*flags[:-1],'-O2','-S',str(path),'-o',str(temp/'probe.s')],check=True)
    assembly=(temp/'probe.s').read_text()
    for name in ['reference','candidate']:
        function=assembly.split('_'+name+':',1)[1].split('.cfi_endproc',1)[0]
        ops=re.findall(r'^\s+([a-z][a-z0-9]*)\s',function,re.M)
        print(name,'static_instructions',len(ops),'call_sites',sum(op=='bl' for op in ops),flush=True)
