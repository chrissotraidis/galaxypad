// Private host for the unmodified reference register-cache implementation.
// This is not the runtime JIT and has no executable-memory/code-cache interface.
#pragma once
#include "Common/Arm64Emitter.h"
#include "Core/PowerPC/JitCommon/ConstantPropagation.h"
#include <cstdlib>
#ifdef AOT_EXACT_FP
#include "aot-exact-fp-conversion.h"
#endif
class JitArm64 : public Arm64Gen::ARM64XEmitter {
public:
  using ARM64XEmitter::ARM64XEmitter;
  JitCommon::ConstantPropagation& GetConstantPropagation() { return constants; }
  void ConvertSingleToDoublePair(size_t, Arm64Gen::ARM64Reg dest, Arm64Gen::ARM64Reg source,
                                Arm64Gen::ARM64Reg) {
#ifdef AOT_EXACT_FP
    AotWidenSingle(*this,dest,source,true);
#else
    std::abort();
#endif
  }
  void ConvertSingleToDoubleLower(size_t, Arm64Gen::ARM64Reg dest, Arm64Gen::ARM64Reg source,
                                 Arm64Gen::ARM64Reg) {
#ifdef AOT_EXACT_FP
    AotWidenSingle(*this,dest,source,false);
#else
    std::abort();
#endif
  }
  bool IsFPRStoreSafe(size_t) {
#ifdef AOT_EXACT_FP
    return false; // No offline precision proof supplied yet.
#else
    std::abort();
#endif
  }
private:
  JitCommon::ConstantPropagation constants;
};
