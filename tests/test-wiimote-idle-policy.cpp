// SPDX-License-Identifier: GPL-3.0-or-later
#include "../apple/shared/GalaxyPadWiimoteIdlePolicy.h"
#include <cassert>
#include <cstdio>
#include <vector>
int main() {
  using namespace galaxypad::wiimote;
  constexpr auto offset=kSleepAddress-0x80000000u;
  constexpr auto code=kSetterAddress-0x80000000u;
  std::vector<std::uint8_t> ram(offset+2, 0xA5);
  for (std::size_t i=0;i<kSetterWords.size();++i)
    for (unsigned j=0;j<4;++j) ram[code+i*4+j]=kSetterWords[i]>>(24-j*8);
  for (std::uint8_t minutes : {5,15}) {
    ram[offset]=minutes;
    const auto before=ram;
    assert(DisableGuestAutoSleep(ram.data(),ram.size(),kSDA)==minutes);
    assert(ram[offset]==0);
    ram[offset]=minutes;
    assert(ram==before); // No other byte, including guest instructions, changed.
  }
  for (std::uint8_t minutes : {0,1,7,255}) {
    ram[offset]=minutes;
    assert(!DisableGuestAutoSleep(ram.data(),ram.size(),kSDA));
    assert(ram[offset]==minutes);
  }
  // Model repeated scene policy resets and the SDK's actual idle predicate.
  // This tests the policy; hardware acceptance still needs a real idle run.
  for (unsigned seconds=0;seconds<3600;++seconds) {
    if (seconds%600==0) ram[offset]=seconds%1200==0?5:15;
    DisableGuestAutoSleep(ram.data(),ram.size(),kSDA);
    const bool sdkWouldDisconnect=ram[offset]>0 && seconds>60u*ram[offset];
    assert(!sdkWouldDisconnect);
  }
  ram[offset]=5;
  assert(!DisableGuestAutoSleep(nullptr,ram.size(),kSDA));
  assert(!DisableGuestAutoSleep(ram.data(),offset,kSDA));
  assert(!DisableGuestAutoSleep(ram.data(),ram.size(),kSDA+4));
  for (std::size_t i=0;i<kSetterWords.size()*4;++i) {
    ram[code+i]^=1;
    assert(!DisableGuestAutoSleep(ram.data(),ram.size(),kSDA));
    assert(ram[offset]==5);
    ram[code+i]^=1;
  }
  puts("PASS: virtual Wiimote sleep policy, exact code/r13/bounds guards, only 5/15-minute data changes");
}
