// Private FP cache binding. Requires adapt-arm64-fpr-cache.py's split-lane IO.
#pragma once
#include "aot-cpu-gpr-layout.h"
#undef PPCSTATE_OFF_PS0
#undef PPCSTATE_OFF_PS1
#define PPCSTATE_OFF_PS0(i) (offsetof(CPUState,fpr)+sizeof(f64)*(i))
#define PPCSTATE_OFF_PS1(i) (offsetof(CPUState,ps1)+sizeof(f64)*(i))
static_assert(sizeof(CPUState::fpr)==32*sizeof(f64));
static_assert(sizeof(CPUState::ps1)==32*sizeof(f64));
static_assert(offsetof(CPUState,ps1)!=offsetof(CPUState,fpr)+sizeof(f64));
