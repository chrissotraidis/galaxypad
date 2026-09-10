"""Private source-pinned cache IO adapter; leaves the vendor tree unchanged.

The caller MUST reserve Q31 after cache.Init, for split-lane IO scratch.
Single conversion hooks require the private AOT_EXACT_FP host mode.
"""
import hashlib
import re


def adapt(source):
    assert hashlib.sha256(source.encode()).hexdigest() == 'ddb545c1c708066ca19e46dad4fddf788e0ebd11604e5417df402e893c0b825a'
    prefix = r'''
#include "Core/PowerPC/JitArm64/JitArm64_RegCache.h"
#include "core/cpu.h"
#include <cassert>
using namespace Arm64Gen;
static void AotLoadFP(ARM64FloatEmitter* emit, unsigned size, ARM64Reg reg, size_t preg) {
  assert(reg!=ARM64Reg::Q31 && (size==64 || size==128) && preg<32);
  emit->LDR(64, IndexType::Unsigned, reg, ARM64Reg::X29, PPCSTATE_OFF_PS0(preg));
  if(size==128) {
    emit->LDR(64, IndexType::Unsigned, ARM64Reg::Q31, ARM64Reg::X29, PPCSTATE_OFF_PS1(preg));
    emit->INS(64, reg, 1, ARM64Reg::Q31, 0);
  }
}
static void AotStoreFP(ARM64FloatEmitter* emit, unsigned size, ARM64Reg reg, size_t preg) {
  assert(reg!=ARM64Reg::Q31 && (size==64 || size==128) && preg<32);
  emit->STR(64, IndexType::Unsigned, reg, ARM64Reg::X29, PPCSTATE_OFF_PS0(preg));
  if(size==128) {
    emit->DUP(64, ARM64Reg::Q31, reg, 1);
    emit->STR(64, IndexType::Unsigned, ARM64Reg::Q31, ARM64Reg::X29, PPCSTATE_OFF_PS1(preg));
  }
}
'''
    pattern = (r'm_float_emit->(LDR|STR)\((load_size|store_size|128|64), IndexType::Unsigned, '
               r'(host_reg|flush_reg), PPC_REG,\s*(?:static_cast<s32>|u32)\(PPCSTATE_OFF_PS0\(preg\)\)\);')
    def replace(match):
        op, size, reg = match.groups()
        return f'Aot{"Load" if op=="LDR" else "Store"}FP(m_float_emit.get(), {size}, {reg}, preg);'
    source, count = re.subn(pattern, replace, source)
    assert count == 5, count
    old = '''m_float_emit->STP(64, IndexType::Signed, host_reg, host_reg, PPC_REG,
                          static_cast<s32>(PPCSTATE_OFF_PS0(preg)));'''
    assert source.count(old) == 1
    source = source.replace(old, '''AotStoreFP(m_float_emit.get(), 64, host_reg, preg);
        m_float_emit->STR(64, IndexType::Unsigned, host_reg, PPC_REG, PPCSTATE_OFF_PS1(preg));''')
    return prefix + source
