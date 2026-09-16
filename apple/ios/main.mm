// SPDX-License-Identifier: GPL-3.0-or-later
// Native bring-up entry. Product overlay/import/menu are tracked separately;
// development host paths are Simulator-only and never a device import substitute.
#import "GalaxyPadCoreHost.h"
#import "GalaxyPadMetalView.h"
#import "GalaxyPadGameOverlay.h"
#import "../shared/GalaxyPadSettings.h"
#import "../shared/GalaxyPadDiagnostics.h"
#import "GalaxyPadReportViewController.h"
#import "GalaxyPadAboutViewController.h"
#import "GalaxyPadControllers.h"
#import "GalaxyPadImportTransaction.h"
#include "../shared/GalaxyPadImportActivation.h"
#include "../shared/GalaxyPadMovementTrace.h"
#include "GalaxyPadDiscIdentity.h"
#import <UniformTypeIdentifiers/UniformTypeIdentifiers.h>
#import "../shared/GalaxyPadControllerMappingStore.h"
#import <UIKit/UIKit.h>
#import <GameController/GCEventViewController.h>
#import <TargetConditionals.h>
#include <stdlib.h>
#include <float.h>
#include <sys/resource.h>
#include <mach/mach.h>

static double GalaxyPadProcessCPUSeconds(void) {
  struct rusage usage = {};
  if (getrusage(RUSAGE_SELF, &usage) != 0) return NAN;
  return usage.ru_utime.tv_sec + usage.ru_stime.tv_sec +
    (usage.ru_utime.tv_usec + usage.ru_stime.tv_usec) / 1000000.0;
}
static double GalaxyPadResidentMiB(void) {
  mach_task_basic_info_data_t info = {};
  mach_msg_type_number_t count = MACH_TASK_BASIC_INFO_COUNT;
  return task_info(mach_task_self(), MACH_TASK_BASIC_INFO,
    reinterpret_cast<task_info_t>(&info), &count) == KERN_SUCCESS
      ? info.resident_size / (1024.0 * 1024.0) : NAN;
}
#if TARGET_OS_SIMULATOR
#include "GalaxyPadSimulatorInput.h"
#endif

