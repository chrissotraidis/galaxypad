"""Isolated NI-mode branch hint: exact conversion oracle and code-shape check."""
from pathlib import Path
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
core = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
source = (core/'cpu_interpreter_float.c').read_text()
start = source.index('f32 force_single(')
end = source.index('\nf64 force_double(', start)
body = source[start:end]
old = 'if (cpu->fpscr & FPSCR_NI_BIT)'
assert body.count(old) == 1
hinted = body.replace(old, 'if (__builtin_expect((cpu->fpscr & FPSCR_NI_BIT) != 0, 0))')
candidate_source = source[:start] + hinted + source[end:]
driver = r'''
#pragma STDC FENV_ACCESS ON
#include "cpu_interpreter_float.c"
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
CANDIDATE
__attribute__((noinline)) static f32 reference(CPUState* cpu, f64 value) {
  return force_single(cpu,value);
}
int main(void) {
  u64 seed=739, saved;
  __asm__ volatile("mrs %0, fpcr":"=r"(saved));
  const u64 special[]={0,0x8000000000000000ull,1,0x000fffffffffffffull,
    0x0010000000000000ull,0x380fffffffffffffull,0x3810000000000000ull,
    0x7fefffffffffffffull,0x7ff0000000000000ull,0xfff0000000000000ull,
    0x7ff0000000000001ull,0x7ff8000000000123ull,0xfff8000000000123ull};
  for(unsigned rn=0;rn<4;++rn)for(unsigned ni=0;ni<2;++ni){
    CPUState cpu={0};cpu.fpscr=rn|(ni?FPSCR_NI_BIT:0);
    ppc_fpscr_control_updated(&cpu);
    for(unsigned i=0;i<100000;++i){
      seed^=seed<<13;seed^=seed>>7;seed^=seed<<17;
      f64 value=f64_value(i<sizeof(special)/sizeof(*special)?special[i]:seed);
      feclearexcept(FE_ALL_EXCEPT);
      f32 a=reference(&cpu,value);int af=fetestexcept(FE_ALL_EXCEPT);
      feclearexcept(FE_ALL_EXCEPT);
      f32 b=force_single_candidate(&cpu,value);int bf=fetestexcept(FE_ALL_EXCEPT);
      u32 ab,bb;memcpy(&ab,&a,4);memcpy(&bb,&b,4);
      assert(ab==bb && af==bf);
      assert(cpu.fpscr==(rn|(ni?FPSCR_NI_BIT:0)));
    }
  }
  __asm__ volatile("msr fpcr, %0"::"r"(saved));
  puts("800000 conversion cases: bits, host flags and unchanged FPSCR match");
}
'''.replace('CANDIDATE', '__attribute__((noinline)) '+hinted.replace('force_single(', 'force_single_candidate(', 1))

with tempfile.TemporaryDirectory(prefix='galaxypad-single-mode-') as directory:
    stage = Path(directory)
    flags = ['clang','-O2','-std=c11','-ffp-contract=off','-fno-fast-math',
             '-I'+str(core),'-I'+str(core.parent.parent/'include')]
    path = stage/'probe.c';path.write_text(driver)
    subprocess.run([*flags,'-fsanitize=undefined','-Wl,-dead_strip',str(path),'-o',str(stage/'probe')],check=True)
    subprocess.run([str(stage/'probe')],check=True)
    for name, text in [('original',source),('hinted',candidate_source)]:
        path=stage/f'{name}.c';path.write_text(text)
        assembly=stage/f'{name}.s'
        subprocess.run([*flags,'-S',str(path),'-o',str(assembly)],check=True)
        text=assembly.read_text()
        match=re.search(r'^_ppc_ps_add_op:.*?\.cfi_endproc',text,re.M|re.S)
        assert match
        instructions=re.findall(r'^\t[a-z][a-z0-9.]*\s',match[0],re.M)
        print(name,'ps_add static instructions:',len(instructions))
print('Source hint only; no module mutation, dynamic cost or gameplay proof')
