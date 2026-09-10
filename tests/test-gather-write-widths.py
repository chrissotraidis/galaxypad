"""Source-derived AOT gather writes and actual burst/spill logic; no runtime edits."""
from pathlib import Path
import re
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
base=root/'ref/ModernGekko/vendor/dolphin/Source/Core'
gp=(base/'Core/HW/GPFifo.cpp').read_text()
hooks=(base/'Core/PowerPC/StaticRecomp/StaticRecompCore_Hooks.cpp').read_text()
def function(text, signature):
    start=text.index(signature);brace=text.index('{',start);end=brace+1;depth=1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[brace:end]
names=['UpdateGatherPipe','FastWrite8','FastWrite16','FastWrite32','FastWrite64']
methods=[]
for name in names:
    signature=re.search(r'void GPFifoManager::'+name+r'\([^)]*\)',gp)[0]
    methods.append(signature.replace('GPFifoManager::','')+function(gp,signature))
hook=function(hooks,'void StaticRecompCore::HookExternalWrite(')
switch=hook[hook.index('    switch (size)'):hook.index('\n  core->PropagateGuestMSR();')]
assert switch.rstrip().endswith('}')
switch=switch.rstrip()[:-1] # remove enclosing gather-page branch only
program=r'''
#include <cassert>
#include <cstdint>
#include <cstring>
#include <vector>
#include <cstdio>
#include <initializer_list>
using u8=uint8_t;using u16=uint16_t;using u32=uint32_t;using u64=uint64_t;
namespace Common {u16 swap16(u16 v){return __builtin_bswap16(v);}u32 swap32(u32 v){return __builtin_bswap32(v);}u64 swap64(u64 v){return __builtin_bswap64(v);}}
struct Memory {
 std::vector<u8> bytes;std::vector<u32> addresses;
 void CopyToEmu(u32 address,const u8* data,size_t size){assert(size==32);addresses.push_back(address);bytes.insert(bytes.end(),data,data+size);}
};
struct PI {u32 m_fifo_cpu_write_pointer=0x1000,m_fifo_cpu_base=0x1000,m_fifo_cpu_end=0x1020;};
struct CP {unsigned bursts=0;void GatherPipeBursted(){bursts++;}};
struct State {u8* gather_pipe_ptr;};
struct System {
 Memory memory;PI pi;CP cp;State state;
 auto& GetMemory(){return memory;}auto& GetProcessorInterface(){return pi;}
 auto& GetCommandProcessor(){return cp;}auto& GetPPCState(){return state;}
};
struct Pipe {
 static constexpr size_t GATHER_PIPE_SIZE=32;
 u8 storage[128];u8* m_gather_pipe=storage+32;System m_system;
 Pipe(){memset(storage,0xa5,sizeof storage);m_system.state.gather_pipe_ptr=m_gather_pipe;}
 size_t GetGatherPipeCount(){return m_system.state.gather_pipe_ptr-m_gather_pipe;}
 void SetGatherPipeCount(size_t n){m_system.state.gather_pipe_ptr=m_gather_pipe+n;}
 METHODS
 void Check(){if(GetGatherPipeCount()>=32)UpdateGatherPipe();}
 void Write8(u8 v){FastWrite8(v);Check();}void Write16(u16 v){FastWrite16(v);Check();}
 void Write32(u32 v){FastWrite32(v);Check();}void Write64(u64 v){FastWrite64(v);Check();}
 void aot(u64 value,u8 size){auto& gpfifo=*this;SWITCH}
};
int main(){
 unsigned cases=0;u64 seed=771;
 for(unsigned residual=0;residual<32;residual++)for(unsigned width:{1u,2u,4u,8u})
 for(unsigned pattern=0;pattern<256;pattern++){
   Pipe a,b;std::vector<u8> expected;
   for(unsigned i=0;i<residual;i++){a.Write8(i);b.Write8(i);expected.push_back(i);}
   for(unsigned write=0;write<40;write++){
     seed^=seed<<13;seed^=seed>>7;seed^=seed<<17;
     a.aot(seed,width);
     switch(width){case 1:b.Write8(seed);break;case 2:b.Write16(seed);break;case 4:b.Write32(seed);break;case 8:b.Write64(seed);break;}
     for(unsigned byte=width;byte;byte--)expected.push_back(seed>>((byte-1)*8));
     assert(a.GetGatherPipeCount()==expected.size()%32 && a.GetGatherPipeCount()==b.GetGatherPipeCount());
     assert(a.m_system.memory.bytes==b.m_system.memory.bytes);
     assert(a.m_system.memory.addresses==b.m_system.memory.addresses);
     assert(a.m_system.cp.bursts==expected.size()/32 && b.m_system.cp.bursts==a.m_system.cp.bursts);
     assert(!memcmp(a.m_gather_pipe,b.m_gather_pipe,a.GetGatherPipeCount()));
     for(unsigned i=0;i<32;i++)assert(a.storage[i]==0xa5 && a.storage[96+i]==0xa5 && b.storage[i]==0xa5 && b.storage[96+i]==0xa5);
   }
   auto actual=a.m_system.memory.bytes;actual.insert(actual.end(),a.m_gather_pipe,a.m_gather_pipe+a.GetGatherPipeCount());assert(actual==expected);
   for(unsigned i=0;i<a.m_system.memory.addresses.size();i++)assert(a.m_system.memory.addresses[i]==0x1000+(i%2)*32);
   cases++;
 }
 printf("%u width/residual/value sequences pass; byte order, spill, burst count and FIFO wrap agree\n",cases);
}
'''.replace('METHODS','\n'.join(methods)).replace('SWITCH',switch)
with tempfile.TemporaryDirectory(prefix='galaxypad-gather-widths-') as directory:
    cpp=Path(directory)/'test.cpp';binary=Path(directory)/'test';cpp.write_text(program)
    subprocess.run(['clang++','-std=c++20','-O2','-fsanitize=address,undefined',str(cpp),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
print('Memory/CP are stubs: no concurrent GPU, MMU translation, display-list or live producer proof.')
