"""Bit-level proof checks for an isolated 25-bit C-operand identity shortcut."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
core = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
source = (core/'cpu_interpreter_float.c').read_text()
assert hashlib.sha256(source.encode()).hexdigest() == '554149a2e7d08783402af38e5a2b898aff476370b0e3a6af0ed4bd411aab934f'
start = source.index('f64 force_25bit_c(')
brace = source.index('{',start)
end, depth = brace+1,1
while depth:
    depth += (source[end]=='{')-(source[end]=='}');end += 1
function = source[start:end]
helper_start = source.index('unsigned leading_zeroes_u64(')
helper_end = source.index('\n}',helper_start)+2
program = r'''
#include "cpu_interpreter_private.h"
#include <assert.h>
#include <stdio.h>
LEADING_ZEROES
REFERENCE
CANDIDATE
int main(void) {
 u64 seed=0x7e19af4324ull;unsigned long count=0,identity=0;
 for(u64 sign_exp=0;sign_exp<4096;sign_exp++) for(unsigned i=0;i<1024;i++) {
  seed^=seed<<13;seed^=seed>>7;seed^=seed<<17;
  u64 bits=(sign_exp<<52)|(seed&0xfffffffffffffull);
  for(unsigned kind=0;kind<3;kind++) {
   u64 input=kind==0?bits:kind==1?(bits&~0xfffffffull):(sign_exp<<52)|(1ull<<(i%52));
   u64 a=f64_bits(reference(f64_value(input))),b=f64_bits(candidate(f64_value(input)));
   assert(a==b);
   if((input&0xfffffffull)==0) {assert(a==input);identity++;}
   count++;
  }
 }
 printf("%lu bit-pattern comparisons; %lu guarded identities\n",count,identity);
}
'''.replace('LEADING_ZEROES',source[helper_start:helper_end]).replace('REFERENCE',function.replace('force_25bit_c','reference')).replace(
    'CANDIDATE',function.replace('force_25bit_c','candidate').replace(
        'u64 integral = f64_bits(d);','u64 integral = f64_bits(d);\n    if ((integral & 0x0fffffffull) == 0) return d;'))
with tempfile.TemporaryDirectory(prefix='galaxypad-25bit-') as directory:
    temp = Path(directory)
    (temp/'probe.c').write_text(program)
    subprocess.run(['clang','-O2','-fsanitize=address,undefined','-std=c11',
                    '-I',str(core),'-I',str(core.parent.parent/'include'),
                    str(temp/'probe.c'),'-o',str(temp/'probe')],check=True)
    subprocess.run([str(temp/'probe')],check=True)
