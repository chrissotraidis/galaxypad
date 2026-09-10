// SPDX-License-Identifier: GPL-3.0-or-later
#import <UIKit/UIKit.h>
#import <QuartzCore/CAMetalLayer.h>
@interface GalaxyPadMetalView : UIView
@property(nonatomic, readonly) CAMetalLayer *metalLayer;
@end
