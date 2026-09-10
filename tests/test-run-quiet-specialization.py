"""Private native-burst differential; no product source or build is changed.

Extract the complete current inner native loop, retaining its live eligibility
lambda. Only optional configuration is specialized. Runtime services are stubs:
this is not full Dolphin integration, a cost benchmark, or gameplay acceptance.
"""
from pathlib import Path
import argparse
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp'
source = SOURCE.read_text()
start = source.index('        do\n        {\n          if (dispatch_trace')
end = source.index('\n        SyncOut();', start)
loop = source[start:end]
start = source.index('  const auto fast_dispatchable_at = [this](u32 address) {')
end = source.index('\n  };', start) + len('\n  };')
lookup = source[start:end]
# Compile-time specialization of the SAME body, not a handwritten second loop.
# No pointer snapshots, timing changes, or cached SMC/hook results.
specialized = loop
for old, new, count in [
    ('if (dispatch_trace &&', 'if (!Quiet && dispatch_trace &&', 1),
    ('lockstep_enabled &&', '!Quiet && lockstep_enabled &&', 1),
    ('if (m_collect_dispatch_samples &&', 'if (!Quiet && m_collect_dispatch_samples &&', 1),
    ('if (m_has_rel_modules)', 'if (!Quiet && m_has_rel_modules)', 2),
    ('if (m_direct_boundary_enabled)', 'if (!Quiet && m_direct_boundary_enabled)', 1),
]:
    assert specialized.count(old) == count, old
    specialized = specialized.replace(old, new)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--candidate-source', type=Path)
parser.add_argument('--emit-harness', type=Path, help='Write the private fixture without compiling it')
args = parser.parse_args()
if args.candidate_source:
    actual = args.candidate_source.read_text()
    prefix = '        const auto native_burst = [&]<bool Quiet>() {\n'
    suffix = '''
        };
        if (!dispatch_trace && !lockstep_enabled && !m_collect_dispatch_samples &&
            !m_has_rel_modules && !m_direct_boundary_enabled)
          native_burst.template operator()<true>();
        else
          native_burst.template operator()<false>();'''
    assert source.count(loop) == 1
    assert actual == source.replace(loop, prefix + specialized + suffix)
    print('Exact full candidate source and specialization entry gate match', flush=True)

