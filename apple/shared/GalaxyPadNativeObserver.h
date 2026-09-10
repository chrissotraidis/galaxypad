// SPDX-License-Identifier: GPL-3.0-or-later
// Optional GalaxyPad module extension, independent of ModManager replacements.
#pragma once
#include <stdbool.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
struct CPUState;
typedef void (*GalaxyPadNativeObservation)(const struct CPUState*, uint32_t site, void* user);
typedef struct GalaxyPadNativeObserverAPI {
  uint32_t version, cpu_abi_version, cpu_state_size;
  const char* dol_sha256;
  const uint32_t* sites;
  uint32_t site_count;
  // Attach/detach only while the emulation CPU is stopped. Callback/user must
  // outlive the session; detach after CPU stop and before unloading the module.
  bool (*attach)(uint32_t version, uint32_t cpu_size, GalaxyPadNativeObservation, void* user);
} GalaxyPadNativeObserverAPI;
#define GALAXYPAD_NATIVE_OBSERVER_SYMBOL "galaxypad_get_native_observer"
typedef const GalaxyPadNativeObserverAPI* (*GalaxyPadGetNativeObserver)(void);
const GalaxyPadNativeObserverAPI* galaxypad_get_native_observer(void);
void galaxypad_native_observe(const struct CPUState*, uint32_t site);
#ifdef __cplusplus
}
#endif
