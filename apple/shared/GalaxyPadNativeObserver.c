// SPDX-License-Identifier: GPL-3.0-or-later
// Linked only into explicitly instrumented candidate modules, never the app.
#include "GalaxyPadNativeObserver.h"
#ifndef GALAXYPAD_OBSERVER_CPU_HEADER
#define GALAXYPAD_OBSERVER_CPU_HEADER "moderngekko/cpu_state.h"
#endif
#include GALAXYPAD_OBSERVER_CPU_HEADER
#ifndef GALAXYPAD_OBSERVER_CPU_ABI
#define GALAXYPAD_OBSERVER_CPU_ABI MODERNGEKKO_CPU_ABI_VERSION
#endif
static const uint32_t sites[]={0x803fb0ecu,0x80178ec8u};
static GalaxyPadNativeObservation callback;
static void* callback_user;
static bool attach(uint32_t version,uint32_t size,GalaxyPadNativeObservation next,void* user) {
  // Rejection also clears the previous observer; never retain stale ownership.
  callback=0; callback_user=0;
  if (version!=1 || size!=sizeof(CPUState)) return false;
  callback=next; callback_user=next?user:0;
  return true;
}
__attribute__((visibility("default")))
const GalaxyPadNativeObserverAPI* galaxypad_get_native_observer(void) {
  static const GalaxyPadNativeObserverAPI api={1,GALAXYPAD_OBSERVER_CPU_ABI,sizeof(CPUState),
    "2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09",
    sites,2,attach};
  return &api;
}
void galaxypad_native_observe(const CPUState* state,uint32_t site) {
  if (callback && state && (site==sites[0] || site==sites[1]))
    callback(state,site,callback_user);
}
