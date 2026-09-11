// SPDX-License-Identifier: GPL-3.0-or-later
#import <Foundation/Foundation.h>
#import <QuartzCore/CAMetalLayer.h>
#include "../shared/GalaxyPadInput.h"
#include "../shared/GalaxyPadAudioOutputCounters.h"

NS_ASSUME_NONNULL_BEGIN
struct GalaxyPadCadenceEstimate {
  double viRate;
  double speed;
};
struct GalaxyPadRuntimeCounters {
  uint64_t frameMaxGapNs;
  uint64_t frameGapsGe33ms;
  uint64_t frameGapsGe100ms;
  uint64_t efbColorPeeks;
  uint64_t efbDepthPeeks;
  uint64_t efbPeekNs;
  uint64_t efbMaxPeekNs;
  uint64_t efbFramesWithPeeks;
  uint64_t efbMaxPeeksPerFrame;
};
struct GalaxyPadAudioCounters {
  bool valid;
  uint64_t enqueues;
  uint64_t underruns;
  uint64_t backlogDrops;
  uint64_t fullDrops;
  galaxypad::audio::OutputSnapshot output;
};
// Main-thread API. busy stays true until runtime destruction completes; callers
// must not start a replacement host while the previous host is busy.
@interface GalaxyPadCoreHost : NSObject
@property(nonatomic, readonly) BOOL busy;
@property(nonatomic, readonly) BOOL paused;
@property(nonatomic, readonly) uint64_t renderedFrames;
- (GalaxyPadCadenceEstimate)cadenceEstimate;
- (GalaxyPadRuntimeCounters)runtimeCounters;
- (GalaxyPadAudioCounters)audioCounters;
- (void)requestDevelopmentCheckpoint;
- (void)restoreDevelopmentCheckpoint;
@property(nonatomic, readonly) CGRect normalizedViewport;
@property(nonatomic, copy, nullable) void (^onExit)(NSString * _Nullable error);
@property(nonatomic, copy, nullable) void (^onInputReset)(void);
- (void)publishInput:(galaxypad::InputState)input source:(galaxypad::InputSource)source;
- (void)clearInput;
- (instancetype)initWithLayer:(CAMetalLayer *)layer;
- (BOOL)startWithGameRoot:(NSString *)root discImage:(NSString *)disc
                  module:(NSString *)module userDirectory:(NSString *)user;
- (void)setApplicationActive:(BOOL)active;
- (void)setNativeUIBlocked:(BOOL)blocked pauseRuntime:(BOOL)pauseRuntime;
- (void)stop;
@end
NS_ASSUME_NONNULL_END
