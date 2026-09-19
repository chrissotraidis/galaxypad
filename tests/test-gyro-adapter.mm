// SPDX-License-Identifier: GPL-3.0-or-later
// Headless Simulator test. Fake sensor samples exercise the production adapter;
// this process has its own defaults domain and never installs/replaces GalaxyPad.
#import "../apple/ios/GalaxyPadGyroPointer.h"
#import "../apple/shared/GalaxyPadSettings.h"
#import <CoreMotion/CoreMotion.h>
#import <QuartzCore/QuartzCore.h>
#include <cassert>
#include <cstdio>
@interface GalaxyPadGyroPointer (TestAccess)
- (void)tick;
@end
@interface MotionSample : CMDeviceMotion
@property CMRotationRate rate;
@property NSTimeInterval time;
@end
@implementation MotionSample
- (CMRotationRate)rotationRate { return _rate; }
- (NSTimeInterval)timestamp { return _time; }
@end
@interface MotionManager : CMMotionManager
@property BOOL available;
@property BOOL running;
@property(nonatomic,strong) MotionSample *sample;
@end
@implementation MotionManager
- (BOOL)isDeviceMotionAvailable { return _available; }
- (BOOL)isDeviceMotionActive { return _running; }
- (CMDeviceMotion *)deviceMotion { return _sample; }
- (void)startDeviceMotionUpdates { _running=YES; }
- (void)stopDeviceMotionUpdates { _running=NO; }
@end
@interface ControllerMotion : NSObject
@property BOOL hasRotationRate;
@property BOOL hasGravityAndUserAcceleration;
@property BOOL sensorsRequireManualActivation;
@property BOOL sensorsActive;
@property GCRotationRate rotationRate;
@property GCAcceleration gravity;
@property(nonatomic,copy) GCMotionValueChangedHandler valueChangedHandler;
@end
@implementation ControllerMotion
@end
@interface MotionOwner : NSObject
@property(nonatomic,strong) ControllerMotion *motion;
@end
@implementation MotionOwner
@end
static void drain() { CFRunLoopRunInMode(kCFRunLoopDefaultMode,.005,false); }
int main() { @autoreleasepool {
  GalaxyPadSettings *settings=GalaxyPadSettings.sharedSettings;
  settings.gyroPointerSource=GalaxyPadGyroPointerDevice;
  settings.gyroPointerSensitivity=1;settings.gyroPointerInvertY=NO;
  MotionManager *manager=[MotionManager new];manager.available=YES;
  manager.sample=[MotionSample new];manager.sample.time=CACurrentMediaTime()-.1;
  GalaxyPadGyroPointer *adapter=[GalaxyPadGyroPointer new];
  [adapter setValue:manager forKey:@"motion"];
  __block BOOL allowed=YES;
  __block UIInterfaceOrientation orientation=UIInterfaceOrientationPortrait;
  __block galaxypad::InputState output;
  __block NSString *status;
  adapter.inputAllowed=^BOOL { return allowed; };
  adapter.orientation=^UIInterfaceOrientation { return orientation; };
  adapter.inputChanged=^(galaxypad::InputState state) { output=state; };
  adapter.statusChanged=^(NSString *text) { status=text; };
  [adapter tick];assert(manager.running && output.pointerVisible && output.pointerX==.5);
  manager.sample.rate={0,-1,0};manager.sample.time+=.05;
  [adapter tick];assert(output.pointerX>.54 && !output.buttons);
  float previous=output.pointerX;[adapter tick];assert(output.pointerX==previous);
  galaxypad::InputState touch;touch.pointerContact=touch.pointerVisible=true;
  touch.pointerX=.2;touch.pointerY=.8;[adapter acceptTouch:touch];
  manager.sample.time+=.01;[adapter tick];assert(output.pointerX==.2f && output.pointerY==.8f);
  touch.pointerContact=false;[adapter acceptTouch:touch];
  manager.sample.time+=.01;[adapter tick];assert(output.pointerX>.2f && output.pointerX<.23f);
  [adapter setStickX:0 y:0 recenter:YES];[adapter tick];assert(output.pointerX==.5);
  manager.sample.time+=.01;[adapter tick];assert(output.pointerX>.5);
  [adapter setStickX:0 y:0 recenter:YES];[adapter tick];assert(output.pointerX>.5); // one reset per press
  orientation=UIInterfaceOrientationLandscapeRight;[adapter tick];assert(output.pointerX==.5);
  manager.sample.time=CACurrentMediaTime()-.4;[adapter tick];
  assert(output.pointerVisible && output.pointerX==.5f && [status containsString:@"Waiting"]);
  allowed=NO;[adapter tick];assert(!manager.running && !output.pointerVisible);
  allowed=YES;manager.available=NO;[adapter tick];
  assert(!output.pointerVisible && [status containsString:@"unavailable"]);
  settings.gyroPointerSource=GalaxyPadGyroPointerController;
  MotionOwner *owner=[MotionOwner new];owner.motion=[ControllerMotion new];
  owner.motion.hasRotationRate=YES;owner.motion.sensorsRequireManualActivation=YES;
  adapter.controller=^GCController * { return (GCController *)owner; };
  [adapter tick];assert(owner.motion.sensorsActive && owner.motion.valueChangedHandler);
  auto queued=owner.motion.valueChangedHandler;
  owner.motion.rotationRate={0,-1,0};queued((GCMotion *)owner.motion);drain();
  [adapter tick];assert(output.pointerVisible);
  // A callback queued before reset must not revive the same reconnected object.
  [adapter reset];[adapter tick];
  queued((GCMotion *)owner.motion);drain();[adapter tick];assert(!output.pointerVisible);
  owner.motion.valueChangedHandler((GCMotion *)owner.motion);drain();
  [adapter tick];assert(output.pointerVisible);
  settings.gyroPointerSource=GalaxyPadGyroPointerOff;[adapter tick];
  assert(!owner.motion.sensorsActive && !owner.motion.valueChangedHandler && !output.pointerVisible);
  // Motion sensors already enabled by another owner must not be disabled by us.
  owner.motion.sensorsActive=YES;settings.gyroPointerSource=GalaxyPadGyroPointerController;
  [adapter tick];[adapter reset];assert(owner.motion.sensorsActive);
  settings.gyroPointerSource=(GalaxyPadGyroPointerSource)99;assert(settings.gyroPointerSource==0);
  settings.gyroPointerSensitivity=NAN;assert(settings.gyroPointerSensitivity==1);
  puts("Gyro adapter: device samples, touch ownership, recenter edges, stale data, pause, unavailable sensors, controller generation and activation pass");
  return 0;
} }
