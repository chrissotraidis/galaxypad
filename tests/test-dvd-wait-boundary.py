"""Source-derived check that timing the existing queue wait preserves result order."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/HW/DVD/DVDThread.cpp').read_text()
finish = source.split('void DVDThread::FinishRead(u64 id, s64 cycles_late)', 1)[1]
body = finish[finish.index('  ReadResult result;'):finish.index('  // We have now obtained')]
installed = ('m_system.GetPerfMetrics().GetCPUDVDWaitTiming().Measure(\n'
             '          [this] { m_result_queue.WaitForData(); });')
if installed in body:
    assert body.count(installed) == 1
    body = body.replace(installed, 'm_result_queue.WaitForData();')
assert body.count('m_result_queue.WaitForData();') == 1
candidate = body.replace('m_result_queue.WaitForData();',
    'timing.MeasureWithClock([&] { m_result_queue.WaitForData(); }, [&] { ++clocks; return ticks += 10; });')
assert candidate.replace('timing.MeasureWithClock([&] { m_result_queue.WaitForData(); }, [&] { ++clocks; return ticks += 10; });',
                         'm_result_queue.WaitForData();') == body
program = '''
#include <cassert>
#include <map>
#include <deque>
#include <utility>
#include "idle-wait-timing.h"
using u64=unsigned long long;
struct Request {u64 id;};
using ReadResult=std::pair<Request,unsigned>;
struct Queue {
 std::deque<ReadResult> data;
 unsigned waits=0,pops=0;
 void WaitForData() {++waits;assert(!data.empty());}
 void Pop(ReadResult& result) {++pops;result=data.front();data.pop_front();}
};
struct Probe {
 Queue m_result_queue;
 std::map<u64,ReadResult> m_result_map;
 galaxypad::IdleWaitTiming timing;
 unsigned clocks=0;u64 ticks=0;
 ReadResult reference(u64 id) {REFERENCE return result;}
 ReadResult candidate(u64 id) {CANDIDATE return result;}
};
int main() {
 for(bool enabled:{false,true}) {
  Probe a,b;b.timing.Configure(enabled);
  for(u64 id:{3,1,2}) {a.m_result_queue.data.push_back({{id},unsigned(id*7)});}
  b.m_result_queue.data=a.m_result_queue.data;
  for(u64 id:{1,3,2}) {
   auto x=a.reference(id),y=b.candidate(id);
   assert(x.first.id==y.first.id && x.second==y.second);
   assert(a.m_result_queue.waits==b.m_result_queue.waits);
   assert(a.m_result_queue.pops==b.m_result_queue.pops);
   assert(a.m_result_map.size()==b.m_result_map.size());
   if(id==3) assert(b.m_result_queue.waits==2); // map hit does not wait
  }
  assert(b.m_result_queue.waits==3 && b.m_result_map.empty());
  assert(b.clocks==(enabled?6u:0u));
  assert(b.timing.ElapsedNs()==(enabled?30u:0u));
 }
}
'''.replace('REFERENCE', body).replace('CANDIDATE', candidate)
with tempfile.TemporaryDirectory(prefix='galaxypad-dvd-wait-') as directory:
    path=Path(directory)/'probe.cpp';path.write_text(program)
    binary=Path(directory)/'probe'
    subprocess.run(['clang++','-std=c++17','-O2','-fsanitize=address,undefined',
                    '-I',str(root/'patches/experiments'),str(path),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
print('Exact DVD result loop: map-hit/no-wait, out-of-order queue and disabled/enabled timing pass')
