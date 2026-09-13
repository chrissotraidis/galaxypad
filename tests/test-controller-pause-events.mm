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
@end
void GalaxyPadLog(NSString *format, ...) { (void)format; }
static NSArray<GCController *> *listed;
static NSArray<GCController *> *Controllers(id,SEL) { return listed; }
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
  method_setImplementation(enumeration,original); listed=nil;
  std::puts("PASS: queued guest Plus taps/holds/releases, View app pause/resume, modal/reset suppression, stale ownership, nil Options");
} }
