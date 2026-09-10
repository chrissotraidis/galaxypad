#include "moderngekko/mod_loader.hpp"
#include <cassert>
#include <chrono>
#include <cstdio>
#include <cstring>

static unsigned returns;
static unsigned starts;
static void started(CPUState *s) { ++starts; s->gpr[3]=123; }
static void patch(CPUState *s) { s->pc=s->lr; }
static void returning(CPUState *) { ++returns; }
int main() {
  const ModernGekkoModPatch patches[]={RECOMP_PATCH(0x80452398,patch)};
  const ModernGekkoModHook hooks[]={RECOMP_HOOK_RETURN(0x80453000,returning)};
  const ModernGekkoModCallback callbacks[]={RECOMP_CALLBACK("*","runtime_start",started)};
  ModernGekkoModDesc desc{};
  desc.abi_version=MODERNGEKKO_MOD_ABI_VERSION;
  desc.cpu_abi_version=MODERNGEKKO_CPU_ABI_VERSION;
  desc.cpu_state_size=sizeof(CPUState);std::memcpy(desc.game_id,"TEST01",7);
  desc.id="lookup_test";desc.version="1.0.0";desc.display_name="Lookup test";
  desc.patches=patches;desc.num_patches=1;desc.hooks=hooks;desc.num_hooks=1;
  desc.callbacks=callbacks;desc.num_callbacks=1;
  moderngekko::ModManager manager; // Descriptors must outlive their manager.
  assert(manager.Load({moderngekko::ModSource::AttachedDescriptor(&desc)},"TEST01"));
  assert(!manager.Dispatch(nullptr,0)); assert(starts==0);
  CPUState first{}; first.gpr[3]=7;
  assert(!manager.Dispatch(&first,0)); assert(starts==1 && first.gpr[3]==7);
  for(auto a:{0u,0xffffffffu,0x80452394u,0x8045239cu,0x80453004u})
    assert(!manager.Dispatch(&first,a));
  assert(starts==1);
  first.lr=0x80001000;
  assert(manager.Dispatch(&first,0x80452398)); assert(first.pc==first.lr);
  assert(manager.HandlesAddress(0x80452398));
  assert(manager.HandlesAddress(0x80453000));
  for(auto a:{0u,0xffffffffu,0x80452394u,0x8045239cu,0x80452ffcu,0x80453004u})
    assert(!manager.HandlesAddress(a));
  for(auto lr:{0u,0x80000100u,0x90001000u,0xfffffffcu}) {
    CPUState s{};s.lr=lr;s.gpr[1]=0x81700000;
    assert(!manager.Dispatch(&s,0x80453000));
    assert(manager.HandlesAddress(lr));
    s.gpr[1]-=16;
    assert(!manager.Dispatch(&s,lr)); assert(manager.HandlesAddress(lr));
    s.gpr[1]+=16;
    assert(!manager.Dispatch(&s,lr));
    assert(!manager.HandlesAddress(lr));
  }
  assert(returns==4);
  // Calls remain out of line; no LTO. Lookup microbenchmark, not game FPS.
  auto start=std::chrono::steady_clock::now();
  unsigned hits=0;
  for(unsigned i=0;i<20000000;i++)hits+=manager.HandlesAddress(0x80000000+(i%0x100000)*4);
  auto elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  assert(hits==0);std::printf("negative_lookups=20000000 seconds=%.6f\n",elapsed);
  manager.Unload();assert(!manager.HandlesAddress(0x80452398));
  assert(manager.Load({moderngekko::ModSource::AttachedDescriptor(&desc)},"TEST01"));
  assert(manager.HandlesAddress(0x80452398));
  assert(!manager.Dispatch(&first,0)); assert(starts==2);
}
