// SPDX-License-Identifier: GPL-3.0-or-later
// SunPad fcdc1411 CoreHost: CAMetalLayer runtime embedding and lifecycle retry
// pattern. Galaxy owns this adaptation; no GMSE01 timing/patch/input carryover.
#import "GalaxyPadCoreHost.h"
#import "../shared/GalaxyPadSettings.h"
#import "../shared/GalaxyPadDiagnostics.h"
#import <AVFAudio/AVFAudio.h>
#import <UIKit/UIKit.h>
#include <memory>
#include <mutex>
#include "moderngekko/runtime.hpp"
#include "Core/Core.h"
#include "Core/System.h"
#include "Core/Config/MainSettings.h"
#include "Core/Config/GraphicsSettings.h"
#include "AudioCommon/AudioCommon.h"
#include "../shared/GalaxyPadInputDevice.h"
#include "InputCommon/ControllerInterface/ControllerInterface.h"
#include "VideoCommon/Present.h"
#include "VideoCommon/PerformanceMetrics.h"
#include "VideoCommon/VideoEvents.h"
#import <TargetConditionals.h>
#if TARGET_OS_SIMULATOR
#include "Core/State.h"
#include "GalaxyPadDevelopmentCheckpoint.h"
#include <pthread.h>
#import <CommonCrypto/CommonDigest.h>
#include "GalaxyPadDiscIdentity.h"
#include "../shared/GalaxyPadPointerContext.h"
#include "../shared/GalaxyPadMenuPointerReadiness.h"
#include "Core/HW/WiimoteEmu/Camera.h"
#include <chrono>
#include "Core/HW/Memmap.h"
#include "Core/PowerPC/PowerPC.h"
#include "GalaxyPadPointerHooks.h"
#if GALAXYPAD_ENABLE_NATIVE_THP
#include "../shared/GalaxyPadTHPMod.h"
#endif
#include "../shared/GalaxyPadNativeObserverBinding.h"
#include "Common/DynamicLibrary.h"
#endif

namespace {
static NSString *RuntimeFailureMessage(const moderngekko::RuntimeError& error) {
  if (error.code == moderngekko::RuntimeErrorCode::BootFailed) {
    GalaxyPadLogRuntimeEvent(@"error", @"core", @"boot_failed");
    return @"Game data may be missing or incomplete. Finish importing or transferring it, then tap Restart Game. If it still fails, use Import or Reimport Game Data in the menu. Saves are unchanged.";
  }
  return @(error.message.c_str());
}

struct Session {
  std::mutex mutex;
  std::mutex viewportMutex;
  CGRect viewport = CGRectZero;
  moderngekko::Runtime *runtime = nullptr; // guarded; owned by worker
  bool stopping = false;
  bool stopRetryScheduled = false;
  bool inputRegistrationQueued = false;
  int queuedVolume = -1;
  bool queuedMute = false;
#if TARGET_OS_SIMULATOR
  // Independent lock: CPU observations must never wait on runtime lifecycle work.
  std::mutex pointerConfigurationMutex;
  std::optional<galaxypad::MenuPointerConfiguration> pointerConfiguration;
  std::chrono::steady_clock::time_point pointerConfigurationTime{};
  bool pointerMotionInvalidated=false; // experimental neutral-only session
#endif
  std::shared_ptr<galaxypad::InputMixer> mixer = std::make_shared<galaxypad::InputMixer>();
  std::shared_ptr<ciface::Core::Device> device = galaxypad::makeInputDevice(mixer);
};
// Caller holds Session::mutex. A second platform request after a grace period
// leaves MainLoop and runs Core::Stop/Shutdown if the guest ignores the first
// STM power-button event (observed during early startup).
void RequestSessionStop(const std::shared_ptr<Session>& session) {
  if (!session->runtime) return;
  if (Core::GetState(Core::System::GetInstance()) == Core::State::Paused)
    session->runtime->Resume();
  session->runtime->RequestStop();
  if (session->stopRetryScheduled) return;
  session->stopRetryScheduled = true;
  dispatch_after(dispatch_time(DISPATCH_TIME_NOW, 10 * NSEC_PER_SEC),
    dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
      std::lock_guard lock(session->mutex);
      if (session->stopping && session->runtime) {
        NSLog(@"[GalaxyPad] guest shutdown grace expired; requesting core teardown");
        session->runtime->RequestStop();
      }
    });
}
void RuntimeLog(moderngekko::RuntimeLogLevel level, const char *category,
                const char *message, void *) {
  NSString *categoryString = category ? [NSString stringWithUTF8String:category] : @"runtime";
  NSString *messageString = message ? [NSString stringWithUTF8String:message] : @"";
  GalaxyPadLogRuntimeEvent(level == moderngekko::RuntimeLogLevel::Error ? @"error" : @"warning",
    categoryString ?: @"runtime", messageString ?: @"");
}
}

