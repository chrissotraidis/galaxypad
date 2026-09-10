// SPDX-License-Identifier: GPL-3.0-or-later
// Adapted from SunPad fcdc1411 MetalSurfaceView and drawable layout policy.
#import "GalaxyPadMetalView.h"
#import <Metal/Metal.h>
@implementation GalaxyPadMetalView
+ (Class)layerClass { return CAMetalLayer.class; }
- (CAMetalLayer *)metalLayer { return (CAMetalLayer *)self.layer; }
- (instancetype)initWithFrame:(CGRect)frame {
  if ((self = [super initWithFrame:frame])) {
    self.backgroundColor = UIColor.blackColor;
    self.metalLayer.device = MTLCreateSystemDefaultDevice();
    self.metalLayer.pixelFormat = MTLPixelFormatBGRA8Unorm;
    self.metalLayer.framebufferOnly = YES;
  }
  return self;
}
- (void)layoutSubviews {
  [super layoutSubviews];
  // Match reference's one drawable pixel per point, not Retina supersampling.
  // Internal EFB scale is separately controlled by the runtime.
  CGSize size = CGSizeMake(MAX(1, floor(self.bounds.size.width)),
                           MAX(1, floor(self.bounds.size.height)));
  if (!CGSizeEqualToSize(self.metalLayer.drawableSize, size)) {
    [CATransaction begin];
    [CATransaction setDisableActions:YES];
    self.metalLayer.drawableSize = size;
    [CATransaction commit];
  }
}
@end
