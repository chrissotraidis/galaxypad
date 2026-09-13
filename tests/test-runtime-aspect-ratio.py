#!/usr/bin/env python3
"""Compile the public setting and execute the actual runtime configuration block."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / 'ref/ModernGekko'
source = (RUNTIME / 'src/runtime/dolphin_runtime.cpp').read_text()
start = source.index('  if (impl->config.graphics.aspect_ratio_mode)')
end = source.index('  Config::SetBase(Config::GFX_SHADER_CACHE', start)
block = source[start:end]
fixture = r'''
#include "moderngekko/runtime.hpp"
#include <cassert>
enum class AspectMode {Auto, ForceStandard, ForceWide, Stretch};
namespace Config {
constexpr int GFX_ASPECT_RATIO = 1;
int writes = 0;
AspectMode actual = AspectMode::Stretch;
void SetBase(int key, AspectMode value) {
  assert(key == GFX_ASPECT_RATIO); ++writes; actual = value;
}
}
struct Impl {moderngekko::RuntimeConfig config;};
void apply(Impl* impl) {
BLOCK
}
int main() {
  Impl impl;
  assert(!impl.config.graphics.aspect_ratio_mode.has_value());
  apply(&impl);
  assert(Config::writes == 0 && Config::actual == AspectMode::Stretch);
  const AspectMode expected[] = {AspectMode::ForceStandard, AspectMode::ForceWide, AspectMode::Stretch};
  for (int value = 0; value < 3; ++value) {
    impl.config.graphics.aspect_ratio_mode = value;
    apply(&impl);
    assert(Config::actual == expected[value]);
    assert(Config::writes == value + 1);
  }
  for (int value : {-1, 3, 100}) {
    impl.config.graphics.aspect_ratio_mode = value;
    apply(&impl);
    assert(Config::actual == AspectMode::Auto);
  }
  assert(Config::writes == 6);
}
'''.replace('BLOCK', block)
with tempfile.TemporaryDirectory(prefix='galaxypad-aspect-ratio-') as tmp:
    src = Path(tmp) / 'test.cpp'
    exe = Path(tmp) / 'test'
    src.write_text(fixture)
    subprocess.run(['xcrun', 'clang++', '-std=c++20', '-O1', '-fsanitize=address,undefined',
                    '-I', str(RUNTIME / 'include'), str(src), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
print('Runtime aspect setting: omitted, standard, wide, stretch and invalid modes passed.')
