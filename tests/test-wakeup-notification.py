"""Source-derived notification-only observer contract; not a concurrency proof."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'ref/ModernGekko/vendor/dolphin/Source/Core/Common/BlockingLoop.h').read_text()
if 'void WakeupWithNotification(Notify&& notify)' in source:
    assert 'WakeupWithNotification([](Event& event) { event.Set(); });' in source
    body = source.split('  void WakeupWithNotification(Notify&& notify)\n  {', 1)[1].split('\n  }', 1)[0]
    assert body.count('notify(m_new_work_event);') == 1
    body = body.replace('notify(m_new_work_event);', 'm_new_work_event.Set();')
else:
    body = source.split('  void Wakeup()\n  {', 1)[1].split('\n  }', 1)[0]
assert body.count('m_new_work_event.Set();') == 1
candidate = body.replace('m_new_work_event.Set();', 'notify(m_new_work_event);')
program = r'''
#include <atomic>
#include <cassert>
#include "idle-wait-timing.h"
struct Event { unsigned calls=0; void Set() {++calls;} };
struct Probe {
 enum {STATE_SLEEPING=0,STATE_DONE=1,STATE_LAST_EXECUTION=2,STATE_NEED_EXECUTION=3};
 std::atomic<int> m_running_state{0};
 Event m_new_work_event;
 void reference() {REFERENCE}
 template<class Notify> void candidate(Notify&& notify) {CANDIDATE}
};
int main() {
 for(bool enabled:{false,true}) for(int initial=0;initial<=3;++initial) {
  Probe a,b;a.m_running_state=initial;b.m_running_state=initial;
  galaxypad::IdleWaitTiming timing;timing.Configure(enabled);
  unsigned observers=0,clocks=0;std::uint64_t ticks=0;
  auto notify=[&](Event& event) {
   ++observers;
   timing.MeasureWithClock([&] {event.Set();},[&] {++clocks;return ticks+=10;});
  };
  a.reference();b.candidate(notify);
  assert(a.m_running_state==b.m_running_state);
  assert(b.m_running_state==3);
  assert(a.m_new_work_event.calls==b.m_new_work_event.calls);
  assert(observers==(initial==0?1u:0u));
  assert(b.m_new_work_event.calls==observers);
  assert(clocks==((enabled&&initial==0)?2u:0u));
  assert(timing.ElapsedNs()==((enabled&&initial==0)?10u:0u));
  a.reference();b.candidate(notify); // pending work never re-notifies
  assert(a.m_new_work_event.calls==b.m_new_work_event.calls);
  assert(observers==(initial==0?1u:0u));
 }
}
'''.replace('REFERENCE', body).replace('CANDIDATE', candidate)
with tempfile.TemporaryDirectory(prefix='galaxypad-wakeup-contract-') as temporary:
    path = Path(temporary) / 'probe.cpp'
    path.write_text(program)
    binary = Path(temporary) / 'probe'
    subprocess.run(['clang++', '-std=c++17', '-O2', '-fsanitize=address,undefined',
                    '-I', str(root / 'patches/experiments/rolling'), str(path),
                    '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print('Wakeup source states, notification-only observation, disabled clocks and repeat suppression pass')
