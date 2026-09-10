"""Exercise actual diagnostic header: opt-in events and unchanged counters."""
from pathlib import Path
import csv
import hashlib
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
header = root/'ref/ModernGekko/vendor/dolphin/Source/Core/Common/GalaxyPadDiagnostics.h'
checkout = header.read_bytes()
event_lines = [
    b'  RecordPhase("dma_underrun", ordinal);\n',
    b'  RecordPhase("dma_backlog_drop", ordinal);\n',
    b'  RecordPhase("dma_queue_full_drop", s_dma_enqueues.load(std::memory_order_relaxed));\n',
]
original = checkout
for line in event_lines:
    assert original.count(line) <= 1
    original = original.replace(line, b'')
assert hashlib.sha256(original).hexdigest() == '6f9c2dda1739eec70b137060ea8f12e00694639a9b4475fa0f8e6e9c795256d0'
bootstrap = (root/'scripts/bootstrap-dependencies.sh').read_text()
assert '"$wakeup_core_patch" "$psq_scale_patch" "$audio_events_patch"' in bootstrap
assert bootstrap.index('apply --reverse "$audio_events_patch"') < bootstrap.index('apply --reverse "$psq_scale_patch"')
assert bootstrap.index('apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$audio_events_patch"') > bootstrap.index('apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$wakeup_core_patch"')
program = r'''
#include "Source/Core/Common/GalaxyPadDiagnostics.h"
#include <cassert>
int main() {
  using namespace GalaxyPadDiagnostics;
  Reset();
  RecordDmaEnqueue(5, 100);
  RecordDmaUnderrun();
  RecordDmaUnderrun();
  RecordDmaEnqueue(2, 200);
  RecordDmaBacklogDrop();
  RecordDmaQueueFullDrop();
  assert(s_dma_enqueues.load()==2 && s_dma_underruns.load()==2);
  assert(s_dma_backlog_drops.load()==1 && s_dma_queue_full_drops.load()==1);
  assert(s_dma_first_underrun_enqueue.load()==1 && s_dma_last_underrun_enqueue.load()==1);
  assert(s_dma_first_backlog_enqueue.load()==2 && s_dma_last_backlog_enqueue.load()==2);
  if(auto* file=GetPhaseTraceFile()) std::fflush(file);
  else assert(s_phase_trace_ordinal.load()==0);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-audio-events-') as directory:
    folder=Path(directory)
    target=folder/'Source/Core/Common/GalaxyPadDiagnostics.h'
    target.parent.mkdir(parents=True)
    target.write_bytes(original)
    patch=root/'patches/experiments/audio-phase-events.patch'
    assert hashlib.sha256(patch.read_bytes()).hexdigest() == 'd0f1d941e552e4baa85b9fe623922dcf8ded804d393708d3f4e321276d99bc89'
    subprocess.run(['git','apply','--check',str(patch)],cwd=folder,check=True)
    subprocess.run(['git','apply',str(patch)],cwd=folder,check=True)
    assert hashlib.sha256(target.read_bytes()).hexdigest() == '9c11e94e0b7c22abe93b319e92f32030e436d9eefb30c487c09aee27c64f772b'
    assert checkout in (original, target.read_bytes()), 'unknown or partial diagnostic overlay'
    test=folder/'test.cpp'; test.write_text(program)
    env=dict(os.environ); env.pop('GALAXYPAD_PHASE_TRACE',None)
    for name,flags in [('sanitized',['-O1','-fsanitize=address,undefined']),('optimized',['-O2'])]:
        binary=folder/name
        subprocess.run(['clang++','-std=c++20',*flags,'-I',str(folder),str(test),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],env=env,check=True)
        trace=folder/(name+'.csv')
        subprocess.run([str(binary)],env={**env,'GALAXYPAD_PHASE_TRACE':str(trace)},check=True)
        with trace.open() as stream:
            rows=list(csv.DictReader(stream))
        assert [(r['event'],int(r['value'])) for r in rows] == [
            ('dma_enqueue',5),('dma_underrun',1),('dma_underrun',1),
            ('dma_enqueue',2),('dma_backlog_drop',2),('dma_queue_full_drop',2)]
        assert [int(r['ordinal']) for r in rows] == list(range(6))
        assert all(int(a['steady_ns']) <= int(b['steady_ns']) for a,b in zip(rows,rows[1:]))
    subprocess.run(['git','apply','--reverse',str(patch)],cwd=folder,check=True)
    assert target.read_bytes()==original
assert header.read_bytes()==checkout
print('Opt-in audio events preserve counts/ordinals, include repeated events and reverse exactly')
