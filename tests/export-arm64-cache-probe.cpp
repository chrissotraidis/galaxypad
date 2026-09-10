// GPR cache/callback boundary prerequisite; no PPC decoder or FP lowering yet.
#include "Core/PowerPC/JitArm64/Jit.h"
#include "Core/PowerPC/JitArm64/JitArm64_RegCache.h"
#include "Common/MsgHandler.h"
#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
namespace Common {
bool MsgAlertFmtImpl(bool, MsgType, Log::LogType, const char* file, int line,
                     fmt::string_view, const fmt::format_args&) {
  std::fprintf(stderr, "Emitter/cache assertion: %s:%d\n", file, line);
  std::abort();
}
}
int main() {
  using namespace Arm64Gen;
  using enum ARM64Reg;
  alignas(16) std::array<u8, 4096> storage{};
  JitArm64 emit(storage.data(), storage.data()+storage.size());
  // Reference cache uses callee-saved registers; preserve the full GPR set here.
  emit.STP(IndexType::Pre, X29, X30, SP, -96);
  for (int reg=19; reg<=27; reg+=2)
    emit.STP(IndexType::Signed, static_cast<ARM64Reg>(static_cast<int>(X0)+reg),
             static_cast<ARM64Reg>(static_cast<int>(X0)+reg+1), SP, 16+(reg-19)*8);
  emit.MOV(X29, X0);
  Arm64GPRCache cache;
  cache.Init(&emit);
  auto add = [&](size_t dest, size_t a, size_t b) {
    auto left=cache.R(a), right=cache.R(b);
    cache.BindToRegister(dest, false);
    emit.ADD(cache.R(dest), left, right);
  };
  add(3,3,4);
  add(7,3,6);
  cache.Flush(FlushMode::All, INVALID_REG);
  emit.MOV(X0, X29);
  auto helper_offset=emit.GetCodePtr()-storage.data();
  auto branch=emit.BL();
  emit.SetJumpTarget(branch);
  // Flush(All) invalidates cache bindings; callback-modified values must reload.
  add(5,3,6);
  cache.Flush(FlushMode::All, INVALID_REG);
  for (int reg=19; reg<=27; reg+=2)
    emit.LDP(IndexType::Signed, static_cast<ARM64Reg>(static_cast<int>(X0)+reg),
             static_cast<ARM64Reg>(static_cast<int>(X0)+reg+1), SP, 16+(reg-19)*8);
  emit.LDP(IndexType::Post, X29, X30, SP, 96);
  emit.RET();
  if(emit.HasWriteFailed()) return 1;
  std::puts(".text\n.p2align 2\n.globl _galaxypad_aot_cache_probe\n_galaxypad_aot_cache_probe:");
  for(std::ptrdiff_t offset=0;offset<emit.GetCodePtr()-storage.data();offset+=4) {
    if(offset==helper_offset) std::puts("  bl _galaxypad_aot_cache_callback");
    else { u32 word;std::memcpy(&word,storage.data()+offset,4);std::printf("  .long 0x%08x\n",word); }
  }
}
