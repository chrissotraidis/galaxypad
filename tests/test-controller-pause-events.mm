// SPDX-License-Identifier: GPL-3.0-or-later
// Host-side regression of the production iOS adapter, using software GC objects.
#import "../apple/ios/GalaxyPadControllers.h"
#import "../apple/shared/GalaxyPadDiagnostics.h"
#import <GameController/GameController.h>
#import <objc/runtime.h>
#include <cstdio>
#include <cstdlib>
@interface GalaxyPadControllers (EventTestAccess)
- (void)publishWithSeconds:(float)seconds;
- (void)connectionChanged:(NSNotification *)notification;
@end
void GalaxyPadLog(NSString *format, ...) { (void)format; }
static NSArray<GCController *> *listed;
static NSArray<GCController *> *Controllers(id,SEL) { return listed; }
static GCController *profileOwner;
static GCExtendedGamepad *replacementProfile;
static IMP originalProfile;
static GCExtendedGamepad *Profile(id self,SEL selector) {
  if (self==profileOwner && replacementProfile) return replacementProfile;
  return ((GCExtendedGamepad *(*)(id,SEL))originalProfile)(self,selector);
}
static GCControllerButtonInput *NoOptions(id,SEL) { return nil; }
static void Check(bool ok,const char* what) {
  if (!ok) { std::fprintf(stderr,"FAIL: %s\n",what); std::exit(1); }
}
// The pad's live state is deliberately already released when both queued
// events arrive. The old general handler re-reads zero and loses this tap.
static void Event(GCController* c,GCControllerButtonInput* button,BOOL pressed) {
  auto h=button.pressedChangedHandler;
  if(h) h(button,pressed?1:0,pressed);
  else if(c.extendedGamepad.valueChangedHandler)
    c.extendedGamepad.valueChangedHandler(c.extendedGamepad,button);
}
int main() { @autoreleasepool {
  Method enumeration=class_getClassMethod(GCController.class,@selector(controllers));
  IMP original=method_setImplementation(enumeration,(IMP)Controllers);
  GCController *c=[GCController controllerWithExtendedGamepad];
  listed=@[c];
  GalaxyPadControllers *adapter=[GalaxyPadControllers new];
  __block bool paused=false,modal=false;
  __block unsigned toggles=0;
  __block galaxypad::InputState published;
  __weak GalaxyPadControllers* weakAdapter=adapter;
  adapter.pauseToggleAllowed=^BOOL { return !modal; };
  adapter.inputAllowed=^BOOL { return !paused && !modal; };
  adapter.pauseRequested=^{++toggles; paused=!paused; [weakAdapter reset];};
  adapter.inputChanged=^(galaxypad::InputState v){published=v;};
  [adapter reconcile]; [adapter publishWithSeconds:0];
  Event(c,c.extendedGamepad.buttonMenu,YES);
  Event(c,c.extendedGamepad.buttonMenu,NO);
  Check(toggles==0 && !paused && (published.buttons & galaxypad::Plus),
        "queued quick Menu tap sends guest Plus without freezing runtime");
  [NSThread sleepForTimeInterval:0.8]; [adapter publishWithSeconds:0];
  Check(!(published.buttons & galaxypad::Plus),"queued Plus releases after minimum pulse");
  Event(c,c.extendedGamepad.buttonMenu,YES);
  [NSThread sleepForTimeInterval:0.8]; [adapter publishWithSeconds:0];
  Check(published.buttons & galaxypad::Plus,"physical hold survives minimum pulse duration");
  Event(c,c.extendedGamepad.buttonMenu,NO);
  Check(!(published.buttons & galaxypad::Plus),"long physical hold releases immediately");
  [c.extendedGamepad.leftThumbstick.xAxis setValue:0.5];
  Event(c,c.extendedGamepad.buttonOptions,YES); Event(c,c.extendedGamepad.buttonOptions,NO);
  Check(toggles==1 && paused,"View pauses app independently");
  Event(c,c.extendedGamepad.buttonMenu,YES); Event(c,c.extendedGamepad.buttonMenu,NO);
  Check(toggles==1 && paused,"Menu does not escape native pause or inject guest Plus");
  Event(c,c.extendedGamepad.buttonOptions,YES);
  Check(toggles==2 && !paused,"View resumes with held stick");
  [adapter reset]; Event(c,c.extendedGamepad.buttonOptions,YES);
  Check(toggles==2,"reset does not rearm held View");
  Event(c,c.extendedGamepad.buttonOptions,NO);
  modal=true; [adapter reset];
  Event(c,c.extendedGamepad.buttonMenu,YES);
  Event(c,c.extendedGamepad.buttonOptions,YES);
  Check(toggles==2,"modal consumes View");
  modal=false; [adapter publishWithSeconds:0];
  Event(c,c.extendedGamepad.buttonMenu,YES);
  Event(c,c.extendedGamepad.buttonOptions,YES);
  Check(toggles==2 && !(published.buttons & galaxypad::Plus),"held modal keys do not revive");
  Event(c,c.extendedGamepad.buttonMenu,NO);
  Event(c,c.extendedGamepad.buttonOptions,NO);
  Event(c,c.extendedGamepad.buttonMenu,YES);
  Check(published.buttons & galaxypad::Plus,"fresh Menu works even with stick held after reset");
  [adapter reset]; [adapter publishWithSeconds:0];
  Check(!(published.buttons & galaxypad::Plus),"reset cancels active guest hold");
  Event(c,c.extendedGamepad.buttonMenu,YES);
  Check(!(published.buttons & galaxypad::Plus),"held Menu is not rearmed by reset");
  Event(c,c.extendedGamepad.buttonMenu,NO);
  [c.extendedGamepad.leftThumbstick.xAxis setValue:0];
  [adapter publishWithSeconds:0]; [adapter publishWithSeconds:0];
  auto menuHandler=c.extendedGamepad.buttonMenu.pressedChangedHandler;
  c.extendedGamepad.buttonMenu.pressedChangedHandler=nil;
  [c.extendedGamepad.buttonMenu setValue:1]; [adapter publishWithSeconds:0];
  Check(!(published.buttons & galaxypad::Plus),"general snapshot cannot revive consumed Menu");
  [c.extendedGamepad.buttonMenu setValue:0];
  c.extendedGamepad.buttonMenu.pressedChangedHandler=menuHandler;
  auto stale=menuHandler;
  GCController *next=[GCController controllerWithExtendedGamepad];
  [next.extendedGamepad.buttonMenu setValue:1];
  listed=@[next]; [adapter reconcile];
  Check(c.extendedGamepad.buttonMenu.pressedChangedHandler==nil &&
        c.extendedGamepad.buttonOptions.pressedChangedHandler==nil,"old owner clears both handlers");
  stale(c.extendedGamepad.buttonMenu,1,YES);
  Event(next,next.extendedGamepad.buttonMenu,YES);
  Check(!(published.buttons & galaxypad::Plus),"stale callback and initially held owner cannot inject Plus");
  Event(next,next.extendedGamepad.buttonMenu,NO);
  Event(next,next.extendedGamepad.buttonMenu,YES);
  Check(published.buttons & galaxypad::Plus,"reconnected owner accepts fresh Menu");
  Event(next,next.extendedGamepad.buttonMenu,NO);
  [adapter reset];
  auto intact=next.extendedGamepad.buttonMenu.pressedChangedHandler;
  [adapter reconcile];
  Check(next.extendedGamepad.buttonMenu.pressedChangedHandler==intact,
        "periodic reconciliation preserves queued pause handlers");
  Event(next,next.extendedGamepad.buttonOptions,YES);
  unsigned beforeRecovery=toggles;
  [adapter reconcile]; Event(next,next.extendedGamepad.buttonOptions,YES);
  Check(toggles==beforeRecovery,"intact reconciliation cannot rearm queued held View");
  Event(next,next.extendedGamepad.buttonOptions,NO);
  paused=false;
  [next.extendedGamepad.buttonMenu setValue:0];
  auto beforeRepair=next.extendedGamepad.buttonMenu.pressedChangedHandler;
  next.extendedGamepad.valueChangedHandler=nil;
  next.extendedGamepad.buttonOptions.pressedChangedHandler=nil;
  [adapter reconcile];
  Check(next.extendedGamepad.valueChangedHandler &&
        next.extendedGamepad.buttonOptions.pressedChangedHandler,
        "same owner repairs missing handlers after idle");
  beforeRepair(next.extendedGamepad.buttonMenu,1,YES);
  Check(!(published.buttons & galaxypad::Plus),"repair invalidates stale queued callbacks");
  [adapter publishWithSeconds:0]; [adapter publishWithSeconds:0];
  [next.extendedGamepad.buttonA setValue:1]; [adapter publishWithSeconds:0];
  Check(published.buttons & galaxypad::A,"repaired owner accepts gameplay after neutral");
  [next.extendedGamepad.buttonA setValue:0];
  Event(next,next.extendedGamepad.buttonMenu,YES);
  Check(published.buttons & galaxypad::Plus,"repaired owner accepts fresh Menu");
  Event(next,next.extendedGamepad.buttonMenu,NO);
  Method profile=class_getInstanceMethod(GCController.class,@selector(extendedGamepad));
  GCExtendedGamepad *oldPad=next.extendedGamepad;
  GCController *profileSource=[GCController controllerWithExtendedGamepad];
  replacementProfile=profileSource.extendedGamepad; profileOwner=next;
  [replacementProfile.buttonMenu setValue:1];
  originalProfile=method_setImplementation(profile,(IMP)Profile);
  [adapter reconcile];
  Check(oldPad.valueChangedHandler==nil && oldPad.buttonMenu.pressedChangedHandler==nil &&
        replacementProfile.valueChangedHandler,"same identity profile replacement rebinds handlers");
  Event(next,replacementProfile.buttonMenu,YES);
  Check(!(published.buttons & galaxypad::Plus),"replacement profile held Menu cannot inject Plus");
  Event(next,replacementProfile.buttonMenu,NO); Event(next,replacementProfile.buttonMenu,YES);
  Check(published.buttons & galaxypad::Plus,"replacement profile accepts fresh Menu");
  method_setImplementation(profile,originalProfile); replacementProfile=nil; profileOwner=nil;
  [adapter reconcile];
  auto sameObjectStale=next.extendedGamepad.buttonMenu.pressedChangedHandler;
  listed=@[]; Event(next,next.extendedGamepad.buttonMenu,NO);
  Check(next.extendedGamepad.buttonMenu.pressedChangedHandler==nil,"unlisted owner reconciles");
  [next.extendedGamepad.buttonMenu setValue:0]; listed=@[next]; [adapter reconcile];
  sameObjectStale(next.extendedGamepad.buttonMenu,1,YES);
  Check(!(published.buttons & galaxypad::Plus),"old same-object generation cannot inject");
  Event(next,next.extendedGamepad.buttonMenu,YES);
  Check(published.buttons & galaxypad::Plus,"current ownership accepts first neutral Menu");
  listed=@[]; [adapter reconcile];
  Method options=class_getInstanceMethod(GCExtendedGamepad.class,@selector(buttonOptions));
  IMP originalOptions=method_setImplementation(options,(IMP)NoOptions);
  GCController *menuOnly=[GCController controllerWithExtendedGamepad]; listed=@[menuOnly];
  [adapter reconcile]; Event(menuOnly,menuOnly.extendedGamepad.buttonMenu,YES);
  Check(published.buttons & galaxypad::Plus,"nil Options still supports original game pause");
  listed=@[]; [adapter reconcile];
  method_setImplementation(options,originalOptions);
  GCController *idle=[GCController controllerWithExtendedGamepad]; listed=@[idle];
  [adapter reconcile]; [adapter publishWithSeconds:0];
  [idle.extendedGamepad.leftThumbstick.xAxis setValue:0.8];
  [adapter publishWithSeconds:0];
  Check(published.moveX>0.5,"pre-disconnect movement is published");
  auto staleMove=idle.extendedGamepad.valueChangedHandler;
  // The framework enumeration intentionally still lists the old object.
  [adapter connectionChanged:[NSNotification notificationWithName:GCControllerDidDisconnectNotification object:idle]];
  Check(published.moveX==0 && !published.connected,"disconnect immediately clears held movement despite stale enumeration");
  staleMove(idle.extendedGamepad,idle.extendedGamepad.leftThumbstick);
  [adapter reconcile]; [adapter publishWithSeconds:0];
  Check(published.moveX==0 && !published.connected && !idle.extendedGamepad.valueChangedHandler,
        "stale callback and periodic poll cannot revive disconnected owner");
  [adapter connectionChanged:[NSNotification notificationWithName:GCControllerDidConnectNotification object:idle]];
  [adapter publishWithSeconds:0];
  Check(published.moveX==0,"same-object reconnect suppresses cached held axis until neutral");
  [idle.extendedGamepad.leftThumbstick.xAxis setValue:0];
  [adapter publishWithSeconds:0]; [adapter publishWithSeconds:0];
  [idle.extendedGamepad.leftThumbstick.xAxis setValue:0.8];
  [adapter publishWithSeconds:0];
  Check(published.moveX>0.5,"reconnected controller accepts fresh movement after release");
  [adapter connectionChanged:[NSNotification notificationWithName:GCControllerDidConnectNotification object:idle]];
  [adapter publishWithSeconds:0];
  Check(published.moveX==0,"connect event resets unchanged owner even when disconnect was not observed");
  listed=@[]; [adapter reconcile];
  method_setImplementation(enumeration,original); listed=nil;
  std::puts("PASS: queued guest Plus taps/holds/releases, View app pause/resume, modal/reset suppression, stale ownership, same-owner handler/profile recovery, nil Options");
} }
