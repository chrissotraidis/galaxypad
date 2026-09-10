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
- (void)setMenuPresented:(BOOL)presented;
- (void)stop;
@end
NS_ASSUME_NONNULL_END
