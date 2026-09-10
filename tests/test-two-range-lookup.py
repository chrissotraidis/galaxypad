"""Actual generated tables/reference lookup against exact two-range candidate."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
from two_range_lookup import transform,START,END
generated=root/'generated/modules-thp-r205/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-daa33a86eff05b70/dolrecomp-output/RMGE01_generated'
source=(generated/'RMGE01.h').read_text()
changed=transform(source)
start=source.index(START);end=source.index(END,start)
assert changed[:start]==source[:start]
assert changed.split(END,1)[1]==source.split(END,1)[1]
try:
    transform(source+'\n')
except ValueError:
    pass
else:
    raise AssertionError('Unpinned header accepted')
tables=source[source.index('#define DOLRECOMP_LOOKUP_RUNS'):start]
names=re.findall(r'^    (func_[0-9A-F]+),$',tables,re.M)
assert len(names)==len(set(names))==1322
stubs='\n'.join(f'static void {name}(void) {{ selected={i}u; }}' for i,name in enumerate(names))
reference=source[start:end].replace('dolrecomp_find_original','reference_lookup')
candidate=changed[start:changed.index(END,start)].replace('dolrecomp_find_original','candidate_lookup')
program=r'''
#include <stdint.h>
#include <stddef.h>
#include <assert.h>
#include <stdio.h>
typedef uint32_t u32;
typedef void (*DolRecompFunction)(void);
#define DOLRECOMP_UNUSED
static volatile u32 selected;
STUBS
TABLES
REFERENCE
CANDIDATE
static uint64_t cases,hits;
static void compare(u32 address) {
 DolRecompFunction expected=reference_lookup(address),actual=candidate_lookup(address);
 assert(actual==expected);cases++;hits+=actual!=NULL;
}
int main(void) {
 // Every byte across both supported runs, their hole and surrounding pages.
 for(uint64_t address=0x7ffff000ull;address<0x8052e000ull;address++)compare((u32)address);
 // Explicit wrap, alias, MMIO and far out-of-range probes.
 const u32 edges[]={0,1,3,0xffffffffu,0xfffffffcu,0x7fffffffu,0x80000000u,
  0x80004000u,0x800064e0u,0x800070a0u,0x8052d280u,0x90000000u,0xc0004000u,0xd0000000u};
 for(unsigned i=0;i<sizeof(edges)/sizeof(*edges);i++)
  for(int delta=-16;delta<=16;delta++)compare(edges[i]+(u32)delta);
 u32 seed=0x3552026u;
 for(unsigned i=0;i<1000000;i++) {
  seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;compare(seed);
 }
 // Every chunk entry resolves to the corresponding distinct function.
 for(unsigned i=0;i<1322;i++) {
  u32 address=i<3?0x80004000u+i*4096:0x800070a0u+(i-3)*4096;
  selected=0xffffffffu;candidate_lookup(address)();assert(selected==i);
 }
 assert(hits>1000000);
 printf("%llu lookup comparisons, %llu hits, 1322 chunk identities pass\n",
        (unsigned long long)cases,(unsigned long long)hits);
}
'''.replace('STUBS',stubs).replace('TABLES',tables).replace('REFERENCE',reference).replace('CANDIDATE',candidate)
with tempfile.TemporaryDirectory(prefix='galaxypad-two-range-') as temporary:
    directory=Path(temporary);harness=directory/'probe.c';harness.write_text(program)
    for name,flags in [('sanitized',['-O1','-fsanitize=address,undefined']),('optimized',['-O2'])]:
        binary=directory/name
        subprocess.run(['clang','-std=c11',*flags,str(harness),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
