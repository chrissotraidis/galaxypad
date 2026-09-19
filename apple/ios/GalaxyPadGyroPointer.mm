// SPDX-License-Identifier: GPL-3.0-or-later
#import "GalaxyPadGyroPointer.h"
#import <CoreMotion/CoreMotion.h>
#import <QuartzCore/QuartzCore.h>
#import "../shared/GalaxyPadSettings.h"
#include "../shared/GalaxyPadGyroAim.h"

@implementation GalaxyPadGyroPointer {
  CMMotionManager *_motion;
  GCMotion *_controllerMotion;
  NSTimer *_timer;
  galaxypad::GyroAim _aim;
  NSInteger _source;
  uint64_t _generation;
  UIInterfaceOrientation _lastOrientation;
  double _lastTick, _controllerSampleTime;
  double _controllerPitch, _controllerYaw;
  float _stickX,_stickY;
  BOOL _recenterHeld,_touchHeld,_activatedControllerSensors,_hasAim;
  NSString *_status;
}
- (instancetype)init {
  if ((self=[super init])) { _motion=[CMMotionManager new]; _source=-1; }
  return self;
}
- (void)start {
  if (_timer) return;
  __weak GalaxyPadGyroPointer *weakSelf=self;
  _timer=[NSTimer timerWithTimeInterval:1.0/60 repeats:YES block:^(NSTimer *timer) {
    GalaxyPadGyroPointer *host=weakSelf;
    if (!host) { [timer invalidate]; return; }
    [host tick];
  }];
  [NSRunLoop.mainRunLoop addTimer:_timer forMode:NSRunLoopCommonModes];
}
- (void)stopSensors {
  ++_generation;
  [_motion stopDeviceMotionUpdates];
  _controllerMotion.valueChangedHandler=nil;
  if (_activatedControllerSensors) _controllerMotion.sensorsActive=NO;
  _activatedControllerSensors=NO;
  _controllerMotion=nil;
  _controllerSampleTime=0;
}
- (void)dealloc { [_timer invalidate]; [self stopSensors]; }
- (void)reset {
  [self stopSensors];
  _source=-1; _lastTick=0; _lastOrientation=UIInterfaceOrientationUnknown;
  _stickX=_stickY=0; _touchHeld=NO; _recenterHeld=NO;
  _aim.reset(); _hasAim=NO;
  if (self.inputChanged) self.inputChanged({});
}
- (void)recenter { _aim.reset(); }
- (void)setStickX:(float)x y:(float)y recenter:(BOOL)recenter {
  _stickX=x; _stickY=y;
  if (recenter && !_recenterHeld) [self recenter];
  _recenterHeld=recenter;
}
- (void)acceptTouch:(galaxypad::InputState)state {
  _touchHeld=state.pointerContact && state.pointerVisible;
  if (_touchHeld) _aim.anchor(state.pointerX,state.pointerY);
}
- (void)report:(NSString *)status {
  if ([_status isEqualToString:status]) return;
  _status=[status copy];
  if (self.statusChanged) self.statusChanged(status);
}
- (void)tick {
  NSAssert(NSThread.isMainThread,@"Motion API requires main thread");
  GalaxyPadSettings *settings=GalaxyPadSettings.sharedSettings;
  NSInteger source=settings.gyroPointerSource;
  BOOL allowed=self.inputAllowed && self.inputAllowed();
  if (!allowed || source==GalaxyPadGyroPointerOff) {
    if (_source!=-1) [self reset];
    [self report:source==GalaxyPadGyroPointerOff ? @"Off" : @"Paused — resumes during normal gameplay"];
    return;
  }
  if (_source!=source) { [self reset]; _source=source; }
  const double now=CACurrentMediaTime();
  double dt=_lastTick ? now-_lastTick : 0; _lastTick=now;
  double pitch=0,yaw=0,sampleTime=0;
  if (source==GalaxyPadGyroPointerDevice) {
    if (!_motion.deviceMotionAvailable) {
      [self report:@"Device motion unavailable — touch and stick still work"];
      if (self.inputChanged) self.inputChanged({});
      return;
    }
    if (!_motion.deviceMotionActive) {
      _motion.deviceMotionUpdateInterval=1.0/60;
      [_motion startDeviceMotionUpdates];
    }
    UIInterfaceOrientation orientation=self.orientation?self.orientation():UIInterfaceOrientationUnknown;
    if (orientation!=_lastOrientation) { _aim.reset(); _lastOrientation=orientation; }
    CMDeviceMotion *sample=_motion.deviceMotion;
    auto axes=galaxypad::GyroAim::Orientation::Portrait;
    if (orientation==UIInterfaceOrientationLandscapeLeft) axes=galaxypad::GyroAim::Orientation::LandscapeLeft;
    else if (orientation==UIInterfaceOrientationLandscapeRight) axes=galaxypad::GyroAim::Orientation::LandscapeRight;
    else if (orientation==UIInterfaceOrientationPortraitUpsideDown) axes=galaxypad::GyroAim::Orientation::UpsideDown;
    galaxypad::GyroAim::screenRates(sample.rotationRate.x,sample.rotationRate.y,axes,pitch,yaw);
    sampleTime=sample.timestamp;
  } else {
    GCController *owner=self.controller?self.controller():nil;
    GCMotion *motion=owner.motion;
    if (motion!=_controllerMotion) {
      [self stopSensors]; _aim.reset(); _hasAim=NO;
      if (motion.hasRotationRate) {
        _controllerMotion=motion;
        __weak GalaxyPadGyroPointer *weakSelf=self;
        const uint64_t generation=_generation;
        motion.valueChangedHandler=^(GCMotion *sample) {
          // GameController's owner uses the main handler queue. Marshal anyway
          // for injected/test controllers, and reject callbacks from old owners.
          const GCRotationRate rate=sample.rotationRate;
          const GCAcceleration gravity=sample.gravity;
          const double length=std::sqrt(gravity.x*gravity.x+gravity.y*gravity.y+gravity.z*gravity.z);
          const double yaw=sample.hasGravityAndUserAcceleration && std::isfinite(length) && length>.5
            ? -(rate.x*gravity.x+rate.y*gravity.y+rate.z*gravity.z)/length : rate.y;
          const double time=CACurrentMediaTime();
          dispatch_async(dispatch_get_main_queue(),^{
            GalaxyPadGyroPointer *host=weakSelf;
            if (!host || host->_controllerMotion!=sample || host->_generation!=generation) return;
            host->_controllerPitch=rate.x; host->_controllerYaw=yaw;
            host->_controllerSampleTime=time;
          });
        };
        if (motion.sensorsRequireManualActivation && !motion.sensorsActive) {
          _activatedControllerSensors=YES;
          motion.sensorsActive=YES;
        }
      }
    }
    if (!_controllerMotion) {
      [self report:@"Controller gyro unavailable — touch and stick still work"];
      if (self.inputChanged) self.inputChanged({});
      return;
    }
    pitch=_controllerPitch; yaw=_controllerYaw; sampleTime=_controllerSampleTime;
  }
  BOOL fresh=_aim.sample(_touchHeld?0:pitch,_touchHeld?0:yaw,sampleTime,now,
                         settings.gyroPointerSensitivity,settings.gyroPointerInvertY);
  if (!fresh) {
    [self report:@"Waiting for motion — touch and stick still work"];
    // Retain the last cursor position, never the last angular velocity. Once
    // gyro owns aim, keep stick adjustment here during a sensor gap to avoid
    // jumping back to the controller's independent cursor position.
    if (!_hasAim) {
      if (self.inputChanged) self.inputChanged({});
      return;
    }
  } else {
    _hasAim=YES;
  }
  if (!_touchHeld) _aim.stick(_stickX,_stickY,dt);
  galaxypad::InputState state;
  state.pointerX=_aim.x(); state.pointerY=_aim.y(); state.pointerVisible=true;
  if (self.inputChanged) self.inputChanged(state);
  if (fresh) [self report:source==GalaxyPadGyroPointerDevice ? @"Move this device to aim" : @"Move the controller to aim"];
}
@end
