"""Execute actual save-helper entry cases; default reproduces accepted-app defect."""
from pathlib import Path
import argparse
import re
import subprocess
import tempfile
parser=argparse.ArgumentParser()
parser.add_argument('--source', type=Path)
parser.add_argument('--expect-fixed', action='store_true')
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
if args.source:
    source=args.source.read_text()
else:
    module=Path((root/'generated/modules/RMGE01/active-module.txt').read_text().strip())
    chunks=module.parent/'dolrecomp-output/RMGE01_generated/chunks'
    source=next(chunks.glob('*805170A0.c')).read_text()
switch=source.split('switch (ctx->pc) {',1)[1].split('default:',1)[0]
cases='\n'.join(re.search(r'case 0x'+pc+r'u: [^\n]+',switch)[0]
                for pc in ['805174FC','80517538'])
body='label_805174FC:'+source.split('label_805174FC:',1)[1].split('label_80517548:',1)[0]
body=body.replace('goto return_dispatch_805170A0;', 'return;')
prefix=r'''
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#include <stdio.h>
typedef uint32_t u32; typedef int32_t s32;
typedef struct {u32 pc,lr,gpr[32]; int64_t downcount;} CPUState;
static unsigned writes;
static void mem_write32(CPUState* c,u32 ea,u32 value){++writes;}
static void run(CPUState* ctx) {
  switch(ctx->pc) {
ACTUAL_ENTRY_CASES
    default: assert(false);
  }
'''
test=r'''
}
int main() {
  CPUState c={0}; c.pc=0x805174fc;c.lr=0x80001000;
  run(&c); assert(writes==18 && c.downcount==-19);
  writes=0;c.pc=0x80517538;c.downcount=0;
  run(&c); assert(writes==3 && c.pc==0x80001000);
  printf("interior entry: stores=%u generated_charge=%lld expected_simple_instruction_charge=4\n",writes,(long long)-c.downcount);
  assert(c.downcount==EXPECTED_DOWNCOUNT);
}
'''
with tempfile.TemporaryDirectory() as tmp:
    tmp=Path(tmp); f=tmp/'probe.c'
    f.write_text(prefix.replace('ACTUAL_ENTRY_CASES',cases)+body+
                 test.replace('EXPECTED_DOWNCOUNT','-4' if args.expect_fixed else '0'))
    subprocess.run(['clang','-std=c11','-fsanitize=undefined',str(f),'-o',str(tmp/'probe')],check=True)
    subprocess.run([str(tmp/'probe')],check=True)
