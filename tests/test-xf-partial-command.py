"""Exercise the actual XF case on truncated/refilled input, with callback stubs."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root/'ref/ModernGekko/vendor/dolphin/Source/Core/VideoCommon/OpcodeDecoding.h').read_text()
case = source.split('case Opcode::GX_LOAD_XF_REG:\n  {', 1)[1].split(
    '\n  case Opcode::GX_LOAD_INDX_A:', 1)[0]
assert case.rstrip().endswith('}')
case = case.rstrip()[:-1]
program = r'''
#include <cassert>
#include <cstdint>
#include <stdexcept>
#include <vector>
#include <cstdio>
using u8=uint8_t; using u16=uint16_t; using u32=uint32_t;
#define ASSERT_MSG(category, condition, ...) do { if (!(condition)) throw std::runtime_error("XF length"); } while(0)
namespace Common { u32 swap32(const u8* p) { return u32(p[0])<<24|u32(p[1])<<16|u32(p[2])<<8|p[3]; } }
struct Callback {
  unsigned calls=0; u16 address=0; unsigned count=0;
  void OnXF(u16 a,u8 n,const u8* p) {
    ++calls;address=a;count=n;
    for(unsigned i=0;i<n*4;++i) assert(p[i]==0x55);
  }
};
u32 decode(const u8* data,u32 available,Callback& callback) {
CASE
}
int main() {
  unsigned cases=0;
  for(unsigned words=1;words<=16;++words) {
    std::vector<u8> command={0x10,0,u8(words-1),0x10,0x00};
    command.resize(5+4*words,0x55);
    for(unsigned split=0;split<command.size();++split) {
      // Separate allocation makes sanitizer check the actual truncated bound.
      std::vector<u8> pending(command.begin(),command.begin()+split);
      Callback callback;
      assert(decode(pending.data(),pending.size(),callback)==0);
      assert(callback.calls==0);
      pending.insert(pending.end(),command.begin()+split,command.end());
      assert(decode(pending.data(),pending.size(),callback)==command.size());
      assert(callback.calls==1 && callback.address==0x1000 && callback.count==words);
      ++cases;
    }
  }
  const u8 captured[]={0x10,0,0x61,0x16,0};
  Callback callback;
  bool rejected=false;
  try { decode(captured,sizeof(captured),callback); }
  catch(const std::runtime_error&) { rejected=true; }
  assert(rejected && callback.calls==0);
  std::printf("%u valid XF truncation/refill cases pass; captured malformed header rejects\n",cases);
}
'''.replace('CASE', case)
with tempfile.TemporaryDirectory(prefix='galaxypad-xf-partial-') as directory:
    cpp = Path(directory)/'test.cpp'
    binary = Path(directory)/'test'
    cpp.write_text(program)
    subprocess.run(['clang++','-std=c++20','-O2','-fsanitize=address,undefined',
                    str(cpp),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
print('Tests actual XF case only, not FIFO concurrency, producer correctness or whole decoder.')
