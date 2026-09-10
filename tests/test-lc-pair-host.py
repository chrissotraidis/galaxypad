"""Compile host callback prototype with deterministic host state stubs."""
from pathlib import Path
import os
import argparse
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--empty-rel', action='store_true', help='Test isolated empty-relocation-list guard')
args=parser.parse_args()
source=(root/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Hooks.cpp').read_text()
body='void* StaticRecompCore::HookExternalPointer'+source.split('void* StaticRecompCore::HookExternalPointer',1)[1].split('\nu32 StaticRecompCore::HookSPRRead',1)[0]
candidate=body.replace('  auto& memory = core->m_system.GetMemory();',
    (root/'patches/experiments/lc-pair-host.inc').read_text()+'  auto& memory = core->m_system.GetMemory();')
if '  if (size == 0)\n' in body:
    candidate=body  # Test the integrated callback directly during candidate build.
if args.empty_rel:
    anchor='    if (core->TranslateRelAddress(ea) != ea || core->TranslateRelAddress(ea + 1) != ea + 1)'
    replacement=('    if (!core->m_active_rel_sections.empty() &&\n'
        '        (core->TranslateRelAddress(ea) != ea || core->TranslateRelAddress(ea + 1) != ea + 1))')
    assert candidate.count(anchor)==1 or candidate.count(replacement)==1
    candidate=candidate.replace(anchor,replacement)
prefix=r'''
#include <cstdint>
#include <cstdlib>
#include <cassert>
#include <vector>
using u32=uint32_t; using u8=uint8_t;
constexpr u32 LOCKED_CACHE_BASE=0xe0000000;
struct CPUState { void* external_user_data; u32 msr; };
struct Memory { u8 bytes[16]{}; u8* GetL1Cache(){return bytes;} u32 GetL1CacheSize(){return 16;} };
struct MMU { unsigned calls=0; bool eligible=true; u8 bytes[2]{};
  u8* TryGetLockedCachePair(u32){++calls;return eligible?bytes:nullptr;} };
struct System {
  Memory memory; MMU mmu; struct { struct { u32 Hex=0; } msr; } ppc;
  Memory& GetMemory(){return memory;} MMU& GetMMU(){return mmu;}
  auto& GetPPCState(){return ppc;}
};
struct Verifier { bool m_ls_journaling=false; };
struct StaticRecompCore {
  System m_system; Verifier verifier; Verifier* m_lockstep_verifier=&verifier;
  u32 relocated=0;
  std::vector<u32> m_active_rel_sections;
  unsigned translations=0;
  u32 TranslateRelAddress(u32 x){++translations;return x==relocated?x+16:x;}
  static void* HookExternalPointer(CPUState*,u32,u32);
};
'''
test=r'''
int main(int argc,char** argv) {
  StaticRecompCore core; CPUState cpu{&core,0};
  bool expected=argv[1][0]=='1'; constexpr u32 ea=0xe0000000;
  auto result=core.HookExternalPointer(&cpu,ea,0);
  assert((result!=nullptr)==expected);
  assert(core.m_system.mmu.calls==(expected?1u:0u));
#ifdef EMPTY_REL
  assert(core.translations==0);
#endif
  // Legacy positive-size behavior stays unchanged regardless of opt-in.
  assert(core.HookExternalPointer(&cpu,ea,2)==core.m_system.memory.bytes);
  if(!expected) return 0;
  auto reject=[&] {
    unsigned before=core.m_system.mmu.calls;
    assert(!core.HookExternalPointer(&cpu,ea,0));
    assert(core.m_system.mmu.calls==before && core.m_system.ppc.msr.Hex==0);
  };
  cpu.msr=1;reject();cpu.msr=0;
  core.verifier.m_ls_journaling=true;reject();core.verifier.m_ls_journaling=false;
  core.m_active_rel_sections.push_back(ea);
  core.relocated=ea;reject();core.relocated=ea+1;reject();core.relocated=0;
  // Nonempty lists that do not match must still perform both lookups.
  unsigned before=core.translations;
  assert(core.HookExternalPointer(&cpu,ea,0));
  assert(core.translations==before+2);
  core.m_active_rel_sections.clear();
  assert(!core.HookExternalPointer(&cpu,0x80000000,0));
  core.m_system.mmu.eligible=false;
  assert(!core.HookExternalPointer(&cpu,ea,0));
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-pair-host-') as directory:
    path=Path(directory); cpp=path/'probe.cpp'
    cpp.write_text(prefix+candidate+test)
    flags=['-DEMPTY_REL'] if args.empty_rel else []
    subprocess.run(['clang++',*flags,'-std=c++20','-O2','-fsanitize=address,undefined',str(cpp),'-o',str(path/'probe')],check=True)
    for setting,trace,expected in [(None,None,False),('0',None,False),('true',None,False),
                                  ('10',None,False),('1',None,True),('1','1',False),('1','0',True)]:
        env=dict(os.environ)
        for key,value in [('GALAXYPAD_LC_PAIR_FAST',setting),('GALAXYPAD_PIXEL_STORE_TRACE',trace)]:
            if value is None: env.pop(key,None)
            else: env[key]=value
        subprocess.run([str(path/'probe'),'1' if expected else '0'],env=env,check=True)
print('Pair host exact opt-in, trace exclusion, MSR/journal/relocation rejection and legacy path passed')
