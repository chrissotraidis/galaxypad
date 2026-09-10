"""Compare exact current Run lambda with isolated metadata-snapshot candidate.

Generated harness stays private/temporary. This tests dispatch eligibility, not
the complete execution loop, concurrent lifecycle safety or gameplay speed.
"""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp').read_text()
start = source.index('  const auto fast_dispatchable_at = [this](u32 address) {')
end = source.index('\n  };', start) + len('\n  };')
reference = source[start:end]
candidate = (root/'patches/experiments/run-lookup-snapshot.inc').read_text()
program = r'''
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <vector>
using u32 = uint32_t; using u8 = uint8_t;
struct Fixture {
  bool m_has_rel_modules = false, m_module_active = true;
  std::vector<int> m_forced_fallback_ranges;
  std::vector<int> m_chunk_lookup_table;
  std::vector<u8> m_chunk_state{0, 1, 2};
  u32 m_lookup_ram_size = 4096, m_lookup_exram_size = 8192;
  static constexpr u8 CHUNK_VERIFIED = 1;
  uint64_t slow_calls = 0, cases = 0;
  bool FastDispatchableAt(u32 address) {
    ++slow_calls;
    return m_module_active && (address & 7) == 4;
  }
  void compare_all() {
    REFERENCE
    const auto reference = fast_dispatchable_at;
    {
      CANDIDATE
      const auto compare = [&](u32 address) {
        const auto before = slow_calls;
        const bool a = reference(address);
        const auto middle = slow_calls;
        const bool b = fast_dispatchable_at(address);
        assert(a == b && slow_calls - middle == middle - before);
        ++cases;
      };
      // Exercise valid/invalid chunks and live invalidation after snapshot.
      for (unsigned state = 0; state < 3; ++state) {
        for (auto& value : m_chunk_state) value = state;
        for (bool active : {false, true}) {
          m_module_active = active;
          for (u32 base : {0u, 0x80000000u, 0x90000000u, 0xc0000000u})
            for (int delta = -8; delta < 8200; ++delta)
              compare(base + static_cast<u32>(delta));
        }
      }
      u32 seed = 0x4672026;
      for (unsigned n = 0; n < 1000000; ++n) {
        seed ^= seed << 13; seed ^= seed >> 17; seed ^= seed << 5;
        compare(seed);
      }
    }
  }
};
int main() {
  Fixture f;
  f.m_chunk_lookup_table.resize(3072);
  for (unsigned i = 0; i < 3072; ++i) f.m_chunk_lookup_table[i] = int(i % 4) - 1;
  f.compare_all();
  f.m_has_rel_modules = true; f.compare_all();
  f.m_has_rel_modules = false; f.m_forced_fallback_ranges.push_back(1); f.compare_all();
  f.m_forced_fallback_ranges.clear();
  f.m_chunk_lookup_table.clear(); f.compare_all();
  assert(f.cases > 4000000 && f.slow_calls > 0);
  std::printf("%llu eligibility comparisons pass, including live verification/module state and slow-path calls\n",
              static_cast<unsigned long long>(f.cases));
}
'''.replace('REFERENCE', reference).replace('CANDIDATE', candidate)
with tempfile.TemporaryDirectory(prefix='galaxypad-run-lookup-') as directory:
    path = Path(directory)
    harness = path/'probe.cpp'
    harness.write_text(program)
    for name, flags in [('sanitized', ['-O1', '-fsanitize=address,undefined']),
                        ('optimized', ['-O2'])]:
        binary = path/name
        subprocess.run(['clang++', '-std=c++20', '-Wall', '-Wextra', '-Werror',
                        *flags, str(harness), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
