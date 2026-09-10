"""Cost screen for the exact extracted burst, NOT an actual Dolphin speed test.

Separate translation units keep configuration and guest callbacks opaque to the
loop compiler. Stub services/layout remain a limitation. Uses host optimization
policy with a macOS target so no Simulator is needed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import statistics
import subprocess

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
candidate = root / 'generated/quiet-run-r816/candidate.cpp'
fixture = out / 'fixture.cpp'
subprocess.run(['python3', str(root / 'tests/test-run-quiet-specialization.py'),
                '--candidate-source', str(candidate), '--emit-harness', str(fixture)], check=True)
text = fixture.read_text().split('int main(){')[0]
text = text.replace('static Fixture* current;', 'extern Fixture* current;')
start = text.index('  static void callback(Guest* g,u32 address) {')
end = text.index('  void reference(){', start)
callback = text[start:end].replace('  static void callback(', 'void Fixture::callback(', 1)
callback = callback.replace('f.observed.push_back(*g);', '')
callback = callback.replace('if(f.calls!=f.trigger)return;', '''
    for(unsigned j=0;j<f.work;++j)g->ctr=(g->ctr^g->lr)*1664525u+1013904223u;
    if(f.calls!=f.trigger)return;
    if(f.reason==0)f.ppc.downcount=0;
''')
text = text[:start] + '  static void callback(Guest*,u32);\n' + text[end:]
text = text.replace('unsigned reason=0,', 'unsigned work=0, reason=0,')
(out / 'fixture.h').write_text('#pragma once\n' + text)
(out / 'callback.cpp').write_text('#include "fixture.h"\nFixture* current=nullptr;\n' + callback)
(out / 'loops.cpp').write_text('''#include "fixture.h"
extern "C" __attribute__((noinline)) void baseline(Fixture* f){ f->reference(); }
extern "C" __attribute__((noinline)) void quiet(Fixture* f){
  if(!f->dispatch_trace && !f->lockstep_enabled && !f->m_collect_dispatch_samples &&
     !f->m_has_rel_modules && !f->m_direct_boundary_enabled)
    f->candidate<true>();
  else f->candidate<false>();
}
''')
(out / 'driver.cpp').write_text(r'''
#include "fixture.h"
#include <ctime>
#include <cstdlib>
extern "C" void baseline(Fixture*);
extern "C" void quiet(Fixture*);
static uint64_t ns(){timespec t{};if(clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t))std::abort();
 return uint64_t(t.tv_sec)*1000000000ull+t.tv_nsec;}
int main(){
 for(unsigned length : {1u,16u,128u})for(unsigned work : {0u,16u,128u})
  for(unsigned reason : {0u,3u,4u}){
   const unsigned count=100000/length;
   uint64_t expected=0;
   for(unsigned order=0;order<8;++order){
    bool candidate=(order%4==1 || order%4==2); // A B B A A B B A
    Fixture f;f.work=work;f.reason=reason;f.trigger=length;current=&f;
    auto run=candidate?quiet:baseline;
    uint64_t checksum=0,dispatches=0;
    auto start=ns();
    for(unsigned n=0;n<count;++n){
     f.calls=0;f.hooked=false;f.ppc.downcount=100000;f.ppc.Exceptions=0;
     f.m_guest.pc=0x80000000;f.m_guest.downcount=0;
     run(&f);dispatches+=f.calls;
     checksum+=f.m_guest.ctr+f.m_guest.timebase+f.m_charged_cycles;
     if(f.calls!=length)std::abort();
    }
    auto elapsed=ns()-start;
    if(order==0)expected=checksum;else if(checksum!=expected)std::abort();
    std::printf("%u,%u,%u,%u,%u,%llu,%llu,%llu\n",length,work,reason,order,
     unsigned(candidate),(unsigned long long)elapsed,(unsigned long long)dispatches,
     (unsigned long long)checksum);
   }
  }
}
''')
# Cached Simulator host entry is O3, no LTO/PGO. Architecture/optimization
# retained; SDK and deployment target intentionally adapted to a macOS process.
flags = ['-std=c++23', '-O3', '-DNDEBUG', '-arch', 'arm64', '-march=armv8-a+crc',
         '-fno-strict-aliasing', '-fno-exceptions', '-fvisibility-inlines-hidden',
         '-fvisibility=hidden', '-fomit-frame-pointer']
commands = []
for name in ['callback', 'loops', 'driver']:
    command = ['clang++', *flags, '-c', str(out / (name+'.cpp')), '-o', str(out / (name+'.o'))]
    commands.append(command)
    subprocess.run(command, check=True)
binary = out / 'probe'
subprocess.run(['clang++', *(str(out / (n+'.o')) for n in ['callback','loops','driver']),
                '-o', str(binary)], check=True)
assembly = subprocess.check_output(['xcrun', 'llvm-objdump', '--disassemble', '--demangle',
                                    str(out/'loops.o')], text=True)
(out / 'loops.asm').write_text(assembly)
assert 'blr' in assembly, 'Lost opaque indirect callback'
raw = subprocess.check_output([str(binary)], text=True)
(out / 'timings.csv').write_text('length,work,reason,order,candidate,cpu_ns,dispatches,checksum\n'+raw)
groups = {}
for line in raw.splitlines():
    length, work, reason, order, cand, elapsed, dispatches, checksum = map(int, line.split(','))
    groups.setdefault((length,work,reason), {0:[],1:[]})[cand].append(elapsed/dispatches)
rows = []
for (length, work, reason), times in groups.items():
    a,b = (statistics.median(times[n]) for n in [0,1])
    rows.append(dict(length=length, work=work, reason=reason, baseline_ns=a,
                     candidate_ns=b, percent_saved=100*(a-b)/a, samples=times))
report = dict(boundary='Synthetic extracted burst, stub layout/services; no game FPS inference',
              compile_commands=commands, target_adaptation='Simulator ARM64 to host macOS ARM64',
              candidate_source_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest(), rows=rows)
(out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
for row in rows:
    print(f"length={row['length']:3} work={row['work']:3} exit={row['reason']} "
          f"{row['baseline_ns']:.2f} -> {row['candidate_ns']:.2f} ns/dispatch "
          f"saved={row['percent_saved']:.2f}%")
