// SPDX-License-Identifier: GPL-3.0-or-later
#import <Foundation/Foundation.h>
#include "../shared/GalaxyPadInput.h"
// Main-thread owner of the SunPad-derived controller reconciliation adapter.
@interface GalaxyPadControllers : NSObject
@property(nonatomic, copy) void (^inputChanged)(galaxypad::InputState state);
@property(nonatomic, copy) void (^pauseRequested)(void);
@property(nonatomic, copy) void (^ownershipChanged)(void);
@property(nonatomic, copy) BOOL (^inputAllowed)(void);
- (void)start;
- (void)reset;
- (void)reconcile;
- (void)reloadMapping;
@end
