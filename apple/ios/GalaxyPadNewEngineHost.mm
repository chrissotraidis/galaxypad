// SPDX-License-Identifier: GPL-3.0-or-later
#import "GalaxyPadNewEngineHost.h"
#import "GalaxyPadGameOverlay.h"
#import "GalaxyPadControllers.h"
#import "GalaxyPadControllerMappingPrompt.h"
#import "GalaxyPadGyroPointer.h"
#import "GalaxyPadAboutViewController.h"
#import "GalaxyPadGameDataStatus.h"
#import "GalaxyPadReportViewController.h"
#import "../shared/GalaxyPadDiagnostics.h"
#import "../shared/GalaxyPadSettings.h"
#import <GameController/GameController.h>
#import <QuartzCore/QuartzCore.h>
#include "../shared/GalaxyPadInput.h"
#include <cmath>
#include <stdlib.h>

// GalaxyPadEngine.framework (ref/galaxypad-engine native/app/engine_entry.mm).
extern "C" void galaxypad_engine_input(uint32_t buttons, float stickX, float stickY, int pointerVisible,
                                       float pointerX, float pointerY);
extern "C" int galaxypad_engine_image(float *x, float *y, float *width, float *height);
extern "C" int galaxypad_engine_started(void);
extern "C" void galaxypad_engine_switch_to_original(void);
extern "C" void galaxypad_engine_quit(void);
extern "C" void galaxypad_engine_pause(int paused);
extern "C" void galaxypad_engine_set_volume(float volume);
extern "C" int galaxypad_engine_widescreen(int value);
extern "C" int galaxypad_engine_smooth_motion(int value);
extern "C" uint64_t galaxypad_engine_presented_frames(void);

// Render Resolution for the New engine: 0 is automatic (the screen's pixels, or
// 3x with Smooth Motion), otherwise that many times the game's own image.
static NSString *const GalaxyPadNewEngineRenderScaleKey = @"GalaxyPadNewEngineRenderScale";

@interface GalaxyPadNewEngineHost : NSObject <GalaxyPadGameOverlayDelegate>
@end

// The overlay's own view controller, in a window above the engine's: menus and
// alerts present from it as they do over the Old engine.
@interface GalaxyPadNewEngineControlsController : UIViewController
@end
@implementation GalaxyPadNewEngineControlsController
- (UIInterfaceOrientationMask)supportedInterfaceOrientations { return UIDevice.currentDevice.userInterfaceIdiom == UIUserInterfaceIdiomPad ? UIInterfaceOrientationMaskAll : UIInterfaceOrientationMaskLandscape; }
- (BOOL)prefersStatusBarHidden { return YES; }
- (BOOL)prefersHomeIndicatorAutoHidden { return YES; }
@end

@implementation GalaxyPadNewEngineHost {
  GalaxyPadGameOverlay *_overlay;
  GalaxyPadControllers *_controllers;
  GalaxyPadGyroPointer *_gyro;
  galaxypad::InputMixer _mixer;
  UIWindow *_controlsWindow;
  UILabel *_fpsLabel;
  NSTimer *_timer;
  CGRect _image;
  BOOL _started;
  BOOL _active;
  BOOL _blocked;
  BOOL _paused;
  float _volume;
  BOOL _logFrameRateWindows;
  CFTimeInterval _fpsTime, _windowTime;
  uint64_t _fpsFrames, _windowFrames;
}

