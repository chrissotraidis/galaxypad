"""Exercise the actual unlinked gather branch with an opt-in wait observer.

This checks call ordering and guards, not concurrent FIFO correctness.
"""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'ref/ModernGekko/vendor/dolphin/Source/Core/VideoCommon/CommandProcessor.cpp').read_text()
function = source.split('void CommandProcessorManager::GatherPipeBursted()', 1)[1]
body = function[function.index('  SetCPStatusFromCPU();'):function.index('  // update the fifo pointer')]
original = 'm_system.GetFifo().FlushGpu();'
installed = ('m_system.GetPerfMetrics().GetCPUGatherWaitTiming().Measure(\n'
             '            [this] { m_system.GetFifo().FlushGpu(); });')
if installed in body:
    assert body.count(installed) == 1
    body = body.replace(installed, original)
assert body.count(original) == 1
wrapped = ('timing.MeasureWithClock([&] { m_system.GetFifo().FlushGpu(); }, '
           '[&] { ++clocks; return ticks += 10; });')
candidate = body.replace(original, wrapped)
assert candidate.replace(wrapped, original) == body
program = r'''
#include <atomic>
#include <cassert>
#include <vector>
#include "idle-wait-timing.h"
struct GPU {
 bool deterministic=false;
 std::vector<int> events;
 bool UseDeterministicGPUThread() {return deterministic;}
 void FlushGpu() {events.push_back(2);}
 void RunGpu() {events.push_back(3);}
};
struct PI {unsigned m_fifo_cpu_end=8,m_fifo_cpu_base=4;};
struct System {
 GPU gpu; PI pi; bool on_thread=true;
 GPU& GetFifo() {return gpu;}
 PI& GetProcessorInterface() {return pi;}
};
bool IsOnThread(System& system) {return system.on_thread;}
struct Probe {
 System m_system;
 struct {bool GPLinkEnable=false;} m_cp_ctrl_reg;
 struct {std::atomic<unsigned> CPEnd{8},CPBase{4},CPReadWriteDistance{1};} m_fifo;
 galaxypad::IdleWaitTiming timing;
 unsigned clocks=0; std::uint64_t ticks=0;
 void SetCPStatusFromCPU() {m_system.gpu.events.push_back(1);}
 void reference() {REFERENCE m_system.gpu.events.push_back(4);}
 void candidate() {CANDIDATE m_system.gpu.events.push_back(4);}
};
int main() {
 for(unsigned mask=0;mask<128;++mask) {
  Probe a,b;
  const bool enabled=mask&64;
  for(auto* p:{&a,&b}) {
   p->m_cp_ctrl_reg.GPLinkEnable=mask&1;
   p->m_system.on_thread=mask&2;
   p->m_system.gpu.deterministic=mask&4;
   p->m_fifo.CPEnd=(mask&8)?8:9;
   p->m_fifo.CPBase=(mask&16)?4:5;
   p->m_fifo.CPReadWriteDistance=(mask&32)?1:0;
  }
  b.timing.Configure(enabled);
  a.reference(); b.candidate();
  bool waits=!(mask&1) && (mask&2) && !(mask&4) &&
             (mask&8) && (mask&16) && (mask&32);
  std::vector<int> expected{1};
  if(mask&1) expected.push_back(4);
  else {if(waits) expected.push_back(2); expected.push_back(3);}
  assert(a.m_system.gpu.events==expected);
  assert(b.m_system.gpu.events==expected);
  assert(b.clocks==((enabled&&waits)?2u:0u));
  assert(b.timing.ElapsedNs()==((enabled&&waits)?10u:0u));
 }
}
'''.replace('REFERENCE', body).replace('CANDIDATE', candidate)
with tempfile.TemporaryDirectory(prefix='galaxypad-gather-wait-') as directory:
    path = Path(directory) / 'probe.cpp'
    path.write_text(program)
    binary = Path(directory) / 'probe'
    subprocess.run(['clang++', '-std=c++17', '-O2', '-fsanitize=address,undefined',
                    '-I', str(root / 'patches/experiments/rolling'), str(path),
                    '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print('Gather wait: 128 source-derived guard/ordering/disabled-clock cases pass')
