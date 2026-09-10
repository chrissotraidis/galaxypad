// SPDX-License-Identifier: GPL-3.0-or-later
#import <UIKit/UIKit.h>
#include "../shared/GalaxyPadInput.h"
@interface GalaxyPadTouchOverlay : UIView
@property(nonatomic, copy) void (^inputChanged)(galaxypad::InputState state);
@property(nonatomic, copy) CGRect (^viewportProvider)(void);
@property(nonatomic) BOOL editingLayout;
@property(nonatomic) BOOL tiltMode;
@property(nonatomic) CGFloat tiltSensitivity;
@property(nonatomic) BOOL tiltInvertY;
- (void)resetLayout;
- (void)reset;
@end