- (instancetype)init {
  if ((self = [super init])) {
    _active = YES;
    _volume = -1;
    _logFrameRateWindows = [NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadLogFrameRateWindows"];
    NSNotificationCenter *center = NSNotificationCenter.defaultCenter;
    [center addObserver:self selector:@selector(windowBecameKey:) name:UIWindowDidBecomeKeyNotification object:nil];
    [center addObserver:self selector:@selector(becameActive) name:UIApplicationDidBecomeActiveNotification object:nil];
    [center addObserver:self selector:@selector(resignedActive) name:UIApplicationWillResignActiveNotification object:nil];
  }
  return self;
}

// The engine's SDL window appeared: GalaxyPad's overlay goes in a window of its
// own above it (the engine's root view is a Metal view, which draws over any
// subview). The window stays hidden until the game starts, so a tap reaches the
// engine's shader preparation screen.
- (void)windowBecameKey:(NSNotification *)note {
  UIWindow *window = note.object;
  if (_overlay || !window.windowScene) return;
  // Smooth Motion starts on for ProMotion screens, once; the menu changes it.
  NSUserDefaults *defaults = NSUserDefaults.standardUserDefaults;
  if (![defaults boolForKey:@"GalaxyPadSmoothMotionDefaultApplied"]) {
    if (window.screen.maximumFramesPerSecond >= 120) galaxypad_engine_smooth_motion(1);
    [defaults setBool:YES forKey:@"GalaxyPadSmoothMotionDefaultApplied"];
  }
  GalaxyPadNewEngineControlsController *controller = [GalaxyPadNewEngineControlsController new];
  _controlsWindow = [[UIWindow alloc] initWithWindowScene:window.windowScene];
  _controlsWindow.windowLevel = window.windowLevel + 1;
  _controlsWindow.backgroundColor = UIColor.clearColor;
  _controlsWindow.rootViewController = controller;
  _controlsWindow.hidden = YES;
  controller.view.backgroundColor = UIColor.clearColor;
  _overlay = [[GalaxyPadGameOverlay alloc] initWithFrame:controller.view.bounds];
  _overlay.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
  _overlay.delegate = self;
  _overlay.hostedByNewEngine = YES;
  _overlay.gameplayAvailable = NO;
  [_overlay applySettings];
  [controller.view addSubview:_overlay];
  // The FPS counter, as over the Old engine (Display, Show FPS Counter).
  _fpsLabel = [[UILabel alloc] initWithFrame:CGRectMake(12, 12, 180, 28)];
  _fpsLabel.font = [UIFont monospacedDigitSystemFontOfSize:12 weight:UIFontWeightMedium];
  _fpsLabel.textAlignment = NSTextAlignmentCenter;
  _fpsLabel.layer.cornerRadius = 12;
  _fpsLabel.clipsToBounds = YES;
  _fpsLabel.textColor = UIColor.whiteColor;
  _fpsLabel.backgroundColor = [UIColor colorWithWhite:0 alpha:0.65];
  _fpsLabel.userInteractionEnabled = NO;
  _fpsLabel.hidden = YES;
  [controller.view addSubview:_fpsLabel];

  __weak GalaxyPadNewEngineHost *weakSelf = self;
  __weak GalaxyPadGameOverlay *weakOverlay = _overlay;
  _overlay.viewportProvider = ^CGRect {
    GalaxyPadNewEngineHost *host = weakSelf;
    return host ? host->_image : CGRectZero;
  };
  _overlay.inputChanged = ^(galaxypad::InputState input) {
    GalaxyPadNewEngineHost *host = weakSelf;
    if (!host) return;
    [host->_gyro acceptTouch:input];
    host->_mixer.set(galaxypad::InputSource::Touch, input);
    [host sendInput];
  };
  _overlay.nativeUIChanged = ^{ [weakSelf reconcile]; };
  _overlay.gyroSettingsChanged = ^{ [weakSelf clearInput]; };

  // Game controllers: GalaxyPad's own adapter and mapping, as over the Old
  // engine (the engine ignores them itself: PETARI_SDL_GAMEPADS=0).
  _controllers = [[GalaxyPadControllers alloc] init];
  __weak GalaxyPadControllers *weakControllers = _controllers;
  _controllers.inputAllowed = ^BOOL {
    GalaxyPadNewEngineHost *host = weakSelf;
    return host && host->_active && host->_started && !host->_blocked;
  };
  _controllers.pauseToggleAllowed = ^BOOL {
    GalaxyPadNewEngineHost *host = weakSelf;
    return host && host->_active && host->_started &&
      !host->_controlsWindow.rootViewController.presentedViewController &&
      (!host->_blocked || host->_overlay.nativePauseVisible);
  };
  _controllers.pauseRequested = ^{ [weakOverlay toggleNativePause]; };
  _controllers.inputChanged = ^(galaxypad::InputState input) {
    GalaxyPadNewEngineHost *host = weakSelf;
    if (!host) return;
    host->_mixer.set(galaxypad::InputSource::Controller, input);
    [host sendInput];
  };
  _controllers.ownershipChanged = ^{
    [weakSelf clearInput];
    [weakOverlay refreshControllerVisibility];
  };

  _gyro = [GalaxyPadGyroPointer new];
  __weak GalaxyPadGyroPointer *weakGyro = _gyro;
  _overlay.gyroRecenterRequested = ^{ [weakGyro recenter]; };
  _controllers.aimChanged = ^(float x, float y, BOOL recenter) { [weakGyro setStickX:x y:y recenter:recenter]; };
  _gyro.inputAllowed = ^BOOL {
    GalaxyPadNewEngineHost *host = weakSelf;
    return host && host->_active && host->_started && !host->_blocked &&
      !weakControllers.motionController.extendedGamepad.leftShoulder.isPressed;
  };
  _gyro.orientation = ^UIInterfaceOrientation { return weakOverlay.window.windowScene.interfaceOrientation; };
  _gyro.controller = ^GCController * { return weakControllers.motionController; };
  _gyro.inputChanged = ^(galaxypad::InputState state) {
    GalaxyPadNewEngineHost *host = weakSelf;
    if (!host) return;
    host->_mixer.set(galaxypad::InputSource::Gyro, state);
    [host sendInput];
  };
  _gyro.statusChanged = ^(NSString *status) { weakOverlay.gyroStatus = status; };
  [_controllers start];
  [_gyro start];
  _timer = [NSTimer scheduledTimerWithTimeInterval:0.1 repeats:YES block:^(NSTimer *timer) {
    GalaxyPadNewEngineHost *host = weakSelf;
    if (!host) { [timer invalidate]; return; }
    [host tick];
  }];
  [self tick];
  GalaxyPadLog(@"new engine: GalaxyPad controls attached");
}

- (void)tick {
  float x = 0, y = 0, width = 0, height = 0;
  const CGRect image = galaxypad_engine_image(&x, &y, &width, &height) ? CGRectMake(x, y, width, height) : CGRectZero;
  if (!CGRectEqualToRect(image, _image)) {
    _image = image;
    [_overlay setNeedsLayout];
  }
  if (!_started && galaxypad_engine_started()) {
    _started = YES;
    _controlsWindow.hidden = NO;
    _overlay.gameplayAvailable = YES;
    _overlay.stopRequested = ^{
      GalaxyPadLog(@"new engine: Stop Game");
      galaxypad_engine_quit();
    };
    _fpsTime = _windowTime = CACurrentMediaTime();
    _fpsFrames = _windowFrames = galaxypad_engine_presented_frames();
    GalaxyPadLog(@"new engine: game started; GalaxyPad controls shown");
  }
  GalaxyPadSettings *settings = GalaxyPadSettings.sharedSettings;
  const float volume = settings.mainAudioMuted ? 0.f : settings.mainVolume / 100.f;
  if (volume != _volume) {
    _volume = volume;
    galaxypad_engine_set_volume(volume);
  }
  [self reconcile];
  [self updateFrameRate];
}

// The FPS counter, and with Detailed Performance Logging five-second summaries
// in the diagnostic log. Frames presented, in-between Smooth Motion frames included.
- (void)updateFrameRate {
  if (!_started) return;
  const CFTimeInterval now = CACurrentMediaTime();
  const uint64_t frames = galaxypad_engine_presented_frames();
  const BOOL show = GalaxyPadSettings.sharedSettings.showFPSCounter;
  _fpsLabel.hidden = !show;
  if (now - _fpsTime >= 1.0) {
    const double fps = (frames - _fpsFrames) / (now - _fpsTime);
    if (show) _fpsLabel.text = _paused ? @"Paused" : [NSString stringWithFormat:@"%.1f FPS", fps];
    _fpsTime = now;
    _fpsFrames = frames;
  }
  if (_logFrameRateWindows && now - _windowTime >= 5.0) {
    GalaxyPadLog(@"new engine frames: fps=%.1f window=%.1fs paused=%d smooth_motion=%d thermal=%ld",
      (frames - _windowFrames) / (now - _windowTime), now - _windowTime, _paused,
      galaxypad_engine_smooth_motion(-1), (long)NSProcessInfo.processInfo.thermalState);
    _windowTime = now;
    _windowFrames = frames;
  }
}

- (void)sendInput {
  galaxypad::InputState out;
  if (_active && _started && !_blocked) out = _mixer.consume();
  // The engine steers balls and rays from the stick, so the tilt stick is a stick too.
  const float x = std::fabs(out.tiltX) > std::fabs(out.moveX) ? out.tiltX : out.moveX;
  const float y = std::fabs(out.tiltY) > std::fabs(out.moveY) ? out.tiltY : out.moveY;
  galaxypad_engine_input(out.buttons, x, y, out.pointerVisible, out.pointerX, out.pointerY);
}

- (void)clearInput {
  _mixer.clearAll();
  [_gyro reset];
  [_controllers reset];
  [self sendInput];
}

// GalaxyPad's menus and sheets stop game input and hold the game, and so does
// leaving the app. Unlike the Old engine, the three-dot menu holds it too: this
// engine runs the game on the main thread, which UIKit needs to animate the menu
// and track touches in it, so a running game makes the menu lag.
- (void)reconcile {
  if (!_overlay) return;
  const BOOL presented = _controlsWindow.rootViewController.presentedViewController != nil;
  const BOOL nativeMenu = _overlay.nativeMenuVisible;
  const BOOL blocked = _overlay.blocksGameplay || nativeMenu || presented;
  const BOOL paused = _started && (!_active || blocked);
  if (blocked != _blocked) {
    _blocked = blocked;
    [self clearInput];
    if (!blocked) [_controllers reconcile];
  }
  if (paused != _paused) {
    _paused = paused;
    galaxypad_engine_pause(paused);
    GalaxyPadLog(@"new engine: %@", paused ? @"paused" : @"resumed");
  }
  UIApplication.sharedApplication.idleTimerDisabled = _active && _started;
}

- (void)becameActive {
  _active = YES;
  [_controllers reconcile];
  [self reconcile];
}
- (void)resignedActive {
  _active = NO;
  [_overlay reset];
  [self clearInput];
  [self reconcile];
}

- (UIViewController *)presenter {
  UIViewController *controller = _controlsWindow.rootViewController;
  while (controller.presentedViewController) controller = controller.presentedViewController;
  return controller;
}

- (NSString *)diagnosticContext {
  float x = 0, y = 0, w = 0, h = 0;
  galaxypad_engine_image(&x, &y, &w, &h);
  return [NSString stringWithFormat:
    @"engine=new build=%@ platform=%@ os=%@ thermalState=%ld lowPowerMode=%d maxFPS=%ld "
     "smoothMotion=%d widescreen=%d renderScaleSetting=%ld image=%.3f,%.3f,%.3fx%.3f paused=%d framesPresented=%llu",
    [NSBundle.mainBundle objectForInfoDictionaryKey:@"CFBundleVersion"] ?: @"?",
    TARGET_OS_SIMULATOR ? @"simulator" : @"device", UIDevice.currentDevice.systemVersion,
    (long)NSProcessInfo.processInfo.thermalState, NSProcessInfo.processInfo.lowPowerModeEnabled,
    (long)_controlsWindow.screen.maximumFramesPerSecond, galaxypad_engine_smooth_motion(-1),
    galaxypad_engine_widescreen(-1),
    (long)[NSUserDefaults.standardUserDefaults integerForKey:GalaxyPadNewEngineRenderScaleKey],
    x, y, w, h, _paused, (unsigned long long)galaxypad_engine_presented_frames()];
}

#pragma mark - Menu

- (NSArray<UIMenuElement *> *)gameOverlayDisplayItems:(GalaxyPadGameOverlay *)overlay {
  __weak GalaxyPadGameOverlay *weakOverlay = overlay;
  NSUserDefaults *defaults = NSUserDefaults.standardUserDefaults;
  const NSInteger scale = [defaults integerForKey:GalaxyPadNewEngineRenderScaleKey];
  NSMutableArray<UIMenuElement *> *scales = [NSMutableArray array];
  NSArray<NSString *> *names = @[@"Automatic (Recommended)", @"", @"2×", @"3×", @"4× (Higher GPU Cost)"];
  for (NSInteger value : {0, 2, 3, 4}) {
    UIAction *action = [UIAction actionWithTitle:names[value] image:nil identifier:nil
      handler:^(__kindof UIAction *unused) {
        (void)unused;
        [NSUserDefaults.standardUserDefaults setInteger:value forKey:GalaxyPadNewEngineRenderScaleKey];
        [weakOverlay refreshMenuButton];
      }];
    if (value == 0) action.subtitle = @"Screen resolution; 3× with Smooth Motion";
    else action.subtitle = @"Times the game's own 640×480 image";
    action.state = scale == value ? UIMenuElementStateOn : UIMenuElementStateOff;
    [scales addObject:action];
  }
  UIMenu *render = [UIMenu menuWithTitle:@"Render Resolution (Next Launch)" children:scales];

  const int wide = galaxypad_engine_widescreen(-1);
  NSMutableArray<UIMenuElement *> *aspects = [NSMutableArray array];
  for (int value : {0, 1}) {
    UIAction *action = [UIAction actionWithTitle:value ? @"16:9 (Restart Required)" : @"4:3 (Restart Required)"
      image:nil identifier:nil handler:^(__kindof UIAction *unused) {
        (void)unused;
        galaxypad_engine_widescreen(value);
        [weakOverlay refreshMenuButton];
      }];
    action.state = wide == value ? UIMenuElementStateOn : UIMenuElementStateOff;
    [aspects addObject:action];
  }
  UIMenu *aspect = [UIMenu menuWithTitle:@"Aspect Ratio" children:aspects];

  const BOOL proMotion = _controlsWindow.screen.maximumFramesPerSecond >= 120;
  UIAction *smooth = [UIAction actionWithTitle:@"Smooth Motion (120 FPS)" image:[UIImage systemImageNamed:@"wind"]
    identifier:@"galaxypad.menu.smooth-motion" handler:^(__kindof UIAction *unused) {
      (void)unused;
      galaxypad_engine_smooth_motion(galaxypad_engine_smooth_motion(-1) ? 0 : 1);
      [weakOverlay refreshMenuButton];
    }];
  smooth.subtitle = proMotion ? @"Draws between the game's 60 steps on this 120 Hz screen"
                              : @"Needs a 120 Hz ProMotion screen";
  smooth.state = galaxypad_engine_smooth_motion(-1) ? UIMenuElementStateOn : UIMenuElementStateOff;
  if (!proMotion) smooth.attributes = UIMenuElementAttributesDisabled;
  return @[smooth, render, aspect];
}

- (void)switchToOldEngineWithTitle:(NSString *)title message:(NSString *)message {
  UIAlertController *alert = [UIAlertController alertControllerWithTitle:title message:message
    preferredStyle:UIAlertControllerStyleAlert];
  [alert addAction:[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil]];
  [alert addAction:[UIAlertAction actionWithTitle:@"Switch" style:UIAlertActionStyleDefault
    handler:^(UIAlertAction *action) {
      (void)action;
      GalaxyPadLog(@"new engine: switching to the Old engine");
      galaxypad_engine_switch_to_original();
    }]];
  [[self presenter] presentViewController:alert animated:YES completion:nil];
}

- (void)gameOverlayRequestsOldEngine:(GalaxyPadGameOverlay *)overlay {
  (void)overlay;
  [self switchToOldEngineWithTitle:@"Switch to the Old Engine?"
    message:@"GalaxyPad copies your saved progress to the Old engine and closes. Unsaved progress since your last save is lost. Open GalaxyPad again to play."];
}

// Importing and removing game data happen while no game runs: GalaxyPad closes,
// opens once without the game (main.mm, GalaxyPadOpenShellOnce), then plays
// with the New engine again.
- (void)gameDataNeedsOldEngine {
  UIAlertController *alert = [UIAlertController alertControllerWithTitle:@"Manage Game Data"
    message:@"GalaxyPad closes so the game isn't running. Open it again, then choose Game Data & Saves in the three-dot menu. Your saves are kept."
    preferredStyle:UIAlertControllerStyleAlert];
  [alert addAction:[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil]];
  [alert addAction:[UIAlertAction actionWithTitle:@"Close GalaxyPad" style:UIAlertActionStyleDefault
    handler:^(UIAlertAction *action) {
      (void)action;
      [NSUserDefaults.standardUserDefaults setBool:YES forKey:@"GalaxyPadOpenShellOnce"];
      [NSUserDefaults.standardUserDefaults synchronize];
      GalaxyPadLog(@"new engine: closing for Game Data & Saves");
      galaxypad_engine_quit();
    }]];
  [[self presenter] presentViewController:alert animated:YES completion:nil];
}
- (void)gameOverlayRequestsGameDataChange:(GalaxyPadGameOverlay *)overlay { (void)overlay; [self gameDataNeedsOldEngine]; }
- (void)gameOverlayRequestsGameDataFolderImport:(GalaxyPadGameOverlay *)overlay { (void)overlay; [self gameDataNeedsOldEngine]; }
- (void)gameOverlayRequestsGameDataRemoval:(GalaxyPadGameOverlay *)overlay { (void)overlay; [self gameDataNeedsOldEngine]; }

- (void)gameOverlayRequestsGameDataStatus:(GalaxyPadGameOverlay *)overlay {
  (void)overlay;
  [[self presenter] presentViewController:GalaxyPadGameDataStatusAlert() animated:YES completion:nil];
}

- (void)gameOverlayRequestsControllerMapping:(GalaxyPadGameOverlay *)overlay {
  (void)overlay;
  __weak GalaxyPadNewEngineHost *weakSelf = self;
  GalaxyPadPresentControllerMapping([self presenter], ^{
    GalaxyPadNewEngineHost *host = weakSelf;
    if (!host) return;
    [host->_controllers reloadMapping];
    [host clearInput];
  });
}

- (void)gameOverlayRequestsDiagnosticLog:(GalaxyPadGameOverlay *)overlay {
  (void)overlay;
  NSError *error = nil;
  NSURL *url = GalaxyPadDiagnosticsReportURL(NSUUID.UUID.UUIDString, @{}, [self diagnosticContext], &error);
  [GalaxyPadReportViewController presentReportURL:url from:[self presenter]];
}

- (void)gameOverlayRequestsAbout:(GalaxyPadGameOverlay *)overlay {
  (void)overlay;
  UINavigationController *navigation = [[UINavigationController alloc]
    initWithRootViewController:[[GalaxyPadAboutViewController alloc] init]];
  navigation.modalPresentationStyle = UIModalPresentationPageSheet;
  [[self presenter] presentViewController:navigation animated:YES completion:nil];
}

- (void)gameOverlayRequestsProblemReport:(GalaxyPadGameOverlay *)overlay {
  (void)overlay;
  __weak GalaxyPadNewEngineHost *weakSelf = self;
  [GalaxyPadReportViewController presentReportPromptFrom:[self presenter] technicalContext:^NSString * {
    return [weakSelf diagnosticContext] ?: @"engine=new";
  }];
}
@end

void GalaxyPadNewEngineHostInstall(void) {
  // GalaxyPad's touch controls and game-controller adapter replace the engine's own.
  setenv("PETARI_TOUCH_CONTROLS", "0", 1);
  setenv("PETARI_SDL_GAMEPADS", "0", 1);
  const NSInteger scale = [NSUserDefaults.standardUserDefaults integerForKey:GalaxyPadNewEngineRenderScaleKey];
  if (scale >= 2 && scale <= 4) setenv("PETARI_RENDER_SCALE", [@(scale).stringValue UTF8String], 1);
  GalaxyPadDiagnosticsStart();
  // Lives as long as the app (the engine never returns).
  static GalaxyPadNewEngineHost *host = [GalaxyPadNewEngineHost new];
  (void)host;
}
