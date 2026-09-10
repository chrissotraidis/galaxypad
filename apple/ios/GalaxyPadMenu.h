// SPDX-License-Identifier: GPL-3.0-or-later
#import <UIKit/UIKit.h>

// Galaxy-owned native settings. Hierarchy follows SunPad's Controls grouping;
// unsupported product actions are added only with their implementations.
@interface GalaxyPadMenu : UITableViewController
@property(nonatomic) BOOL touchControls;
@property(nonatomic) CGFloat controlOpacity;
@property(nonatomic) BOOL tiltMode;
@property(nonatomic) CGFloat tiltSensitivity;
@property(nonatomic) BOOL tiltInvertY;
@property(nonatomic, copy) void (^onTiltSettings)(BOOL, CGFloat, BOOL);
@property(nonatomic, copy) void (^onRecenter)(void);
@property(nonatomic, copy) void (^onTouchControls)(BOOL);
@property(nonatomic, copy) void (^onOpacity)(CGFloat);
@property(nonatomic, copy) void (^onClose)(void);
@property(nonatomic, copy) void (^onStop)(void);
@property(nonatomic, copy) void (^onEditLayout)(void);
@property(nonatomic, copy) void (^onResetLayout)(void);
@end
