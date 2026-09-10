"""Actual non-deterministic FIFO append/compaction, not a concurrency oracle."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root/'ref/ModernGekko/vendor/dolphin/Source/Core/VideoCommon/Fifo.cpp').read_text()
method = source.split('void FifoManager::ReadDataFromFifo(u32 read_ptr)', 1)[1].split(
    '// The deterministic_gpu_thread version.', 1)[0]
assert method.strip().endswith('}')
program = r'''
#include <cassert>
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <stdexcept>
using u8=uint8_t;using u32=uint32_t;
namespace GPFifo {constexpr size_t GATHER_PIPE_SIZE=32;}
template<class... T> void PanicAlertFmt(const char*,T...) {throw std::runtime_error("bounds");}
struct Memory {
 u8 burst[32];unsigned copies=0;
 void CopyFromEmu(u8* dest,u32 address,size_t size) {
   assert(address==0x123400 && size==32);memcpy(dest,burst,size);copies++;
 }
};
struct System {Memory memory;Memory& GetMemory(){return memory;}};
struct FifoManager {
 static constexpr size_t FIFO_SIZE=256;
 u8 storage[FIFO_SIZE+64];u8* m_video_buffer=storage+32;
 u8* m_video_buffer_read_ptr=m_video_buffer;
 u8* m_video_buffer_write_ptr=m_video_buffer;
 System m_system;
 void ReadDataFromFifo(u32 read_ptr) METHOD
};
int main() {
 unsigned cases=0;
 for(unsigned consumed=0;consumed<=256;consumed++)
 for(unsigned pending=0;pending<=256-consumed;pending++) {
   FifoManager f;memset(f.storage,0xa5,sizeof f.storage);
   for(unsigned i=0;i<256;i++)f.m_video_buffer[i]=u8(i*37+11);
   for(unsigned i=0;i<32;i++)f.m_system.memory.burst[i]=u8(i*19+7);
   f.m_video_buffer_read_ptr=f.m_video_buffer+consumed;
   f.m_video_buffer_write_ptr=f.m_video_buffer+consumed+pending;
   u8 expected[288];memcpy(expected,f.m_video_buffer_read_ptr,pending);
   memcpy(expected+pending,f.m_system.memory.burst,32);
   bool rejected=false;
   try {f.ReadDataFromFifo(0x123400);}catch(const std::runtime_error&){rejected=true;}
   assert(rejected==(pending+32>256));
   if(!rejected) {
     assert(f.m_system.memory.copies==1);
     assert(f.m_video_buffer_write_ptr-f.m_video_buffer_read_ptr==pending+32);
     assert(!memcmp(f.m_video_buffer_read_ptr,expected,pending+32));
     assert(f.m_video_buffer_read_ptr==f.m_video_buffer+(consumed+pending+32>256?0:consumed));
   } else {assert(!f.m_system.memory.copies);assert(!memcmp(f.m_video_buffer_read_ptr,expected,pending));}
   for(unsigned i=0;i<32;i++)assert(f.storage[i]==0xa5 && f.storage[288+i]==0xa5);
   cases++;
 }
 // R742 boundary shape, with and without compaction. Preserve invalid input;
 // the append routine must not silently repair or drop the two-byte prefix.
 for(unsigned consumed: {0u,254u}) {
   FifoManager f;f.m_video_buffer_read_ptr=f.m_video_buffer+consumed;
   f.m_video_buffer_write_ptr=f.m_video_buffer_read_ptr+2;
   f.m_video_buffer_read_ptr[0]=0x10;f.m_video_buffer_read_ptr[1]=0;
   memset(f.m_system.memory.burst,0,32);
   for(unsigned i=0;i<6;i++){f.m_system.memory.burst[i*5]=0x61;f.m_system.memory.burst[i*5+1]=0x16+i;}
   f.ReadDataFromFifo(0x123400);
   assert(f.m_video_buffer_write_ptr-f.m_video_buffer_read_ptr==34);
   assert(f.m_video_buffer_read_ptr[0]==0x10 && f.m_video_buffer_read_ptr[1]==0);
   assert(!memcmp(f.m_video_buffer_read_ptr+2,f.m_system.memory.burst,32));
 }
 printf("%u FIFO occupancy/compaction cases and2 residual-prefix cases pass\n",cases);
}
'''.replace('METHOD', method).replace('#include <cassert>', '#include <cassert>\n#include <initializer_list>')
with tempfile.TemporaryDirectory(prefix='galaxypad-fifo-compaction-') as directory:
    cpp=Path(directory)/'test.cpp';binary=Path(directory)/'test'
    cpp.write_text(program)
    subprocess.run(['clang++','-std=c++20','-O2','-fsanitize=address,undefined',
                    str(cpp),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
print('Actual append/compaction with stub CopyFromEmu; no producer, DMA or concurrency proof.')
