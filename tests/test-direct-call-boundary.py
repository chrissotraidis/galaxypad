"""Exercise actual core boundary/outer-charge bodies with explicit runtime stubs."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp').read_text()
guard = source[source.index('int StaticRecompCore::HookDirectCallBoundary('):source.index('\nvoid StaticRecompCore::Run()')]
start = source.index('          const s64 charge = -m_guest.downcount;')
end_text = 'm_timebase_cycle_remainder = total_cycles % SystemTimers::TIMER_RATIO;'
charge = source[start:source.index(end_text, start)+len(end_text)]
program = r'''
#include <cassert>
#include <cstdint>
#include <memory>
using u32=uint32_t; using u64=uint64_t; using s64=int64_t;
constexpr u32 SYNC_EXCEPTION_MASK=1, ASYNC_EXCEPTION_MASK=2, MSR_EE=0x8000;
namespace SystemTimers { constexpr int TIMER_RATIO=12; }
namespace CPU { enum class State { Running, Paused }; }
struct CPUState { void* external_user_data=nullptr; s64 downcount=0;
  u64 timebase=100;u32 pc=0x80001000,msr=MSR_EE,exception=0; };
struct PPC { int downcount=10000; u32 Exceptions=0; };
struct PowerPC { PPC state; PPC& GetPPCState() { return state; } };
struct Cpu { CPU::State state=CPU::State::Running; const CPU::State* GetStatePtr(){return &state;} };
struct System { PowerPC ppc; Cpu cpu; PowerPC& GetPowerPC(){return ppc;} Cpu& GetCPU(){return cpu;} };
struct Verifier { bool enabled=false; bool IsEnabled(){return enabled;} };
struct StaticRecompCore {
  System m_system;
  CPUState m_guest;
  bool m_direct_boundary_enabled=true,m_in_native_dispatch=true,m_direct_must_yield=false;
  bool m_direct_segment_committed=false,m_module_active=true,m_has_rel_modules=false;
  u64 m_charged_cycles=0,m_timebase_cycle_remainder=0,m_direct_boundary_checks=0,m_direct_transfers=0;
  u32 m_idle_pc=0;
  bool verified=true,hooked=false,forced=false;
  std::unique_ptr<Verifier> m_lockstep_verifier=std::make_unique<Verifier>();
  StaticRecompCore(){m_guest.external_user_data=this;}
  bool FastDispatchableAt(u32){return verified&&!forced;}
  bool IsHostCallAddress(u32){return hooked;}
  void AdvanceGuestTimebase(u64 n){n+=m_timebase_cycle_remainder;m_guest.timebase+=n/12;m_timebase_cycle_remainder=n%12;}
  static int HookDirectCallBoundary(CPUState*,u32);
  void finish(){ auto& ppc=m_system.ppc.state; CHARGE }
};
GUARD
int main(){
  assert(!StaticRecompCore::HookDirectCallBoundary(nullptr,0));
  CPUState no_owner; assert(!StaticRecompCore::HookDirectCallBoundary(&no_owner,0));
  for(int reason=0;reason<13;++reason){
    StaticRecompCore c;c.m_guest.downcount=-13;
    switch(reason){
      case 0:c.m_module_active=false;break;
      case 1:c.m_has_rel_modules=true;break;
      case 2:c.m_lockstep_verifier->enabled=true;break;
      case 3:c.m_guest.pc++;break;
      case 4:c.m_system.cpu.state=CPU::State::Paused;break;
      case 5:c.m_system.ppc.state.downcount=13;break;
      case 6:c.m_guest.exception=1;break;
      case 7:c.m_system.ppc.state.Exceptions=SYNC_EXCEPTION_MASK;break;
      case 8:c.m_system.ppc.state.Exceptions=ASYNC_EXCEPTION_MASK;break;
      case 9:c.m_idle_pc=0x80001000;break;
      case 10:c.verified=false;break;
      case 11:c.hooked=true;break;
      case 12:c.forced=true;break;
    }
    assert(!c.HookDirectCallBoundary(&c.m_guest,0x80001000));
    assert(c.m_direct_must_yield&&c.m_direct_segment_committed);
    assert(c.m_charged_cycles==13&&c.m_guest.downcount==0);
    assert(c.m_guest.timebase==101&&c.m_timebase_cycle_remainder==1);
    assert(!c.HookDirectCallBoundary(&c.m_guest,0x80001000));
    c.finish();
    assert(c.m_charged_cycles==13&&c.m_guest.timebase==101); // No glue-only extra cycle.
  }
  for(int reason=0;reason<3;++reason){
    StaticRecompCore c;c.m_guest.downcount=-7;
    if(reason==0)c.m_direct_boundary_enabled=false;
    if(reason==1)c.m_in_native_dispatch=false;
    CPUState other=c.m_guest;
    assert(!c.HookDirectCallBoundary(reason==2?&other:&c.m_guest,0x80001000));
    assert(c.m_charged_cycles==0&&c.m_guest.downcount==-7);
  }
  for(unsigned n=0;n<257;++n){
    StaticRecompCore c;
    // Two completed original dispatch segments, then a final outer segment.
    c.m_guest.downcount=-s64(n);
    assert(c.HookDirectCallBoundary(&c.m_guest,c.m_guest.pc));
    c.m_guest.downcount=-s64(n+1);
    assert(c.HookDirectCallBoundary(&c.m_guest,c.m_guest.pc));
    c.m_guest.downcount=-s64(n+2);c.finish();
    const u64 expected=(n?n:1)+(n+1)+(n+2);
    assert(c.m_charged_cycles==expected);
    assert(c.m_system.ppc.state.downcount==10000-int(expected));
    assert(c.m_guest.timebase==100+expected/12&&c.m_timebase_cycle_remainder==expected%12);
  }
  StaticRecompCore disabled_interrupt;
  disabled_interrupt.m_guest.msr=0;
  disabled_interrupt.m_system.ppc.state.Exceptions=ASYNC_EXCEPTION_MASK;
  assert(disabled_interrupt.HookDirectCallBoundary(&disabled_interrupt.m_guest,0x80001000));
}
'''.replace('GUARD', guard).replace('CHARGE', charge)
nested = r'''
#include "binding.h"
static unsigned depth=0, limit=24, resumed_inner=0, resumed_outer=0, scenario=0;
static int dolrecomp_call_enter(){if(depth>=limit)return 0; ++depth;return 1;}
static void dolrecomp_call_leave(){assert(depth);--depth;}
static int dolrecomp_dispatch_replacement(CPUState*,u32){return 0;}
#include "transfer.h"
static void leaf(CPUState* ctx){
  ctx->downcount-=11;
  ctx->pc=scenario==1?104:204;
  auto* c=static_cast<StaticRecompCore*>(ctx->external_user_data);
  if(scenario==1)c->forced=true;
  if(scenario==2)c->m_system.cpu.state=CPU::State::Paused;
  if(scenario==3)c->m_system.ppc.state.Exceptions=SYNC_EXCEPTION_MASK;
}
static void inner(CPUState* ctx){
  ctx->downcount-=7;ctx->pc=200;
  if(!galaxypad_direct_transfer(ctx,200,scenario==1?104:204,leaf))return;
  ++resumed_inner;ctx->downcount-=13;ctx->pc=104;
}
static void nested_tests(){
  galaxypad_bind_direct_calls_v1(1,StaticRecompCore::HookDirectCallBoundary);
  for(scenario=0;scenario<5;++scenario){
    StaticRecompCore c;
    depth=resumed_inner=resumed_outer=0;limit=scenario==4?1:24;
    c.m_guest.pc=100;c.m_guest.downcount=-5;
    if(galaxypad_direct_transfer(&c.m_guest,100,104,inner)){
      ++resumed_outer;c.m_guest.downcount-=17;c.m_guest.pc=900;
    }
    c.finish();
    // Original dispatcher segments: 5,7,11,13,17. A denied nested boundary
    // stops after 11; exhausted depth yields at target200 after the 7 segment.
    const u64 expected=scenario==0?53:(scenario==4?12:23);
    assert(c.m_charged_cycles==expected);
    assert(c.m_guest.timebase==100+expected/12);
    assert(c.m_timebase_cycle_remainder==expected%12);
    assert(c.m_system.ppc.state.downcount==10000-int(expected));
    assert(!depth);
    assert(resumed_inner==(scenario==0)&&resumed_outer==(scenario==0));
    if(scenario==1){
      assert(c.m_guest.pc==104&&c.m_direct_must_yield);
      assert(c.m_direct_boundary_checks==3); // Outer matching104 stayed latched.
    }
    if(scenario==4)assert(c.m_guest.pc==200);
  }
  galaxypad_bind_direct_calls_v1(1,nullptr);
}
'''
program = program.replace('int main(){', nested + '\nint main(){\n  nested_tests();')
with tempfile.TemporaryDirectory(prefix='galaxypad-direct-boundary-') as directory:
    stage = Path(directory)
    (stage / 'test.cpp').write_text(program)
    binary = stage / 'test'
    extension = root / 'apple/experiments/guarded-direct-calls'
    binding = stage / 'binding.o'
    subprocess.run(['clang', '-std=c11', '-fsanitize=address,undefined',
                    '-c', str(extension / 'binding.c'), '-o', str(binding)], check=True)
    subprocess.run(['clang++', '-std=c++20', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', '-I', str(extension),
                    str(stage / 'test.cpp'), str(binding), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print('Actual boundary/transfer/binding and outer charge: nested unwind, depth, exceptions, cycles and timebase pass; full runtime integration pending')
