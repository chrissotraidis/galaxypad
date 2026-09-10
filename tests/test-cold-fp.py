"""Isolate unchanged NaN-result handling from paired add/sub common paths."""
from pathlib import Path
import subprocess
import tempfile
import re
import sys

root=Path(__file__).resolve().parents[1]
core=root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
source=(core/'cpu_interpreter_float.c').read_text()
sys.path.insert(0,str(root/'scripts'))
from cold_fp_transform import transform
transformed=transform(source)
def end_brace(text,start):
    depth=1;i=start+1
    while depth:
        depth+=(text[i]=='{')-(text[i]=='}');i+=1
    return i
def extract(signature,text=source):
    start=text.index(signature);brace=text.index('{',start)
    return text[start:end_brace(text,brace)]
parts=[]
for op in ['add','sub']:
    cold=extract('__attribute__((noinline,cold)) static FPRes cold_'+op+'(',transformed)
    hot=extract('FPRes ni_'+op+'(',transformed)
    hot=hot.replace('FPRes ni_'+op+'(', 'static FPRes candidate_ni_'+op+'(')
    helper=extract('void ppc_ps_'+op+'_op(')
    helper=helper.replace('void ppc_ps_'+op+'_op(', 'static void candidate_'+op+'(').replace('ni_'+op+'(', 'candidate_ni_'+op+'(')
    parts.extend([cold,hot,helper])
dispatch='''
static void candidate(CPUState* c,u8 d,u8 a,u8 b,bool subtract) {
    if(subtract) candidate_sub(c,d,a,b); else candidate_add(c,d,a,b);
}
'''
probe=(root/'tests/probe-ps-finite.c').read_text()
start=probe.index('static void candidate(');end=probe.index('static u64 random_bits',start)
probe=probe[:start]+'\n'.join(parts)+dispatch+probe[end:]
probe=probe.replace('finite-path/reference','cold-exception/reference')
module=Path((root/'generated/modules/RMGE01/active-module.txt').read_text().strip())
chunk=next((module.parent/'dolrecomp-output/RMGE01_generated/chunks').glob('*804520A0.c'))
calls=re.findall(r'    ppc_ps_(?:add|sub)_op\(ctx, [^;]+;',chunk.read_text())[:24]
assert len(calls)==24
mix='\n'.join(calls)
candidate_mix=mix.replace('ppc_ps_add_op','candidate_add').replace('ppc_ps_sub_op','candidate_sub')
mix_functions='\nstatic void reference_mix(CPUState* ctx) {\n'+mix+'\n}\n'
mix_functions+='static void candidate_mix(CPUState* ctx) {\n'+candidate_mix+'\n}\n'
probe=probe.replace('static u64 random_bits',mix_functions+'\nstatic u64 random_bits',1)
mix_test=r'''
    // Shared ni_add/sub also return an exception field to scalar callers;
    // paired wrappers do not consume that field, so compare it directly.
    for(unsigned m=0;m<4;m++) {
      assert(fesetround(modes[m])==0);
      for(unsigned i=0;i<50000;i++) {
        CPUState a={0};a.fpscr=(u32)random_bits(&seed);CPUState b=a;
        f64 x=f64_value(i<169?special[i/13]:random_bits(&seed));
        f64 y=f64_value(i<169?special[i%13]:random_bits(&seed));
        feclearexcept(FE_ALL_EXCEPT);
        FPRes expected=(i&1)?ni_sub(&a,x,y):ni_add(&a,x,y);
        int flags=fetestexcept(FE_ALL_EXCEPT);
        feclearexcept(FE_ALL_EXCEPT);
        FPRes actual=(i&1)?candidate_ni_sub(&b,x,y):candidate_ni_add(&b,x,y);
        assert(flags==fetestexcept(FE_ALL_EXCEPT));
        assert(expected.exception==actual.exception);
        assert(f64_bits(expected.value)==f64_bits(actual.value));
        assert(!memcmp(&a,&b,sizeof a));
      }
    }
    puts("200k scalar-result exception/value/state/host-flags comparisons passed");
    // Actual 24-call register mix, not a contiguous guest execution trace.
    for(unsigned m=0;m<4;m++) {
      assert(fesetround(modes[m])==0);
      for(unsigned i=0;i<2500;i++) {
        CPUState a={0};a.fpscr=(u32)random_bits(&seed);
        for(unsigned r=0;r<32;r++) {
          a.fpr[r]=f64_value(random_bits(&seed));a.ps1[r]=f64_value(random_bits(&seed));
        }
        CPUState b=a;
        feclearexcept(FE_ALL_EXCEPT);reference_mix(&a);int f=fetestexcept(FE_ALL_EXCEPT);
        feclearexcept(FE_ALL_EXCEPT);candidate_mix(&b);
        assert(f==fetestexcept(FE_ALL_EXCEPT) && !memcmp(&a,&b,sizeof a));
      }
    }
    puts("10k actual-register-call-mix state and host flags comparisons passed");
    assert(fesetround(FE_TONEAREST)==0);
    CPUState initial={0};
    for(unsigned r=0;r<32;r++){initial.fpr[r]=r*.125;initial.ps1[r]=-(double)r*.0625;}
    for(unsigned trial=0;trial<4;trial++) {
      double times[2];
      for(unsigned order=0;order<2;order++) {
        unsigned choice=order^(trial&1);
        void (*volatile fn)(CPUState*)=choice?candidate_mix:reference_mix;
        clock_t begin=clock();
        for(unsigned i=0;i<500000;i++){CPUState c=initial;fn(&c);}
        times[choice]=(double)(clock()-begin)/CLOCKS_PER_SEC;
      }
      printf("register mix candidate/reference %.4f (%.6f/%.6f)\n",times[1]/times[0],times[1],times[0]);
    }
'''
probe=probe.replace('    return 0;\n}',mix_test+'\n    return 0;\n}')
if '--correctness-only' in sys.argv:
    probe=probe.replace('repeat<4','repeat<0').replace('trial<4','trial<0')
assert 'if (!isfinite(a0)' not in probe
with tempfile.TemporaryDirectory(prefix='galaxypad-cold-fp-') as temp:
    base=Path(temp);(base/'test.c').write_text(probe)
    flags=['clang','-O2','-std=c11','-ffp-contract=off','-fno-fast-math',
           '-ffunction-sections','-fdata-sections','-I',str(core),
           '-I',str(core.parent.parent/'include'),str(base/'test.c'),'-Wl,-dead_strip']
    for mode in ['sanitize','benchmark']:
        print(mode+' (only unsanitized timings count)',flush=True)
        subprocess.run(flags+(['-fsanitize=undefined'] if mode=='sanitize' else [])+
                       ['-o',str(base/mode)],check=True)
        subprocess.run([str(base/mode)],check=True)
    assembly=base/'test.s'
    subprocess.run(['clang','-O2','-std=c11','-ffp-contract=off','-fno-fast-math',
        '-I',str(core),'-I',str(core.parent.parent/'include'),'-S',str(base/'test.c'),
        '-o',str(assembly)],check=True)
    asm=assembly.read_text()
    for symbol in ['ppc_ps_add_op','candidate_add','ppc_ps_sub_op','candidate_sub','cold_add','cold_sub']:
        marker='_'+symbol+':'
        if marker in asm:
            body=asm.split(marker,1)[1].split('.cfi_endproc',1)[0]
            instructions=len(re.findall(r'^\t[a-z][a-z0-9.]*\s',body,re.M))
            print(symbol,'assembly instruction lines',instructions)
        else:
            print(symbol,'inlined or omitted as standalone symbol')