@interface GalaxyPadGameViewController : GCEventViewController <GalaxyPadGameOverlayDelegate, UIDocumentPickerDelegate>
- (void)setApplicationActive:(BOOL)active;
- (void)reconcileControllerFocus;
@end
@implementation GalaxyPadGameViewController {
  GalaxyPadMetalView *_surface;
  GalaxyPadCoreHost *_host;
  UILabel *_status;
  BOOL _attemptedStart;
  NSString *_lastGeometry;
  NSTimer *_startupTimer;
  GalaxyPadGameOverlay *_overlay;
  GalaxyPadControllers *_controllers;
  BOOL _applicationActive;
  NSTimer *_uiTimer;
  UILabel *_fpsLabel;
  UIButton *_restartButton;
  CFTimeInterval _fpsTime;
  uint64_t _fpsFrames;
  BOOL _logFrameRateWindows;
  CFTimeInterval _frameWindowStart;
  double _frameWindowCPU;
  NSInteger _activeRenderScale;
  uint64_t _frameWindowFrames;
  double _frameWindowMinFPS;
  double _frameWindowMaxObservationSeconds;
  CGRect _layoutViewport;
  BOOL _menuPresented;
  BOOL _runtimePauseRequested;
  GalaxyPadImportTransaction *_import;
  UIAlertController *_importProgress;
  BOOL _activateImportAfterExit;
  BOOL _removingGameData;
#if TARGET_OS_SIMULATOR
  NSString *_simulatorInputPath;
  double _simulatorInputNotBefore;
  uint32_t _simulatorLastInputButtons;
  BOOL _simulatorLastInputPointerVisible;
#endif
}
- (void)viewDidLoad {
  [super viewDidLoad];
  // Keep controller events on GCController profiles when UIKit focus changes.
  // Touch interaction remains enabled; Menu/View use our controller adapter.
  self.controllerUserInteractionEnabled = NO;
  GalaxyPadDiagnosticsStart();
  // Normal sessions retain sparse summaries for problem reports. The opt-in
  // switch increases cadence and enables the RemoteIO PCM scan; neither file
  // persistence nor PCM scanning is added to the normal gameplay thread.
  [NSUserDefaults.standardUserDefaults registerDefaults:@{@"GalaxyPadLogFrameRateWindows":@NO}];
  const BOOL diagnostics = [NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadLogFrameRateWindows"];
  setenv("GALAXYPAD_AUDIO_OUTPUT_DIAGNOSTICS", diagnostics ? "1" : "0", 1);
  self.view.backgroundColor = UIColor.blackColor;
  _surface = [[GalaxyPadMetalView alloc] initWithFrame:self.view.bounds];
  _surface.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
  [self.view addSubview:_surface];
  _host = [[GalaxyPadCoreHost alloc] initWithLayer:_surface.metalLayer];
  _status = [[UILabel alloc] init];
  _status.textColor = UIColor.whiteColor;
  _status.backgroundColor = [UIColor.blackColor colorWithAlphaComponent:0.7];
  _status.numberOfLines = 0;
  _status.textAlignment = NSTextAlignmentCenter;
  _status.text = @"GalaxyPad — development build\nNative host ready; game-data setup pending.";
  [self.view addSubview:_status];
  __weak GalaxyPadGameViewController *weakSelf = self;
#if TARGET_OS_SIMULATOR
  _simulatorInputPath=[NSUserDefaults.standardUserDefaults stringForKey:@"GalaxyPadDevInputFile"];
  _simulatorInputNotBefore=NSDate.date.timeIntervalSince1970;
  if (_simulatorInputPath.length) GalaxyPadLog(@"Simulator diagnostic input enabled; physical controller source reserved");
#endif
  _overlay = [[GalaxyPadGameOverlay alloc] initWithFrame:self.view.bounds];
  _overlay.delegate = self;
  _overlay.gameplayAvailable = NO;
  [_overlay applySettings];
  _overlay.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
  _overlay.hidden = NO; // SunPad menu must also be available before game setup.
  [self.view insertSubview:_overlay aboveSubview:_surface];
  _restartButton = [UIButton buttonWithType:UIButtonTypeSystem];
  UIButtonConfiguration *restartConfiguration = [UIButtonConfiguration filledButtonConfiguration];
  restartConfiguration.title = @"Restart Game";
  restartConfiguration.image = [UIImage systemImageNamed:@"play.fill"];
  restartConfiguration.imagePadding = 8;
  _restartButton.configuration = restartConfiguration;
  _restartButton.accessibilityIdentifier = @"galaxypad.restart";
  [_restartButton addTarget:self action:@selector(restartGame) forControlEvents:UIControlEventTouchUpInside];
  _restartButton.hidden = YES;
  [self.view addSubview:_restartButton];
  _overlay.inputChanged = ^(galaxypad::InputState input) {
    GalaxyPadGameViewController *view = weakSelf;
    if (view && !view->_menuPresented) {
      static galaxypad::MovementTrace trace("touch");
      trace.record(input.moveX,input.moveY);
      [view->_host publishInput:input source:galaxypad::InputSource::Touch];
    }
  };
  __weak GalaxyPadGameOverlay *weakOverlay = _overlay;
  _controllers = [[GalaxyPadControllers alloc] init];
  __weak GalaxyPadControllers *weakControllers = _controllers;
  _host.onInputReset = ^{
    [weakOverlay reset]; [weakControllers reset];
#if TARGET_OS_SIMULATOR
    GalaxyPadGameViewController *view=weakSelf;
    if (view) view->_simulatorInputNotBefore=NSDate.date.timeIntervalSince1970;
#endif
  };
  _controllers.inputChanged = ^(galaxypad::InputState input) {
    GalaxyPadGameViewController *view = weakSelf;
    if (view) [view->_host publishInput:input source:galaxypad::InputSource::Controller];
  };
  _controllers.pauseRequested = ^{
    GalaxyPadGameViewController *view = weakSelf;
    if (!view) return;
    if (view->_host.audioInterrupted && !view->_overlay.nativePauseVisible) {
      [view->_host resumeInterruptedAudio];
      return;
    }
    [view->_overlay toggleNativePause];
  };
  _controllers.pauseToggleAllowed = ^BOOL {
    GalaxyPadGameViewController *view = weakSelf;
#if TARGET_OS_SIMULATOR
    if (view && view->_simulatorInputPath.length) return NO;
#endif
    return view && view->_applicationActive && view->_host.busy &&
      !view.presentedViewController && !view->_import && !view->_removingGameData &&
      (!view->_menuPresented || view->_overlay.nativePauseVisible);
  };
  _controllers.inputAllowed = ^BOOL {
    GalaxyPadGameViewController *view = weakSelf;
#if TARGET_OS_SIMULATOR
    if (view && view->_simulatorInputPath.length) return NO;
#endif
    return view && view->_applicationActive && view->_host.busy &&
      !view->_host.paused && !view->_menuPresented;
  };
  _controllers.ownershipChanged = ^{
    GalaxyPadGameViewController *view = weakSelf;
    if (!view) return;
    [view->_host clearInput];
    [view->_overlay refreshControllerVisibility];
    GalaxyPadLog(@"controller ownership changed; input cleared");
  };
  [_controllers start];
  _overlay.nativeUIChanged = ^{ [weakSelf reconcileNativeUI]; };
  // This is the emulation/VI frame-event rate, not a display-completion FPS
  // measurement. Keep that distinction visible in the gameplay HUD.
  _fpsLabel = [[UILabel alloc] initWithFrame:CGRectMake(12, 12, 180, 28)];
  _fpsLabel.font = [UIFont monospacedDigitSystemFontOfSize:12 weight:UIFontWeightMedium];
  _fpsLabel.textAlignment = NSTextAlignmentCenter;
  _fpsLabel.layer.cornerRadius = 12;
  _fpsLabel.clipsToBounds = YES;
  _fpsLabel.textColor = UIColor.whiteColor;
  _fpsLabel.backgroundColor = [UIColor colorWithWhite:0 alpha:0.65];
  _fpsLabel.userInteractionEnabled = NO;
  _fpsLabel.hidden = YES;
  [self.view addSubview:_fpsLabel];
  _fpsTime = CACurrentMediaTime();
  // Bounded five-second diagnostic summaries, persisted locally for reports.
  // Observation gaps are UI timer delays, not display-completion intervals.
  _logFrameRateWindows = [NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadLogFrameRateWindows"];
  _uiTimer = [NSTimer scheduledTimerWithTimeInterval:0.1 repeats:YES block:^(NSTimer *timer) {
    GalaxyPadGameViewController *view = weakSelf;
    if (!view) { [timer invalidate]; return; }
    [view reconcileNativeUI];
    const CGRect viewport = view->_host.normalizedViewport;
    if (!CGRectEqualToRect(viewport, view->_layoutViewport)) {
      view->_layoutViewport = viewport;
      [view->_overlay setNeedsLayout];
      GalaxyPadLog(@"Overlay viewport changed: %@", NSStringFromCGRect(viewport));
    }
#if TARGET_OS_SIMULATOR
    if (view->_simulatorInputPath.length) {
      const double now=NSDate.date.timeIntervalSince1970;
      if (!view->_applicationActive || !view->_host.busy || view->_host.paused || view->_menuPresented)
        view->_simulatorInputNotBefore=now;
      auto input=GalaxyPadReadSimulatorInput(view->_simulatorInputPath,now,view->_simulatorInputNotBefore);
      if (input.buttons != view->_simulatorLastInputButtons ||
          input.pointerVisible != view->_simulatorLastInputPointerVisible) {
        GalaxyPadLog(@"simulator input accepted buttons=%u pointer_visible=%d pointer=(%.3f,%.3f) connected=%d",
          input.buttons, input.pointerVisible, input.pointerX, input.pointerY, input.connected);
        view->_simulatorLastInputButtons=input.buttons;
        view->_simulatorLastInputPointerVisible=input.pointerVisible;
      }
      [view->_host publishInput:input source:galaxypad::InputSource::Controller];
    }
#endif
    view->_fpsLabel.hidden = !GalaxyPadSettings.sharedSettings.showFPSCounter || !view->_host.busy;
    CFTimeInterval now = CACurrentMediaTime();
    if (now - view->_fpsTime >= 1) {
      uint64_t frames = view->_host.renderedFrames;
      const double observationSeconds = now - view->_fpsTime;
      double fps = frames >= view->_fpsFrames ? (frames - view->_fpsFrames) / (now - view->_fpsTime) : 0;
      view->_fpsLabel.text = view->_host.paused ? @"Paused" : [NSString stringWithFormat:@"%.1f FPS", fps];
      view->_fpsLabel.accessibilityLabel = [NSString stringWithFormat:@"%.1f frame events per second", fps];
      view->_fpsTime = now; view->_fpsFrames = frames;
      { // Sparse baseline windows are always available to problem reports.
        // A three-dot UIMenu blocks gameplay input but deliberately leaves
        // the runtime running. Keep that interval in the diagnostic window so
        // a menu-open freeze is observable instead of being filtered out.
        // Explicit pause/modal UI is excluded by the host pause request (and
        // by the paused-state check), preserving active-gameplay semantics.
        const BOOL eligible = view->_host.busy && !view->_host.paused &&
          view->_applicationActive && !view->_runtimePauseRequested && frames > 0;
        if (!eligible || frames < view->_frameWindowFrames) {
          view->_frameWindowStart = 0;
        } else if (view->_frameWindowStart == 0) {
          view->_frameWindowStart = now;
          view->_frameWindowCPU = GalaxyPadProcessCPUSeconds();
          view->_frameWindowFrames = frames;
          view->_frameWindowMinFPS = fps;
          view->_frameWindowMaxObservationSeconds = observationSeconds;
        } else {
          view->_frameWindowMinFPS = MIN(view->_frameWindowMinFPS, fps);
          view->_frameWindowMaxObservationSeconds = MAX(view->_frameWindowMaxObservationSeconds, observationSeconds);
          if (now - view->_frameWindowStart >= (view->_logFrameRateWindows ? 5.0 : 15.0)) {
            NSMutableArray<NSString *> *summary = [NSMutableArray arrayWithCapacity:4];
            const double seconds = now - view->_frameWindowStart;
            const uint64_t count = frames - view->_frameWindowFrames;
            const auto cadence = [view->_host cadenceEstimate];
            // 'presented' is retained for old parsers; this counter originates
            // at after_frame_event, not a display-completion callback.
            [summary addObject:[NSString stringWithFormat:@"[GalaxyPad frame window] counter_source=after_frame_event mono=%.6f seconds=%.6f presented=%llu fps=%.6f min_observed_fps=%.3f max_observation_seconds=%.3f vi_rate_estimate=%.3f emulation_speed_estimate=%.6f native_menu=%d ui_blocked=%d pause_requested=%d",
                  now, seconds, (unsigned long long)count, count / seconds,
                  view->_frameWindowMinFPS, view->_frameWindowMaxObservationSeconds,
                  cadence.viRate, cadence.speed, view->_overlay.nativeMenuVisible,
                  view->_menuPresented, view->_runtimePauseRequested]];
            const double cpu = GalaxyPadProcessCPUSeconds();
            const auto runtime = [view->_host runtimeCounters];
            [summary addObject:[NSString stringWithFormat:@"[GalaxyPad performance] mono=%.6f seconds=%.3f process_cpu_percent=%.2f resident_mib=%.1f thermal_state=%ld low_power=%d active_render_scale=%ld output_max_hz=%ld cpu_percent_scope=all_threads_one_core_100",
              now, seconds, (cpu - view->_frameWindowCPU) / seconds * 100.0,
              GalaxyPadResidentMiB(), (long)NSProcessInfo.processInfo.thermalState,
              NSProcessInfo.processInfo.lowPowerModeEnabled, (long)view->_activeRenderScale,
              (long)view.view.window.screen.maximumFramesPerSecond]];
            summary[summary.count - 1] = [summary.lastObject stringByAppendingFormat:@" %@",
              [view->_controllers diagnosticSnapshot]];
            summary[summary.count - 1] = [summary.lastObject stringByAppendingFormat:
              @" surface_first_responder=%d window_key=%d screen_idle_disabled=%d",
              view->_surface.isFirstResponder, view.view.window.isKeyWindow,
              UIApplication.sharedApplication.idleTimerDisabled];
            [summary addObject:[NSString stringWithFormat:@"[GalaxyPad runtime counters] frame_max_gap_ms=%.3f frame_gaps_ge_33ms=%llu frame_gaps_ge_100ms=%llu efb_color_peeks=%llu efb_depth_peeks=%llu efb_total_peek_ms=%.3f efb_max_peek_ms=%.3f efb_frames_with_peeks=%llu efb_max_peeks_per_frame=%llu",
              runtime.frameMaxGapNs / 1e6,
              (unsigned long long)runtime.frameGapsGe33ms,
              (unsigned long long)runtime.frameGapsGe100ms,
              (unsigned long long)runtime.efbColorPeeks,
              (unsigned long long)runtime.efbDepthPeeks,
              runtime.efbPeekNs / 1e6, runtime.efbMaxPeekNs / 1e6,
              (unsigned long long)runtime.efbFramesWithPeeks,
              (unsigned long long)runtime.efbMaxPeeksPerFrame]];
            view->_frameWindowCPU = cpu;
            // Cumulative mixer events, bracketed independently of frame counts.
            // RemoteIO's separate opt-in counters report their availability.
            // Do not confuse disabled measurement with zero delivered audio.
            const double audioBefore = CACurrentMediaTime();
            const auto audio = [view->_host audioCounters];
            const double audioAfter = CACurrentMediaTime();
            if (audio.valid) {
              [summary addObject:[NSString stringWithFormat:@"[GalaxyPad audio counters] mono_before=%.6f mono_after=%.6f dma_enqueues=%llu dma_underruns=%llu dma_backlog_drops=%llu dma_full_drops=%llu dma_queue_min=%llu dma_queue_max=%llu dma_producer_max_gap_ms=%.3f dma_gaps_ge_50ms=%llu dma_gaps_ge_100ms=%llu dma_first_underrun_enqueue=%llu dma_last_underrun_enqueue=%llu output_counters_available=%d output_callbacks=%llu output_requested_frames=%llu output_frames=%llu output_nonzero_frames=%llu output_short_callbacks=%llu output_peak=%u",
                    audioBefore, audioAfter, (unsigned long long)audio.enqueues,
                    (unsigned long long)audio.underruns,
                    (unsigned long long)audio.backlogDrops,
                    (unsigned long long)audio.fullDrops,
                    (unsigned long long)audio.queueMin,
                    (unsigned long long)audio.queueMax,
                    audio.producerMaxGapNs / 1e6,
                    (unsigned long long)audio.gapsGe50ms,
                    (unsigned long long)audio.gapsGe100ms,
                    (unsigned long long)audio.firstUnderrunEnqueue,
                    (unsigned long long)audio.lastUnderrunEnqueue,
                    audio.output.available,
                    (unsigned long long)audio.output.callbacks,
                    (unsigned long long)audio.output.requestedFrames,
                    (unsigned long long)audio.output.frames,
                    (unsigned long long)audio.output.nonzeroFrames,
                    (unsigned long long)audio.output.shortCallbacks, audio.output.peak]];
            }
            GalaxyPadLogPerformanceWindow(summary);
            view->_frameWindowStart = now;
            view->_frameWindowFrames = frames;
            view->_frameWindowMinFPS = DBL_MAX;
            view->_frameWindowMaxObservationSeconds = 0;
          }
        }
      }
    }
  }];
  _overlay.viewportProvider = ^CGRect {
    GalaxyPadGameViewController *view = weakSelf;
    return view ? view->_host.normalizedViewport : CGRectZero;
  };
  _host.onExit = ^(NSString *error) {
    GalaxyPadGameViewController *view = weakSelf;
    if (!view) return;
    view->_status.hidden = NO;
    view->_status.text = error ?: @"Game stopped.";
    GalaxyPadLog(@"runtime exit failed=%d", error != nil);
    view->_overlay.hidden = NO;
    view->_overlay.userInteractionEnabled = YES;
    view->_overlay.gameplayAvailable = NO;
    [view reconcileControllerFocus];
    view->_overlay.stopRequested = nil;
    view->_restartButton.hidden = view->_activateImportAfterExit || view->_removingGameData;
    [view->_startupTimer invalidate];
    view->_startupTimer = nil;
    if (view->_activateImportAfterExit) [view finishImportActivation];
    if (view->_removingGameData) [view finishGameDataRemoval];
  };
}
- (void)viewDidLayoutSubviews {
  [super viewDidLayoutSubviews];
  CGRect safe = UIEdgeInsetsInsetRect(self.view.bounds, self.view.safeAreaInsets);
  _fpsLabel.frame = CGRectMake(CGRectGetMinX(safe)+12, CGRectGetMinY(safe)+20, 112, 24);
  _status.frame = CGRectMake(CGRectGetMidX(safe) - MIN(300, safe.size.width/2),
      CGRectGetMidY(safe)-50, MIN(600, safe.size.width), 100);
  _restartButton.frame = CGRectMake(CGRectGetMidX(safe)-90, CGRectGetMidY(safe)+60, 180, 48);
  UIWindowScene *scene = self.view.window.windowScene;
  NSString *geometry = [NSString stringWithFormat:@"bounds=%@ scene=%@ orientation=%ld drawable=%@",
      NSStringFromCGRect(self.view.bounds), NSStringFromCGRect(scene.coordinateSpace.bounds),
      (long)scene.interfaceOrientation, NSStringFromCGSize(_surface.metalLayer.drawableSize)];
  if (![_lastGeometry isEqualToString:geometry]) {
    _lastGeometry = geometry;
    NSLog(@"[GalaxyPad geometry] %@", geometry);
    NSLog(@"[GalaxyPad display] window=%@ screen=%@ native=%@ scale=%.2f deviceOrientation=%ld",
      NSStringFromCGRect(self.view.window.bounds), NSStringFromCGRect(scene.screen.bounds),
      NSStringFromCGRect(scene.screen.nativeBounds), scene.screen.scale,
      (long)UIDevice.currentDevice.orientation);
    if (@available(iOS 26.0, *)) {
      NSLog(@"[GalaxyPad effective geometry] %@", scene.effectiveGeometry);
    }
  }
}
- (BOOL)prefersStatusBarHidden { return YES; }
- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  [self reconcileControllerFocus];
  [self setNeedsUpdateOfSupportedInterfaceOrientations];
  UIWindowScene *scene = self.view.window.windowScene;
  [scene requestGeometryUpdateWithPreferences:[[UIWindowSceneGeometryPreferencesIOS alloc]
      initWithInterfaceOrientations:UIInterfaceOrientationMaskLandscape]
      errorHandler:^(NSError *error) { NSLog(@"[GalaxyPad] landscape request: %@", error); }];
  if (_attemptedStart) return;
  _attemptedStart = YES;
  [self startGame];
}
- (void)restartGame {
  if (_host.busy || _import || _removingGameData || self.presentedViewController) return;
  [self startGame];
}
- (void)startGame {
  if (_host.busy || _import || _removingGameData) return;
  _fpsFrames = 0;
  _fpsTime = CACurrentMediaTime();
  _frameWindowStart = 0;
  _status.hidden = NO;
  [_surface setNeedsLayout];
  [_surface layoutIfNeeded]; // ensure nonzero drawable before runtime creation
  NSString *root = nil;
  NSString *disc = nil;
  // Both platforms prefer the packaged module. Only Simulator development
  // launches may explicitly override it; imported data never supplies code.
  NSString *module = [NSBundle.mainBundle pathForResource:@"gRMGE01_recomp"
    ofType:@"dylib" inDirectory:@"Frameworks"];
#if TARGET_OS_SIMULATOR
  NSUserDefaults *args = NSUserDefaults.standardUserDefaults;
  root = [args stringForKey:@"GalaxyPadDevGameRoot"];
  disc = [args stringForKey:@"GalaxyPadDevDiscImage"];
  NSString *developmentModule = [args stringForKey:@"GalaxyPadDevModule"];
  if (developmentModule.length) module = developmentModule;
#endif
  NSURL *installed=[[self gameDataSupportURL] URLByAppendingPathComponent:@"GameData"];
  NSString *installedDisc=[[installed URLByAppendingPathComponent:@"RMGE01.wbfs"] path];
  if ([NSFileManager.defaultManager fileExistsAtPath:installedDisc]) {
    root=[[installed URLByAppendingPathComponent:@"RMGE01"] path];
    disc=installedDisc;
  }
  if (root.length && disc.length && module.length) {
    NSURL *support = [NSFileManager.defaultManager URLsForDirectory:NSApplicationSupportDirectory
      inDomains:NSUserDomainMask].firstObject;
    NSURL *user = [support URLByAppendingPathComponent:@"GalaxyPad" isDirectory:YES];
    NSError *error = nil;
    if (![NSFileManager.defaultManager createDirectoryAtURL:user withIntermediateDirectories:YES
        attributes:nil error:&error]) {
      _status.text = error.localizedDescription;
      return;
    }
    _status.text = @"Starting Galaxy…";
    _activeRenderScale = GalaxyPadSettings.sharedSettings.renderScale;
    const NSInteger aspectRatioMode = GalaxyPadSettings.sharedSettings.aspectRatioMode;
    GalaxyPadLog(@"Starting runtime: render_scale=%ld aspect_ratio_mode=%ld pointer_mode=virtual_wiimote_ir pointer_yaw=25 pointer_pitch=20 pointer_vertical_offset_cm=10 frame_logging=1 detailed_frame_logging=%d",
      (long)_activeRenderScale, (long)aspectRatioMode, _logFrameRateWindows);
    if (![_host startWithGameRoot:root discImage:disc module:module userDirectory:user.path]) return;
    _restartButton.hidden = YES;
    _overlay.gameplayAvailable = YES;
    [self reconcileControllerFocus];
    __weak GalaxyPadGameViewController *stopOwner = self;
    _overlay.stopRequested = ^{ [stopOwner stopGame]; };
    _overlay.hidden = NO;
    __weak GalaxyPadGameViewController *weakSelf = self;
    _startupTimer = [NSTimer scheduledTimerWithTimeInterval:0.25 repeats:YES block:^(NSTimer *timer) {
      GalaxyPadGameViewController *view = weakSelf;
      if (!view) { [timer invalidate]; return; }
      if (view->_host.renderedFrames > 0) {
        view->_status.hidden = YES; // renderer is presenting, not gameplay acceptance
        [timer invalidate];
        view->_startupTimer = nil;
      }
    }];
  } else {
    _status.hidden = NO;
    _status.text = module.length
      ? @"Import your supported Galaxy image using the three-dot menu, then relaunch GalaxyPad."
      : @"This build is missing its game module. Install a complete GalaxyPad build before importing game data.";
  }
}
- (void)reconcileControllerFocus {
  const BOOL keepAwake = _applicationActive && _host.busy && _overlay.gameplayAvailable;
  // Controller profile input bypasses UIKit touch activity. Keep the screen
  // awake even during app pause, then restore automatic sleep on stop/background.
  if (UIApplication.sharedApplication.idleTimerDisabled != keepAwake)
    UIApplication.sharedApplication.idleTimerDisabled = keepAwake;
  if (!keepAwake) {
    if (_surface.isFirstResponder) [_surface resignFirstResponder];
    return;
  }
  // Native editors/import alerts own their responder while presented. Reclaim
  // the game surface only at a gameplay lifecycle boundary, never every frame.
  if ((_menuPresented && !_overlay.nativePauseVisible) || self.presentedViewController || _import || _removingGameData ||
      !self.view.window.isKeyWindow) return;
  if (!_surface.isFirstResponder) [_surface becomeFirstResponder];
}
- (void)setApplicationActive:(BOOL)active {
  _frameWindowStart = 0;
  _applicationActive = active;
  GalaxyPadLog(@"scene active=%d", active);
  [_host setApplicationActive:active];
  [self reconcileControllerFocus];
  if (active) [_controllers reconcile];
}
- (void)reconcileNativeUI {
  BOOL nativeMenu = _overlay.nativeMenuVisible;
  BOOL modalUI = self.presentedViewController != nil || _import != nil || _removingGameData;
  BOOL blocked = _overlay.blocksGameplay || modalUI;
  // The three-dot UIMenu is an input-owned HUD surface; it must not stop the
  // emulated CPU/audio clock. Native alerts, import sheets, and the explicit
  // Pause panel still request a runtime pause.
  // UIMenu presentation is host UI only. Keep this explicit so a future
  // UIKit presentation-controller change cannot turn the three-dot menu into
  // a runtime pause just because presentedViewController became non-nil.
  BOOL pauseRuntime = !nativeMenu && (modalUI || _overlay.blocksGameplay);
  if (_menuPresented == blocked && _runtimePauseRequested == pauseRuntime) return;
  BOOL wasBlocked = _menuPresented;
  _frameWindowStart = 0;
  _menuPresented = blocked;
  _runtimePauseRequested = pauseRuntime;
  GalaxyPadLog(@"native UI blocked=%d pause_runtime=%d; input cleared overlay=%d native_menu=%d presented=%d import=%d removal=%d",
    blocked, pauseRuntime, _overlay.blocksGameplay, nativeMenu,
    self.presentedViewController != nil,
    _import != nil, _removingGameData);
  [_host setNativeUIBlocked:blocked pauseRuntime:pauseRuntime];
  if (wasBlocked && !blocked) [_controllers reconcile];
  [self reconcileControllerFocus];
}
- (void)presentViewController:(UIViewController *)controller animated:(BOOL)animated
    completion:(void (^)(void))completion {
  _frameWindowStart = 0;
  _menuPresented = YES;
  // Mark native UI as input-blocking immediately, but defer the pause decision
  // until UIKit has identified what it presented. The three-dot UIMenu uses
  // this override on iPadOS and must not pause the emulated runtime.
  _runtimePauseRequested = NO;
  [_host setNativeUIBlocked:YES pauseRuntime:NO];
  __weak GalaxyPadGameViewController *weakSelf = self;
  [super presentViewController:controller animated:animated completion:^{
    [weakSelf reconcileNativeUI];
    if (completion) completion();
  }];
}
- (void)stopGame {
  _frameWindowStart = 0;
  if (!_host.busy) {
    _status.hidden=NO;
    _status.text=@"Game stopped.";
    return; // No onExit callback will arrive to re-enable an idle overlay.
  }
  [_startupTimer invalidate];
  _startupTimer = nil;
  _status.hidden = NO;
  _status.text = @"Stopping game…";
  _overlay.gameplayAvailable = NO;
  [self reconcileControllerFocus];
  _overlay.userInteractionEnabled = NO;
  [_host stop];
}
- (NSURL *)gameDataSupportURL {
  NSURL *support=[NSFileManager.defaultManager URLsForDirectory:NSApplicationSupportDirectory
    inDomains:NSUserDomainMask].firstObject;
  return [support URLByAppendingPathComponent:@"GalaxyPad" isDirectory:YES];
}
- (void)gameOverlayRequestsGameDataChange:(GalaxyPadGameOverlay *)overlay {
  (void)overlay;
  if (_import || _removingGameData) return;
  UIAlertController *notice=[UIAlertController alertControllerWithTitle:@"Import Game Data"
    message:@"Select your supported RMGE01 revision 0 WBFS image. GalaxyPad makes and verifies a private copy. After verification, the current game stops before data is replaced. Saves are kept. Other image formats are not supported yet."
    preferredStyle:UIAlertControllerStyleAlert];
  [notice addAction:[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil]];
  __weak GalaxyPadGameViewController *weakSelf=self;
  [notice addAction:[UIAlertAction actionWithTitle:@"Choose Image" style:UIAlertActionStyleDefault
    handler:^(UIAlertAction *action) {
      (void)action;
      [weakSelf dismissViewControllerAnimated:YES completion:^{
        // SunPad document-picker flow; open in place because the transaction
        // owns its cancellable copy rather than creating an extra system copy.
        UIDocumentPickerViewController *picker=[[UIDocumentPickerViewController alloc]
          initForOpeningContentTypes:@[UTTypeData] asCopy:NO];
        picker.delegate=weakSelf;
        picker.allowsMultipleSelection=NO;
        picker.shouldShowFileExtensions=YES;
        [weakSelf presentViewController:picker animated:YES completion:nil];
      }];
    }]];
  [self presentViewController:notice animated:YES completion:nil];
}
- (void)gameOverlayRequestsGameDataStatus:(GalaxyPadGameOverlay *)overlay {
  (void)overlay;
  NSURL *root=[self gameDataSupportURL];
  NSFileManager *files=NSFileManager.defaultManager;
  BOOL image=[files fileExistsAtPath:[root URLByAppendingPathComponent:@"GameData/RMGE01.wbfs"].path];
  BOOL save=[files fileExistsAtPath:[root URLByAppendingPathComponent:@"Wii/title/00010000/524d4745/data/GameData.bin"].path];
  NSString *message=[NSString stringWithFormat:
    @"Supported: Super Mario Galaxy\nRMGE01 · revision 0\n\n"
     "Imported image: %@\nWii save file: %@\n\n"
     "Expected main.dol SHA-256:\n%@\n\n"
     "File presence only. Integrity and saved progress are not checked here.",
    image ? @"Detected" : @"Not detected", save ? @"Detected" : @"Not detected", @(GalaxyPadDOLSHA256)];
  UIAlertController *alert=[UIAlertController alertControllerWithTitle:@"Game Data & Saves"
    message:message preferredStyle:UIAlertControllerStyleAlert];
  [alert addAction:[UIAlertAction actionWithTitle:@"Done" style:UIAlertActionStyleCancel handler:nil]];
  [self presentViewController:alert animated:YES completion:nil];
}
- (void)documentPicker:(UIDocumentPickerViewController *)picker didPickDocumentsAtURLs:(NSArray<NSURL *> *)urls {
  if (urls.count!=1 || _import) return;
  [picker dismissViewControllerAnimated:YES completion:^{ [self beginImport:urls.firstObject]; }];
}
- (void)beginImport:(NSURL *)source {
  if (_import || _removingGameData) return;
  NSURL *root=[self gameDataSupportURL];
  if (![NSFileManager.defaultManager createDirectoryAtURL:root withIntermediateDirectories:YES attributes:nil error:nil]) {
    _status.hidden=NO; _status.text=@"Private import storage is unavailable."; return;
  }
  _import=[[GalaxyPadImportTransaction alloc] initWithRoot:root];
  _importProgress=[UIAlertController alertControllerWithTitle:@"Importing Game Data"
    message:@"Preparing private copy…" preferredStyle:UIAlertControllerStyleAlert];
  __weak GalaxyPadGameViewController *weakSelf=self;
  UIAlertAction *cancel=[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel
    handler:^(UIAlertAction *action) {
      (void)action;
      GalaxyPadGameViewController *view=weakSelf;
      if (!view) return;
      [view->_import cancel];
      view->_status.hidden=NO;
      view->_status.text=@"Cancelling import and cleaning private staging…";
    }];
  [_importProgress addAction:cancel];
  [self presentViewController:_importProgress animated:YES completion:nil];
  [_import prepareImage:source progress:^(NSString *message,double fraction) {
    GalaxyPadGameViewController *view=weakSelf;
    if (view) view->_importProgress.message=[NSString stringWithFormat:@"%@ — %.0f%%",message,100*fraction];
  } completion:^(BOOL ok,NSString *error) {
    GalaxyPadGameViewController *view=weakSelf;
    if (!view) return;
    if (!ok) { [view endImportWithMessage:error]; return; }
    cancel.enabled=NO; // Verified stage is now committed to stop/activation.
    view->_activateImportAfterExit=YES;
    view->_importProgress.message=@"Verified. Waiting for the game to stop…";
    if (view->_host.busy) [view stopGame];
    else [view finishImportActivation];
  }];
}
- (void)gameOverlayRequestsGameDataFolderImport:(GalaxyPadGameOverlay *)overlay {
  (void)overlay;
  if (_import || _removingGameData) return;
  // SunPad's Documents-folder selection flow. Only Documents is Files-visible;
  // installed images, staging, runtime logs and NAND stay in Application Support.
  NSURL *documents=[NSFileManager.defaultManager URLsForDirectory:NSDocumentDirectory
    inDomains:NSUserDomainMask].firstObject;
  NSError *error=nil;
  NSArray<NSURL *> *entries=[NSFileManager.defaultManager contentsOfDirectoryAtURL:documents
    includingPropertiesForKeys:@[NSURLIsRegularFileKey,NSURLIsSymbolicLinkKey]
    options:NSDirectoryEnumerationSkipsHiddenFiles error:&error];
  NSMutableArray<NSURL *> *images=[NSMutableArray array];
  for (NSURL *entry in entries) {
    NSNumber *regular=nil, *link=nil;
    if (![entry getResourceValue:&regular forKey:NSURLIsRegularFileKey error:nil] ||
        ![entry getResourceValue:&link forKey:NSURLIsSymbolicLinkKey error:nil]) continue;
    if (regular.boolValue && !link.boolValue && [entry.pathExtension.lowercaseString isEqualToString:@"wbfs"])
      [images addObject:entry];
  }
  [images sortUsingComparator:^NSComparisonResult(NSURL *a,NSURL *b) {
    return [a.lastPathComponent localizedStandardCompare:b.lastPathComponent];
  }];
  NSString *message=error ? @"The GalaxyPad folder could not be read. Try selecting the image through Import or Reimport Game Data."
    : images.count ? @"Choose your supported RMGE01 revision 0 WBFS. A private copy is verified before stopping the game and replacing stored data. Saves stay separate."
    : @"No WBFS image was found. In Files, place your supported image directly in On My iPad or On My iPhone → GalaxyPad, then try again.";
  UIAlertController *alert=[UIAlertController alertControllerWithTitle:@"GalaxyPad Folder"
    message:message preferredStyle:UIAlertControllerStyleAlert];
  __weak GalaxyPadGameViewController *weakSelf=self;
  for (NSURL *image in images) {
    [alert addAction:[UIAlertAction actionWithTitle:image.lastPathComponent style:UIAlertActionStyleDefault
      handler:^(UIAlertAction *action) {
        (void)action;
        [weakSelf dismissViewControllerAnimated:YES completion:^{ [weakSelf beginImport:image]; }];
      }]];
  }
  [alert addAction:[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil]];
  [self presentViewController:alert animated:YES completion:nil];
}
- (void)finishImportActivation {
  if (!_activateImportAfterExit || _host.busy) return;
  _activateImportAfterExit=NO;
  NSString *error=nil;
  BOOL ok=[_import activateWithRuntimeStopped:!_host.busy error:&error];
  if (!ok) {
    _importProgress.message=@"Activation failed. Cleaning unactivated staging…";
    __weak GalaxyPadGameViewController *weakSelf=self;
    [_import discardUnactivatedStage:^(BOOL removed,NSString *cleanupError) {
      [weakSelf endImportWithMessage:removed?error:
        [NSString stringWithFormat:@"%@ %@",error ?: @"Activation failed.",cleanupError ?: @""]];
    }];
    return;
  }
  NSString *success=@"Game data imported. Previous data, if any, is retained for recovery. Saves are unchanged.";
  success=[success stringByAppendingString:@" Relaunch GalaxyPad to play."];
  [self endImportWithMessage:ok
    ? success
    : error];
}
- (void)gameOverlayRequestsGameDataRemoval:(GalaxyPadGameOverlay *)overlay {
  (void)overlay;
  if (_import || _removingGameData) return;
  // The existing SunPad destructive confirmation precedes this delegate call.
  _removingGameData=YES;
  [self reconcileNativeUI];
  if (_host.busy) [self stopGame];
  else [self finishGameDataRemoval];
}
- (void)finishGameDataRemoval {
  if (!_removingGameData || _host.busy) return;
  NSURL *root=[self gameDataSupportURL];
  NSString *name=[@"GameData.removal-" stringByAppendingString:NSUUID.UUID.UUIDString];
  _status.hidden=NO;
  _status.text=@"Removing installed game data…";
  _overlay.userInteractionEnabled=NO;
  dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY,0), ^{
    auto error=galaxypad::detachInstalledData(root.fileSystemRepresentation,name.UTF8String,true);
    BOOL removed=NO;
    if (!error) removed=[NSFileManager.defaultManager removeItemAtURL:
      [root URLByAppendingPathComponent:name isDirectory:YES] error:nil];
    NSString *message;
    if (error==std::errc::no_such_file_or_directory) message=@"No installed game data was found. Saves are unchanged.";
    else if (error) message=@"Stored game data could not be removed. No data was detached.";
    else if (!removed) message=@"Game data was detached, but storage cleanup failed. Saves are unchanged; cleanup is still needed.";
    else message=@"Installed game data removed. Saves and control settings are unchanged. Any prior recovery copies are retained.";
    dispatch_async(dispatch_get_main_queue(), ^{
      self->_removingGameData=NO;
      self->_status.text=message;
      self->_overlay.userInteractionEnabled=YES;
      [self reconcileNativeUI];
    });
  });
}
- (void)endImportWithMessage:(NSString *)message {
  _status.hidden=NO;
  _status.text=message ?: @"Import did not complete.";
  _import=nil;
  _activateImportAfterExit=NO;
  _overlay.userInteractionEnabled=YES;
  if (_importProgress.presentingViewController) [_importProgress dismissViewControllerAnimated:YES completion:nil];
  _importProgress=nil;
  [self reconcileNativeUI];
}
- (NSString *)diagnosticContext {
  const auto audio = [_host audioCounters];
  return [NSString stringWithFormat:
    @"configuredTarget=RMGE01 revision=0 configuredImageSHA256=%s configuredDOLSHA256=%s; "
     "runtimeBusy=%d paused=%d frameEvents=%llu counterSource=after_frame_event "
     "renderScaleSelectedForNextLaunch=%ld activeRenderScale=%ld performanceLogging=1 detailedPerformanceLogging=%d; "
     "platform=%@ os=%@ thermalState=%ld lowPowerMode=%d; "
     "audioCountersAvailable=%d dmaEnqueues=%llu dmaUnderruns=%llu "
     "dmaBacklogDrops=%llu dmaFullDrops=%llu dmaQueueMin=%llu dmaQueueMax=%llu "
     "dmaProducerMaxGapMs=%.3f dmaGapsGe50ms=%llu dmaGapsGe100ms=%llu "
     "dmaFirstUnderrunEnqueue=%llu dmaLastUnderrunEnqueue=%llu; "
     "counterScope=cumulative_current_session_not_timed_window; "
     "frameEvents are not display completion; thermalState 0=nominal_or_unsupported,1=fair,2=serious,3=critical; "
     "pointerMode=classic; loaded module identity, signature and dispatch diagnostics not yet integrated",
    GalaxyPadImageSHA256,GalaxyPadDOLSHA256,_host.busy,_host.paused,
    (unsigned long long)_host.renderedFrames,(long)GalaxyPadSettings.sharedSettings.renderScale,
    (long)_activeRenderScale, _logFrameRateWindows,
    TARGET_OS_SIMULATOR ? @"simulator" : @"device", UIDevice.currentDevice.systemVersion,
    (long)NSProcessInfo.processInfo.thermalState, NSProcessInfo.processInfo.lowPowerModeEnabled,
    audio.valid, (unsigned long long)audio.enqueues, (unsigned long long)audio.underruns,
    (unsigned long long)audio.backlogDrops, (unsigned long long)audio.fullDrops,
    (unsigned long long)audio.queueMin, (unsigned long long)audio.queueMax,
    audio.producerMaxGapNs / 1e6, (unsigned long long)audio.gapsGe50ms,
    (unsigned long long)audio.gapsGe100ms,
    (unsigned long long)audio.firstUnderrunEnqueue,
    (unsigned long long)audio.lastUnderrunEnqueue];
}
- (void)presentDiagnosticReportURL:(NSURL *)url {
  if (url) {
    GalaxyPadReportViewController *report=[[GalaxyPadReportViewController alloc] initWithReportURL:url];
    UINavigationController *navigation=[[UINavigationController alloc] initWithRootViewController:report];
    navigation.modalPresentationStyle=UIModalPresentationPageSheet;
    [self presentViewController:navigation animated:YES completion:nil];
  } else {
    UIAlertController *failure=[UIAlertController alertControllerWithTitle:@"Report Unavailable"
      message:@"The local report could not be saved. Check available storage and try again."
      preferredStyle:UIAlertControllerStyleAlert];
    [failure addAction:[UIAlertAction actionWithTitle:@"OK" style:UIAlertActionStyleDefault handler:nil]];
    [self presentViewController:failure animated:YES completion:nil];
  }
}
- (void)gameOverlayRequestsDiagnosticLog:(GalaxyPadGameOverlay *)overlay {
  (void)overlay;
  NSError *error=nil;
  NSURL *url=GalaxyPadDiagnosticsReportURL(NSUUID.UUID.UUIDString,@{},[self diagnosticContext],&error);
  // Review first. The preview's Share button alone presents the system sheet.
  [self presentDiagnosticReportURL:url];
}
- (void)gameOverlayRequestsDevelopmentCheckpoint:(GalaxyPadGameOverlay *)overlay {
  (void)overlay;
  [_host requestDevelopmentCheckpoint];
}
- (void)gameOverlayRequestsDevelopmentCheckpointRestore:(GalaxyPadGameOverlay *)overlay {
  (void)overlay;
  [_host restoreDevelopmentCheckpoint];
}
- (void)gameOverlayRequestsAbout:(GalaxyPadGameOverlay *)overlay {
  (void)overlay;
  UINavigationController *navigation=[[UINavigationController alloc]
    initWithRootViewController:[[GalaxyPadAboutViewController alloc] init]];
  navigation.modalPresentationStyle=UIModalPresentationPageSheet;
  [self presentViewController:navigation animated:YES completion:nil];
}
- (void)gameOverlayRequestsProblemReport:(GalaxyPadGameOverlay *)overlay {
  (void)overlay;
  // Review a GitHub draft before opening the issue tracker; logs are optional.
  UIAlertController *prompt = [UIAlertController alertControllerWithTitle:@"Report a Problem"
    message:@"Describe the problem without private information. Review a GitHub issue draft with app status, then optionally prepare a diagnostic log to attach. Nothing is submitted automatically."
    preferredStyle:UIAlertControllerStyleAlert];
  for (NSString *placeholder in @[@"What went wrong?", @"Area and what you were doing (optional)",
                                  @"Every time, sometimes, once, or unsure?"]) {
    [prompt addTextFieldWithConfigurationHandler:^(UITextField *field) {
      field.placeholder = placeholder;
      field.clearButtonMode = UITextFieldViewModeWhileEditing;
    }];
  }
  [prompt addAction:[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil]];
  __weak GalaxyPadGameViewController *weakSelf = self;
  __weak UIAlertController *weakPrompt = prompt;
  [prompt addAction:[UIAlertAction actionWithTitle:@"Review GitHub Report" style:UIAlertActionStyleDefault
    handler:^(UIAlertAction *action) {
      (void)action;
      GalaxyPadGameViewController *view = weakSelf;
      UIAlertController *questions = weakPrompt;
      if (!view || questions.textFields.count != 3) return;
      NSDictionary *answers = @{@"problem": questions.textFields[0].text ?: @"",
        @"context": questions.textFields[1].text ?: @"", @"frequency": questions.textFields[2].text ?: @""};
      NSString *context = [view diagnosticContext];
      // Explicit dismissal completion avoids presenting underneath the alert.
      [view dismissViewControllerAnimated:YES completion:^{
        GalaxyPadReportViewController *report = [[GalaxyPadReportViewController alloc]
          initWithReporterAnswers:answers technicalContext:context];
        UINavigationController *navigation = [[UINavigationController alloc] initWithRootViewController:report];
        [view presentViewController:navigation animated:YES completion:nil];
      }];
    }]];
  [self presentViewController:prompt animated:YES completion:nil];
}
- (void)gameOverlayRequestsControllerMapping:(GalaxyPadGameOverlay *)overlay {
  (void)overlay; [self presentControllerMapping];
}
- (void)presentControllerMapping {
  // SunPad's assignment-list/physical-choice flow, with Galaxy's action set.
  const auto mapping=GalaxyPadControllerMappingStore.mapping;
  NSArray *games=@[@"A", @"B", @"Spin", @"C", @"Z"];
  NSArray *physical=@[@"A", @"B", @"X", @"Y", @"Left Trigger"];
  UIAlertController *alert=[UIAlertController alertControllerWithTitle:@"Controller Button Mapping"
    message:@"Assignments swap to keep every action reachable. Left stick moves; right stick aims; click right stick to recenter. Hold Left Shoulder for right-stick tilt. Right Shoulder is also A; Right Trigger is also B, so you can aim while using either action. Menu/Start or the on-screen + opens Galaxy’s original pause menu, including Return to Observatory when available. View/Select toggles app pause; press it again to resume. D-pad controls the camera. Connect a controller to test."
    preferredStyle:UIAlertControllerStyleAlert];
  __weak GalaxyPadGameViewController *weakSelf=self;
  for (unsigned i=0;i<5;++i) {
    [alert addAction:[UIAlertAction actionWithTitle:[NSString stringWithFormat:@"%@ — %@",games[i],physical[mapping.physical[i]]]
      style:UIAlertActionStyleDefault handler:^(UIAlertAction *action) {
        (void)action;
        [weakSelf dismissViewControllerAnimated:YES completion:^{ [weakSelf presentControllerChoices:i]; }];
      }]];
  }
  [alert addAction:[UIAlertAction actionWithTitle:@"Reset to Default" style:UIAlertActionStyleDestructive
    handler:^(UIAlertAction *action) {
      (void)action;
      GalaxyPadGameViewController *view=weakSelf;
      if (!view) return;
      [GalaxyPadControllerMappingStore reset];
      [view->_controllers reloadMapping]; [view->_host clearInput];
      [view dismissViewControllerAnimated:YES completion:^{ [view presentControllerMapping]; }];
    }]];
  [alert addAction:[UIAlertAction actionWithTitle:@"Done" style:UIAlertActionStyleCancel handler:nil]];
  [self presentViewController:alert animated:YES completion:nil];
}
- (void)presentControllerChoices:(unsigned)game {
  if (game>=5) return;
  NSArray *games=@[@"A", @"B", @"Spin", @"C", @"Z"];
  NSArray *physical=@[@"A", @"B", @"X", @"Y", @"Left Trigger"];
  UIAlertController *alert=[UIAlertController alertControllerWithTitle:games[game]
    message:@"Choose a physical button. Its existing assignment swaps with this one."
    preferredStyle:UIAlertControllerStyleAlert];
  __weak GalaxyPadGameViewController *weakSelf=self;
  for (unsigned i=0;i<5;++i) {
    [alert addAction:[UIAlertAction actionWithTitle:physical[i] style:UIAlertActionStyleDefault
      handler:^(UIAlertAction *action) {
        (void)action;
        GalaxyPadGameViewController *view=weakSelf;
        if (!view) return;
        [GalaxyPadControllerMappingStore setMapping:GalaxyPadControllerMappingStore.mapping.assigning(game,i)];
        [view->_controllers reloadMapping]; [view->_host clearInput];
        [view dismissViewControllerAnimated:YES completion:^{ [view presentControllerMapping]; }];
      }]];
  }
  [alert addAction:[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel
    handler:^(UIAlertAction *action) {
      (void)action;
      [weakSelf dismissViewControllerAnimated:YES completion:^{ [weakSelf presentControllerMapping]; }];
    }]];
  [self presentViewController:alert animated:YES completion:nil];
}
- (UIInterfaceOrientationMask)supportedInterfaceOrientations { return UIInterfaceOrientationMaskLandscape; }
- (UIInterfaceOrientation)preferredInterfaceOrientationForPresentation { return UIInterfaceOrientationLandscapeLeft; }
// Match SunPad: permit rotation between the two supported landscape sides.
// iOS 26 scene-orientation locking is not a landscape-only mask.
@end

