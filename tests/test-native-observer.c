#include "moderngekko/cpu_state.h"
#include "../apple/shared/GalaxyPadNativeObserver.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
static void observe(const CPUState* state,uint32_t site,void* user) {
  assert(state->gpr[3]==42 && site==0x803fb0ec);
  ++*(unsigned*)user;
}
int main(void) {
  const GalaxyPadNativeObserverAPI* api=galaxypad_get_native_observer();
  assert(api->version==1 && api->cpu_abi_version==MODERNGEKKO_CPU_ABI_VERSION);
  assert(api->cpu_state_size==sizeof(CPUState) && api->site_count==2);
  assert(api->sites[0]==0x803fb0ec && api->sites[1]==0x80178ec8);
  assert(strcmp(api->dol_sha256,"2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09")==0);
  CPUState state={0}; state.gpr[3]=42; CPUState original=state;
  unsigned count=0;
  galaxypad_native_observe(&state,api->sites[0]); assert(count==0);
  assert(api->attach(1,sizeof(state),observe,&count));
  galaxypad_native_observe(&state,api->sites[0]); assert(count==1);
  assert(memcmp(&state,&original,sizeof(state))==0);
  galaxypad_native_observe(&state,0x80000000); assert(count==1);
  galaxypad_native_observe(0,api->sites[0]); assert(count==1);
  assert(!api->attach(2,sizeof(state),observe,&count));
  galaxypad_native_observe(&state,api->sites[0]); assert(count==1);
  assert(!api->attach(1,sizeof(state)-1,observe,&count));
  assert(api->attach(1,sizeof(state),observe,&count));
  assert(api->attach(1,sizeof(state),0,0));
  galaxypad_native_observe(&state,api->sites[0]); assert(count==1);
  puts("Native observer bridge: identity, ABI/size, site filter, rejection and detach pass");
}
