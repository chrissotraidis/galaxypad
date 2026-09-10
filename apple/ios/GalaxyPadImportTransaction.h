// SPDX-License-Identifier: GPL-3.0-or-later
#import <Foundation/Foundation.h>

// SunPad-style private sibling staging. All public calls are main-thread only.
// The app must retain one transaction and serialize imports through it.
@interface GalaxyPadImportTransaction : NSObject
@property(nonatomic, readonly) BOOL preparing;
@property(nonatomic, readonly) BOOL verified;
@property(nonatomic, readonly) BOOL previousDataRetained;
// root must be the app-owned Application Support/GalaxyPad directory.
- (instancetype)initWithRoot:(NSURL *)root;
- (void)prepareImage:(NSURL *)source
  progress:(void (^)(NSString *, double))progress
  completion:(void (^)(BOOL, NSString *))completion;
- (void)cancel;
// Discard only this transaction's unactivated stage after preparation finishes.
// Refuses active workers and activated/recovery data. Cleanup runs off main.
- (void)discardUnactivatedStage:(void (^)(BOOL, NSString *))completion;
// Call only after CoreHost has reported completion, not immediately after stop.
- (BOOL)activateWithRuntimeStopped:(BOOL)stopped error:(NSString **)error;
@end
