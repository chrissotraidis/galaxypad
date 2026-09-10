"""Exercise actual opt-in init and timing-boundary trigger fragments."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
core=root/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp'
init=(core/'StaticRecompCore.cpp').read_text().split('  const char* fallback_pcs =',1)[1].split('  const char* fallback_override',1)[0]
init='  const char* fallback_pcs ='+init
run=(core/'StaticRecompCore_Run.cpp').read_text().split('    // Diagnostic only: poll',1)[1].split('    const std::string current_game_id',1)[0]
run='    // Diagnostic only: poll'+run
program=r'''
#include "FallbackHistogram.h"
#include <memory>
#include <string>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cassert>
using u32=uint32_t;
struct Probe {
  std::unique_ptr<galaxypad::diagnostics::FallbackHistogram<>> m_fallback_histogram;
  std::string m_fallback_start_file;
  u32 m_fallback_start_poll=0;
  uint64_t m_native_dispatches=42;
  struct Memory {
    const uint8_t* GetRAM() const { return nullptr; }
    size_t GetRamSizeReal() const { return 0; }
  } memory;
  struct { u32 pc=0x80004000; } ppc;
  void Init() { INIT }
  void Tick() { RUN }
};
int main(int argc,char**argv) {
  assert(argc==2);
  unsetenv("GALAXYPAD_FALLBACK_PCS");
  setenv("GALAXYPAD_FALLBACK_START_FILE",argv[1],1);
  Probe p;p.Init();assert(!p.m_fallback_histogram && p.m_fallback_start_file.empty());
  setenv("GALAXYPAD_FALLBACK_PCS","1",1);
  p.Init();assert(!p.m_fallback_histogram && !p.m_fallback_start_file.empty());
  for(int i=0;i<2048;++i)p.Tick();
  assert(!p.m_fallback_histogram);
  auto* f=std::fopen(argv[1],"wb");assert(f);std::fclose(f);
  for(int i=0;i<1023;++i)p.Tick();assert(!p.m_fallback_histogram);
  p.Tick();assert(p.m_fallback_histogram && p.m_fallback_start_file.empty());
  p.m_fallback_histogram->Record(0,galaxypad::diagnostics::FallbackPath::Uncovered);
  for(int i=0;i<2048;++i)p.Tick();assert(p.m_fallback_histogram->total==1);
  f=std::fopen(argv[1],"rb");assert(f);std::fclose(f);
  unsetenv("GALAXYPAD_FALLBACK_START_FILE");p.Init();
  assert(p.m_fallback_histogram && p.m_fallback_histogram->total==0);
}
'''.replace('INIT',init).replace('RUN',run)
with tempfile.TemporaryDirectory(prefix='galaxypad-fallback-start-') as directory:
    folder=Path(directory); cpp=folder/'test.cpp'; binary=folder/'test'
    cpp.write_text(program)
    subprocess.run(['clang++','-std=c++17','-fsanitize=address,undefined','-I'+str(core),str(cpp),'-o',str(binary)],check=True)
    subprocess.run([str(binary),str(folder/'marker')],check=True)
print('Fallback start: opt-out, absent marker, polling boundary, one-shot, retention and legacy mode pass')
