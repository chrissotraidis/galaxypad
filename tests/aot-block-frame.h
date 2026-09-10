#pragma once
#include "Core/PowerPC/PowerPC.h"
#include "core/cpu.h"
#include <array>
#include <cstddef>
#include <cstring>
// Byte layout only: never construct/copy the reference state's owning caches.
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Winvalid-offsetof"
constexpr size_t aot_gpr_offset=__builtin_offsetof(PowerPC::PowerPCState,gpr);
#pragma clang diagnostic pop
struct AotBlockFrame {
  alignas(PowerPC::PowerPCState) std::array<unsigned char,sizeof(PowerPC::PowerPCState)> layout{};
  CPUState* guest;
  void ImportGPRs() { std::memcpy(layout.data()+aot_gpr_offset,guest->gpr,sizeof(guest->gpr)); }
  void ExportGPRs() { std::memcpy(guest->gpr,layout.data()+aot_gpr_offset,sizeof(guest->gpr)); }
};
static_assert(offsetof(AotBlockFrame,layout)==0);
