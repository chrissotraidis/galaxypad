// SPDX-License-Identifier: GPL-3.0-or-later
// Adapted from SunPad fcdc1411e483a86ca80ec82e7cd53839c51ff865,
// SunPadGameViewController controller callbacks and authoritative reconciliation.
#import "GalaxyPadControllers.h"
#import <GameController/GameController.h>
#import <QuartzCore/QuartzCore.h>
#include "../shared/GalaxyPadControllerSlots.h"
#include "../shared/GalaxyPadControllerInput.h"
#import "../shared/GalaxyPadControllerMappingStore.h"

@implementation GalaxyPadControllers {
  GalaxyPadControllerSlots _slots;
  galaxypad::ControllerInput _input;
  GCController *_owner;
  NSTimer *_timer;
  CFTimeInterval _lastTick, _lastReconcile;
}
- (void)start {
  NSAssert(NSThread.isMainThread, @"Controller API requires main thread");
  if (_timer) return;
  [self reloadMapping];
  [NSNotificationCenter.defaultCenter addObserver:self selector:@selector(connectionChanged:)
    name:GCControllerDidConnectNotification object:nil];
  [NSNotificationCenter.defaultCenter addObserver:self selector:@selector(connectionChanged:)
    name:GCControllerDidDisconnectNotification object:nil];
  [self reconcile];
  _lastTick = CACurrentMediaTime();
  __weak GalaxyPadControllers *weakSelf = self;
  _timer = [NSTimer timerWithTimeInterval:1.0/60.0 repeats:YES block:^(NSTimer *timer) {
    GalaxyPadControllers *host = weakSelf;
    if (!host) { [timer invalidate]; return; }
    CFTimeInterval now = CACurrentMediaTime();
    float seconds = (float)(now-host->_lastTick);
    host->_lastTick=now;
    if (now-host->_lastReconcile>=1) [host reconcile];
    [host publishWithSeconds:seconds];
  }];
  [NSRunLoop.mainRunLoop addTimer:_timer forMode:NSRunLoopCommonModes];
}
- (void)dealloc {
  [_timer invalidate];
  _owner.extendedGamepad.valueChangedHandler=nil;
  _owner.playerIndex=GCControllerPlayerIndexUnset;
  [NSNotificationCenter.defaultCenter removeObserver:self];
}
- (void)reset { _input.reset(); }
- (void)reloadMapping { _input.setMapping(GalaxyPadControllerMappingStore.mapping); }
- (void)connectionChanged:(NSNotification *)notification {
  (void)notification;
  if (NSThread.isMainThread) [self reconcile];
  else dispatch_async(dispatch_get_main_queue(), ^{ [self reconcile]; });
}
- (void)reconcile {
  NSAssert(NSThread.isMainThread, @"Controller API requires main thread");
  _lastReconcile=CACurrentMediaTime();
  NSArray<GCController *> *controllers=GCController.controllers;
  std::vector<uintptr_t> instances;
  for (GCController *controller in controllers)
    if (controller.extendedGamepad) instances.push_back((uintptr_t)(__bridge void *)controller);
  _slots.Reconcile(instances);
  GCController *next=nil;
  for (GCController *controller in controllers)
    if ((uintptr_t)(__bridge void *)controller==_slots.InstanceAt(0)) { next=controller; break; }
  if (next==_owner) return;
  _owner.extendedGamepad.valueChangedHandler=nil;
  _owner.playerIndex=GCControllerPlayerIndexUnset;
  _owner=next;
  [self reset];
  if (self.ownershipChanged) self.ownershipChanged();
  if (self.inputChanged) self.inputChanged({});
  if (!_owner) return;
  _owner.playerIndex=GCControllerPlayerIndex1;
  _owner.handlerQueue=dispatch_get_main_queue();
  __weak GalaxyPadControllers *weakSelf=self;
  __weak GCController *weakOwner=_owner;
  _owner.extendedGamepad.valueChangedHandler=^(GCExtendedGamepad *pad, GCControllerElement *element) {
    (void)pad; (void)element;
    GalaxyPadControllers *host=weakSelf;
    GCController *controller=weakOwner;
    if (!host || !controller || host->_owner!=controller) return;
    // Never let a queued event from an unlisted/disconnected controller revive input.
    if ([GCController.controllers indexOfObjectIdenticalTo:controller]==NSNotFound) {
      [host reconcile]; return;
    }
    [host publishWithSeconds:0]; // button edges now, pointer integration only on ticks
  };
}
- (void)publishWithSeconds:(float)seconds {
  if (!_owner) return;
  if ([GCController.controllers indexOfObjectIdenticalTo:_owner]==NSNotFound) {
    [self reconcile]; return;
  }
  if (!self.inputAllowed || !self.inputAllowed()) { [self reset]; return; }
  GCExtendedGamepad *pad=_owner.extendedGamepad;
  if (!pad) { [self reconcile]; return; }
  galaxypad::ControllerSnapshot snapshot;
  snapshot.a=pad.buttonA.isPressed; snapshot.b=pad.buttonB.isPressed;
  snapshot.x=pad.buttonX.isPressed; snapshot.y=pad.buttonY.isPressed;
  snapshot.leftShoulder=pad.leftShoulder.isPressed; snapshot.rightShoulder=pad.rightShoulder.isPressed;
  snapshot.leftTrigger=pad.leftTrigger.isPressed; snapshot.rightTrigger=pad.rightTrigger.isPressed;
  snapshot.menu=pad.buttonMenu.isPressed; snapshot.options=pad.buttonOptions.isPressed;
  snapshot.recenter=pad.rightThumbstickButton.isPressed;
  snapshot.up=pad.dpad.up.isPressed; snapshot.down=pad.dpad.down.isPressed;
  snapshot.left=pad.dpad.left.isPressed; snapshot.right=pad.dpad.right.isPressed;
  snapshot.moveX=pad.leftThumbstick.xAxis.value; snapshot.moveY=pad.leftThumbstick.yAxis.value;
  snapshot.rightX=pad.rightThumbstick.xAxis.value; snapshot.rightY=pad.rightThumbstick.yAxis.value;
  auto state=_input.update(snapshot,seconds);
  if (self.inputChanged) self.inputChanged(state);
}
@end
