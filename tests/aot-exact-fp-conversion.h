// Offline integer-only IEEE binary32 widening. No FPCR/FPSR dependence,
// executable allocation, helper addresses or runtime precision assumptions.
#pragma once
#include "Common/Arm64Emitter.h"
inline void AotWidenSingle(Arm64Gen::ARM64XEmitter& e, Arm64Gen::ARM64Reg dest,
                           Arm64Gen::ARM64Reg source, bool pair) {
  using namespace Arm64Gen;using enum ARM64Reg;
  ARM64FloatEmitter fp(&e);
  e.STP(IndexType::Pre,X0,X1,SP,-64);
  e.STP(IndexType::Signed,X2,X3,SP,16);
  e.STP(IndexType::Signed,X4,X5,SP,32);
  e.STP(IndexType::Signed,X6,X7,SP,48);
  e.MRS(X5,PStateField::NZCV);
  // Capture both packed inputs before writing an aliased destination.
  fp.UMOV(64,X6,source,0);e.MOV(W0,W6);
  auto widen=[&] {
    e.UBFX(W2,W0,23,8);e.UBFX(W3,W0,0,23);
    auto zero_exp=e.CBZ(W2);
    e.CMP(W2,255u);auto special=e.B(CCFlags::CC_EQ);
    e.ADD(W2,W2,896u);auto join_normal=e.B();
    e.SetJumpTarget(special);e.MOVI2R(W2,2047);auto join_special=e.B();
    e.SetJumpTarget(zero_exp);auto zero=e.CBZ(W3);
    e.CLZ(W4,W3);e.SUB(W4,W4,8u);e.LSLV(W3,W3,W4);
    e.UBFX(W3,W3,0,23);e.MOVI2R(W2,897);e.SUB(W2,W2,W4);
    e.SetJumpTarget(zero);e.SetJumpTarget(join_normal);e.SetJumpTarget(join_special);
    e.UBFX(X1,X0,31,1);e.LSL(X1,X1,63);
    e.LSL(X2,X2,52);e.ORR(X1,X1,X2);
    e.LSL(X3,X3,29);e.ORR(X1,X1,X3);
  };
  widen();fp.FMOV(EncodeRegToDouble(dest),X1);
  if(pair) {
    e.LSR(X0,X6,32);widen();fp.INS(64,dest,1,X1);
  }
  e._MSR(PStateField::NZCV,X5);
  e.LDP(IndexType::Signed,X2,X3,SP,16);
  e.LDP(IndexType::Signed,X4,X5,SP,32);
  e.LDP(IndexType::Signed,X6,X7,SP,48);
  e.LDP(IndexType::Post,X0,X1,SP,64);
}
