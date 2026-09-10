#!/usr/bin/env python3
from pathlib import Path
import os
import csv
import subprocess
import tempfile
import runpy

root = Path(__file__).resolve().parents[1]
probe = runpy.run_path(str(root / 'scripts/prepare-metal-staging-probe.py'))
source = (root / 'ref/ModernGekko/vendor/dolphin/Source/Core/VideoBackends/Metal/MTLTexture.mm').read_bytes()
staged = probe['instrument'](source)
tracker = (root / 'ref/ModernGekko/vendor/dolphin/Source/Core/VideoBackends/Metal/MTLStateTracker.mm').read_bytes()
instrumented_tracker = probe['instrument_tracker'](tracker)
assert instrumented_tracker.count('TraceStaging("completion_handler"') == 1
assert instrumented_tracker.count('std::lock_guard<std::mutex> guard(backref->mtx);') == tracker.decode().count('std::lock_guard<std::mutex> guard(backref->mtx);')
assert instrumented_tracker.count('addCompletedHandler:') == tracker.decode().count('addCompletedHandler:')
try:
    probe['instrument_tracker'](tracker + b'\n')
    raise AssertionError('unreviewed tracker accepted')
except ValueError:
    pass
assert staged.count('TraceStaging(') == 2 and staged.count('TraceStagingGPU(') == 1
assert staged.index('[m_wait_buffer waitUntilCompleted]') < staged.index('[m_wait_buffer GPUStartTime]')
for call in ('[m_wait_buffer waitUntilCompleted];', 'g_state_tracker->FlushEncoders();',
             'g_state_tracker->NotifyOfCPUGPUSync();'):
    assert staged.count(call) == source.decode().count(call)
try:
    probe['instrument'](source + b'\n')
    raise AssertionError('unreviewed source accepted')
except ValueError:
    pass
