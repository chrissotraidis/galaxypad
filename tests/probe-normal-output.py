"""Compare the exact software-normal reader with a local-output-pointer candidate.

Isolated prototype only: no vendor source, runtime, or installed app changes.
Caller ownership requires separate input, output, loader and cache allocations.
"""
from pathlib import Path
import json
import shlex
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'ref/ModernGekko/vendor/dolphin/Source/Core/VideoCommon/VertexLoader_Normal.cpp').read_text()
begin = source.index('template <typename T>\nconstexpr float FracAdjust')
end = source.index('template <typename T, u32 N>\nvoid Normal_ReadDirect')
original = source[begin:end]
assert original.count('DataWrite(value);') == 1
candidate = original.replace('void ReadIndirect(', 'void Candidate(')
candidate = candidate[candidate.index('template <typename T, u32 N, u32 Offset>'):]
candidate = candidate.replace('  for (u32 i = Offset;',
                              '  u8* const output = g_vertex_manager_write_ptr;\n  for (u32 i = Offset;')
candidate = candidate.replace('    DataWrite(value);',
                              '    std::memcpy(output + (i - Offset) * sizeof(float), &value, sizeof(value));')
candidate = candidate.replace('  LOG_NORM();',
                              '  g_vertex_manager_write_ptr = output + N * sizeof(float);\n  LOG_NORM();')
preamble = r'''
#include <array>
#include <bit>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <random>
#include <type_traits>
using u8 = uint8_t; using u32 = uint32_t;
struct VertexLoader { int m_remaining; };
namespace VertexLoaderManager {
float normal_cache[3], tangent_cache[3], binormal_cache[3];
}
u8* g_vertex_manager_write_ptr;
template<typename T> void DataWrite(T value) {
  std::memcpy(g_vertex_manager_write_ptr, &value, sizeof(T));
  g_vertex_manager_write_ptr += sizeof(T);
}
namespace Common {
template<typename T> T FromBigEndian(T value) {
  std::array<u8, sizeof(T)> bytes;
  std::memcpy(bytes.data(), &value, sizeof(T));
  for (unsigned i=0; i<sizeof(T)/2; ++i) std::swap(bytes[i], bytes[sizeof(T)-1-i]);
  std::memcpy(&value, bytes.data(), sizeof(T));
  return value;
}
}
#define LOG_NORM()
'''
checks = r'''
std::array<u8,36> cache() {
  std::array<u8,36> result;
  std::memcpy(result.data(), VertexLoaderManager::normal_cache, 12);
  std::memcpy(result.data()+12, VertexLoaderManager::tangent_cache, 12);
  std::memcpy(result.data()+24, VertexLoaderManager::binormal_cache, 12);
  return result;
}
void reset() {
  std::memset(VertexLoaderManager::normal_cache, 0xa5, 12);
  std::memset(VertexLoaderManager::tangent_cache, 0xa5, 12);
  std::memset(VertexLoaderManager::binormal_cache, 0xa5, 12);
}
template<typename T, u32 N, u32 Offset> void test(std::mt19937& random) {
  std::array<T, 9> input;
  for (int iteration=0; iteration<5000; ++iteration) {
    // Includes every float bit class without fast-math; byte comparison catches NaN differences.
    for (auto& value : input) { u32 bits=random(); std::memcpy(&value, &bits, sizeof(T)); }
    for (int remaining : {0, 1, 2, 3, 100}) {
      VertexLoader loader{remaining};
      std::array<u8, 64> a, b; a.fill(0xcc); b.fill(0xcc);
      reset(); g_vertex_manager_write_ptr=a.data()+1;
      ReadIndirect<T,N,Offset>(&loader, input.data());
      assert(g_vertex_manager_write_ptr==a.data()+1+N*sizeof(float));
      auto expected=cache();
      reset(); g_vertex_manager_write_ptr=b.data()+1;
      Candidate<T,N,Offset>(&loader, input.data());
      assert(g_vertex_manager_write_ptr==b.data()+1+N*sizeof(float));
      assert(a==b && expected==cache() && loader.m_remaining==remaining);
    }
  }
}
template<typename T> void all(std::mt19937& r) {
  test<T,3,0>(r); test<T,3,3>(r); test<T,3,6>(r); test<T,9,0>(r);
}
int main() {
  std::mt19937 r(683);
  all<uint8_t>(r); all<int8_t>(r); all<uint16_t>(r); all<int16_t>(r); all<float>(r);
  std::cout << "500000 normal conversions: bytes, caches, cursor and guards match\n";
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-normal-') as directory:
    folder = Path(directory)
    cpp = folder / 'probe.cpp'
    cpp.write_text(preamble + original + candidate + checks)
    binary = folder / 'probe'
    subprocess.run(['clang++', '-std=c++20', '-O2', '-fsanitize=address,undefined',
                    str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True, timeout=30)
    if '--benchmark' in sys.argv:
        bench = r'''
