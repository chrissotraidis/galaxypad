// SPDX-License-Identifier: GPL-3.0-or-later
#include "../apple/ios/GalaxyPadSimulatorInput.h"
#include <cassert>
#include <cstdio>
int main() { @autoreleasepool {
  NSString *path=[NSTemporaryDirectory() stringByAppendingPathComponent:NSUUID.UUID.UUIDString];
  auto write=[&](NSDictionary *value) {
    NSData *data=[NSJSONSerialization dataWithJSONObject:value options:0 error:nil];
    assert([data writeToFile:path atomically:YES]);
  };
  write(@{@"issued":@100, @"expires":@101, @"buttons":@3,
    @"pointerVisible":@YES, @"pointerX":@0.75, @"moveY":@1});
  auto input=GalaxyPadReadSimulatorInput(path,100.5,99);
  assert(input.buttons==(galaxypad::A|galaxypad::B) && input.pointerVisible && input.pointerX==0.75 && input.moveY==1);
  assert(!GalaxyPadReadSimulatorInput(path,101,99).connected); // expired
  assert(!GalaxyPadReadSimulatorInput(path,100.5,100).connected); // reset
  assert(!GalaxyPadReadSimulatorInput(path,99.5,99).connected); // future
  for (NSDictionary *bad in @[
    @{@"issued":@100,@"expires":@103},
    @{@"issued":@100,@"expires":@101,@"buttons":@1.5},
    @{@"issued":@100,@"expires":@101,@"buttons":@8192},
    @{@"issued":@100,@"expires":@101,@"pointerX":@2},
    @{@"issued":@100,@"expires":@101,@"moveY":@"bad"},
    @{@"issued":@100,@"expires":@101,@"pointerVisible":@2}]) {
    write(bad); assert(!GalaxyPadReadSimulatorInput(path,100.5,99).connected);
  }
  [@"invalid" writeToFile:path atomically:YES encoding:NSUTF8StringEncoding error:nil];
  assert(!GalaxyPadReadSimulatorInput(path,100.5,99).connected);
  [NSFileManager.defaultManager removeItemAtPath:path error:nil];
  assert(!GalaxyPadReadSimulatorInput(path,100.5,99).connected);
  puts("Simulator input lease, reset, chord, axes and malformed-input checks pass");
} }
