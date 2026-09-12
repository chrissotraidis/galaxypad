// SPDX-License-Identifier: GPL-3.0-or-later
// Adapted from SunPad fcdc1411e483a86ca80ec82e7cd53839c51ff865,
// SunPadGameViewController controller callbacks and authoritative reconciliation.
#import "GalaxyPadControllers.h"
#import <GameController/GameController.h>
#import <QuartzCore/QuartzCore.h>
#include "../shared/GalaxyPadControllerSlots.h"
#include "../shared/GalaxyPadControllerInput.h"
#import "../shared/GalaxyPadControllerMappingStore.h"
#import "../shared/GalaxyPadDiagnostics.h"

@implementation GalaxyPadControllers {
  GalaxyPadControllerSlots _slots;
  galaxypad::ControllerInput _input;
  GCController *_owner;
  uint64_t _ownerGeneration;
  NSTimer *_timer;
  CFTimeInterval _lastTick, _lastReconcile;
  uint32_t _lastRawButtons;
  BOOL _menuPressed, _optionsPressed;
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
  _owner.extendedGamepad.buttonMenu.pressedChangedHandler=nil;
  _owner.extendedGamepad.buttonOptions.pressedChangedHandler=nil;
  _owner.playerIndex=GCControllerPlayerIndexUnset;
  [NSNotificationCenter.defaultCenter removeObserver:self];
}
- (void)reset {
  _input.reset();
  _lastRawButtons = 0;
  // Keep event-time pause-button state across UI resets. Re-reading the live
  // snapshot here can erase a queued press and turn one hold into two toggles.
}
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
  _owner.extendedGamepad.buttonMenu.pressedChangedHandler=nil;
  _owner.extendedGamepad.buttonOptions.pressedChangedHandler=nil;
  _owner.playerIndex=GCControllerPlayerIndexUnset;
  _owner=next;
  ++_ownerGeneration;
  // A newly owned controller may already be held: require its release first.
  // A neutral initial snapshot arms the very first press without a prior event.
  _menuPressed=_owner.extendedGamepad.buttonMenu.isPressed;
  _optionsPressed=_owner.extendedGamepad.buttonOptions.isPressed;
  GalaxyPadLog(@"controller ownership: connected=%d extended_controllers=%lu right_stick=pointer speed=1.2x right_stick_click=recenter RB=A RT=B LB=tilt Menu=toggle_pause",
    _owner != nil, (unsigned long)instances.size());
  [self reset];
  if (self.ownershipChanged) self.ownershipChanged();
  if (self.inputChanged) self.inputChanged({});
  if (!_owner) return;
  _owner.playerIndex=GCControllerPlayerIndex1;
  _owner.handlerQueue=dispatch_get_main_queue();
  __weak GalaxyPadControllers *weakSelf=self;
  __weak GCController *weakOwner=_owner;
  const uint64_t ownerGeneration=_ownerGeneration;
  GCControllerButtonValueChangedHandler pauseChanged=^(GCControllerButtonInput *button, float value, BOOL pressed) {
    (void)value;
    GalaxyPadControllers *host=weakSelf;
    GCController *controller=weakOwner;
    if (!host || !controller || host->_owner!=controller ||
        host->_ownerGeneration!=ownerGeneration) return;
    if ([GCController.controllers indexOfObjectIdenticalTo:controller]==NSNotFound) {
      [host reconcile]; return;
    }
    // Use the event's pressed argument. The live isPressed snapshot may already
    // be released when a quick tap's queued main-thread callback executes.
    GCExtendedGamepad *pad=controller.extendedGamepad;
    const BOOL wasHeld=host->_menuPressed || host->_optionsPressed;
    if (button==pad.buttonMenu) host->_menuPressed=pressed;
    else if (button==pad.buttonOptions) host->_optionsPressed=pressed;
    else return;
    if (!pressed || wasHeld || !host.pauseRequested ||
        !host.pauseToggleAllowed || !host.pauseToggleAllowed()) return;
    GalaxyPadLog(@"controller native pause requested source=%@",
      button==pad.buttonMenu ? @"Menu" : @"Options");
    [host reset];
    host.pauseRequested();
  };
  _owner.extendedGamepad.buttonMenu.pressedChangedHandler=pauseChanged;
  _owner.extendedGamepad.buttonOptions.pressedChangedHandler=pauseChanged;
  _owner.extendedGamepad.valueChangedHandler=^(GCExtendedGamepad *pad, GCControllerElement *element) {
    (void)pad; (void)element;
    GalaxyPadControllers *host=weakSelf;
    GCController *controller=weakOwner;
    if (!host || !controller || host->_owner!=controller ||
        host->_ownerGeneration!=ownerGeneration) return;
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
  const BOOL gameplayAllowed = self.inputAllowed && self.inputAllowed();
  const BOOL pauseAllowed = self.pauseToggleAllowed && self.pauseToggleAllowed();
  // Native pause blocks gameplay, but its Menu/Options release and next press
  // must still be observed so the same button can resume.
  if (!gameplayAllowed && !pauseAllowed) { [self reset]; return; }
  GCExtendedGamepad *pad=_owner.extendedGamepad;
  if (!pad) { [self reconcile]; return; }
  const uint32_t rawButtons =
      (pad.buttonA.isPressed ? 1u : 0u) |
      (pad.buttonB.isPressed ? 2u : 0u) |
      (pad.buttonX.isPressed ? 4u : 0u) |
      (pad.buttonY.isPressed ? 8u : 0u) |
      (pad.leftShoulder.isPressed ? 16u : 0u) |
      (pad.rightShoulder.isPressed ? 32u : 0u) |
      (pad.leftTrigger.isPressed ? 64u : 0u) |
      (pad.rightTrigger.isPressed ? 128u : 0u) |
      (pad.buttonMenu.isPressed ? 256u : 0u) |
      (pad.buttonOptions.isPressed ? 512u : 0u) |
      (pad.rightThumbstickButton.isPressed ? 1024u : 0u) |
      (pad.dpad.up.isPressed ? 2048u : 0u) |
      (pad.dpad.down.isPressed ? 4096u : 0u) |
      (pad.dpad.left.isPressed ? 8192u : 0u) |
      (pad.dpad.right.isPressed ? 16384u : 0u);
  const BOOL neutral = rawButtons == 0 &&
      pad.leftThumbstick.xAxis.value == 0 && pad.leftThumbstick.yAxis.value == 0 &&
      pad.rightThumbstick.xAxis.value == 0 && pad.rightThumbstick.yAxis.value == 0;
  if (rawButtons != _lastRawButtons) {
    GalaxyPadLog(@"controller raw_buttons=%u menu=%d options=%d neutral=%d ready=%d",
      rawButtons, (rawButtons & 256u) != 0, (rawButtons & 512u) != 0,
      neutral, !(_menuPressed || _optionsPressed));
  }
  // Menu/Options pause edges belong exclusively to pressedChangedHandler.
  // Snapshot polling must not re-arm a held event or deliver the same edge twice.
  _lastRawButtons = rawButtons;
  if (!gameplayAllowed) { _input.reset(); return; }
  galaxypad::ControllerSnapshot snapshot;
  snapshot.a=pad.buttonA.isPressed; snapshot.b=pad.buttonB.isPressed;
  snapshot.x=pad.buttonX.isPressed; snapshot.y=pad.buttonY.isPressed;
  snapshot.leftShoulder=pad.leftShoulder.isPressed; snapshot.rightShoulder=pad.rightShoulder.isPressed;
  snapshot.leftTrigger=pad.leftTrigger.isPressed; snapshot.rightTrigger=pad.rightTrigger.isPressed;
  // These two buttons are reserved for native pause on iOS. A general pad
  // callback may run before the button callback; never leak guest Plus/Minus.
  snapshot.menu=false; snapshot.options=false;
  snapshot.recenter=pad.rightThumbstickButton.isPressed;
  snapshot.up=pad.dpad.up.isPressed; snapshot.down=pad.dpad.down.isPressed;
  snapshot.left=pad.dpad.left.isPressed; snapshot.right=pad.dpad.right.isPressed;
  snapshot.moveX=pad.leftThumbstick.xAxis.value; snapshot.moveY=pad.leftThumbstick.yAxis.value;
  snapshot.rightX=pad.rightThumbstick.xAxis.value; snapshot.rightY=pad.rightThumbstick.yAxis.value;
  auto state=_input.update(snapshot,seconds);
  if (self.inputChanged) self.inputChanged(state);
}
@end
