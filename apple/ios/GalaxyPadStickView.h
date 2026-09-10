// SPDX-License-Identifier: GPL-3.0-or-later
#import <UIKit/UIKit.h>
@interface GalaxyPadStickView : UIView
@property(nonatomic, copy) void (^valueChanged)(float x, float y);
- (void)reset;
@end
