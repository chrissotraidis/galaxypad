#!/usr/bin/env python3
"""Stage an ABI-preserving 32-byte chunk-eligibility LUT experiment; never build.

32-byte entries are selected only when both RAM sizes and every chunk endpoint
are aligned. Otherwise the original 4-byte table remains. No generated guest
memory, SMC verification policy, class layout, or selected artifact is changed.
"""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import shlex

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp'
PINS = {'StaticRecompCore_Run.cpp':'bbfb1f7976a50fdd44c04f3f3e6997812c07e877eef3ca0ce092f5a78ecd04b6',
        'StaticRecompCore_SMC.cpp':'47668b0d92b04899b8f3ce141465e17e153bc50a2321265ec7bce4048e1d3f23'}
SHIFT = '''  // The initialized table has one entry per 32 bytes only when every
  // chunk/RAM boundary supports it; other modules retain 4-byte entries.
  const bool coarse_lookup = m_chunk_lookup_table.size() ==
                             ((m_lookup_ram_size + m_lookup_exram_size) >> 5);
  const u32 lookup_shift = coarse_lookup ? 5 : 2;
'''
INIT_OLD = '''  u32 total_instructions = (ram_size + exram_size) >> 2;
  m_chunk_lookup_table.assign(total_instructions, -1);'''
INIT_NEW = '''  u32 boundary_bits = ram_size | exram_size;
  for (u32 i = 0; i < m_module->num_chunk_ranges; ++i)
    boundary_bits |= m_module->chunk_ranges[i].start | m_module->chunk_ranges[i].end;
  const u32 lookup_shift = (boundary_bits & 31u) == 0 ? 5 : 2;
  const u32 total_entries = (ram_size + exram_size) >> lookup_shift;
  m_chunk_lookup_table.assign(total_entries, -1);'''


def function(text, signature):
    start=text.index(signature); i=text.index('{',start)+1; depth=1
    while depth:
        depth+=(text[i]=='{')-(text[i]=='}'); i+=1
    return text[start:i]+'\n'


def stage(sources):
    result=dict(sources)
    smc=result['StaticRecompCore_SMC.cpp']
    old=function(smc,'int StaticRecompCore::GetAddressLookupIndex(')
    new=old.replace('{\n','{\n'+SHIFT,1).replace('>> 2','>> lookup_shift')
    assert smc.count(INIT_OLD)==1
    result['StaticRecompCore_SMC.cpp']=smc.replace(old,new).replace(INIT_OLD,INIT_NEW)
    run=result['StaticRecompCore_Run.cpp']
    begin=run.index('  const auto fast_dispatchable_at = [this](u32 address) {')
    end=run.index('\n  };',begin)+6
    old=run[begin:end]
    assert old.count('>> 2')==3
    new=SHIFT+old.replace('[this]','[this, lookup_shift]').replace('>> 2','>> lookup_shift')
    result['StaticRecompCore_Run.cpp']=run.replace(old,new)
    return result


