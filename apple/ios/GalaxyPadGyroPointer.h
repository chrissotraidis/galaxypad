// SPDX-License-Identifier: GPL-3.0-or-later
#import <UIKit/UIKit.h>
#import <GameController/GameController.h>
#include "../shared/GalaxyPadInput.h"

// Main-thread motion owner. Sends only pointer state; never synthesizes buttons.
@interface GalaxyPadGyroPointer : NSObject
@property(nonatomic,copy) BOOL (^inputAllowed)(void);
@property(nonatomic,copy) UIInterfaceOrientation (^orientation)(void);
@property(nonatomic,copy) GCController *(^controller)(void);
@property(nonatomic,copy) void (^inputChanged)(galaxypad::InputState state);
@property(nonatomic,copy) void (^statusChanged)(NSString *status);
- (void)start;
- (void)reset;
- (void)recenter;
- (void)setStickX:(float)x y:(float)y recenter:(BOOL)recenter;
- (void)acceptTouch:(galaxypad::InputState)state;
@end
