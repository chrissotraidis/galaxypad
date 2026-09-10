// Private integer-only layout binding for the reference GPR allocator.
// CR/FP layouts remain reference layouts and MUST NOT be emitted in this mode.
#pragma once
#include "Core/PowerPC/JitArm64/JitArm64_RegCache.h"
#include "core/cpu.h"
#include <cstddef>
#undef PPCSTATE_OFF_GPR
#define PPCSTATE_OFF_GPR(i) (offsetof(CPUState,gpr)+sizeof(u32)*(i))
static_assert(sizeof(CPUState::gpr)==32*sizeof(u32));
