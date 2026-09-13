#!/usr/bin/env python3
"""Build a UIKit regression host using the production focus lifecycle method.
Pass a booted Simulator UUID to install/run; no devices are booted by this test.
"""
from pathlib import Path
import plistlib
import subprocess
import sys
root = Path(__file__).resolve().parents[1]
source = (root/'apple/ios/main.mm').read_text()
start=source.index('- (void)reconcileControllerFocus {')
end=source.index('- (void)setApplicationActive:', start)
method=source[start:end]
app=root/'generated/tests/ControllerFocusTests.app'
app.mkdir(parents=True,exist_ok=True)
unit=r'''
#import <UIKit/UIKit.h>
#import <GameController/GCEventViewController.h>
#import "METAL_HEADER"
#import "CONTROLLER_HEADER"
#import <GameController/GameController.h>
#import <objc/runtime.h>
extern "C" void GalaxyPadLog(NSString *format, ...) { (void)format; }
static NSArray<GCController *> *listed;
static NSArray<GCController *> *Controllers(id,SEL) { return listed; }
#include <cstdlib>
static void Check(BOOL ok,const char *what) {
  if (!ok) { NSLog(@"FAIL: %s",what); exit(1); }
}
@interface TestHost : NSObject
@property BOOL busy;
@end
@implementation TestHost
@end
@interface TestOverlay : UIView
@property BOOL gameplayAvailable;
@property BOOL nativePauseVisible;
@end
@implementation TestOverlay
@end
@interface FocusController : GCEventViewController {
@public
  GalaxyPadMetalView *_surface;
  TestHost *_host;
  TestOverlay *_overlay;
  BOOL _applicationActive, _menuPresented, _removingGameData;
  id _import;
}
- (void)reconcileControllerFocus;
@end
@implementation FocusController
- (void)viewDidLoad {
  [super viewDidLoad]; self.controllerUserInteractionEnabled=NO;
  _surface=[[GalaxyPadMetalView alloc] initWithFrame:self.view.bounds];
  [self.view addSubview:_surface];
  _host=[TestHost new]; _host.busy=YES;
  _overlay=[TestOverlay new]; _overlay.gameplayAvailable=YES;
  _applicationActive=YES;
}
METHOD
@end
@interface TestDelegate : UIResponder <UIApplicationDelegate>
@property(nonatomic,strong) UIWindow *window;
@end
@implementation TestDelegate
- (BOOL)application:(UIApplication *)app didFinishLaunchingWithOptions:(NSDictionary *)options {
  (void)app;(void)options;
  self.window=[[UIWindow alloc] initWithFrame:UIScreen.mainScreen.bounds];
  FocusController *vc=[FocusController new];self.window.rootViewController=vc;
  [self.window makeKeyAndVisible];
  dispatch_after(dispatch_time(DISPATCH_TIME_NOW,500*NSEC_PER_MSEC),dispatch_get_main_queue(),^{
    [vc reconcileControllerFocus];
    Check(vc->_surface.isFirstResponder,"game surface becomes actual first responder");
    Check(UIApplication.sharedApplication.idleTimerDisabled,"active game suppresses screen idle");
    vc->_menuPresented=YES; [vc reconcileControllerFocus];
    Check(UIApplication.sharedApplication.idleTimerDisabled,"native pause keeps screen awake");
    vc->_overlay.nativePauseVisible=YES;
    vc->_applicationActive=NO; [vc reconcileControllerFocus];
    vc->_applicationActive=YES; [vc reconcileControllerFocus];
    Check(vc->_surface.isFirstResponder,"foreground during native pause restores controller responder");
    Method enumeration=class_getClassMethod(GCController.class,@selector(controllers));
    IMP original=method_setImplementation(enumeration,(IMP)Controllers);
    GCController *controller=[GCController controllerWithExtendedGamepad]; listed=@[controller];
    GalaxyPadControllers *adapter=[GalaxyPadControllers new];
    adapter.pauseToggleAllowed=^BOOL { return YES; };
    adapter.pauseRequested=^{vc->_menuPresented=NO;vc->_overlay.nativePauseVisible=NO;[vc reconcileControllerFocus];};
    [adapter reconcile];
    auto viewPress=controller.extendedGamepad.buttonOptions.pressedChangedHandler;
    Check(viewPress!=nil,"View resume handler installed while paused");
    viewPress(controller.extendedGamepad.buttonOptions,1,YES);
    Check(!vc->_menuPresented && vc->_surface.isFirstResponder,"View resumes after paused foreground return");
    listed=@[];[adapter reconcile];method_setImplementation(enumeration,original);
    UIViewController *modal=[UIViewController new];
    UITextField *field=[[UITextField alloc] initWithFrame:CGRectMake(20,100,250,45)];
    [modal.view addSubview:field];
    [vc presentViewController:modal animated:NO completion:^{
      Check([field becomeFirstResponder],"modal text field becomes first responder");
      [vc reconcileControllerFocus];
      Check(field.isFirstResponder && !vc->_surface.isFirstResponder,"reconciliation preserves modal text input");
      [vc dismissViewControllerAnimated:NO completion:^{
        [vc reconcileControllerFocus];
        Check(vc->_surface.isFirstResponder,"dismissal restores game responder");
        vc->_applicationActive=NO; [vc reconcileControllerFocus];
        Check(!UIApplication.sharedApplication.idleTimerDisabled && !vc->_surface.isFirstResponder,"background releases responder and screen idle");
        vc->_applicationActive=YES; [vc reconcileControllerFocus];
        Check(vc->_surface.isFirstResponder && UIApplication.sharedApplication.idleTimerDisabled,"foreground reacquires responder and idle policy");
        vc->_overlay.gameplayAvailable=NO; [vc reconcileControllerFocus];
        Check(!UIApplication.sharedApplication.idleTimerDisabled && !vc->_surface.isFirstResponder,"stop request releases even before busy clears");
        vc->_host.busy=NO; [vc reconcileControllerFocus];
        Check(!UIApplication.sharedApplication.idleTimerDisabled,"stopped host leaves idle enabled");
        NSLog(@"PASS: controller focus actual UIKit acquisition/modal preservation/restoration/background/pause/stop");
        exit(0);
      }];
    }];
  });
  return YES;
}
@end
int main(int argc,char **argv) { @autoreleasepool {
  return UIApplicationMain(argc,argv,nil,NSStringFromClass(TestDelegate.class));
} }
'''.replace('METAL_HEADER',str(root/'apple/ios/GalaxyPadMetalView.h')).replace('CONTROLLER_HEADER',str(root/'apple/ios/GalaxyPadControllers.h')).replace('METHOD',method)
cpp=app.parent/'controller-focus-test.mm';cpp.write_text(unit)
sdk=subprocess.check_output(['xcrun','--sdk','iphonesimulator','--show-sdk-path'],text=True).strip()
subprocess.run(['xcrun','clang++','-std=c++23','-fobjc-arc','-fblocks','-Wall','-Wextra','-target','arm64-apple-ios17.0-simulator','-isysroot',sdk,str(cpp),str(root/'apple/ios/GalaxyPadMetalView.mm'),str(root/'apple/ios/GalaxyPadControllers.mm'),str(root/'apple/shared/GalaxyPadControllerMappingStore.mm'),'-framework','UIKit','-framework','GameController','-framework','Metal','-framework','QuartzCore','-o',str(app/'ControllerFocusTests')],check=True)
(app/'Info.plist').write_bytes(plistlib.dumps({'CFBundleIdentifier':'org.galaxypad.controller-focus-tests','CFBundleExecutable':'ControllerFocusTests','CFBundlePackageType':'APPL','CFBundleVersion':'1','CFBundleName':'ControllerFocusTests','UILaunchScreen':{},'UIDeviceFamily':[1,2]}))
if len(sys.argv)>1:
    subprocess.run(['xcrun','simctl','install',sys.argv[1],str(app)],check=True)
    result=subprocess.run(['xcrun','simctl','launch','--console',sys.argv[1],'org.galaxypad.controller-focus-tests'],capture_output=True,text=True,timeout=40)
    log=app.parent/'controller-focus-results.log';log.write_text(result.stdout+result.stderr)
    if result.returncode or 'PASS: controller focus actual UIKit' not in log.read_text():
        print(log.read_text());raise SystemExit(1)
    print('PASS: actual Simulator UIKit focus lifecycle; log:',log)
else:
    print('Built:',app)
