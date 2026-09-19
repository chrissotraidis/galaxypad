// SPDX-License-Identifier: GPL-3.0-or-later
#import <Foundation/Foundation.h>
#include "../shared/GalaxyPadInput.h"
@class GCController;
// Main-thread owner of the SunPad-derived controller reconciliation adapter.
@interface GalaxyPadControllers : NSObject
@property(nonatomic, copy) void (^inputChanged)(galaxypad::InputState state);
// View/Options toggles app pause; Menu sends original Wii Plus through inputChanged.
@property(nonatomic, copy) void (^pauseRequested)(void);
@property(nonatomic, copy) void (^ownershipChanged)(void);
@property(nonatomic, copy) BOOL (^inputAllowed)(void);
@property(nonatomic, copy) BOOL (^pauseToggleAllowed)(void);
@property(nonatomic, copy) void (^aimChanged)(float x, float y, BOOL recenter);
@property(nonatomic, readonly) GCController *motionController;
// Read-only diagnostics; does not consume events or reset controller state.
- (NSString *)diagnosticSnapshot;
- (void)start;
- (void)reset;
- (void)reconcile;
- (void)reloadMapping;
@end
