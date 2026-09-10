"""Exercise the production failure-window helper with bounded formatting stubs.

This checks memory bounds, not a live FIFO reproduction or formatting-library behavior.
"""
from pathlib import Path
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'ref/ModernGekko/vendor/dolphin/Source/Core/VideoCommon/OpcodeDecoding.cpp').read_text()
body = re.search(r'std::string detail::DescribeCommandWindow\([^\n]+\)\n\{(.*?)\n\}', source, re.S).group(1)
program = r'''
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <string>
#include <vector>
using u8 = uint8_t;
using u32 = uint32_t;
std::string ArrayToString(const u8* data, u32 size, int) {
  assert(size <= 32);
  std::string result;
  for (u32 i = 0; i < size; ++i) result += static_cast<char>(data[i]);
  return result;
}
namespace fmt {
std::string format(const char*, size_t offset, u32 available,
                   const std::string& before, const std::string& after) {
  assert(before.size() == std::min<size_t>(offset, 32));
  assert(after.size() == std::min<u32>(available, 32));
  return before + after;
}
}
std::string describe(const u8* data, u32 available, const u8* run_begin) {
BODY
}
int main() {
  for (size_t length = 1; length <= 128; ++length) {
    std::vector<u8> bytes(length, 'x');
    for (size_t offset = 0; offset <= length; ++offset) {
      auto text = describe(bytes.data() + offset, length - offset, bytes.data());
      assert(text.size() == std::min<size_t>(offset, 32) +
                            std::min<size_t>(length - offset, 32));
    }
  }
}
'''.replace('BODY', body)
with tempfile.TemporaryDirectory(prefix='galaxypad-xf-context-') as directory:
    cpp = Path(directory) / 'test.cpp'
    binary = Path(directory) / 'test'
    cpp.write_text(program)
    subprocess.run(['clang++', '-std=c++20', '-fsanitize=address,undefined',
                    str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print('XF failure-context bounds passed (ASan/UBSan); live reproduction pending')
