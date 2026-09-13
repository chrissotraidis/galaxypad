"""Check diagnostic dispatch wrapper: exact values, order and future synchronization."""
from pathlib import Path
import csv
import hashlib
import os
import subprocess
import tempfile
from efb_source import without_dispatch_overlay

root = Path(__file__).resolve().parents[1]
program = r'''
#include "timing.h"
#include <cassert>
#include <bit>
#include <future>
#include <thread>
#include <vector>
using namespace GalaxyPadDiagnostics;
int main() {
  for (bool asynchronous : {false, true}) {
    for (unsigned bits : {0u, 0x80000000u, 0x3f800000u, 0x7f800000u, 0x7fc12345u}) {
      std::vector<int> order;
      int calls = 0;
      auto dispatch = [&](auto callback) {
        order.push_back(1);
        if (!asynchronous) {
          auto result = callback(); order.push_back(3); return result;
        }
        std::packaged_task<float()> task(callback);
        auto future = task.get_future();
        std::thread worker(std::move(task));
        auto result = future.get();
        worker.join();
        order.push_back(3); return result;
      };
      auto value = TraceEFBDispatch(dispatch, [&] {
        ++calls; order.push_back(2); return std::bit_cast<float>(bits);
      }, 482, 378, 0x804ba23c, 0x80385be0);
      assert(calls == 1 && std::bit_cast<unsigned>(value) == bits);
      assert((order == std::vector<int>{1, 2, 3}));
    }
  }
  if (auto* file = GetEFBDispatchTrace()) std::fflush(file);
}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-efb-dispatch-') as directory:
    folder = Path(directory)
    name = 'Source/Core/VideoCommon/EFBInterface.cpp'
    source = root/'ref/ModernGekko/vendor/dolphin'/name
    checkout = source.read_bytes()
    original = without_dispatch_overlay(checkout)
    assert hashlib.sha256(original).hexdigest() == '9164b11a36e898f4e2ee479b975c751deb2752f2b27047d610feb0290197405f'
    target = folder/name
    target.parent.mkdir(parents=True)
    target.write_bytes(original)
    patch = root/'patches/experiments/efb-dispatch-timing.patch'
    assert hashlib.sha256(patch.read_bytes()).hexdigest() == '5226881b8ce0f00b0b2673b68f40040fa4490771d170aade1289db00ae19b638'
    subprocess.run(['git', 'apply', '--check', str(patch)], cwd=folder, check=True)
    subprocess.run(['git', 'apply', str(patch)], cwd=folder, check=True)
    assert hashlib.sha256(target.read_bytes()).hexdigest() == 'a9caaf2ec38b064acacb3eb36ab0d62810da51aafd85cb721f93a47a8c54a010'
    for unknown in (original+b'\n', target.read_bytes()+b'\n'):
        try:
            without_dispatch_overlay(unknown)
        except (AssertionError, subprocess.CalledProcessError):
            pass
        else:
            raise AssertionError('unknown source accepted')
    assert checkout in (original, target.read_bytes())
    patched_header = folder/'Source/Core/Common/GalaxyPadEFBDispatchTiming.h'
    assert patched_header.read_bytes() == (root/'patches/experiments/efb-dispatch-timing.h').read_bytes()
    live_header = root/'ref/ModernGekko/vendor/dolphin/Source/Core/Common/GalaxyPadEFBDispatchTiming.h'
    assert live_header.exists() == (checkout != original)
    if live_header.exists():
        assert live_header.read_bytes() == patched_header.read_bytes()
    (folder/'timing.h').write_bytes(patched_header.read_bytes())
    (folder/'test.cpp').write_text(program)
    env = dict(os.environ)
    env.pop('GALAXYPAD_EFB_DISPATCH_TRACE', None)
    for name, flags in [('sanitized', ['-O1', '-fsanitize=address,undefined']), ('optimized', ['-O2'])]:
        binary = folder/name
        subprocess.run(['clang++', '-std=c++20', '-pthread', *flags, str(folder/'test.cpp'), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], env=env, check=True)
        subprocess.run([str(binary)], env={**env, 'GALAXYPAD_EFB_DISPATCH_TRACE': ''}, check=True)
        subprocess.run([str(binary)], env={**env, 'GALAXYPAD_EFB_DISPATCH_TRACE': str(folder)}, check=True)
        trace = folder/(name+'.csv')
        subprocess.run([str(binary)], env={**env, 'GALAXYPAD_EFB_DISPATCH_TRACE': str(trace)}, check=True)
        rows = list(csv.DictReader(trace.open()))
        assert len(rows) == 10
        for row in rows:
            times = [int(row[k]) for k in ('queued_ns', 'entered_ns', 'finished_ns', 'returned_ns')]
            assert times == sorted(times) and times[0] > 0
            assert [row[k] for k in ('x', 'y', 'guest_pc', 'guest_lr')] == ['482', '378', '0x804ba23c', '0x80385be0']
    subprocess.run(['git', 'apply', '--reverse', str(patch)], cwd=folder, check=True)
    assert target.read_bytes() == original and source.read_bytes() == checkout
    assert not patched_header.exists()
print('EFB stage timing preserves float bits, single invocation, synchronous/future order and opt-out')
