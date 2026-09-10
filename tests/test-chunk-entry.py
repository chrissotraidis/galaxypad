"""Execute both private whole-chunk variants against identical memory callbacks."""
from pathlib import Path
import argparse
import hashlib
import subprocess
import tempfile
import importlib.util

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--optimized', action='store_true', help='O2/ThinLTO without sanitizers')
parser.add_argument('--huffman-y', action='store_true', help='Test the isolated luminance decoder extraction')
parser.add_argument('--dcbz', action='store_true', help='Test guarded whole-line clears in the unchanged decoder chunk')
parser.add_argument('--dcbz-loop', action='store_true', help='Preserve the decoder loop shape')
parser.add_argument('--cached-reads', action='store_true', help='Cache read-only loop mappings, refreshing after callbacks')
parser.add_argument('--remap-reads', action='store_true', help='With cached reads, mutate mapping and next address inside read callbacks')
args = parser.parse_args()
assert not args.remap_reads or args.cached_reads
if args.dcbz_loop:
    args.dcbz = True
if sum((args.dcbz, args.huffman_y, args.cached_reads)) > 1:
    parser.error('Select only one experiment')
root = Path(__file__).resolve().parents[1]
source = root/('generated/huffman-y-r263' if args.huffman_y or args.dcbz or args.cached_reads else 'generated/chunk-entry-r182')
hashes = {
    'reference': 'f1be7297ea3f8176e5be440a5fa596deb1c706a1885cb91e084f8fede5f423ca',
    'candidate': '76fdb33cad574c96f4aa2affd392e892f6a2a6e9837e851fe0aeb0fcd5b1405b',
} if args.huffman_y or args.dcbz or args.cached_reads else {
    'reference': 'e81b3bf9c80e34b325f15c9d78e525a46646c6048c2e6ed519d069f8e29bee32',
    'candidate': 'd248002b3b8021c79cd6b2c4ea1d15f015dd0b447b31fe060d54354dd45fe32b',
}
for variant, expected in hashes.items():
    if (args.dcbz or args.cached_reads) and variant == 'candidate':
        continue
    assert hashlib.sha256((source/(variant+'.c')).read_bytes()).hexdigest() == expected
includes = ['-I', str(root/'ref/ModernGekko/vendor/dolphin/GXRuntime/include')]
program = r'''
#include "core/cpu.h"
#include <assert.h>
#include <setjmp.h>
#include <stdio.h>
#include <string.h>
void reference_chunk(CPUState*);
void candidate_chunk(CPUState*);
PPCMemWriteJournal g_mem_write_journal;
void* g_mem_write_journal_user;
unsigned dolrecomp_call_depth;
static u8 memory[4096],initial[4096],expected_memory[4096];
typedef struct {u32 pc,ea,size,write,cr,xer,reserve_addr,reserve_valid;u64 value; s64 downcount;u32 gpr[32];} Event;
static Event events[4096],expected[4096];
static unsigned count,mutate,journal_events,reservation_clears;
static jmp_buf stop;
static void record(CPUState* c,u32 ea,u8 size,u64 value,unsigned write) {
 if(count==4096) longjmp(stop,1);
 Event* e=&events[count++];memset(e,0,sizeof *e);
 e->pc=c->pc;e->ea=ea;e->size=size;e->value=value;e->write=write;
 e->cr=c->cr;e->xer=c->xer;e->downcount=c->downcount;
 e->reserve_addr=c->reserve_addr;e->reserve_valid=c->reserve_valid;
 memcpy(e->gpr,c->gpr,sizeof e->gpr);
 if(mutate && count%7==0) { c->gpr[12]^=3;c->xer^=0x80000000;c->exception^=1; }
}
static u64 read_external(CPUState* c,u32 ea,u8 size) {
 u64 value=0;for(unsigned i=0;i<size;i++) value=(value<<8)|memory[(ea+i)&4095];
 record(c,ea,size,value,0);return value;
}
static void write_external(CPUState* c,u32 ea,u64 value,u8 size) {
 record(c,ea,size,value,1);
 for(unsigned i=0;i<size;i++) memory[(ea+i)&4095]=(u8)(value>>(8*(size-i-1)));
}
static void journal(u32 offset,u32 size,void* user) {
 journal_events++;
 record((CPUState*)user,offset,(u8)size,0,2);
}
static u32 random_word(u32* s) { *s^=*s<<13;*s^=*s>>17;*s^=*s<<5;return *s; }
static CPUState a,b;
static unsigned capped;
static int execute(void(*f)(CPUState*),CPUState* c) {
 count=0;memcpy(memory,initial,sizeof memory);g_mem_write_journal_user=c;
 if(setjmp(stop)) return 1;
 f(c);return 0;
}
int main(void) {
 u32 seed=0x73ad29ef;unsigned cases=0;
#ifdef HUFFMAN_Y_TEST
 const s64 budgets[]={-257,0,1,16,64,256,1024,4096};
 const unsigned trials=8;
#else
 const unsigned trials=4;
#endif
 for(unsigned mode=0;mode<8;mode++) for(unsigned trial=0;trial<trials;trial++)
 for(unsigned entry=0;entry<1024;entry++) {
  memset(&a,0,sizeof a);
  for(unsigned i=0;i<sizeof initial;i++) initial[i]=(u8)(random_word(&seed)&15);
  for(unsigned i=0;i<32;i++) a.gpr[i]=random_word(&seed);
  a.pc=0x804530A0+entry*4;a.cr=random_word(&seed);a.xer=random_word(&seed);
  a.lr=0x90001000;a.ctr=1+trial;a.downcount=trial%2?0:-257;
#ifdef HUFFMAN_Y_TEST
  a.downcount=budgets[trial];
#endif
  a.external_read=read_external;a.external_write=write_external;
  // The existing get_ram_ptr contract requires initialized nonempty MEM1.
  a.ram=memory;a.ram_size=sizeof memory;
  mutate=mode&1;
  if(mode&2) {for(unsigned i=0;i<32;i++) a.gpr[i]=0x80000000+(random_word(&seed)&4092);}
  g_mem_write_journal=(mode&4)?journal:NULL;
  a.reserve_valid=true;a.reserve_addr=0x80000000+(random_word(&seed)&4092);
  b=a;
  int acap=execute(reference_chunk,&a);unsigned acount=count;
  memcpy(expected,events,count*sizeof(Event));memcpy(expected_memory,memory,sizeof memory);
  int bcap=execute(candidate_chunk,&b);
  if(acap!=bcap||acount!=count||memcmp(&a,&b,sizeof a)||
     memcmp(expected,events,count*sizeof(Event))||memcmp(expected_memory,memory,sizeof memory)) {
   fprintf(stderr,"mismatch mode=%u trial=%u entry=%08x callbacks=%u/%u capped=%d/%d\n",mode,trial,0x804530A0+entry*4,acount,count,acap,bcap);return 1;
  }
  reservation_clears+=!a.reserve_valid;capped+=acap;cases++;
 }
 assert(journal_events>0 && reservation_clears>0);
 printf("%u complete-chunk entry/state/memory/callback comparisons; capped=%u journal_events=%u reservation_clears=%u\n",cases,capped,journal_events,reservation_clears);
 return capped?2:0;
}
'''
if args.remap_reads:
    anchor = 'record(c,ea,size,value,0);return value;'
    assert program.count(anchor) == 1
    program = program.replace('static unsigned count,mutate,journal_events,reservation_clears;',
                              'static unsigned count,mutate,journal_events,reservation_clears,remaps;')
    program = program.replace(anchor, '''record(c,ea,size,value,0);
 if(mutate && count%7==0) {
  remaps++;
  c->ram=memory+64;c->ram_size=sizeof(memory)-64;
  c->exram=(count&1)?memory:NULL;c->exram_size=sizeof(memory);
  c->gpr[6]=0x80000000u-4u;
 }
 return value;''')
    program = program.replace('return capped?2:0;', 'assert(remaps>0); printf("mapping_changes=%u\\n",remaps); return capped?2:0;')