program = r'''
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <memory>
#include <unordered_map>
#include <vector>
using u32=uint32_t; using u64=uint64_t; using s64=int64_t;
constexpr u32 SYNC_EXCEPTION_MASK=1, ASYNC_EXCEPTION_MASK=2, MSR_EE=0x8000;
namespace SystemTimers { constexpr int TIMER_RATIO=12; }
namespace CPU { enum class State { Running, Paused }; }
struct Guest {
  u32 pc=0x80000000, lr=0, ctr=0, cr=0, msr=MSR_EE, exception=0, program_exception=0;
  u64 timebase=100; s64 downcount=0; bool host_call=true;
  bool operator==(const Guest&) const = default;
};
struct PPC { int downcount=200; u32 Exceptions=0; bool operator==(const PPC&) const=default; };
struct Timing { unsigned idles=0; void Idle(){++idles;} };
struct System { Timing timing; Timing& GetCoreTiming(){return timing;} };
struct Verifier {
  bool ShouldCheck(u32){assert(false);return false;}
  void Prepare(Guest&){assert(false);} void Verify(Guest&){assert(false);}
};
struct Fixture;
struct Module { void (*dispatch)(Guest*,u32); };
static Fixture* current;
struct Fixture {
  Guest m_guest; PPC ppc; System m_system; CPU::State state=CPU::State::Running;
  bool m_module_active=true, m_has_rel_modules=false, m_collect_dispatch_samples=false;
  bool m_direct_boundary_enabled=false, m_in_native_dispatch=false;
  bool m_direct_segment_committed=false, m_direct_must_yield=false;
  bool lockstep_enabled=false;
  std::unique_ptr<std::FILE, decltype(&std::fclose)> dispatch_trace{nullptr,&std::fclose};
  Verifier verifier; Verifier* m_lockstep_verifier=&verifier;
  u64 m_native_dispatches=0, m_charged_cycles=0, m_timebase_cycle_remainder=0, m_native_exceptions=0;
  u32 m_idle_pc=0, m_lookup_ram_size=64, m_lookup_exram_size=64;
  std::vector<int> m_forced_fallback_ranges, m_chunk_lookup_table=std::vector<int>(32,0);
  std::vector<int> m_chunk_state{1}; static constexpr int CHUNK_VERIFIED=1;
  std::unordered_map<u32,u64> m_dispatch_samples;
  unsigned reason=0, trigger=1, calls=0, hook_checks=0, slow_checks=0;
  bool hooked=false; std::vector<Guest> observed;
  Module module{callback}; Module* m_module=&module;
  bool FastDispatchableAt(u32){++slow_checks; return m_module_active && m_chunk_state[0]==1;}
  bool IsHostCallAddress(u32){++hook_checks;return hooked;}
  void ResolveNativeAddress(u32,u32*,void*){assert(false);}
  u32 TranslateRelAddress(u32){assert(false);return 0;}
  static void callback(Guest* g,u32 address) {
    auto& f=*current; assert(g==&f.m_guest && address==g->pc);
    f.observed.push_back(*g); ++f.calls;
    g->downcount=-s64(f.calls%7); // Includes empty dispatch progress.
    g->pc=0x80000000+4*(f.calls%16); g->lr+=7; g->cr^=f.calls;
    if(f.calls!=f.trigger)return;
    switch(f.reason) {
      case 0: break;
      case 1: f.m_chunk_state[0]=0; break;
      case 2: f.m_chunk_state[0]=2; break;
      case 3: f.hooked=true; break;
      case 4: f.ppc.Exceptions=SYNC_EXCEPTION_MASK; break;
      case 5: f.ppc.Exceptions=ASYNC_EXCEPTION_MASK; break;
      case 6: f.ppc.Exceptions=ASYNC_EXCEPTION_MASK;g->msr=0;break;
      case 7: f.state=CPU::State::Paused; break;
      case 8: f.m_module_active=false; break;
      case 9: g->exception=1;g->program_exception=1;break;
      case 10: g->pc=0x70000000;break;
      case 11: g->pc=0x90000000;break;
      case 12: g->downcount=-500;break;
      case 13: f.m_chunk_lookup_table[0]=-1;g->pc=0x80000000;break;
    }
  }
  void reference(){
    const CPU::State* state_ptr=&state;
    LOOKUP
    REFERENCE
  }
  template<bool Quiet> void candidate(){
    const CPU::State* state_ptr=&state;
    LOOKUP
    CANDIDATE
  }
  void compare(const Fixture& b) const {
    assert(m_guest==b.m_guest && ppc==b.ppc && state==b.state);
    assert(observed==b.observed && calls==b.calls && hook_checks==b.hook_checks);
    assert(slow_checks==b.slow_checks && m_system.timing.idles==b.m_system.timing.idles);
    assert(m_native_dispatches==b.m_native_dispatches && m_charged_cycles==b.m_charged_cycles);
    assert(m_timebase_cycle_remainder==b.m_timebase_cycle_remainder);
    assert(m_native_exceptions==b.m_native_exceptions && m_chunk_state==b.m_chunk_state);
    assert(m_chunk_lookup_table==b.m_chunk_lookup_table && m_module_active==b.m_module_active);
    assert(m_in_native_dispatch==b.m_in_native_dispatch);
    assert(m_direct_segment_committed==b.m_direct_segment_committed);
    assert(m_direct_must_yield==b.m_direct_must_yield && m_dispatch_samples==b.m_dispatch_samples);
  }
};
int main(){
  unsigned cases=0;
  for(unsigned reason=0;reason<14;++reason)
    for(unsigned trigger : {1u,2u,7u,23u})
      for(unsigned remainder=0;remainder<12;++remainder)
        for(unsigned mode=0;mode<8;++mode){
          Fixture a,b,c;
          for(auto* f : {&a,&b,&c}){
            f->reason=reason;f->trigger=trigger;f->m_timebase_cycle_remainder=remainder;
            if(mode&1)f->m_forced_fallback_ranges.push_back(1);
            if(mode&2)f->m_idle_pc=0x80000004;
            if(mode&4)f->m_guest.host_call=false;
          }
          current=&a;a.reference();current=&b;b.candidate<true>();
          current=&c;c.candidate<false>();a.compare(b);a.compare(c);
          assert(a.calls>0 && a.m_guest.downcount==0);
          assert(a.m_guest.timebase==100+(remainder+a.m_charged_cycles)/12);
          assert(a.m_timebase_cycle_remainder==(remainder+a.m_charged_cycles)%12);
          ++cases;
        }
  std::printf("%u complete native-burst differential cases pass (stub services; not full runtime)\n",cases);
}
'''.replace('LOOKUP', lookup).replace('REFERENCE', loop).replace('CANDIDATE', specialized)

if args.emit_harness:
    with args.emit_harness.open('x') as output:
        output.write(program)
    raise SystemExit(0)

with tempfile.TemporaryDirectory(prefix='galaxypad-quiet-loop-') as directory:
    stage = Path(directory)
    harness = stage / 'test.cpp'
    harness.write_text(program)
    for name, flags in [('sanitized', ['-O1', '-fsanitize=address,undefined']),
                        ('optimized', ['-O2'])]:
        binary = stage / name
        subprocess.run(['clang++', '-std=c++20', '-Wall', '-Wextra', '-Werror',
                        *flags, str(harness), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
