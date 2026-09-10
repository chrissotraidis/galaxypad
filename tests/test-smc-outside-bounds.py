"""Compare actual invalidation body with an unselected bounds shortcut."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_SMC.cpp').read_text()
body = source.split('void StaticRecompCore::OnICacheInvalidate(u32 address, u32 length)', 1)[1].strip()
# This method is currently last in the file; fail rather than silently truncate.
assert body.startswith('{') and body.endswith('}')
candidate = body.replace('  // Binary search to find',
    (root/'patches/experiments/smc-outside-bounds.inc').read_text()+'  // Binary search to find', 1)
assert candidate != body
prefix = r'''
#include <cstdint>
#include <vector>
#include <cassert>
using u32=uint32_t;
enum { CHUNK_UNVERIFIED, CHUNK_VERIFIED, CHUNK_FAILED };
struct Range { u32 start,end; };
struct Module { u32 num_chunk_ranges; std::vector<Range> chunk_ranges; };
struct Fallback {
  unsigned calls=0; u32 address=0,length=0;
  Fallback* GetBlockCache(){return this;}
  void InvalidateICache(u32 a,u32 n,bool){++calls;address=a;length=n;}
};
struct Core {
  Fallback* m_fallback_jit=nullptr; bool m_module_active=true; Module* m_module;
  std::vector<int> m_chunk_state; unsigned m_failed_chunks=0,m_reverify_events=0;
  unsigned resolves=0; u32 relocation=0;
  void ResolveNativeAddress(u32 a,u32* out,void*){++resolves;*out=a+relocation;}
  void reference(u32,u32); void candidate(u32,u32);
};
'''
test = r'''
int main() {
  uint64_t seed=17;
  auto random=[&](){seed^=seed<<13;seed^=seed>>7;seed^=seed<<17;return u32(seed);};
  for(unsigned trial=0;trial<200000;++trial) {
    Module m; m.num_chunk_ranges=trial%33;
    u32 pos=0x80000000;
    for(unsigned i=0;i<m.num_chunk_ranges;++i) {
      pos+=random()%64; u32 end=pos+4+random()%8192;
      m.chunk_ranges.push_back({pos,end});pos=end;
    }
    Core a,b; Fallback fa,fb;
    a.m_module=&m; a.m_module_active=trial%7!=0;
    a.relocation=trial%3?0:0x100;
    for(unsigned i=0;i<m.num_chunk_ranges;++i) {
      int state=random()%3; a.m_chunk_state.push_back(state);
      a.m_failed_chunks+=state==CHUNK_FAILED;
    }
    b=a;
    if(trial%2){a.m_fallback_jit=&fa;b.m_fallback_jit=&fb;}
    u32 address=trial%2 ? 0x7fffffe0+random()%200000 : random();
    u32 length=trial%5 ? random()%8192 : random();
    if(trial%11==0)length=0;
    a.reference(address,length);b.candidate(address,length);
    assert(a.m_chunk_state==b.m_chunk_state);
    assert(a.m_failed_chunks==b.m_failed_chunks && a.m_reverify_events==b.m_reverify_events);
    assert(a.resolves==b.resolves);
    assert(fa.calls==fb.calls && fa.address==fb.address && fa.length==fb.length);
  }
}
'''
with tempfile.TemporaryDirectory() as tmp:
    tmp=Path(tmp); cpp=tmp/'test.cpp'
    cpp.write_text(prefix+'void Core::reference(u32 address,u32 length)'+body+
        '\nvoid Core::candidate(u32 address,u32 length)'+candidate+test)
    subprocess.run(['clang++','-std=c++17','-O2','-fsanitize=address,undefined',str(cpp),'-o',str(tmp/'test')],check=True)
    subprocess.run([str(tmp/'test')],check=True)
print('SMC bounds prototype matches actual invalidation state and callback effects')
