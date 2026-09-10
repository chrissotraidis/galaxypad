// Private offline lowering for paired-merge values and optional record update.
// Caller owns guest entry/availability/PC/cycle handling and must reserve Q30
// plus the split-lane cache adapter's Q31. No arithmetic or precision narrowing.
#pragma once
#include "Core/PowerPC/JitArm64/JitArm64_RegCache.h"
#include <cassert>
#include <optional>
#include "core/cpu.h"

struct AotPairedMerge {
  unsigned dest,a,b,lane_a,lane_b;
  bool record;
};

inline std::optional<AotPairedMerge> AotDecodePairedMerge(u32 word) {
  const unsigned xo=(word>>1)&1023;
  // PPCTables' exact opcode4 entries. Record forms additionally update CR1.
  if((word>>26)!=4 ||
     (xo!=528 && xo!=560 && xo!=592 && xo!=624)) return std::nullopt;
  const unsigned selector=(xo-528)/32;
  return AotPairedMerge{(word>>21)&31,(word>>16)&31,(word>>11)&31,
                       selector>>1,selector&1,bool(word&1)};
}

inline void AotRecordCR1(Arm64Gen::ARM64XEmitter& emit) {
  using namespace Arm64Gen;using enum ARM64Reg;
  // Preserve integer cache/caller values; none of these instructions sets NZCV.
  emit.STP(IndexType::Pre,X0,X1,SP,-16);
  emit.LDR(IndexType::Unsigned,W0,X29,offsetof(CPUState,cr));
  emit.LDR(IndexType::Unsigned,W1,X29,offsetof(CPUState,fpscr));
  emit.UBFX(W1,W1,28,4); // FX,FEX,VX,OX, in CR1 bit order.
  emit.BFI(W0,W1,24,4);
  emit.STR(IndexType::Unsigned,W0,X29,offsetof(CPUState,cr));
  emit.LDP(IndexType::Post,X0,X1,SP,16);
}

inline void AotMergePair(Arm64Gen::ARM64XEmitter& emit, Arm64FPRCache& cache,
                         unsigned dest, unsigned a, unsigned b,
                         unsigned lane_a, unsigned lane_b) {
  using namespace Arm64Gen;using enum ARM64Reg;
  assert(dest<32 && a<32 && b<32 && lane_a<2 && lane_b<2);
  ARM64FloatEmitter fp(&emit);
  // Capture A before acquiring B: cache allocation can spill/reuse A's host
  // register. Q31 is NOT suitable staging because split-lane IO overwrites it.
  const auto source_a=cache.R(a,RegType::Register);
  fp.DUP(64,Q30,source_a,lane_a);
  const auto source_b=cache.R(b,RegType::Register);
  fp.INS(64,Q30,1,source_b,lane_b);
  // Both old source lanes are now safe even when dest aliases either source
  // or acquiring the destination evicts a source register.
  fp.MOV(cache.RW(dest,RegType::Register),Q30);
}
