#!/usr/bin/env python3
"""Execute the actual Metal Flush method with bounded command-buffer doubles.

Control-flow contract only; no Metal device, GPU scheduling or pixel proof.
"""
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
path=root/'ref/ModernGekko/vendor/dolphin/Source/Core/VideoBackends/Metal/MTLTexture.mm'
source=path.read_text()
start=source.index('void Metal::StagingTexture::Flush()')
end=source.index('\nstatic void InitDesc',start)
body=source[start:end]
assert body.count('waitUntilCompleted')==1
program=r'''
#import <Foundation/Foundation.h>
#include <cassert>
#include <vector>
enum { MTLCommandBufferStatusNotEnqueued=0, MTLCommandBufferStatusCommitted=2,
       MTLCommandBufferStatusCompleted=4, MTLCommandBufferStatusError=5 };
static std::vector<int> events;
@interface FakeBuffer : NSObject
@property int status;
@end
@implementation FakeBuffer
- (void)waitUntilCompleted { events.push_back(3); self.status=MTLCommandBufferStatusCompleted; }
@end
struct Tracker {
  void FlushEncoders() { events.push_back(1); }
  void NotifyOfCPUGPUSync() { events.push_back(2); }
};
static Tracker tracker;
static Tracker* g_state_tracker=&tracker;
namespace Metal {
struct StagingTexture {
  bool m_needs_flush=true;
  FakeBuffer* m_wait_buffer=nullptr;
  void Flush();
};
}
'''+body+r'''
int main() { @autoreleasepool {
  Metal::StagingTexture texture;
  texture.Flush();assert(events.empty());assert(!texture.m_needs_flush);
  for(int status : {MTLCommandBufferStatusNotEnqueued,MTLCommandBufferStatusCommitted,
                   MTLCommandBufferStatusCompleted,MTLCommandBufferStatusError}) {
    FakeBuffer* buffer=[FakeBuffer new];buffer.status=status;
    texture.m_wait_buffer=buffer;texture.m_needs_flush=true;events.clear();
    texture.Flush();
    assert(!texture.m_needs_flush && !texture.m_wait_buffer);
    assert(events==(status==MTLCommandBufferStatusCompleted ? std::vector<int>{} : std::vector<int>{1,2,3}));
    events.clear();texture.Flush();assert(events.empty());
    [buffer release];
  }
}}
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-metal-flush-') as directory:
    out=Path(directory)
    (out/'probe.mm').write_text(program)
    subprocess.run(['clang++','-std=c++17','-O1','-fsanitize=address,undefined',
                    '-framework','Foundation',str(out/'probe.mm'),'-o',str(out/'probe')],check=True)
    subprocess.run([str(out/'probe')],check=True)
print('Actual staging Flush: absent/completed/pending/error states, ordered wait, clear and repeat pass')
