#include "../apple/shared/GalaxyPadNativeObserverBinding.h"
#include <cassert>
#include <iostream>
static unsigned attaches=0,detaches=0;
static bool accept=true;
static bool attach(uint32_t version,uint32_t size,GalaxyPadNativeObservation cb,void*) {
  assert(version==1 && size==3528);
  if(cb) ++attaches; else ++detaches;
  return accept;
}
static void observe(const CPUState*,uint32_t,void*) {}
int main() {
  uint32_t sites[]={0x803fb0ec,0x80178ec8};
  GalaxyPadNativeObserverAPI good{1,3,3528,"exact-test-hash",sites,2,attach};
  auto valid=[&](const GalaxyPadNativeObserverAPI* api) {
    return galaxypad::ValidNativeObserverAPI(api,3,3528,"exact-test-hash");
  };
  assert(valid(&good) && !valid(nullptr));
  for(unsigned i=0;i<7;++i) {
    auto bad=good;
    if(i==0) bad.version=2;
    if(i==1) bad.cpu_abi_version=4;
    if(i==2) bad.cpu_state_size=0;
    if(i==3) bad.dol_sha256="different";
    if(i==4) bad.site_count=1;
    if(i==5) bad.sites=nullptr;
    if(i==6) bad.attach=nullptr;
    assert(!valid(&bad));
  }
  sites[1]=sites[0]; assert(!valid(&good)); sites[1]=0x80178ec8;
  {
    galaxypad::NativeObserverBinding binding;
    assert(binding.bind(&good,3,3528,"exact-test-hash",observe,nullptr));
    assert(!binding.bind(nullptr,3,3528,"exact-test-hash",observe,nullptr));
    assert(attaches==1 && detaches==1); // invalid replacement clears old callback
    binding.reset(); assert(detaches==1);
    accept=false;
    assert(!binding.bind(&good,3,3528,"exact-test-hash",observe,nullptr));
    accept=true;
    assert(binding.bind(&good,3,3528,"exact-test-hash",observe,nullptr));
  }
  assert(detaches==2); // scope cleanup once, while module API is still alive
  std::cout<<"Observer binding: compatibility rejection, replacement and scope cleanup pass\n";
}
