// Private paired multiply/FMA lowering for the split-lane resident cache.
// FP-only region owns X0-X7/NZCV and Q24-Q31 as scratch; caller allocates
// 16 stack bytes at SP+144. No integer cache may retain values in that set.
// ABI preservation belongs to the outer static region, not each operation.
#pragma once
#include "Core/PowerPC/JitArm64/JitArm64_RegCache.h"
#include "core/cpu.h"
#include <optional>

inline void AotMultiplyPair(Arm64Gen::ARM64XEmitter& e, Arm64FPRCache& cache,
                            unsigned dest,unsigned a,unsigned c,
                            int b=-1,bool subtract=false,bool negative=false,
                            int c_lane=-1,int sum_lane=-1,bool scalar=false) {
  using namespace Arm64Gen;using enum ARM64Reg;
  ARM64FloatEmitter fp(&e);
  const bool fused=b>=0 && sum_lane<0;
  std::optional<FixupBranch> invalid_gate;
  if(scalar) fp.MOV(Q27,cache.R(dest,RegType::Register));
  // Capture operands before another cache acquisition can evict either source.
  fp.MOV(Q28,cache.R(a,RegType::Register));
  fp.MOV(Q29,cache.R(c,RegType::Register));
  if(b>=0) fp.MOV(Q27,cache.R(unsigned(b),RegType::Register));
  if(sum_lane==1) fp.MOV(Q26,Q28); // Passthrough low lane must not destroy A0.
  for(unsigned lane=0;lane<(scalar?1u:2u);++lane) {
    const unsigned selected=c_lane<0?lane:unsigned(c_lane);
    if(sum_lane>=0 && lane!=unsigned(sum_lane)) {
      fp.UMOV(64,X2,Q29,lane);
    } else {
    fp.UMOV(64,X0,Q28,lane);fp.UMOV(64,X1,Q29,selected);
    if(sum_lane>=0) {fp.UMOV(64,X0,sum_lane==1?Q26:Q28,0);fp.UMOV(64,X1,Q27,1);}
    e.MOVI2R(W6,0);
    // Exact force_25bit_c, including arithmetic mask shift for subnormals.
    if(sum_lane<0) {
    e.MOVI2R(X2,0xfffffffff8000000ull);e.MOVI2R(X3,0x8000000ull);
    e.UBFX(X4,X1,52,11);auto normal=e.CBNZ(X4);
    e.UBFX(X4,X1,0,52);auto zero=e.CBZ(X4);
    e.CLZ(X5,X4);e.SUB(X5,X5,11u);
    e.ASRV(X2,X2,X5);e.LSRV(X3,X3,X5);
    e.SetJumpTarget(normal);e.SetJumpTarget(zero);
    e.AND(X2,X1,X2);e.AND(X3,X1,X3);e.ADD(X1,X2,X3);
    }
    if(sum_lane>=0) {
      fp.FMOV(D30,X0);fp.FMOV(D31,X1);fp.FADD(D31,D30,D31);
    } else if(!fused) {
      fp.FMOV(D30,X0);fp.FMOV(D31,X1);fp.FMUL(D31,D30,D31);
    } else {
      fp.FMOV(D24,X0);fp.FMOV(D25,X1);fp.UMOV(64,X3,Q27,lane);fp.FMOV(D26,X3);
      if(subtract) fp.FNEG(D26,D26);
      fp.FMADD(D31,D24,D25,D26);
      // ni_madd_msub single-result halfway correction before f32 rounding.
      fp.FMOV(X2,D31);e.UBFX(X3,X2,0,29);e.MOVI2R(X4,0x10000000ull);e.CMP(X3,X4);
      auto not_tie=e.B(CCFlags::CC_NEQ);
      fp.FSUB(D30,D26,D31); // a_prime
      fp.FADD(D26,D31,D30); // b_prime
      fp.FMADD(D30,D24,D25,D30); // delta_a
      fp.UMOV(64,X3,Q27,lane);fp.FMOV(D24,X3);if(subtract) fp.FNEG(D24,D24);
      fp.FSUB(D24,D24,D26);fp.FADD(D30,D30,D24); // error
      fp.FCMP(D30);auto exact=e.B(CCFlags::CC_EQ);
      e.CSET(W3,CCFlags::CC_GT);fp.FCMP(D31);e.CSET(W4,CCFlags::CC_GT);e.CMP(W3,W4);
      auto smaller=e.B(CCFlags::CC_NEQ);
      e.ADD(X2,X2,1u);auto corrected=e.B();
      e.SetJumpTarget(smaller);e.SUB(X2,X2,1u);e.SetJumpTarget(corrected);fp.FMOV(D31,X2);
      e.SetJumpTarget(exact);e.SetJumpTarget(not_tie);
      // NaN precedence and exception tests use original C, not rounded C.
      fp.UMOV(64,X1,Q29,selected);
    }
    fp.FCMP(D31,D31); // Match actual helper's result classification FP effects.
    fp.FMOV(X2,D31);
    // NaN exception/precedence path shared by multiplication and FMA.
    e.UBFX(X3,X2,52,11);e.CMP(X3,2047u);auto finite=e.B(CCFlags::CC_NEQ);
    e.UBFX(X3,X2,0,52);auto infinity=e.CBZ(X3);
    e.MOVI2R(W6,0);
    auto snan=[&](ARM64Reg value) {
      e.UBFX(X3,value,52,11);e.CMP(X3,2047u);auto not_special=e.B(CCFlags::CC_NEQ);
      e.UBFX(X3,value,0,52);auto no_fraction=e.CBZ(X3);
      e.UBFX(X3,value,51,1);auto quiet=e.CBNZ(X3);
      e.MOVI2R(W6,0x01000000u);
      e.SetJumpTarget(not_special);e.SetJumpTarget(no_fraction);e.SetJumpTarget(quiet);
    };
    snan(X0);snan(X1);
    if(fused) {fp.UMOV(64,X5,Q27,lane);snan(X5);}
    auto exception=[&] {
      e.LDR(IndexType::Unsigned,W3,X29,offsetof(CPUState,fpscr));
      e.AND(W4,W3,W6);e.CMP(W4,W6);auto already=e.B(CCFlags::CC_EQ);
      e.MOVI2R(W4,0x80000000u);e.ORR(W3,W3,W4);e.SetJumpTarget(already);
      e.ORR(W3,W3,W6);
      // ppc_fpscr_updated: recompute VX and FEX from all exception bits.
      e.MOVI2R(W4,0x01f80700u);e.AND(W4,W3,W4);
      e.MOVI2R(W5,0x9fffffffu);e.AND(W3,W3,W5);
      auto no_vx=e.CBZ(W4);e.MOVI2R(W5,0x20000000u);e.ORR(W3,W3,W5);e.SetJumpTarget(no_vx);
      e.LSR(W4,W3,22);e.AND(W4,W4,W3);e.MOVI2R(W5,0xf8u);e.AND(W4,W4,W5);
      auto no_fex=e.CBZ(W4);e.MOVI2R(W5,0x40000000u);e.ORR(W3,W3,W5);e.SetJumpTarget(no_fex);
      e.STR(IndexType::Unsigned,W3,X29,offsetof(CPUState,fpscr));
    };
    auto no_snan=e.CBZ(W6);exception();e.SetJumpTarget(no_snan);
    e.LDR(IndexType::Unsigned,W3,X29,offsetof(CPUState,fpscr));
    e.MOVI2R(W4,0xfff9ffffu);e.AND(W3,W3,W4);
    e.STR(IndexType::Unsigned,W3,X29,offsetof(CPUState,fpscr));
    auto nan_value=[&](ARM64Reg input) {
      e.UBFX(X3,input,52,11);e.CMP(X3,2047u);auto not_special=e.B(CCFlags::CC_NEQ);
      e.UBFX(X3,input,0,52);auto not_nan=e.CBZ(X3);
      e.MOVI2R(X3,0x0008000000000000ull);e.ORR(X2,input,X3);
      auto done=e.B();e.SetJumpTarget(not_special);e.SetJumpTarget(not_nan);return done;
    };
    auto a_nan=nan_value(X0);
    std::optional<FixupBranch> b_nan;
    if(fused) {fp.UMOV(64,X5,Q27,lane);b_nan=nan_value(X5);}
    auto c_nan=nan_value(X1);
    e.MOVI2R(W6,sum_lane>=0?0x00800000u:0x00100000u);
    if(fused) {
      fp.FMOV(D24,X0);fp.FMOV(D25,X1);fp.FMUL(D24,D24,D25);fp.FCMP(D24,D24);
      auto invalid_multiply=e.B(CCFlags::CC_VS);
      e.MOVI2R(W6,0x00800000u);e.SetJumpTarget(invalid_multiply);
    }
    exception();e.MOVI2R(X2,0x7ff8000000000000ull);
    e.SetJumpTarget(a_nan);e.SetJumpTarget(c_nan);
    if(b_nan) e.SetJumpTarget(*b_nan);
    auto nan_done=e.B();
    e.SetJumpTarget(finite);e.SetJumpTarget(infinity);
    if(fused || sum_lane>=0) {
      // Non-NaN FMA clears FI/FR if any original operand is infinite.
      auto clear_if_inf=[&](ARM64Reg value) {
        e.UBFX(X3,value,0,63);e.MOVI2R(X4,0x7ff0000000000000ull);e.CMP(X3,X4);
        auto not_inf=e.B(CCFlags::CC_NEQ);
        e.LDR(IndexType::Unsigned,W3,X29,offsetof(CPUState,fpscr));
        e.MOVI2R(W4,0xfff9ffffu);e.AND(W3,W3,W4);
        e.STR(IndexType::Unsigned,W3,X29,offsetof(CPUState,fpscr));e.SetJumpTarget(not_inf);
      };
      clear_if_inf(X0);clear_if_inf(X1);
      if(fused) {fp.UMOV(64,X5,Q27,lane);clear_if_inf(X5);}
    }
    e.SetJumpTarget(nan_done);
    }
    if(scalar) {
      e.LDR(IndexType::Unsigned,W3,X29,offsetof(CPUState,fpscr));
      e.UBFX(W3,W3,7,1);auto not_gated=e.CBZ(W3);
      invalid_gate=e.CBNZ(W6);e.SetJumpTarget(not_gated);
    }
    // The pinned helper's optimized code converts unconditionally before its
    // NI result selection. Preserve that conversion's raw FPSR effects too.
    const bool passthrough=sum_lane>=0 && lane!=unsigned(sum_lane);
    if(!passthrough) {fp.FMOV(D31,X2);fp.FCVT(32,64,S31,D31);}
    e.LDR(IndexType::Unsigned,W3,X29,offsetof(CPUState,fpscr));
    e.UBFX(W3,W3,2,1);auto gradual=e.CBZ(W3);
    e.UBFX(X3,X2,0,63);e.MOVI2R(X4,0x3810000000000000ull);e.CMP(X3,X4);
    auto not_tiny=e.B(CCFlags::CC_CS);
    e.LSR(X3,X2,32);e.MOVI2R(W4,0x80000000u);e.AND(W3,W3,W4);
    fp.FMOV(S31,W3);
    std::optional<FixupBranch> flushed;
    if(passthrough) flushed=e.B();
    e.SetJumpTarget(gradual);e.SetJumpTarget(not_tiny);
    if(passthrough) {
      // Unlike arithmetic-result selection, the pinned sum helper branches
      // around conversion of a flushed passthrough lane.
      fp.FMOV(D31,X2);fp.FCVT(32,64,S31,D31);e.SetJumpTarget(*flushed);
    }
    if(negative) {
      fp.FCMP(S31,S31);auto is_nan=e.B(CCFlags::CC_VS);
      fp.FNEG(S31,S31);e.SetJumpTarget(is_nan);
    }
    // Keep the low-lane binary32 bits for final FPRF classification.
    fp.FMOV(W6,S31);fp.FCVT(64,32,D31,S31);
    fp.FMOV(X2,D31);
    if(lane==unsigned(sum_lane<0?0:sum_lane)) {
      e.STR(IndexType::Unsigned,W6,SP,144);
    }
    fp.INS(64,Q28,lane,X2);
    if(scalar) fp.INS(64,Q28,1,X2);
  }
  e.LDR(IndexType::Unsigned,W0,SP,144);
  e.UBFX(W1,W0,23,8);e.UBFX(W2,W0,0,23);e.LSR(W3,W0,31);
  e.MOVI2R(W4,4u);auto positive=e.CBZ(W3);e.MOVI2R(W4,8u);e.SetJumpTarget(positive);
  auto nonzero_exp=e.CBNZ(W1);
  e.MOVI2R(W4,0x14u);auto positive_small=e.CBZ(W3);e.MOVI2R(W4,0x18u);e.SetJumpTarget(positive_small);
  auto subnormal=e.CBNZ(W2);
  e.MOVI2R(W4,2u);auto positive_zero=e.CBZ(W3);e.MOVI2R(W4,0x12u);e.SetJumpTarget(positive_zero);
  e.SetJumpTarget(subnormal);auto classified=e.B();e.SetJumpTarget(nonzero_exp);
  e.CMP(W1,255u);auto ordinary=e.B(CCFlags::CC_NEQ);
  e.MOVI2R(W4,0x11u);auto nan=e.CBNZ(W2);
  e.MOVI2R(W4,5u);auto positive_inf=e.CBZ(W3);e.MOVI2R(W4,9u);e.SetJumpTarget(positive_inf);
  e.SetJumpTarget(nan);e.SetJumpTarget(ordinary);e.SetJumpTarget(classified);
  e.LDR(IndexType::Unsigned,W0,X29,offsetof(CPUState,fpscr));
  e.BFI(W0,W4,12,5);e.STR(IndexType::Unsigned,W0,X29,offsetof(CPUState,fpscr));
  if(scalar) {
    e.MOVI2R(W1,0xfff9ffffu);e.AND(W0,W0,W1);
    e.STR(IndexType::Unsigned,W0,X29,offsetof(CPUState,fpscr));
    auto committed=e.B();e.SetJumpTarget(*invalid_gate);fp.MOV(Q28,Q27);e.SetJumpTarget(committed);
  }
  fp.MOV(cache.RW(dest,RegType::Register),Q28);
}
