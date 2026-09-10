// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "GalaxyPadNativeObserver.h"
#include <cstring>
namespace galaxypad {
// Trusted, already validated module memory. This is compatibility checking,
// not a sandbox for an arbitrary malicious dynamic library.
inline bool ValidNativeObserverAPI(const GalaxyPadNativeObserverAPI* api,
                                  uint32_t cpuABI,uint32_t cpuSize,const char* dolHash) {
  return api && api->version==1 && api->cpu_abi_version==cpuABI &&
    api->cpu_state_size==cpuSize && api->dol_sha256 && dolHash &&
    std::strcmp(api->dol_sha256,dolHash)==0 && api->site_count==2 && api->sites &&
    api->sites[0]==0x803fb0ec && api->sites[1]==0x80178ec8 && api->attach;
}
// Own only the registration, not the library. Destroy/reset after CPU stop,
// before closing the library. No copy/move can duplicate callback ownership.
class NativeObserverBinding {
public:
  NativeObserverBinding()=default;
  NativeObserverBinding(const NativeObserverBinding&)=delete;
  NativeObserverBinding& operator=(const NativeObserverBinding&)=delete;
  ~NativeObserverBinding() { reset(); }
  bool bind(const GalaxyPadNativeObserverAPI* api,uint32_t cpuABI,uint32_t cpuSize,
            const char* dolHash,GalaxyPadNativeObservation callback,void* user) {
    reset();
    if (!callback || !ValidNativeObserverAPI(api,cpuABI,cpuSize,dolHash)) return false;
    if (!api->attach(1,cpuSize,callback,user)) return false;
    api_=api;
    return true;
  }
  void reset() {
    if (!api_) return;
    api_->attach(1,api_->cpu_state_size,nullptr,nullptr);
    api_=nullptr;
  }
private:
  const GalaxyPadNativeObserverAPI* api_=nullptr;
};
} // namespace galaxypad
