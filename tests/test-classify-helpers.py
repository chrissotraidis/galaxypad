"""Measure classification-only change inside unchanged arithmetic helpers."""
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
core=root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
source=(core/'cpu_interpreter_float.c').read_text()
def function(name):
    start=source.index('\nu32 '+name+'(')+1 if name=='classify_f32' else source.index('\nvoid '+name+'(')+1
    brace=source.index('{',start);depth=1;end=brace+1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[start:end]
classifier=function('classify_f32').replace('classify_f32(', 'candidate_classify(')
anchor='    u32 fraction = bits & 0x007FFFFFu;'
classifier=classifier.replace(anchor,anchor+'\n'+(root/'patches/experiments/classify-f32-normal.inc').read_text())
functions=[]
for name in ['ppc_ps_add_op','ppc_ps_sub_op','ppc_ps_mul_op','ppc_ps_madd_op']:
    functions.append(function(name).replace(name+'(', 'candidate_'+name+'(').replace('classify_f32(', 'candidate_classify('))
dispatch=r'''
static void reference_op(CPUState* c,u8 d,u8 a,u8 b,unsigned op) {
  switch(op) {
    case 0:ppc_ps_add_op(c,d,a,b);break;
    case 1:ppc_ps_sub_op(c,d,a,b);break;
    case 2:ppc_ps_mul_op(c,d,a,b);break;
    default:ppc_ps_madd_op(c,d,a,b,a,false,false);break;
  }
}
static void candidate(CPUState* c,u8 d,u8 a,u8 b,unsigned op) {
  switch(op) {
    case 0:candidate_ppc_ps_add_op(c,d,a,b);break;
    case 1:candidate_ppc_ps_sub_op(c,d,a,b);break;
    case 2:candidate_ppc_ps_mul_op(c,d,a,b);break;
    default:candidate_ppc_ps_madd_op(c,d,a,b,a,false,false);break;
  }
}
'''
# Reuse the existing strict-rounding/full-CPU-state/FP-flags harness, not
# its rejected finite-arithmetic candidate. Helper bodies above stay exact.
probe=(root/'tests/probe-ps-finite.c').read_text()
start=probe.index('static void candidate(')
end=probe.index('static u64 random_bits',start)
probe=probe[:start]+classifier+'\n'+'\n'.join(functions)+dispatch+probe[end:]
probe=probe.replace('if (i&1) ppc_ps_sub_op(&reference,d,1,2);\n            else ppc_ps_add_op(&reference,d,1,2);',
                    'reference_op(&reference,d,1,2,i%4);')
probe=probe.replace('candidate(&fast,d,1,2,(i&1)!=0);','candidate(&fast,d,1,2,i%4);')
probe=probe.replace('finite-path/reference','classification-only arithmetic/reference')
probe=probe.replace('static void fast_add(CPUState* cpu,u8 d,u8 a,u8 b) { candidate(cpu,d,a,b,false); }',
    'static unsigned bench_op;\n'
    'static void fast_add(CPUState* cpu,u8 d,u8 a,u8 b) { candidate(cpu,d,a,b,bench_op); }\n'
    'static void baseline(CPUState* cpu,u8 d,u8 a,u8 b) { reference_op(cpu,d,a,b,bench_op); }')
probe=probe.replace('bench(ppc_ps_add_op,&fast)','bench(baseline,&fast)')
probe=probe.replace('for (unsigned repeat=0;repeat<4;++repeat) {',
    'for (bench_op=0;bench_op<4;++bench_op) {\n'
    '    for (unsigned repeat=0;repeat<4;++repeat) {')
probe=probe.replace('normal add %u:', 'operation %u trial %u:')
probe=probe.replace('repeat,old_time,new_time,new_time/old_time);',
    'bench_op,repeat,old_time,new_time,new_time/old_time);')
probe=probe.replace('    return 0;\n}', '    }\n    return 0;\n}')
assert 'if (!isfinite(a0)' not in probe
assert 'reference_op(&reference,d,1,2,i%4);' in probe
with tempfile.TemporaryDirectory(prefix='galaxypad-classify-helpers-') as temp:
    base=Path(temp);(base/'test.c').write_text(probe)
    flags=['clang','-O2','-std=c11','-ffp-contract=off','-fno-fast-math',
           '-ffunction-sections','-fdata-sections','-I',str(core),
           '-I',str(core.parent.parent/'include'),str(base/'test.c'),'-Wl,-dead_strip']
    subprocess.run(flags+['-fsanitize=undefined','-o',str(base/'sanitize')],check=True)
    print('Sanitized correctness run; timings below are not performance evidence',flush=True)
    subprocess.run([str(base/'sanitize')],check=True)
    subprocess.run(flags+['-o',str(base/'bench')],check=True)
    print('Unsanitized helper benchmarks (0 add, 1 sub, 2 mul, 3 madd)',flush=True)
    subprocess.run([str(base/'bench')],check=True)
