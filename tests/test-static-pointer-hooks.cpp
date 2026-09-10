// SPDX-License-Identifier: GPL-3.0-or-later
// Exercise the actual pinned ModManager with dynamic modules disabled.
#include "moderngekko/mod_loader.hpp"
#include <cassert>
#include <cstring>
#include <iostream>
static unsigned entries=0, returns=0;
static uint32_t result=0;
static void entry(CPUState* state) { ++entries; state->gpr[3]=99; }
static void returned(CPUState* state) { ++returns; result=state->gpr[3]; state->gpr[3]=99; }
int main() {
  constexpr uint32_t query=0x803fb0ec;
  const ModernGekkoModHook hooks[]={RECOMP_HOOK(query,entry), RECOMP_HOOK_RETURN(query,returned)};
  ModernGekkoModDesc desc{};
  desc.abi_version=MODERNGEKKO_MOD_ABI_VERSION;
  desc.cpu_abi_version=MODERNGEKKO_CPU_ABI_VERSION;
  desc.cpu_state_size=sizeof(CPUState);
  std::strcpy(desc.game_id,"RMGE01");
  desc.id="galaxypad.pointer-probe"; desc.version="0.1.0"; desc.display_name="Pointer probe";
  desc.hooks=hooks; desc.num_hooks=2;
  moderngekko::ModManager manager;
  auto sources=std::vector{moderngekko::ModSource::AttachedDescriptor(&desc,"built-in")};
  assert(!manager.Load(sources,"GMSE01") && manager.Empty());
  ++desc.cpu_state_size;
  assert(!manager.Load(sources,"RMGE01") && manager.Empty());
  --desc.cpu_state_size;
  assert(manager.Load(sources,"RMGE01") && !manager.Empty());
  CPUState state{}; state.pc=query; state.lr=0x80178eb0; state.gpr[1]=0x81700000; state.gpr[3]=0x81144cc8;
  const CPUState original=state;
  assert(manager.HandlesAddress(query));
  assert(!manager.Dispatch(&state,query)); // observer does not replace guest query
  assert(entries==1 && std::memcmp(&state,&original,sizeof(state))==0);
  assert(manager.HandlesAddress(state.lr));
  state.pc=state.lr; state.gpr[3]=1; state.gpr[1]-=16;
  assert(!manager.Dispatch(&state,state.pc) && returns==0); // wrong stack cannot consume return
  state.gpr[1]+=16;
  const CPUState completed=state;
  assert(!manager.Dispatch(&state,state.pc));
  assert(returns==1 && result==1 && std::memcmp(&state,&completed,sizeof(state))==0);
  assert(!manager.HandlesAddress(state.pc));
  assert(!manager.Dispatch(&state,state.pc) && returns==1);
  state=original; assert(!manager.Dispatch(&state,query));
  manager.Unload();
  assert(manager.Empty() && !manager.HandlesAddress(original.lr));
  assert(!manager.Dispatch(&state,original.lr) && returns==1);
  std::cout << "Static pointer hooks: ABI/title rejection, observational entry/return, stack identity and unload pass\n";
}
