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
  __weak GCController *_disconnectedOwner;
  GCExtendedGamepad *_ownerPad;
  uint64_t _ownerGeneration;
  uint64_t _tickCount, _callbackCount;
  NSTimer *_timer;
  CFTimeInterval _lastTick, _lastReconcile;
  uint32_t _lastRawButtons;
  BOOL _menuPressed, _optionsPressed, _guestPlusHeld;
  BOOL _reportedReadiness, _lastReady;
  CFTimeInterval _guestPlusUntil;
}
- (NSString *)diagnosticSnapshot {
  NSAssert(NSThread.isMainThread, @"Controller API requires main thread");
  GCExtendedGamepad *pad=_owner.extendedGamepad;
  const BOOL listed=_owner &&
      [GCController.controllers indexOfObjectIdenticalTo:_owner]!=NSNotFound;
  id<GCDevicePhysicalInputState> live=nil;
  if (@available(iOS 17.0, macOS 14.0, tvOS 17.0, *)) live=_owner.input;
  id<GCButtonElement> liveA=live.buttons[GCInputButtonA];
  id<GCButtonElement> liveB=live.buttons[GCInputButtonB];
  id<GCDirectionPadElement> move=live.dpads[GCInputLeftThumbstick];
  id<GCDirectionPadElement> aim=live.dpads[GCInputRightThumbstick];
  return [NSString stringWithFormat:
    @"controller_snapshot owner=%d listed=%d is_snapshot=%d timer_valid=%d ticks=%llu callbacks=%llu gameplay_allowed=%d pause_allowed=%d profile_matches=%d handlers=%d%d%d legacy_a=%d legacy_b=%d legacy_move=(%.3f,%.3f) legacy_aim=(%.3f,%.3f) legacy_event=%.6f live_available=%d live_elements=%d%d%d%d live_a=%d live_b=%d live_move=(%.3f,%.3f) live_aim=(%.3f,%.3f) live_event=%.6f",
    _owner!=nil, listed, _owner.isSnapshot, _timer.isValid,
    (unsigned long long)_tickCount, (unsigned long long)_callbackCount,
    self.inputAllowed && self.inputAllowed(), self.pauseToggleAllowed && self.pauseToggleAllowed(),
    pad==_ownerPad, pad.valueChangedHandler!=nil,
    pad.buttonMenu.pressedChangedHandler!=nil, pad.buttonOptions.pressedChangedHandler!=nil,
    pad.buttonA.isPressed, pad.buttonB.isPressed,
    pad.leftThumbstick.xAxis.value, pad.leftThumbstick.yAxis.value,
    pad.rightThumbstick.xAxis.value, pad.rightThumbstick.yAxis.value, pad.lastEventTimestamp,
    live!=nil, liveA!=nil, liveB!=nil, move!=nil, aim!=nil,
    liveA.pressedInput.isPressed, liveB.pressedInput.isPressed,
    move.xAxis.value, move.yAxis.value, aim.xAxis.value, aim.yAxis.value, live.lastEventTimestamp];
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
    ++host->_tickCount;
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
  _ownerPad.valueChangedHandler=nil;
  _ownerPad.buttonMenu.pressedChangedHandler=nil;
  _ownerPad.buttonOptions.pressedChangedHandler=nil;
  _owner.playerIndex=GCControllerPlayerIndexUnset;
  [NSNotificationCenter.defaultCenter removeObserver:self];
}
- (GCController *)motionController { return _owner; }
- (void)reset {
  if (self.aimChanged) self.aimChanged(0,0,NO);
  _input.reset();
  _guestPlusHeld = NO;
  _guestPlusUntil = 0;
  _lastRawButtons = 0;
  _reportedReadiness = NO;
  // Keep event-time pause-button state across UI resets. Re-reading the live
  // snapshot here can erase a queued press and turn one hold into two toggles.
}
- (void)reloadMapping { _input.setMapping(GalaxyPadControllerMappingStore.mapping); }
- (void)connectionChanged:(NSNotification *)notification {
  if (!NSThread.isMainThread) {
    dispatch_async(dispatch_get_main_queue(), ^{ [self connectionChanged:notification]; });
    return;
  }
  GCController *controller=notification.object;
  const BOOL disconnected=[notification.name isEqualToString:GCControllerDidDisconnectNotification];
  if (disconnected && controller==_owner) _disconnectedOwner=controller;
  if (!disconnected && controller==_disconnectedOwner) _disconnectedOwner=nil;
  // Enumeration may briefly retain a disconnected object, or reuse the same
  // profile on reconnect. The explicit event must still clear held input and
  // invalidate callbacks from the previous connection.
  [self reconcileForcingOwner:(!disconnected && controller==_owner)];
}
- (void)reconcile { [self reconcileForcingOwner:NO]; }
- (void)reconcileForcingOwner:(BOOL)force {
  NSAssert(NSThread.isMainThread, @"Controller API requires main thread");
  _lastReconcile=CACurrentMediaTime();
  NSArray<GCController *> *controllers=GCController.controllers;
  std::vector<uintptr_t> instances;
  for (GCController *controller in controllers)
    if (controller != _disconnectedOwner && controller.extendedGamepad) instances.push_back((uintptr_t)(__bridge void *)controller);
  _slots.Reconcile(instances);
  GCController *next=nil;
  for (GCController *controller in controllers)
    if ((uintptr_t)(__bridge void *)controller==_slots.InstanceAt(0)) { next=controller; break; }
  GCExtendedGamepad *nextPad=next.extendedGamepad;
  const BOOL sameOwner = next == _owner;
  // A sleeping/reconnected controller can retain its identity while its
  // profile or handlers change. Repair that boundary without resetting intact
  // handlers on the periodic poll: their queued Menu/View edges remain valid.
  const BOOL handlersIntact = nextPad && nextPad.valueChangedHandler &&
      nextPad.buttonMenu.pressedChangedHandler &&
      (!nextPad.buttonOptions || nextPad.buttonOptions.pressedChangedHandler);
  if (!force && sameOwner && nextPad == _ownerPad && (!next || handlersIntact)) return;
  if (sameOwner)
    GalaxyPadLog(@"controller recovery: profile_changed=%d handlers_intact=%d",
      nextPad != _ownerPad, handlersIntact);
  _ownerPad.valueChangedHandler=nil;
  _ownerPad.buttonMenu.pressedChangedHandler=nil;
  _ownerPad.buttonOptions.pressedChangedHandler=nil;
  _owner.playerIndex=GCControllerPlayerIndexUnset;
  _owner=next;
  _ownerPad=nextPad;
  ++_ownerGeneration;
  // A newly owned controller may already be held: require its release first.
  // A neutral initial snapshot arms the very first press without a prior event.
  _menuPressed=_owner.extendedGamepad.buttonMenu.isPressed;
  _optionsPressed=_owner.extendedGamepad.buttonOptions.isPressed;
  GalaxyPadLog(@"controller ownership: connected=%d extended_controllers=%lu right_stick=pointer speed=1.2x right_stick_click=recenter RB=A RT=B LB=tilt Menu=game_Plus View=app_pause",
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
    ++host->_callbackCount;
    if ([GCController.controllers indexOfObjectIdenticalTo:controller]==NSNotFound) {
      [host reconcile]; return;
    }
    // Use the event's pressed argument. The live isPressed snapshot may already
    // be released when a quick tap's queued main-thread callback executes.
    GCExtendedGamepad *pad=host->_ownerPad;
    if (button==pad.buttonMenu) {
      const BOOL wasPressed=host->_menuPressed;
      host->_menuPressed=pressed;
      if (!pressed) host->_guestPlusHeld=NO;
      else if (!wasPressed && host.inputAllowed && host.inputAllowed()) {
        host->_guestPlusHeld=YES;
        // Preserve a quick queued tap long enough for the guest input poll.
        // The physical hold may last longer; modal/lifecycle reset cancels it.
        host->_guestPlusUntil=CACurrentMediaTime()+0.75;
      }
      [host publishWithSeconds:0];
      return;
    }
    if (button!=pad.buttonOptions) return;
    const BOOL wasPressed=host->_optionsPressed;
    host->_optionsPressed=pressed;
    if (!pressed || wasPressed || !host.pauseRequested ||
        !host.pauseToggleAllowed || !host.pauseToggleAllowed()) return;
    GalaxyPadLog(@"controller native pause requested source=View/Options");
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
    ++host->_callbackCount;
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
  // Native pause blocks gameplay, but its View/Options release and next press
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
  auto logRaw = [&](BOOL connected) {
    if (rawButtons != _lastRawButtons) {
      GalaxyPadLog(@"controller raw_buttons=%u menu=%d options=%d snapshot_neutral=%d pause_buttons_released=%d gameplay_allowed=%d pause_allowed=%d input_connected=%d move=(%.3f,%.3f) aim=(%.3f,%.3f)",
        rawButtons, (rawButtons & 256u) != 0, (rawButtons & 512u) != 0,
        neutral, !(_menuPressed || _optionsPressed), gameplayAllowed, pauseAllowed, connected,
        pad.leftThumbstick.xAxis.value, pad.leftThumbstick.yAxis.value,
        pad.rightThumbstick.xAxis.value, pad.rightThumbstick.yAxis.value);
    }
    _lastRawButtons = rawButtons;
  };
  // Menu/Options pause edges belong exclusively to pressedChangedHandler.
  // Snapshot polling must not re-arm a held event or deliver the same edge twice.
  if (!gameplayAllowed) { _input.reset(); logRaw(NO); return; }
  galaxypad::ControllerSnapshot snapshot;
  snapshot.a=pad.buttonA.isPressed; snapshot.b=pad.buttonB.isPressed;
  snapshot.x=pad.buttonX.isPressed; snapshot.y=pad.buttonY.isPressed;
  snapshot.leftShoulder=pad.leftShoulder.isPressed; snapshot.rightShoulder=pad.rightShoulder.isPressed;
  snapshot.leftTrigger=pad.leftTrigger.isPressed; snapshot.rightTrigger=pad.rightTrigger.isPressed;
  // Event handlers own Menu and View. General snapshots cannot revive a
  // consumed modal press or lose a quick tap that is already released.
  snapshot.menu=false; snapshot.options=false;
  snapshot.recenter=pad.rightThumbstickButton.isPressed;
  snapshot.up=pad.dpad.up.isPressed; snapshot.down=pad.dpad.down.isPressed;
  snapshot.left=pad.dpad.left.isPressed; snapshot.right=pad.dpad.right.isPressed;
  snapshot.moveX=pad.leftThumbstick.xAxis.value; snapshot.moveY=pad.leftThumbstick.yAxis.value;
  snapshot.rightX=pad.rightThumbstick.xAxis.value; snapshot.rightY=pad.rightThumbstick.yAxis.value;
  auto state=_input.update(snapshot,seconds);
  if (self.aimChanged) self.aimChanged(state.connected && !snapshot.leftShoulder ? snapshot.rightX : 0,
    state.connected && !snapshot.leftShoulder ? snapshot.rightY : 0,state.connected && snapshot.recenter);
  if (!_reportedReadiness || _lastReady != state.connected) {
    GalaxyPadLog(@"controller input ready=%d raw_buttons=%u move=(%.3f,%.3f) aim=(%.3f,%.3f) profile=%@",
      state.connected, rawButtons, snapshot.moveX, snapshot.moveY,
      snapshot.rightX, snapshot.rightY, NSStringFromClass(pad.class));
    _reportedReadiness=YES;
    _lastReady=state.connected;
  }
  if (_guestPlusHeld || CACurrentMediaTime() < _guestPlusUntil) {
    state.connected=true;
    state.buttons |= galaxypad::Plus;
  }
  logRaw(state.connected);
  if (self.inputChanged) self.inputChanged(state);
}
@end
