#!/usr/bin/env python3
"""Run production recovery/lifecycle methods with controllable audio activation."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'apple/ios/GalaxyPadCoreHost.mm').read_text()

def method(signature):
    start = source.index(signature)
    body = source.index('{', start)
    depth = 1
    end = body + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]

harness = r'''
#import <Foundation/Foundation.h>
#include <cassert>
static NSString *const AVAudioSessionInterruptionTypeKey=@"type";
static const unsigned AVAudioSessionInterruptionTypeBegan=1;
static unsigned attempts;
static BOOL succeeds;
#define AVAudioSession GalaxyPadTestAudioSession
@interface AVAudioSession : NSObject
+ (instancetype)sharedInstance;
- (BOOL)setActive:(BOOL)active error:(NSError **)error;
@end
@implementation AVAudioSession
+ (instancetype)sharedInstance { static id session; if (!session) session=[self new]; return session; }
- (BOOL)setActive:(BOOL)active error:(NSError **)error {
  assert(active); ++attempts;
  if (!succeeds && error) *error=[NSError errorWithDomain:@"test" code:1 userInfo:nil];
  return succeeds;
}
@end
static void GalaxyPadLog(NSString *format, ...) { (void)format; }
@interface GalaxyPadCoreHost : NSObject {
@public
  BOOL _active, _busy, _interrupted, _audioActive, _pauseRequested, _nativeUIBlocked;
  unsigned resets, reconciles;
}
- (BOOL)resumeInterruptedAudio;
- (void)audioInterruption:(NSNotification *)notification;
- (void)setApplicationActive:(BOOL)active;
- (void)setNativeUIBlocked:(BOOL)blocked pauseRuntime:(BOOL)pauseRuntime;
- (void)clearInput;
- (void)reconcileLifecycle;
@end
@implementation GalaxyPadCoreHost
- (void)clearInput { ++resets; }
- (void)reconcileLifecycle { ++reconciles; }
'''
harness += '\n'.join(method(s) for s in [
    '- (BOOL)resumeInterruptedAudio',
    '- (void)setApplicationActive:',
    '- (void)setNativeUIBlocked:',
    '- (void)audioInterruption:',
])
harness += r'''
@end
int main() { @autoreleasepool {
  GalaxyPadCoreHost *host=[GalaxyPadCoreHost new];
  host->_busy=YES; host->_interrupted=YES;
  succeeds=YES;
  assert(![host resumeInterruptedAudio] && attempts==0); // Background cannot steal audio.
  host->_active=YES; host->_pauseRequested=YES;
  assert(![host resumeInterruptedAudio] && attempts==0); // Preserve explicit app pause.
  host->_pauseRequested=NO; succeeds=NO;
  assert(![host resumeInterruptedAudio]);
  assert(host->_interrupted && !host->_audioActive && host->resets==0);
  // Missing ended notification: explicit resume retries, clears stale inputs,
  // and reconciles runtime only after successful session acquisition.
  succeeds=YES;
  assert([host resumeInterruptedAudio]);
  assert(!host->_interrupted && host->_audioActive && host->resets==1 && host->reconciles==1);
  unsigned before=attempts;
  assert([host resumeInterruptedAudio] && attempts==before); // Ordinary pause path unchanged.
  host->_interrupted=YES; host->_audioActive=NO; succeeds=NO;
  [host setApplicationActive:YES];
  assert(host->_interrupted && !host->_audioActive); // Foreground alone cannot clear latch.
  succeeds=YES; [host setApplicationActive:YES];
  assert(!host->_interrupted && host->_audioActive);
  host->_interrupted=YES; host->_audioActive=NO;
  [host setNativeUIBlocked:YES pauseRuntime:YES];
  assert(host->_interrupted);
  [host setNativeUIBlocked:NO pauseRuntime:NO];
  assert(!host->_interrupted && host->_audioActive); // Visible native Resume recovers too.
  host->_interrupted=YES; host->_audioActive=NO;
  before=attempts;
  [host setNativeUIBlocked:NO pauseRuntime:NO];
  assert(host->_interrupted && attempts==before); // Ordinary reconciliation doesn't retry.
  [host audioInterruption:[NSNotification notificationWithName:@"audio" object:nil
      userInfo:@{AVAudioSessionInterruptionTypeKey:@1}]];
  [NSRunLoop.mainRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.02]];
  assert(host->_interrupted && !host->_audioActive);
  succeeds=NO;
  [host audioInterruption:[NSNotification notificationWithName:@"audio" object:nil
      userInfo:@{AVAudioSessionInterruptionTypeKey:@0}]];
  [NSRunLoop.mainRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.02]];
  assert(host->_interrupted && !host->_audioActive); // Ended alone cannot clear latch either.
  succeeds=YES;
  [host audioInterruption:[NSNotification notificationWithName:@"audio" object:nil
      userInfo:@{AVAudioSessionInterruptionTypeKey:@0}]];
  [NSRunLoop.mainRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.02]];
  assert(!host->_interrupted && host->_audioActive);
  puts("PASS: audio interruption explicit/foreground/native resume, failed acquisition, pause/background guards");
} }
'''
with tempfile.TemporaryDirectory(prefix='galaxypad-audio-recovery-') as directory:
    unit = Path(directory) / 'test.mm'
    executable = Path(directory) / 'test'
    unit.write_text(harness)
    subprocess.run(['xcrun', 'clang++', '-std=c++23', '-fobjc-arc', '-fblocks', '-Wall', '-Wextra',
                    str(unit), '-framework', 'Foundation', '-o', str(executable)], check=True)
    subprocess.run([str(executable)], check=True)