PREAMBLE = r'''
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>
using u32=uint32_t;
struct Range { u32 start,end; };
struct Module { u32 num_chunk_ranges; const Range* chunk_ranges; };
'''
CLASS = r'''
struct StaticRecompCore {
 Module* m_module=nullptr;
 u32 m_lookup_ram_size=0,m_lookup_exram_size=0;
 std::vector<int> m_chunk_lookup_table;
 int GetAddressLookupIndex(u32) const;
 void InitLookupTable(u32,u32);
 int Lookup(u32 pc) const {
  int index=GetAddressLookupIndex(pc);
  return index>=0 && index<int(m_chunk_lookup_table.size())?m_chunk_lookup_table[index]:-1;
 }
 bool Verified(u32 pc,const std::vector<bool>& valid)const {
  int index=Lookup(pc);return index>=0 && valid[index];
 }
};
'''
DRIVER = r'''
int main() {
 unsigned comparisons=0,scenarios=0;
 for (u32 ram:{64,128,256})for(u32 exram:{0,64,128}) {
  std::vector<std::vector<Range>> cases={
   {}, {{0x80000000,0x80000020}},
   {{0x80000020,0x80000040},{0x90000000,0x90000020}},
   {{0x80000000,0x80000020},{0x80000040,0x80000060}},
   {{0x80000000,0x80000040},{0x80000020,0x80000040}},
   {{0x80000004,0x80000024}}, {{0x80000000,0x80000024}},
   {{0x80000020,0x80000024},{0x80000024,0x80000040}},
   {{0x80000000+ram-32,0x80000000+ram}},
  };
  for(auto ranges:cases) {
   Module mod{u32(ranges.size()),ranges.data()};
   control::StaticRecompCore a;candidate::StaticRecompCore b;
   a.m_module=b.m_module=&mod;a.InitLookupTable(ram,exram);b.InitLookupTable(ram,exram);
   u32 bits=ram|exram;for(auto r:ranges)bits|=r.start|r.end;
   assert(b.m_chunk_lookup_table.size()==((ram+exram)>>((bits&31)?2:5)));
   std::vector<bool> valid(ranges.size(),true);
   for(unsigned change=0;change<=ranges.size();++change) {
    if(change)valid[change-1]=false;
    for(u32 base:{0u,0x7fffffc0u,0x80000000u,0x80000100u,0x8fffffc0u,0x90000000u,0xc0000000u})
     for(u32 off=0;off<320;++off) {
      assert(a.Lookup(base+off)==b.Lookup(base+off));
      assert(a.Verified(base+off,valid)==b.Verified(base+off,valid));++comparisons;
     }
   }
   auto before=b.m_chunk_lookup_table;b.InitLookupTable(ram,exram);assert(before==b.m_chunk_lookup_table);
   ++scenarios;
  }
 }
 // A RAM endpoint that needs four-byte granularity retains the old allocation.
 for(u32 ram:{68,132}) {
  Range range{0x80000020,0x80000040};Module mod{1,&range};
  control::StaticRecompCore a;candidate::StaticRecompCore b;a.m_module=b.m_module=&mod;
  a.InitLookupTable(ram,64);b.InitLookupTable(ram,64);
  assert(a.m_chunk_lookup_table==b.m_chunk_lookup_table);
 }
 std::cout<<"PASS "<<scenarios<<" scenarios, "<<comparisons<<" byte-address and live-invalidation comparisons\n";
}
'''


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--compile-db',type=Path,default=ROOT/'generated/build/ios-simulator-core/compile_commands.json')
    args=p.parse_args();out=args.output.resolve()
    if out.exists():p.error('Output exists; preserve prior evidence')
    sources={}
    for name,digest in PINS.items():
        data=(SOURCE/name).read_bytes()
        if hashlib.sha256(data).hexdigest()!=digest:p.error('Canonical source changed: '+name)
        sources[name]=data.decode()
    changed=stage(sources);out.mkdir(parents=True)
    patch=[]
    for name,text in changed.items():
        (out/name).write_text(text)
        patch.extend(difflib.unified_diff(sources[name].splitlines(True),text.splitlines(True),
                     fromfile='a/'+name,tofile='b/'+name))
    (out/'coarse-lut.patch').write_text(''.join(patch))
    fixture=PREAMBLE
    for label,text in [('control',sources['StaticRecompCore_SMC.cpp']),('candidate',changed['StaticRecompCore_SMC.cpp'])]:
        fixture+='namespace '+label+' {\n'+CLASS
        fixture+=function(text,'int StaticRecompCore::GetAddressLookupIndex(')
        fixture+=function(text,'void StaticRecompCore::InitLookupTable(')+'}\n'
    (out/'test-coarse-lut.cpp').write_text(fixture+DRIVER)
    commands=[]
    for e in json.loads(args.compile_db.read_text()):
        name=Path(e['file']).name
        if name not in changed:continue
        argv=shlex.split(e['command']);argv[argv.index('-c')+1]=str(out/name)
        argv[argv.index('-o')+1]=str(out/(name+'.o'))
        # Shadow objects retain the original symbol names and class ABI.
        commands.append({'cwd':e['directory'],'argv':argv,'source':name})
    assert len(commands)==2
    manifest={'status':'prepared; no compilation or link performed','source_sha256':PINS,
              'compile_commands':commands,
              'test_command':['clang++','-std=c++20','-O2','-fsanitize=address,undefined',
                              str(out/'test-coarse-lut.cpp'),'-o',str(out/'test-coarse-lut')],
              'integration':'Link both replacement objects before the unchanged libGalaxyPadCore.a; do not combine with ABI/layout experiments. Class layout and symbols unchanged. Keep original sources/objects/archive intact.'}
    overlay = {'version':0,'roots':[{'type':'file','name':str(SOURCE/name),'external-contents':str(out/name)} for name in changed]}
    (out/'host-overlay.json').write_text(json.dumps(overlay,indent=2)+'\n')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(out/'manifest.json')


if __name__=='__main__':main()
