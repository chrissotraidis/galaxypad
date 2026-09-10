#include "Core/PowerPC/PowerPC.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <array>
#include <cstddef>
// Reference CPU state owns noncopyable caches. Test its compiled byte offsets
// without fabricating/copying a C++ PowerPCState or constructing an emulator.
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Winvalid-offsetof"
static constexpr auto gpr_offset = __builtin_offsetof(PowerPC::PowerPCState, gpr);
#pragma clang diagnostic pop
using Registers = std::array<u32,32>;
extern "C" void galaxypad_aot_cache_probe(void*);
static unsigned callbacks;
static u32 expected3, expected7;
extern "C" void galaxypad_aot_cache_callback(void* state) {
  Registers registers;
  auto* address=static_cast<unsigned char*>(state)+gpr_offset;
  std::memcpy(registers.data(),address,sizeof(registers));
  assert(registers[3]==expected3 && registers[7]==expected7);
  for(unsigned i=0;i<32;++i) registers[i]^=0x9e3779b9u*(i+1);
  std::memcpy(address,registers.data(),sizeof(registers));
  ++callbacks;
}
int main() {
  alignas(PowerPC::PowerPCState) std::array<unsigned char,sizeof(PowerPC::PowerPCState)> actual;
  actual.fill(0xa5);
  auto expected=actual;
  Registers registers;
  u32 random=795;
  for(unsigned iteration=0;iteration<100000;++iteration) {
    for(auto& reg:registers) {
      random^=random<<13;random^=random>>17;random^=random<<5;reg=random;
    }
    std::memcpy(actual.data()+gpr_offset,registers.data(),sizeof(registers));
    expected=actual;
    expected3=registers[3]+=registers[4];
    expected7=registers[7]=registers[3]+registers[6];
    for(unsigned i=0;i<32;++i) registers[i]^=0x9e3779b9u*(i+1);
    registers[5]=registers[3]+registers[6];
    std::memcpy(expected.data()+gpr_offset,registers.data(),sizeof(registers));
    galaxypad_aot_cache_probe(actual.data());
    assert(actual==expected);
  }
  assert(callbacks==100000);
  std::puts("100000 reference GPR-cache flush/callback/reload byte-layout comparisons passed");
}
