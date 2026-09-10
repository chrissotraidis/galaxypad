"""Isolated eligibility test, not proof of integrated batching or hardware behavior."""
import ast
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
# Reuse the existing byte-method state stubs without executing its test module.
tree = ast.parse((root / 'tests/test-lc-byte-fast.py').read_text())
stub = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == 'stub' for t in n.targets))
stub = stub.replace('bool TryWriteLockedCacheByte(u32, u8);',
                    'bool TryWriteLockedCacheByte(u32, u8);\n u8* TryGetLockedCachePair(u32 address);')
assert 'TryGetLockedCachePair' in stub
stub = stub.replace('u32 GetL1CacheSize() { return bytes.size(); }',
                    'u32 size=0x4000; u32 GetL1CacheSize() { return size; }')
base = root / 'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC'
constants = '\n'.join(line for line in (base/'MMU.h').read_text().splitlines()
                      if line.startswith(('constexpr int BAT_INDEX', 'constexpr u32 BAT_')))
body = (base/'MMU_Tables.cpp').read_text().split('bool MMU::TryWriteLockedCacheByte', 1)[1].split('\ntemplate <', 1)[0]
candidate = (root/'patches/experiments/lc-pair-pointer.inc').read_text()
test = r'''
int main() {
  MMU m, reference; constexpr u32 base=0xe0000000, alias=0xe0020000;
  for (auto* x : {&m, &reference}) x->m_dbat_table[base >> BAT_INDEX_SHIFT]=base|3;
  for (u32 offset=0; offset<0x4000; ++offset) {
    auto* p=m.TryGetLockedCachePair(base+offset);
    assert((p != nullptr) == (offset < 0x3fff));
    if (p) assert(p == m.m_memory.bytes.data()+offset);
  }
  for (u32 value=0; value<65536; ++value) {
    for (u32 offset : {0u,1u,0x2a00u,0x3ffeu}) {
      auto* p=m.TryGetLockedCachePair(base+offset); assert(p);
      p[0]=value>>8; p[1]=value;
      assert(reference.TryWriteLockedCacheByte(base+offset,value>>8));
      assert(reference.TryWriteLockedCacheByte(base+offset+1,value));
      assert(p[0]==reference.m_memory.bytes[offset] && p[1]==reference.m_memory.bytes[offset+1]);
    }
  }
  assert(m.m_memory.bytes == reference.m_memory.bytes);
  auto unchanged=m.m_memory.bytes;
  for (u32 address : {base-1,base+0x3fff,base+0x4000,base+BAT_PAGE_SIZE-1,UINT32_MAX})
    assert(!m.TryGetLockedCachePair(address));
  m.m_power_pc.checks.on=true; assert(!m.TryGetLockedCachePair(base)); m.m_power_pc.checks.on=false;
  m.m_ppc_state.m_enable_dcache=true; assert(!m.TryGetLockedCachePair(base)); m.m_ppc_state.m_enable_dcache=false;
  StaticRecompLockstep::g_lc_write_journal=true; assert(!m.TryGetLockedCachePair(base));
  StaticRecompLockstep::g_lc_write_journal=false;
  StaticRecompLockstep::g_hw_write_sink=true; assert(!m.TryGetLockedCachePair(base));
  StaticRecompLockstep::g_hw_write_sink=false;
  m.m_memory.available=false; assert(!m.TryGetLockedCachePair(base)); m.m_memory.available=true;
  for (u32 flags : {0u,BAT_MAPPED_BIT,BAT_PHYSICAL_BIT}) {
    m.m_dbat_table[base >> BAT_INDEX_SHIFT]=base|flags;
    assert(!m.TryGetLockedCachePair(base));
  }
  m.m_dbat_table[alias >> BAT_INDEX_SHIFT]=base|3|BAT_WI_BIT;
  assert(m.TryGetLockedCachePair(alias+12)==m.m_memory.bytes.data()+12);
  m.m_dbat_table[alias >> BAT_INDEX_SHIFT]=0x10000000|3;
  assert(!m.TryGetLockedCachePair(alias+12));
  m.m_ppc_state.msr.DR=false;
  assert(m.TryGetLockedCachePair(base)==m.m_memory.bytes.data());
  assert(!m.TryGetLockedCachePair(alias));
  m.m_memory.size=0; assert(!m.TryGetLockedCachePair(base));
  m.m_memory.size=1; assert(!m.TryGetLockedCachePair(base));
  m.m_memory.size=2; assert(m.TryGetLockedCachePair(base));
  assert(!m.TryGetLockedCachePair(base+1));
  assert(m.m_memory.bytes==unchanged);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-lc-pair-') as directory:
    path = Path(directory)
    cpp = path/'probe.cpp'
    cpp.write_text('#include <cstdint>\nusing u32=uint32_t;\n' + constants + stub
                   + 'bool MMU::TryWriteLockedCacheByte' + body + candidate + test)
    subprocess.run(['clang++', '-std=c++20', '-O2', '-fsanitize=undefined,address',
                    str(cpp), '-o', str(path/'probe')], check=True)
    subprocess.run([str(path/'probe')], check=True)
print('Locked-cache pair eligibility, byte parity, guards and live remap tests passed')
