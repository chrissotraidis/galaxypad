"""Compile actual source description helpers with a formatting stub."""
from pathlib import Path
import re
import subprocess
import tempfile
root = Path(__file__).resolve().parents[1]
core = root/'ref/ModernGekko/vendor/dolphin/Source/Core/VideoCommon'
header = (core/'OpcodeDecoding.h').read_text()
source = (core/'OpcodeDecoding.cpp').read_text()
helper = re.search(r'template <typename T>\nstd::string DescribeCommandSource.*?\n}', header, re.S)[0]
method = re.search(r'  std::string DescribeSource\(\) const\n  \{.*?\n  }', source, re.S)[0]
assert source.index('m_display_list_address = address;') < source.index('Run(start_address, size, *this);')
assert source.index('m_display_list_size = size;') < source.index('Run(start_address, size, *this);')
program = r'''
#include <string>
#include <cassert>
#include <cstdint>
using u32=uint32_t;
namespace fmt {
std::string format(const char*,const char* origin,bool preprocess,u32 address,u32 size) {
  return std::string(origin)+":"+std::to_string(preprocess)+":"+
         std::to_string(address)+":"+std::to_string(size);
}
}
HELPER
template<bool is_preprocess> struct Runtime {
  bool m_in_display_list=false;
  u32 m_display_list_address=123, m_display_list_size=456;
METHOD
};
int main() {
  struct Other {};
  assert(DescribeCommandSource(Other{})=="source=unspecified");
  Runtime<false> render;
  assert(DescribeCommandSource(render)=="main-fifo:0:0:0");
  render.m_in_display_list=true;
  assert(DescribeCommandSource(render)=="display-list:0:123:456");
  render.m_in_display_list=false;
  assert(DescribeCommandSource(render)=="main-fifo:0:0:0");
  Runtime<true> preprocess;preprocess.m_in_display_list=true;
  assert(DescribeCommandSource(preprocess)=="display-list:1:123:456");
}
'''.replace('HELPER',helper).replace('METHOD',method)
with tempfile.TemporaryDirectory(prefix='galaxypad-xf-origin-') as directory:
    cpp=Path(directory)/'test.cpp'; binary=Path(directory)/'test'
    cpp.write_text(program)
    subprocess.run(['clang++','-std=c++20','-fsanitize=address,undefined',str(cpp),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
print('XF source helpers: FIFO/display-list/preprocess/unknown and stale-address masking pass')
