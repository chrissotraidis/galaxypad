"""Check the empty-list guard against the actual relocation resolver."""
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
source=(root/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_SMC.cpp').read_text()
start=source.index('bool StaticRecompCore::ResolveRuntimeAddress(')
end=source.index('int StaticRecompCore::GetAddressLookupIndex(', start)
methods=source[start:end]
program=r'''
#include <cassert>
#include <cstdint>
#include <vector>
#include <cstdio>
using u32=uint32_t;using u64=uint64_t;
struct ActiveRelSection {u32 linked_start,runtime_start,size;};
struct StaticRecompCore {
 std::vector<ActiveRelSection> m_active_rel_sections;
 bool ResolveRuntimeAddress(u32,u32*) const;
 u32 TranslateRelAddress(u32);
};
'''+methods+r'''
int main() {
 StaticRecompCore core;unsigned checks=0;
 auto compare=[&](u32 ea) {
  bool original=core.TranslateRelAddress(ea)!=ea || core.TranslateRelAddress(ea+1)!=ea+1;
  bool candidate=!core.m_active_rel_sections.empty() &&
      (core.TranslateRelAddress(ea)!=ea || core.TranslateRelAddress(ea+1)!=ea+1);
  assert(original==candidate);++checks;
 };
 for(unsigned mode=0;mode<5;mode++) {
  core.m_active_rel_sections.clear();
  if(mode) core.m_active_rel_sections.push_back({0xe0000010u,0x80000000u,mode==1?0u:32u});
  if(mode==3) core.m_active_rel_sections.push_back({0xe0000000u,0xe0000000u,128u});
  if(mode==4) core.m_active_rel_sections.push_back({0xffffffffu,0x80000000u,2u});
  for(u32 offset=0;offset<1024;offset++) compare(0xe0000000u+offset);
  compare(0xffffffffu);compare(0xfffffffeu);compare(0);
 }
 // Clear/repopulate: no cached eligibility survives a relocation-list change.
 core.m_active_rel_sections.clear();compare(0xe0000000u);
 core.m_active_rel_sections.push_back({0xe0000000u,0x80000000u,1});compare(0xe0000000u);
 core.m_active_rel_sections.clear();compare(0xe0000000u);
 printf("%u actual-resolver comparisons passed: empty/nonempty/overlap/boundary/wrap/list changes\n",checks);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-rel-empty-') as directory:
    temp=Path(directory)
    (temp/'test.cpp').write_text(program)
    subprocess.run(['clang++','-std=c++20','-O2','-fsanitize=address,undefined',
                    str(temp/'test.cpp'),'-o',str(temp/'test')],check=True)
    subprocess.run([str(temp/'test')],check=True)