program = r'''
#include "metal-staging-timing.h"
#include <cassert>
#include <vector>
#include <mutex>
#include <thread>
using namespace GalaxyPadDiagnostics;
int main() {
  StagingCaptureGate gate;
  int polls=0;
  assert(gate.Allow(false,[&] { ++polls; return false; }) && polls==0);
  for(int i=0;i<64;++i) assert(!gate.Allow(true,[&] { ++polls; return false; }));
  assert(polls==1);
  assert(gate.Allow(true,[&] { ++polls; return true; }));
  for(int i=0;i<100;++i) assert(gate.Allow(true,[&] { ++polls; return false; }));
  assert(polls==2);
  assert(!ValidateStagingGPUInterval(true,0,0).valid);
  assert(!ValidateStagingGPUInterval(false,1,2).valid);
  assert(!ValidateStagingGPUInterval(true,2,1).valid);
  assert(!ValidateStagingGPUInterval(true,NAN,2).valid);
  assert(!ValidateStagingGPUInterval(true,1,INFINITY).valid);
  auto gpu=ValidateStagingGPUInterval(true,1,1.5);
  assert(gpu.valid && gpu.seconds==0.5 && gpu.startSeconds==1 && gpu.endSeconds==1.5);
  const auto hostStart=StagingHostNanoseconds();
  assert(StagingHostNanoseconds()>=hostStart);
  for (bool enabled : {false, true}) {
    std::vector<int> order;
    int ticks=0, calls=0, records=0;
    MeasureStaging(enabled, [&] { ++calls; order.push_back(2); },
      [&] { order.push_back(++ticks==1 ? 1 : 3); return ticks; },
      [&](int begin,int end) { assert(begin==1 && end==2); ++records; order.push_back(4); });
    assert(calls==1 && ticks==(enabled?2:0) && records==(enabled?1:0));
    assert(order==(enabled?std::vector<int>{1,2,3,4}:std::vector<int>{2}));
  }
  // Recording must happen after the original completion-handler lock dies.
  std::mutex mutex;
  MeasureStaging(true, [&] { std::lock_guard<std::mutex> guard(mutex); },
    [] { return 1; }, [&](int,int) { assert(mutex.try_lock()); mutex.unlock(); });
  if (const char* trigger=std::getenv("GALAXYPAD_METAL_STAGING_ARM_FILE")) {
    int operations=0, gpuReads=0;
    for(int i=0;i<1000;++i)
      TraceStagingGPU("wait",[&] { ++operations; },[&] { ++gpuReads; return StagingGPUInterval{}; });
    assert(operations==1000 && gpuReads==0 && StagingTraceCount()==0);
    auto* file=std::fopen(trigger,"w"); assert(file);
    std::fputs("1\n",file); std::fclose(file);
  }
  int calls=0;
  if (std::getenv("GALAXYPAD_TEST_CONCURRENT_TRACE")) {
    std::atomic<int> concurrentCalls{0};
    auto worker = [&] {
      for(int i=0;i<3000;++i)
        TraceStaging("completion_handler", [&] { ++concurrentCalls; }, 42);
    };
    std::thread first(worker), second(worker);
    first.join(); second.join();
    assert(concurrentCalls==6000);
    return 0;
  }
  for(int i=0;i<3000;++i) {
    TraceStaging("copy_setup", [&] { ++calls; });
    TraceStaging("wait", [&] { ++calls; });
  }
  assert(calls==6000);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-metal-timing-') as directory:
    out = Path(directory)
    (out / 'test.cpp').write_text(program)
    subprocess.run(['xcrun', 'clang++', '-std=c++20', '-O1', '-fsanitize=address,undefined',
                    '-I', str(root / 'patches/experiments'), str(out / 'test.cpp'),
                    '-o', str(out / 'test')], check=True)
    env = os.environ.copy()
    env.pop('GALAXYPAD_METAL_STAGING_TRACE', None)
    env.pop('GALAXYPAD_METAL_STAGING_ARM_FILE', None)
    env.pop('GALAXYPAD_TEST_CONCURRENT_TRACE', None)
    subprocess.run([str(out / 'test')], env=env, check=True)
    env['GALAXYPAD_METAL_STAGING_TRACE'] = str(out / 'trace.csv')
    subprocess.run([str(out / 'test')], env=env, check=True)
    with (out / 'trace.csv').open() as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 4096
    assert [int(row['sample']) for row in rows] == list(range(4096))
    assert all(int(row['end_ns']) >= int(row['begin_ns']) for row in rows)
    assert {row['stage'] for row in rows} == {'copy_setup', 'wait'}
    env['GALAXYPAD_METAL_STAGING_TRACE'] = str(out / 'armed.csv')
    env['GALAXYPAD_METAL_STAGING_ARM_FILE'] = str(out / 'trigger')
    subprocess.run([str(out / 'test')], env=env, check=True)
    with (out / 'armed.csv').open() as stream:
        armed_rows = list(csv.DictReader(stream))
    assert len(armed_rows) == 4096 and armed_rows[0]['sample'] == '0'
    env.pop('GALAXYPAD_METAL_STAGING_ARM_FILE')
    env['GALAXYPAD_TEST_CONCURRENT_TRACE'] = '1'
    env['GALAXYPAD_METAL_STAGING_TRACE'] = str(out / 'concurrent.csv')
    subprocess.run([str(out / 'test')], env=env, check=True)
    with (out / 'concurrent.csv').open() as stream:
        concurrent_rows = list(csv.DictReader(stream))
    assert sorted(int(row['sample']) for row in concurrent_rows) == list(range(4096))
    assert all(row['buffer'] == '42' for row in concurrent_rows)
    summarize = runpy.run_path(str(root / 'scripts/summarize-metal-staging.py'))['summarize']
    summary = summarize(rows)
    assert summarize(concurrent_rows)['stages']['completion_handler']['count'] == 4096
    assert summary['cap_reached'] and summary['stages']['wait']['count'] == 2048
    assert summary['gpu_wait_records']['unavailable'] == 2048
    assert summary['gpu_wait_records']['median_ms'] is None
    known = [dict(sample='0', stage='wait', begin_ns='1', end_ns='2', gpu_valid='1', gpu_ms='0.5')]
    assert summarize(known)['gpu_wait_records']['median_ms'] == 0.5
    handler = [dict(sample='0', stage='completion_handler', begin_ns='1', end_ns='1001', gpu_valid='0', gpu_ms='0')]
    assert summarize(handler)['stages']['completion_handler']['median_ms'] == 0.001
    assert summary['wait_handler_correlation']['unrecorded'] == 2048
    correlated = [
        dict(sample='0',stage='wait',begin_ns='100',end_ns='1000',buffer='42'),
        dict(sample='1',stage='completion_handler',begin_ns='300',end_ns='400',buffer='42'),
        # Same pointer reused later must not match the earlier wait.
        dict(sample='2',stage='completion_handler',begin_ns='1200',end_ns='1300',buffer='42'),
        dict(sample='3',stage='wait',begin_ns='2000',end_ns='3000',buffer='43')]
    result = summarize(list(reversed(correlated)))['wait_handler_correlation']
    assert result['matched'] == 1 and result['unmatched'] == 1
    assert result['wait_begin_to_handler_begin_median_ms'] == 0.0002
    assert result['handler_end_to_wait_end_median_ms'] == 0.0006
    duplicate = dict(correlated[1], sample='4')
    result = summarize(correlated + [duplicate])['wait_handler_correlation']
    assert result['ambiguous'] == 1 and result['matched'] == 0
    absolute = [
        dict(sample='0',stage='wait',begin_ns='1000000000',end_ns='2000000000',buffer='42',
             clock='mach_absolute',gpu_valid='1',gpu_ms='100',gpu_start_s='1.1',gpu_end_s='1.2'),
        dict(sample='1',stage='completion_handler',begin_ns='1500000000',end_ns='1600000000',buffer='42',
             clock='mach_absolute',gpu_valid='0',gpu_ms='0',gpu_start_s='0',gpu_end_s='0')]
    result = summarize(absolute)['wait_handler_correlation']['gpu_end_to_handler']
    assert result['available'] == 1 and abs(result['median_ms']-300)<1e-6
    for clock in ('steady',):
        result = summarize([dict(row,clock=clock) for row in absolute])['wait_handler_correlation']['gpu_end_to_handler']
        assert result['unavailable'] == 1 and result['median_ms'] is None
    result = summarize([dict(absolute[0],gpu_end_s='1.7'),absolute[1]])['wait_handler_correlation']['gpu_end_to_handler']
    assert result['invalid_order'] == 1 and result['median_ms'] is None
    for invalid in ([], rows[1:], rows + [rows[0]],
                    [dict(rows[0], end_ns='0')], [dict(rows[0], stage='gpu')],
                    [dict(known[0], gpu_ms='nan')], [dict(known[0], gpu_valid='2')],
                    [dict(known[0], gpu_valid='0')], [dict(known[0], buffer='-1')],
                    [dict(absolute[0],gpu_end_s='nan')], [dict(absolute[0],clock='unknown')]):
        try:
            summarize(invalid)
            raise AssertionError('invalid trace accepted')
        except ValueError:
            pass
print('Staging timing: exact source guard, operation order, disabled clocks, shared cap and CSV pass')
