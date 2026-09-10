"""Compile the actual fixture wrapper against a deterministic fake dispatch."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root/'tests/fixtures/huffman-throughput.c').read_text()
body = source[source.index('static void fixture_dispatch('):source.index('static u64 bad_read(')]
program = '''
#include <assert.h>
#include <stdint.h>
typedef int64_t s64;
typedef struct {s64 downcount;} CPUState;
''' + body + '''
static void step(CPUState* cpu) {
#ifdef RUNTIME_CHARGE_RESET
 assert(cpu->downcount==0);
#endif
 cpu->downcount-=300;
}
int main(void) {
 CPUState cpu={0};s64 charge=0;
 fixture_dispatch(step,&cpu,&charge);
 fixture_dispatch(step,&cpu,&charge);
#ifdef RUNTIME_CHARGE_RESET
 assert(cpu.downcount==-300 && charge==-600);
#else
 assert(cpu.downcount==-600 && charge==0);
#endif
 return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-charge-reset-') as directory:
    path = Path(directory)/'check.c'
    path.write_text(program)
    for flags in ([], ['-DRUNTIME_CHARGE_RESET']):
        binary = Path(directory)/'check'
        subprocess.run(['clang', '-O2', '-fsanitize=undefined', *flags, str(path), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
print('Fixture per-dispatch reset, aggregate charge and legacy stress mode pass')