@interface GalaxyPadSceneDelegate : UIResponder <UIWindowSceneDelegate>
@property(nonatomic, strong) UIWindow *window;
@end
@implementation GalaxyPadSceneDelegate
- (void)scene:(UIScene *)scene willConnectToSession:(UISceneSession *)session
    options:(UISceneConnectionOptions *)options {
  (void)session; (void)options;
  if (![scene isKindOfClass:UIWindowScene.class]) return;
  self.window = [[UIWindow alloc] initWithWindowScene:(UIWindowScene *)scene];
  self.window.rootViewController = [[GalaxyPadGameViewController alloc] init];
  [self.window makeKeyAndVisible];
}
- (void)sceneWillResignActive:(UIScene *)scene {
  (void)scene;
  GalaxyPadLog(@"scene lifecycle will_resign_active");
  [(GalaxyPadGameViewController *)self.window.rootViewController setApplicationActive:NO];
}
- (void)sceneDidBecomeActive:(UIScene *)scene {
  (void)scene;
  GalaxyPadLog(@"scene lifecycle did_become_active");
  [(GalaxyPadGameViewController *)self.window.rootViewController setApplicationActive:YES];
}
@end
@interface GalaxyPadAppDelegate : UIResponder <UIApplicationDelegate>
@end
@implementation GalaxyPadAppDelegate
@end
int main(int argc, char *argv[]) {
  // Guarded decoder byte stores: R647/R648/R650 mobile confirmation.
  // Set before runtime threads start; preserve explicit opt-out and other values.
  setenv("GALAXYPAD_LC_BYTE_FAST", "1", 0);
  @autoreleasepool { return UIApplicationMain(argc, argv, nil, NSStringFromClass(GalaxyPadAppDelegate.class)); }
}
