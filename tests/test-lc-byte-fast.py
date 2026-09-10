"""Compile the actual candidate MMU method against deterministic state stubs."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
base = root / "ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC"
source = (base / "MMU_Tables.cpp").read_text()
body = source.split("bool MMU::TryWriteLockedCacheByte", 1)[1].split("\ntemplate <", 1)[0]
constants = "\n".join(line for line in (base / "MMU.h").read_text().splitlines()
                      if line.startswith(("constexpr int BAT_INDEX", "constexpr u32 BAT_")))
stub = r'''
#include <array>
#include <cassert>
#include <cstdint>
#include <bit>
#include <cstring>
using u8=uint8_t; using u32=uint32_t;
namespace StaticRecompLockstep { bool g_lc_write_journal=false, g_hw_write_sink=false; }
struct Checks { bool on=false; bool HasAny() { return on; } };
struct PC { Checks checks; Checks& GetMemChecks() { return checks; } };
struct State { bool m_enable_dcache=false; struct { bool DR=true; } msr; };
struct Memory {
  std::array<u8, 0x4000> bytes{}; bool available=true;
  u8* GetL1Cache() { return available ? bytes.data() : nullptr; }
  u32 GetL1CacheSize() { return bytes.size(); }
};
struct MMU {
  PC m_power_pc; State m_ppc_state; Memory m_memory;
  std::array<u32, BAT_PAGE_COUNT> m_dbat_table{};
  bool TryWriteLockedCacheByte(u32, u8);
};
'''
test = r'''
int main() {
  MMU m; constexpr u32 base=0xE0000000;
  m.m_dbat_table[base >> BAT_INDEX_SHIFT]=base|BAT_MAPPED_BIT|BAT_PHYSICAL_BIT;
  for (unsigned value=0; value<256; ++value)
    for (u32 offset : {0u,1u,0x2a00u,0x3fffu}) {
      assert(m.TryWriteLockedCacheByte(base+offset, value));
      assert(m.m_memory.bytes[offset]==value);
    }
  auto original=m.m_memory.bytes;
  auto rejected=[&](u32 address) {
    assert(!m.TryWriteLockedCacheByte(address, 123));
    assert(m.m_memory.bytes==original);
  };
  rejected(base+0x4000); rejected(base-1); rejected(0xffffffff);
  m.m_memory.available=false; rejected(base); m.m_memory.available=true;
  m.m_power_pc.checks.on=true; rejected(base); m.m_power_pc.checks.on=false;
  m.m_ppc_state.m_enable_dcache=true; rejected(base); m.m_ppc_state.m_enable_dcache=false;
  StaticRecompLockstep::g_lc_write_journal=true; rejected(base);
  StaticRecompLockstep::g_lc_write_journal=false;
  StaticRecompLockstep::g_hw_write_sink=true; rejected(base);
  StaticRecompLockstep::g_hw_write_sink=false;
  for (u32 flags : {0u, BAT_MAPPED_BIT, BAT_PHYSICAL_BIT}) {
    m.m_dbat_table[base >> BAT_INDEX_SHIFT]=base|flags; rejected(base);
  }
  m.m_dbat_table[base >> BAT_INDEX_SHIFT]=0x10000000|3; rejected(base);
  // A changed mapping is read immediately, not cached.
  m.m_dbat_table[base >> BAT_INDEX_SHIFT]=base|3;
  assert(m.TryWriteLockedCacheByte(base,42));
  m.m_dbat_table[base >> BAT_INDEX_SHIFT]=0;
  m.m_ppc_state.msr.DR=false;
  assert(m.TryWriteLockedCacheByte(base+1,43));
  assert(m.m_memory.bytes[0]==42 && m.m_memory.bytes[1]==43);
  // Differential against the canonical byte-store rotation/byte-swap/memcpy
  // expression, over every offset and byte value in the test cache.
  m.m_ppc_state.msr.DR=true;
  m.m_dbat_table[base >> BAT_INDEX_SHIFT]=base|3|BAT_WI_BIT;
  std::array<u8,0x4000> reference{};
  for (unsigned value=0; value<256; ++value) {
    for (u32 offset=0; offset<reference.size(); ++offset) {
      const u32 data=value, size=1;
      const u32 swapped_data=__builtin_bswap32(std::rotr(data, size*8));
      std::memcpy(reference.data()+offset, &swapped_data, size);
      assert(m.TryWriteLockedCacheByte(base+offset, value));
    }
    assert(m.m_memory.bytes==reference);
  }
  // Distinct effective BAT page maps to the same physical cache; then is
  // remapped away. The method must use live translation, not effective bits.
  constexpr u32 alias=0xE0020000;
  m.m_dbat_table[alias >> BAT_INDEX_SHIFT]=base|3;
  assert(m.TryWriteLockedCacheByte(alias+123, 99));
  assert(m.m_memory.bytes[123]==99);
  m.m_dbat_table[alias >> BAT_INDEX_SHIFT]=0x10000000|3;
  assert(!m.TryWriteLockedCacheByte(alias+123, 88));
  assert(m.m_memory.bytes[123]==99);
}
'''
assert "Common::swap32(std::rotr(data, size * 8))" in source
assert "std::memcpy(&m_memory.GetL1Cache()[em_address & 0x0FFFFFFF], &swapped_data, size)" in source
with tempfile.TemporaryDirectory() as directory:
    cpp = Path(directory) / "test.cpp"
    binary = Path(directory) / "test"
    cpp.write_text("#include <cstdint>\nusing u32=uint32_t;\n" + constants + stub
                   + "bool MMU::TryWriteLockedCacheByte" + body + test)
    subprocess.run(["clang++", "-std=c++20", "-fsanitize=undefined,address", str(cpp), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print("Locked-cache byte candidate guard/value/boundary tests passed")