with tempfile.TemporaryDirectory(prefix='galaxypad-chunk-entry-') as directory:
    temp = Path(directory)
    flags = (['-O2', '-flto=thin'] if args.optimized else ['-O1', '-fsanitize=address,undefined'])
    flags += ['-std=c11', '-ffp-contract=off', '-fno-fast-math', *includes]
    if args.huffman_y or args.dcbz or args.cached_reads:
        flags += ['-DHUFFMAN_Y_TEST']
    for variant in ('reference', 'candidate'):
        input_source = source/(variant+'.c')
        if args.cached_reads:
            text = (source/'reference.c').read_text()
            if variant == 'candidate':
                spec = importlib.util.spec_from_file_location('cached', root/'scripts/cache-huffman-loop-reads.py')
                cached = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(cached)
                text = cached.transform(text)
            input_source = temp/(variant+'.c')
            input_source.write_text(text)
        if args.dcbz:
            text = (source/'reference.c').read_text()
            if variant == 'candidate':
                anchor = 'for (u32 i = 0; i < 32; i += 4) mem_write32(ctx, ea + i, 0);'
                assert text.count(anchor) == 8
                replacement = ('u8* line = galaxypad_dcbz_prepare(ctx, ea);\n'
                    '        for (u32 i = 0; i < 32; i += 4) galaxypad_dcbz_store(ctx, ea, line, i);') if args.dcbz_loop else 'galaxypad_dcbz_ram_line(ctx, ea);'
                text = text.replace(anchor, replacement)
                signature = 'void func_804530A0(CPUState* ctx) {'
                assert text.count(signature) == 1
                helper = (root/('patches/experiments/dcbz-ram-loop.inc' if args.dcbz_loop else 'patches/experiments/dcbz-ram-line.inc')).read_text()
                text = text.replace(signature, '#include <string.h>\n'+helper+'\n'+signature)
            input_source = temp/(variant+'.c')
            input_source.write_text(text)
        subprocess.run(['clang', *flags, '-Dfunc_804530A0='+variant+'_chunk',
                        '-c', str(input_source), '-o', str(temp/(variant+'.o'))], check=True)
    (temp/'harness.c').write_text(program)
    subprocess.run(['clang', *flags, str(temp/'harness.c'), str(temp/'reference.o'),
                    str(temp/'candidate.o'), '-o', str(temp/'test')], check=True)
    subprocess.run([str(temp/'test')], check=True, timeout=45)