@implementation GalaxyPadCoreHost {
#if TARGET_OS_SIMULATOR
  NSString *_developmentModulePath;
  NSString *_developmentUserDirectory;
#endif
  CAMetalLayer *_layer;
  std::shared_ptr<Session> _session;
  dispatch_queue_t _worker;
  NSTimer *_lifecycleTimer;
  BOOL _busy, _paused, _active, _nativeUIBlocked, _pauseRequested, _interrupted, _audioActive;
}
- (instancetype)initWithLayer:(CAMetalLayer *)layer {
  if ((self = [super init])) {
    _layer = layer;
    _active = UIApplication.sharedApplication.applicationState == UIApplicationStateActive;
    _worker = dispatch_queue_create("org.galaxypad.runtime", DISPATCH_QUEUE_SERIAL);
    [NSNotificationCenter.defaultCenter addObserver:self
      selector:@selector(audioInterruption:) name:AVAudioSessionInterruptionNotification
      object:AVAudioSession.sharedInstance];
  }
  return self;
}
- (BOOL)busy { return _busy; }
- (BOOL)paused { return _paused; }
- (CGRect)normalizedViewport {
  if (!_session) return CGRectZero;
  std::lock_guard lock(_session->viewportMutex);
  return _session->viewport;
}
- (void)publishInput:(galaxypad::InputState)input source:(galaxypad::InputSource)source {
  NSAssert(NSThread.isMainThread, @"Host API requires main thread");
  if (!_busy || !_session || !_active || _nativeUIBlocked || _interrupted) return;
  std::lock_guard lock(_session->mutex);
  if (!_session->stopping) _session->mixer->set(source, input);
}
- (void)clearInput {
  NSAssert(NSThread.isMainThread, @"Host API requires main thread");
  if (_session) {
#if TARGET_OS_SIMULATOR
    {
      std::lock_guard lock(_session->pointerConfigurationMutex);
      _session->pointerConfiguration.reset();
      _session->pointerConfigurationTime={};
    }
#endif
    _session->mixer->clearAll();
    _session->device->UpdateInput(); // clear cached device values even when paused
  }
  if (self.onInputReset) self.onInputReset();
}
- (uint64_t)renderedFrames {
  NSAssert(NSThread.isMainThread, @"Host API requires main thread");
  if (!_session) return 0;
  std::lock_guard lock(_session->mutex);
  return _session->runtime ? _session->runtime->GetDiagnosticsSnapshot().frame_count : 0;
}
- (GalaxyPadAudioCounters)audioCounters {
  NSAssert(NSThread.isMainThread, @"Host API requires main thread");
  if (!_session) return {};
  std::lock_guard lock(_session->mutex);
  if (!_session->runtime) return {};
  const auto snapshot = _session->runtime->GetDiagnosticsSnapshot();
  return {true, snapshot.dma_enqueues, snapshot.dma_underruns,
          snapshot.dma_backlog_drops, snapshot.dma_queue_full_drops,
          snapshot.dma_queue_min, snapshot.dma_queue_max,
          snapshot.dma_producer_max_gap_ns, snapshot.dma_gaps_ge_50ms,
          snapshot.dma_gaps_ge_100ms, snapshot.dma_first_underrun_enqueue,
          snapshot.dma_last_underrun_enqueue,
          galaxypad::audio::outputCounters.Read()};
}
- (GalaxyPadCadenceEstimate)cadenceEstimate {
  NSAssert(NSThread.isMainThread, @"Host API requires main thread");
  if (!_session) return {NAN, NAN};
  std::lock_guard lock(_session->mutex);
  if (!_session->runtime) return {NAN, NAN};
  // Both upstream getters are explicitly safe from any thread. These are
  // rolling estimates, not counters over the host's five-second frame window.
  const auto& metrics = Core::System::GetInstance().GetPerfMetrics();
  return {metrics.GetVPS(), metrics.GetSpeed()};
}
- (GalaxyPadRuntimeCounters)runtimeCounters {
  NSAssert(NSThread.isMainThread, @"Host API requires main thread");
  if (!_session) return {};
  std::lock_guard lock(_session->mutex);
  if (!_session->runtime) return {};
  const auto snapshot = _session->runtime->GetDiagnosticsSnapshot();
  return {snapshot.frame_max_gap_ns, snapshot.frame_gaps_ge_33ms,
          snapshot.frame_gaps_ge_100ms, snapshot.efb_color_peeks,
          snapshot.efb_depth_peeks, snapshot.efb_peek_ns,
          snapshot.efb_max_peek_ns, snapshot.efb_frames_with_peeks,
          snapshot.efb_max_peeks_per_frame};
}
- (void)requestDevelopmentCheckpoint {
#if TARGET_OS_SIMULATOR
  NSAssert(NSThread.isMainThread, @"Host API requires main thread");
  if (![NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevCheckpoints"] || !_session)
    return;
  [self clearInput];
  std::lock_guard lock(_session->mutex);
  if (!_session->runtime || _session->stopping) return;
  auto& system = Core::System::GetInstance();
  const auto state = Core::GetState(system);
  if (state != Core::State::Running && state != Core::State::Paused) return;
  NSURL *base = [NSFileManager.defaultManager URLsForDirectory:NSApplicationSupportDirectory
                                                   inDomains:NSUserDomainMask].firstObject;
  if (!base) return;
  NSURL *directory = [base URLByAppendingPathComponent:@"GalaxyPad/DevelopmentCheckpoints"
                                         isDirectory:YES];
  NSError *error = nil;
  if (![NSFileManager.defaultManager createDirectoryAtURL:directory
                            withIntermediateDirectories:YES attributes:nil error:&error]) {
    NSLog(@"[GalaxyPad checkpoint] directory failed: %@", error.localizedDescription);
    return;
  }
  NSArray *existing = [NSFileManager.defaultManager contentsOfDirectoryAtURL:directory
                    includingPropertiesForKeys:nil options:0 error:&error];
  NSNumber *available = nil;
  [directory getResourceValue:&available forKey:NSURLVolumeAvailableCapacityForImportantUsageKey
                        error:&error];
  static CFTimeInterval lastRequest = -INFINITY;
  const CFTimeInterval now = CACurrentMediaTime();
  if (!existing || existing.count >= 8 || !available ||
      available.longLongValue < 2LL * 1024 * 1024 * 1024 || now - lastRequest < 30) {
    NSLog(@"[GalaxyPad checkpoint] request refused: capacity/count/cooldown guard");
    return;
  }
  // Never reuse a slot or overwrite a previous checkpoint or game save.
  NSURL *file = [directory URLByAppendingPathComponent:
      [NSUUID.UUID.UUIDString stringByAppendingPathExtension:@"sav"]];
  if ([NSFileManager.defaultManager fileExistsAtPath:file.path]) return;
  NSDictionary *identity = GalaxyPadCheckpointIdentity(_developmentModulePath, _developmentUserDirectory);
  if (!identity) {
    NSLog(@"[GalaxyPad checkpoint] identity unavailable; save refused");
    return;
  }
  NSUserDefaults *defaults = NSUserDefaults.standardUserDefaults;
  [defaults setObject:@{@"filename":file.lastPathComponent, @"identity":identity}
               forKey:@"GalaxyPadLastDevelopmentCheckpoint"];
  lastRequest = now;
  State::SaveAs(system, file.path.fileSystemRepresentation);
  NSLog(@"[GalaxyPad checkpoint] save requested path=%@; completion not yet verified", file.path);
#endif
}
- (void)restoreDevelopmentCheckpoint {
#if TARGET_OS_SIMULATOR
  NSAssert(NSThread.isMainThread, @"Host API requires main thread");
  if (![NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevCheckpoints"] || !_session)
    return;
  [self clearInput];
  std::lock_guard lock(_session->mutex);
  if (!_session->runtime || _session->stopping) return;
  auto& system = Core::System::GetInstance();
  if (Core::GetState(system) != Core::State::Running && Core::GetState(system) != Core::State::Paused)
    return;
  NSDictionary *saved = [NSUserDefaults.standardUserDefaults dictionaryForKey:@"GalaxyPadLastDevelopmentCheckpoint"];
  NSDictionary *identity = GalaxyPadCheckpointIdentity(_developmentModulePath, _developmentUserDirectory);
  if (!GalaxyPadCheckpointFilenameValid(saved[@"filename"]) ||
      !GalaxyPadCheckpointIdentityMatches(saved[@"identity"], identity)) {
    NSLog(@"[GalaxyPad checkpoint] restore refused: app/module/NAND identity or filename mismatch");
    return;
  }
  NSURL *base = [NSFileManager.defaultManager URLsForDirectory:NSApplicationSupportDirectory
                                                    inDomains:NSUserDomainMask].firstObject;
  if (!base) return;
  NSURL *file = [[base URLByAppendingPathComponent:@"GalaxyPad/DevelopmentCheckpoints" isDirectory:YES]
                URLByAppendingPathComponent:saved[@"filename"]];
  NSDictionary *attributes = [NSFileManager.defaultManager attributesOfItemAtPath:file.path error:nil];
  // Upstream publishes this unique final name only after its write/rename step.
  // Core LoadAs still validates the state format and handles read failure.
  if (![attributes[NSFileType] isEqual:NSFileTypeRegular] ||
      [attributes[NSFileSize] unsignedLongLongValue] < 32 ||
      [attributes[NSFileSize] unsignedLongLongValue] > 512ULL*1024*1024) {
    NSLog(@"[GalaxyPad checkpoint] restore refused: final state file unavailable or invalid size");
    return;
  }
  State::LoadAsWithoutRetainingUndo(system, file.path.fileSystemRepresentation);
  NSLog(@"[GalaxyPad checkpoint] restore requested; visible state and input verification required");
#endif
}
- (BOOL)startWithGameRoot:(NSString *)root discImage:(NSString *)disc
                  module:(NSString *)module userDirectory:(NSString *)user {
  NSAssert(NSThread.isMainThread, @"Host API requires main thread");
  if (_busy) return NO;
#if TARGET_OS_SIMULATOR
  _developmentModulePath = [module copy];
  _developmentUserDirectory = [user copy];
#endif
  NSString *configDirectory = [user stringByAppendingPathComponent:@"Config"];
  NSError *configError = nil;
  [NSFileManager.defaultManager createDirectoryAtPath:configDirectory
    withIntermediateDirectories:YES attributes:nil error:&configError];
  if (!configError) {
    NSString *wiimoteConfig=@(galaxypad::mobileWiimoteConfig);
#if TARGET_OS_SIMULATOR
    // Bounded R580 coverage experiment; normal/device profiles stay unchanged.
    if ([NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevPointerPitch22"]) {
      wiimoteConfig=[wiimoteConfig stringByReplacingOccurrencesOfString:@"IR/Hide ="
        withString:@"IR/Total Pitch = 22\nIR/Hide ="];
      NSLog(@"[GalaxyPad pointer experiment] configured total pitch=22 degrees");
    }
#endif
    [wiimoteConfig writeToFile:
      [configDirectory stringByAppendingPathComponent:@"WiimoteNew.ini"]
      atomically:YES encoding:NSUTF8StringEncoding error:&configError];
  }
  if (configError) {
    if (self.onExit) self.onExit(configError.localizedDescription);
    return NO;
  }
  _session = std::make_shared<Session>();
  auto session = _session;
  CAMetalLayer *layer = _layer;
  const int renderScale = (int)GalaxyPadSettings.sharedSettings.renderScale;
  const int aspectRatioMode = (int)GalaxyPadSettings.sharedSettings.aspectRatioMode;
  const int initialVolume = (int)GalaxyPadSettings.sharedSettings.mainVolume;
  const bool initialMute = GalaxyPadSettings.sharedSettings.mainAudioMuted;
#if TARGET_OS_SIMULATOR
  const bool pointerProbe=[NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevPointerContext"];
  const bool cpuQoSExperiment=[NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevCPUUserInitiatedQoS"];
  const bool nativePointerProbe=[NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevNativePointerObserver"];
  const bool pitch22Profile=[NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevPointerPitch22"];
  if (pitch22Profile && pointerProbe &&
      [NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevCalibratedTouch"]) {
    std::weak_ptr<Session> weakSession=session;
    session->mixer->setTouchPointerMapper([weakSession](const galaxypad::InputState& touch,
        const galaxypad::InputState& merged)->std::optional<std::pair<float,float>> {
      auto owner=weakSession.lock();
      if(!owner) return std::nullopt;
      std::optional<galaxypad::MenuPointerConfiguration> configuration;
      {
        std::lock_guard lock(owner->pointerConfigurationMutex);
        if((merged.buttons&galaxypad::Spin) || merged.tiltX!=0 || merged.tiltY!=0)
          owner->pointerMotionInvalidated=true;
        if(!touch.pointerVisible) return std::nullopt;
        auto age=std::chrono::steady_clock::now()-owner->pointerConfigurationTime;
        if(owner->pointerMotionInvalidated || age<decltype(age)::zero() ||
           age>std::chrono::milliseconds(250)) return std::nullopt;
        configuration=owner->pointerConfiguration;
      }
      if(!configuration) return std::nullopt;
      auto result=galaxypad::InvertPointer(galaxypad::PointerPoint{touch.pointerX,touch.pointerY},
        [&](galaxypad::PointerPoint point) {
          return galaxypad::ProjectMenuPointer(point,*configuration,[](const Common::Matrix44& transform) {
            return WiimoteEmu::CameraLogic::GetCameraPoints(transform,
              {WiimoteEmu::CameraLogic::CAMERA_FOV_X,WiimoteEmu::CameraLogic::CAMERA_FOV_Y});
          });
        });
      if(!result) return std::nullopt;
      return std::pair{result->x,result->y};
    });
    NSLog(@"[GalaxyPad pointer experiment] calibrated touch enabled; file menu only, no automatic buttons");
  }
#endif
  _busy = YES;
  _paused = NO;
  NSError *audioError = nil;
  [AVAudioSession.sharedInstance setCategory:AVAudioSessionCategoryPlayback error:&audioError];
  if (audioError) NSLog(@"[GalaxyPad] audio category failed: %@", audioError);
  __weak GalaxyPadCoreHost *weakSelf = self;
  _lifecycleTimer = [NSTimer scheduledTimerWithTimeInterval:0.25 repeats:YES
    block:^(NSTimer *) { [weakSelf reconcileLifecycle]; }];
  [self reconcileLifecycle];
  dispatch_async(_worker, ^{
    @autoreleasepool {
#if TARGET_OS_SIMULATOR
      NSLog(@"[GalaxyPad scheduling] worker requestedQoS=%u",
        (unsigned)qos_class_self());
#endif
      moderngekko::RuntimeConfig config;
      config.game_root = root.fileSystemRepresentation;
      config.disc_image = disc.fileSystemRepresentation;
      config.user_directory = user.fileSystemRepresentation;
      config.module = moderngekko::ModuleSource::DynamicPath(module.fileSystemRepresentation);
      config.graphics.backend = "Metal";
      config.graphics.internal_resolution_scale = renderScale;
      config.graphics.aspect_ratio_mode = aspectRatioMode;
      config.render_surface = (__bridge void *)layer;
      config.show_fps_in_title = false;
      config.allow_interpreter = false;
      config.log_callback = RuntimeLog;
#if TARGET_OS_SIMULATOR
      if (!nativePointerProbe && [[NSUserDefaults standardUserDefaults] boolForKey:@"GalaxyPadDevPointerHooks"]) {
        NSData *dol=[NSData dataWithContentsOfFile:[root stringByAppendingPathComponent:@"sys/main.dol"]];
        unsigned char digest[CC_SHA256_DIGEST_LENGTH];
        NSMutableString *hash=[NSMutableString string];
        if (dol.length==6283264) {
          CC_SHA256(dol.bytes,(CC_LONG)dol.length,digest);
          for (unsigned char byte:digest) [hash appendFormat:@"%02x",byte];
        }
        if ([hash isEqualToString:@(GalaxyPadDOLSHA256)]) {
          config.builtin_mods={galaxypad::PointerHookDescriptor()};
          NSLog(@"[GalaxyPad pointer hook] exact DOL verified; built-in observer requested");
        } else {
          NSLog(@"[GalaxyPad pointer hook] disabled: DOL mismatch");
        }
      }
#endif
#if GALAXYPAD_ENABLE_NATIVE_THP
      if ([[NSUserDefaults standardUserDefaults] boolForKey:@"GalaxyPadDevNativeTHP"]) {
        NSData *dol=[NSData dataWithContentsOfFile:[root stringByAppendingPathComponent:@"sys/main.dol"]];
        unsigned char digest[CC_SHA256_DIGEST_LENGTH];
        NSMutableString *hash=[NSMutableString string];
        if (dol.length==6283264) {
          CC_SHA256(dol.bytes,(CC_LONG)dol.length,digest);
          for (unsigned char byte:digest) [hash appendFormat:@"%02x",byte];
        }
        if ([hash isEqualToString:@(GalaxyPadDOLSHA256)]) {
          config.builtin_mods.push_back(GalaxyPadTHPModDescriptor());
          NSLog(@"[GalaxyPad native THP] exact DOL verified; private candidate requested");
        } else NSLog(@"[GalaxyPad native THP] disabled: DOL mismatch");
      }
#else
      if ([[NSUserDefaults standardUserDefaults] boolForKey:@"GalaxyPadDevNativeTHP"])
        NSLog(@"[GalaxyPad native THP] requested but unavailable: this app was built with GALAXYPAD_ENABLE_NATIVE_THP=OFF; using original decoder");
#endif
      NSString *failure = nil;
#if TARGET_OS_SIMULATOR
      // Declaration order keeps the module alive until registration is detached,
      // including Runtime::Create/Run failures and runtime destructor cleanup.
      Common::DynamicLibrary observerLibrary;
      galaxypad::NativeObserverBinding observerBinding;
#endif
      auto created = moderngekko::Runtime::Create(std::move(config));
      if (!created) {
        failure = created.error ? RuntimeFailureMessage(*created.error) : @"Runtime creation failed";
      } else {
        bool run;
        {
          std::lock_guard lock(session->mutex);
          session->runtime = created.runtime.get();
          run = !session->stopping;
        }
        if (run) {
          // Config exists after Create; set gain before Run creates the stream.
          Config::SetBaseOrCurrent(Config::MAIN_AUDIO_VOLUME, initialVolume);
          Config::SetBaseOrCurrent(Config::MAIN_AUDIO_MUTED, initialMute);
          // Keep CPU emulation and Metal rendering on separate threads. Set this
          // before Run initializes the core; never change it during gameplay.
          Config::SetCurrent(Config::MAIN_CPU_THREAD, true);
          // Pull Stars use GXPeekZ to validate pointer depth. Disabling EFB
          // access returns zero and makes visible 3D targets unselectable.
          Config::SetCurrent(Config::GFX_HACK_EFB_ACCESS_ENABLE, true);
#if TARGET_OS_SIMULATOR
          if (nativePointerProbe) {
            NSData *dol=[NSData dataWithContentsOfFile:[root stringByAppendingPathComponent:@"sys/main.dol"]];
            unsigned char digest[CC_SHA256_DIGEST_LENGTH];
            NSMutableString *hash=[NSMutableString string];
            if (dol.length==6283264) {
              CC_SHA256(dol.bytes,(CC_LONG)dol.length,digest);
              for (unsigned char byte:digest) [hash appendFormat:@"%02x",byte];
            }
            GalaxyPadGetNativeObserver getObserver=nullptr;
            bool attached=false;
            if ([hash isEqualToString:@(GalaxyPadDOLSHA256)] &&
                observerLibrary.Open(module.fileSystemRepresentation) &&
                observerLibrary.GetSymbol(GALAXYPAD_NATIVE_OBSERVER_SYMBOL,&getObserver)) {
              galaxypad::pointerHookProbe={};
              attached=observerBinding.bind(getObserver(),MODERNGEKKO_CPU_ABI_VERSION,
                sizeof(CPUState),GalaxyPadDOLSHA256,
                [](const CPUState* state,uint32_t site,void*) {
                  if (!Core::IsCPUThread()) return;
                  galaxypad::NativePointerQueryObservation(state,site);
                },nullptr);
            }
            NSLog(@"[GalaxyPad native observer] attached=%d; observational only",attached);
          }
          Common::EventHook pointerHook;
          if (pointerProbe) {
            NSData *dol=[NSData dataWithContentsOfFile:[root stringByAppendingPathComponent:@"sys/main.dol"]];
            unsigned char digest[CC_SHA256_DIGEST_LENGTH];
            NSMutableString *hash=[NSMutableString string];
            if (dol.length==6283264) {
              CC_SHA256(dol.bytes,(CC_LONG)dol.length,digest);
              for (unsigned char byte:digest) [hash appendFormat:@"%02x",byte];
            }
            if ([hash isEqualToString:@(GalaxyPadDOLSHA256)]) {
              NSLog(@"[GalaxyPad pointer context] enabled; exact DOL verified; every sixth VI field");
              pointerHook=GetVideoEvents().vi_end_field_event.Register(
                [session,pitch22Profile,fields=0u, lastObject=UINT32_MAX, lastMode=UINT32_MAX,
                 lastSelector=UINT32_MAX,lastItem=UINT32_MAX,lastFlags=UINT32_MAX,
                 lastNerve=UINT32_MAX,lastPending=UINT32_MAX]() mutable {
                  if (++fields%6 || !Core::IsCPUThread()) return;
                  auto& system=Core::System::GetInstance();
                  auto& memory=system.GetMemory();
                  auto read=[&](uint32_t address)->std::optional<uint32_t> {
                    const bool mem2=address>=0x90000000u;
                    const uint32_t base=mem2?0x90000000u:0x80000000u;
                    const uint32_t size=mem2?memory.GetExRamSizeReal():memory.GetRamSizeReal();
                    const auto* bytes=mem2?memory.GetEXRAM():memory.GetRAM();
                    if (!bytes || address<base || uint64_t(address-base)+4>size) return std::nullopt;
                    bytes+=address-base;
                    return (uint32_t(bytes[0])<<24)|(uint32_t(bytes[1])<<16)|
                           (uint32_t(bytes[2])<<8)|uint32_t(bytes[3]);
                  };
                  auto context=galaxypad::ReadPointerContext(system.GetPowerPC().GetPPCState().gpr[13],read);
                  uint32_t object=context?context->controller:0;
                  uint32_t mode=context?context->mode:UINT32_MAX;
                  auto target=context?galaxypad::ReadFilePointerTarget(*context,read):
                    std::optional<galaxypad::FilePointerTarget>{};
                  uint32_t selector=target?target->selector:0, item=target?target->item:0;
                  uint32_t flags=target?(uint32_t(target->pointing)|(uint32_t(target->invalid)<<1)):UINT32_MAX;
                  auto actor=target?galaxypad::ReadActorPointerState(target->selector,read):
                    std::optional<galaxypad::ActorPointerState>{};
                  uint32_t nerve=actor?actor->current:0, pending=actor?actor->pending:0;
                  auto configuration=galaxypad::MenuPointerReadiness(pitch22Profile,context,actor,
                    galaxypad::ReadPointerCalibration(read),galaxypad::ReadPointerConversionInputs(read));
                  {
                    std::lock_guard lock(session->pointerConfigurationMutex);
                    session->pointerConfiguration=configuration;
                    session->pointerConfigurationTime=std::chrono::steady_clock::now();
                  }
                  if (object==lastObject && mode==lastMode && selector==lastSelector &&
                      item==lastItem && flags==lastFlags && nerve==lastNerve &&
                      pending==lastPending) return;
                  lastObject=object; lastMode=mode;
                  lastSelector=selector; lastItem=item; lastFlags=flags;
                  lastNerve=nerve; lastPending=pending;
                  NSLog(@"[GalaxyPad pointer context] field=%u object=%08x mode=%d selector=%08x item=%08x flags=%d nerve=%08x pending=%08x",
                    fields,object,(int32_t)mode,selector,item,(int32_t)flags,nerve,pending);
                });
            } else {
              NSLog(@"[GalaxyPad pointer context] disabled: exact DOL identity mismatch");
            }
          }
#endif
#if TARGET_OS_SIMULATOR
          // Queue QoS did not reach this thread in R641. Apply the default-off
          // request here once, never changing guest clocks or time accounting.
          auto schedulingHook = GetVideoEvents().vi_end_field_event.Register(
            [cpuQoSExperiment, observed=false]() mutable {
              if (!Core::IsCPUThread() || observed) return;
              observed = true;
              const unsigned before = (unsigned)qos_class_self();
              const int result = cpuQoSExperiment ?
                pthread_set_qos_class_self_np(QOS_CLASS_USER_INITIATED, 0) : -1;
              NSLog(@"[GalaxyPad scheduling] CPU experiment=%d requestedBefore=%u requestedAfter=%u setResult=%d",
                cpuQoSExperiment, before, (unsigned)qos_class_self(), result);
            });
#endif
          // Read presenter geometry on its rendering thread, not from UIKit.
          // A separate lock avoids coupling a paused CPU to frame delivery.
          auto viewportHook = GetVideoEvents().after_present_event.Register([session](PresentInfo&) {
            if (!g_presenter) return;
            const auto rect = g_presenter->GetTargetRectangle();
            const double width = g_presenter->GetBackbufferWidth();
            const double height = g_presenter->GetBackbufferHeight();
            if (width <= 0 || height <= 0) return;
            std::lock_guard lock(session->viewportMutex);
            session->viewport = CGRectMake(rect.left/width, rect.top/height,
              rect.GetWidth()/width, rect.GetHeight()/height);
          });
          auto result = created.runtime->Run();
          if (result.error) failure = RuntimeFailureMessage(*result.error);
        }
        {
          std::lock_guard lock(session->mutex);
          session->runtime = nullptr;
        }
      }
      // Teardown happens on the worker, never by joining on the UIKit thread.
      created.runtime.reset();
#if TARGET_OS_SIMULATOR
      observerBinding.reset(); // CPU stopped even on runtime failure; library still held
#endif
      dispatch_async(dispatch_get_main_queue(), ^{
        GalaxyPadCoreHost *host = weakSelf;
        if (!host) return;
        [host->_lifecycleTimer invalidate];
        host->_lifecycleTimer = nil;
        host->_busy = NO;
        host->_paused = NO;
        [host clearInput];
        [host deactivateAudio];
        if (host.onExit) host.onExit(failure);
      });
    }
  });
  return YES;
}
- (void)setApplicationActive:(BOOL)active {
  NSAssert(NSThread.isMainThread, @"Host API requires main thread");
  _active = active;
  GalaxyPadLog(@"host lifecycle active=%d interrupted=%d ui_blocked=%d pause_requested=%d",
    active, _interrupted, _nativeUIBlocked, _pauseRequested);
  if (!active) [self clearInput];
  if (active) _interrupted = NO; // setActive remains the recovery authority
  [self reconcileLifecycle];
}
- (void)setNativeUIBlocked:(BOOL)blocked pauseRuntime:(BOOL)pauseRuntime {
  NSAssert(NSThread.isMainThread, @"Host API requires main thread");
  _nativeUIBlocked = blocked;
  _pauseRequested = pauseRuntime;
  GalaxyPadLog(@"host lifecycle ui_blocked=%d pause_requested=%d active=%d interrupted=%d",
    blocked, pauseRuntime, _active, _interrupted);
  [self clearInput];
  [self reconcileLifecycle];
}
- (void)deactivateAudio {
  if (!_audioActive) return;
  NSError *error = nil;
  [AVAudioSession.sharedInstance setActive:NO
    withOptions:AVAudioSessionSetActiveOptionNotifyOthersOnDeactivation error:&error];
  if (!error) _audioActive = NO;
}
- (void)reconcileLifecycle {
  if (!_busy) return;
  const bool pause = !_active || _pauseRequested || _interrupted;
  if (pause) [self deactivateAudio];
  else if (!_audioActive) {
    NSError *error = nil;
    [AVAudioSession.sharedInstance setActive:YES error:&error];
    if (error) return; // remain paused and retry, without log flooding
    _audioActive = YES;
  }
  std::lock_guard lock(_session->mutex);
  if (!_session->runtime || _session->stopping) return;
  auto state = Core::GetState(Core::System::GetInstance());
  const int volume = (int)GalaxyPadSettings.sharedSettings.mainVolume;
  const bool muted = GalaxyPadSettings.sharedSettings.mainAudioMuted;
  if ((state == Core::State::Running || state == Core::State::Paused) &&
      (volume != _session->queuedVolume || muted != _session->queuedMute)) {
    _session->queuedVolume = volume;
    _session->queuedMute = muted;
    auto session = _session;
    // Stream ownership stays on the runtime host, never UIKit. Stale jobs from
    // a stopped session must not change a replacement session's global config.
    Core::QueueHostJob([session, volume, muted](Core::System& system) {
      std::lock_guard lock(session->mutex);
      if (!session->runtime || session->stopping) return;
      const auto current = Core::GetState(system);
      if (current != Core::State::Running && current != Core::State::Paused) {
        session->queuedVolume = -1; // allow a later lifecycle tick to retry
        return;
      }
      Config::SetBaseOrCurrent(Config::MAIN_AUDIO_VOLUME, volume);
      Config::SetBaseOrCurrent(Config::MAIN_AUDIO_MUTED, muted);
      AudioCommon::UpdateSoundStream(system);
    });
  }
  if ((state == Core::State::Running || state == Core::State::Paused) &&
      !_session->inputRegistrationQueued) {
    _session->inputRegistrationQueued = true;
    auto session = _session;
    // Core::Init drains pre-start jobs while Uninitialized, so enqueue only
    // after controller initialization. Shutdown removes devices normally.
    Core::QueueHostJob([session](Core::System&) {
      std::lock_guard lock(session->mutex);
      if (session->stopping) return;
      g_controller_interface.PlatformPopulateDevices([session] {
        bool added = g_controller_interface.AddDevice(session->device);
        NSLog(@"[GalaxyPad] mobile input device registered=%d", added);
      });
    });
  }
  // Runtime::Pause can return success before the core is actually pausable.
  // Retry while starting; never infer paused from that return value alone.
  if (pause && state == Core::State::Running) _session->runtime->Pause();
  else if (!pause && state == Core::State::Paused) _session->runtime->Resume();
  const BOOL wasPaused = _paused;
  _paused = Core::GetState(Core::System::GetInstance()) == Core::State::Paused;
  if (wasPaused != _paused)
    GalaxyPadLog(@"host lifecycle runtime_paused=%d active=%d ui_blocked=%d pause_requested=%d interrupted=%d",
      _paused, _active, _nativeUIBlocked, _pauseRequested, _interrupted);
}
- (void)audioInterruption:(NSNotification *)notification {
  BOOL began = [notification.userInfo[AVAudioSessionInterruptionTypeKey] unsignedIntegerValue]
      == AVAudioSessionInterruptionTypeBegan;
  dispatch_async(dispatch_get_main_queue(), ^{
    GalaxyPadLog(@"audio interruption began=%d", began);
    self->_interrupted = began;
    if (began) [self clearInput];
    if (began) self->_audioActive = NO;
    [self reconcileLifecycle];
  });
}
- (void)stop {
  NSAssert(NSThread.isMainThread, @"Host API requires main thread");
  if (!_session) return;
  [self clearInput];
  std::lock_guard lock(_session->mutex);
  _session->stopping = true;
  if (_session->runtime) {
    // RequestStop first delivers the emulated power button when IOS has an
    // STM hook. A menu-paused CPU cannot service that graceful shutdown.
    // Keep host input rejected/audio deactivated, but let the guest finish.
    auto input = _session->runtime->GetDiagnosticsSnapshot();
    NSLog(@"[GalaxyPad input] samples=%llu buttonSamples=%llu transitions=%llu last=%u pointerSamples=%llu",
      input.input_samples, input.input_button_samples, input.input_button_transitions,
      input.input_last_buttons, input.input_ir_visible_samples);
    RequestSessionStop(_session);
  }
}
- (void)dealloc {
  [NSNotificationCenter.defaultCenter removeObserver:self];
  [_lifecycleTimer invalidate];
  if (_session) {
    std::lock_guard lock(_session->mutex);
    _session->stopping = true;
    _session->mixer->clearAll();
    _session->device->UpdateInput();
    if (_session->runtime) {
      // Same graceful STM shutdown contract as an explicit Stop from the menu.
      RequestSessionStop(_session);
    }
  }
}
@end