#include <chrono>
#include <ctime>
#include <iomanip>
using Reader = void (*)(VertexLoader*, const int16_t*);
Reader volatile readers[] = {ReadIndirect<int16_t,3,0>, Candidate<int16_t,3,0>};
int main() {
  std::array<int16_t, 4096> data;
  std::mt19937 random(684);
  for (auto& value : data) value=static_cast<int16_t>(random());
  std::array<u8,64> output;
  VertexLoader loader{100};
  constexpr int calls=50000000;
  uint64_t expected=0;
  std::cout << "round,variant,calls,wall_ns_per_call,cpu_ns_per_call,checksum\n";
  for (int round=0; round<8; ++round) {
    for (int order=0; order<2; ++order) {
      int variant=order^(round&1);
      uint64_t checksum=0;
      Reader reader=readers[variant];
      auto start=std::chrono::steady_clock::now();
      auto cpu=std::clock();
      for (int i=0;i<calls;++i) {
        loader.m_remaining=(i%100); // Include the last-vertex cache path.
        g_vertex_manager_write_ptr=output.data()+1;
        reader(&loader, data.data()+(i%4093));
        uint32_t words[3];
        std::memcpy(words, output.data()+1, sizeof(words));
        checksum+=uint64_t(words[0])+words[1]+words[2];
      }
      double cpu_ns=double(std::clock()-cpu)*1e9/CLOCKS_PER_SEC/calls;
      double wall_ns=std::chrono::duration<double,std::nano>(
        std::chrono::steady_clock::now()-start).count()/calls;
      if (round==0 && order==0) expected=checksum;
      assert(checksum==expected && checksum!=0);
      std::cout << round << ',' << variant << ',' << calls << ','
                << std::setprecision(9) << wall_ns << ',' << cpu_ns << ',' << checksum << '\n';
    }
  }
}
'''
        # Volatile dispatch prevents inline specialization of the two compared readers.
        cpp.write_text(preamble + original + candidate + bench)
        subprocess.run(['clang++', '-std=c++20', '-O3', str(cpp), '-o', str(binary)], check=True)
        result = subprocess.check_output([str(binary)], text=True, timeout=30)
        path = root / 'generated/normal-output-benchmark-r684b.csv'
        with path.open('x') as stream:
            stream.write(result)
        print(result)

if '--compile-simulator' in sys.argv or '--compile-device' in sys.argv:
    # Reuse the real translation unit and target flags, but never replace its object.
    device = '--compile-device' in sys.argv
    build = root / ('generated/build/ios-device-core' if device else
                    'generated/build/ios-simulator-core')
    entries = json.loads((build / 'compile_commands.json').read_text())
    entry, = [e for e in entries if e['file'].endswith('/VertexLoader_Normal.cpp')]
    folder = root / ('generated/normal-output-device-r911' if device else
                     'generated/normal-output-r683')
    folder.mkdir(exist_ok=True)
    staged = folder / 'VertexLoader_Normal.cpp'
    obj = folder / 'VertexLoader_Normal.cpp.o'
    if staged.exists() or obj.exists():
        raise SystemExit('Refusing to overwrite candidate evidence')
    replacement = original[:original.index('template <typename T, u32 N, u32 Offset>')]
    replacement += candidate.replace('void Candidate(', 'void ReadIndirect(')
    staged.write_text(source[:begin] + replacement + source[end:])
    argv = shlex.split(entry['command'])
    argv[argv.index('-o') + 1] = str(obj)
    argv[argv.index('-c') + 1] = str(staged)
    subprocess.run(argv, cwd=entry['directory'], check=True, timeout=60)
    symbol = '__ZN12_GLOBAL__N_116Normal_ReadIndexItsLj1EEEvP12VertexLoader'
    disassembly = subprocess.check_output(['xcrun', 'llvm-objdump', '--disassemble',
                    '--disassemble-symbols=' + symbol, str(obj)], text=True)
    (folder / 'normal-s16-index16.asm').write_text(disassembly)
    print(disassembly)
