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
  Check(!c.extendedGamepad.buttonMenu.isPressed,"software pad starts neutral");
  Event(c,c.extendedGamepad.buttonMenu,YES);
  Event(c,c.extendedGamepad.buttonMenu,NO);
  Check(toggles==1 && paused,"queued quick Menu tap survives already-released live snapshot");
  // First press needs no previous release callback after neutral ownership.
  Check(c.extendedGamepad.buttonMenu.pressedChangedHandler!=nil,"Menu has event-time handler");
  [c.extendedGamepad.leftThumbstick.xAxis setValue:0.5];
  Event(c,c.extendedGamepad.buttonMenu,YES);
  Check(toggles==2 && !paused,"Menu resumes while gameplay blocked and stick held");
  [adapter reset];
  for(int i=0;i<8;++i) [adapter publishWithSeconds:1.f/60];
  Event(c,c.extendedGamepad.buttonMenu,YES);
  Check(toggles==2,"reset and neutral polling cannot re-arm a held event");
  Event(c,c.extendedGamepad.buttonOptions,YES);
  Check(toggles==2,"Menu plus Options chord is one hold");
  Event(c,c.extendedGamepad.buttonMenu,NO);
  Event(c,c.extendedGamepad.buttonOptions,YES);
  Check(toggles==2,"one held button prevents other-button rearm");
  Event(c,c.extendedGamepad.buttonOptions,NO);
  Event(c,c.extendedGamepad.buttonOptions,YES);
  Check(toggles==3 && paused,"fresh Options press toggles");
  Event(c,c.extendedGamepad.buttonOptions,NO);
  modal=true; Event(c,c.extendedGamepad.buttonMenu,YES);
  Check(toggles==3,"Menu cannot escape modal");
  [adapter reset]; modal=false; [adapter publishWithSeconds:0];
  Event(c,c.extendedGamepad.buttonMenu,YES);
  Check(toggles==3,"held modal press stays consumed after dismissal");
  Event(c,c.extendedGamepad.buttonMenu,NO);
  Event(c,c.extendedGamepad.buttonMenu,YES);
  Check(toggles==4 && !paused,"fresh post-modal Menu works");
  Event(c,c.extendedGamepad.buttonMenu,NO);
  [c.extendedGamepad.leftThumbstick.xAxis setValue:0];
  [adapter publishWithSeconds:0]; [adapter publishWithSeconds:0];
  // A general callback observing Menu before its specific handler may not
  // publish guest Plus. No physical mapping outside these native keys changes.
  auto menuHandler=c.extendedGamepad.buttonMenu.pressedChangedHandler;
  c.extendedGamepad.buttonMenu.pressedChangedHandler=nil;
  [c.extendedGamepad.buttonMenu setValue:1]; [adapter publishWithSeconds:0];
  Check((published.buttons & galaxypad::Plus)==0,"general snapshot cannot leak guest Plus");
  [c.extendedGamepad.buttonMenu setValue:0];
  c.extendedGamepad.buttonMenu.pressedChangedHandler=menuHandler;
  auto stale=c.extendedGamepad.buttonMenu.pressedChangedHandler;
  GCController *next=[GCController controllerWithExtendedGamepad];
  [next.extendedGamepad.buttonMenu setValue:1]; // held before acquiring ownership
  listed=@[next]; [adapter reconcile];
  Check(c.extendedGamepad.buttonMenu.pressedChangedHandler==nil &&
        c.extendedGamepad.buttonOptions.pressedChangedHandler==nil,"old ownership clears both handlers");
  stale(c.extendedGamepad.buttonMenu,1,YES);
  Check(toggles==4,"queued stale-owner handler is ignored");
  Event(next,next.extendedGamepad.buttonMenu,YES);
  Check(toggles==4,"reconnect already-held Menu requires release");
  Event(next,next.extendedGamepad.buttonMenu,NO);
  Event(next,next.extendedGamepad.buttonMenu,YES);
  Check(toggles==5,"reconnected owner resumes after release");
  auto sameObjectStale=next.extendedGamepad.buttonMenu.pressedChangedHandler;
  listed=@[];
  Event(next,next.extendedGamepad.buttonMenu,NO);
  Check(next.extendedGamepad.buttonMenu.pressedChangedHandler==nil,"unlisted owner reconciles before handling");
  // The framework may reuse a controller object across reconnection. A queued
  // callback from the previous ownership must not become a fresh press.
  [next.extendedGamepad.buttonMenu setValue:0];
  listed=@[next]; [adapter reconcile];
  sameObjectStale(next.extendedGamepad.buttonMenu,1,YES);
  Check(toggles==5,"queued callback from earlier ownership of same object is ignored");
  Event(next,next.extendedGamepad.buttonMenu,YES);
  Check(toggles==6,"current same-object ownership accepts first neutral press");
  listed=@[]; [adapter reconcile];
  // Controllers without optional Options still retain reliable Menu.
  Method options=class_getInstanceMethod(GCExtendedGamepad.class,@selector(buttonOptions));
  IMP originalOptions=method_setImplementation(options,(IMP)NoOptions);
  GCController *menuOnly=[GCController controllerWithExtendedGamepad]; listed=@[menuOnly];
  [adapter reconcile]; Event(menuOnly,menuOnly.extendedGamepad.buttonMenu,YES);
  Check(toggles==7,"nil optional Options does not disable first neutral Menu press");
  listed=@[]; [adapter reconcile];
  method_setImplementation(options,originalOptions);
  method_setImplementation(enumeration,original); listed=nil;
  std::puts("PASS: queued Menu edges, held/reset/poll deduplication, stick resume, modal gate, stale owner/reconnect, nil Options, no guest Plus");
} }
