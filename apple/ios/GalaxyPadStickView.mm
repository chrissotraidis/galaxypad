// SPDX-License-Identifier: GPL-3.0-or-later
// Adapted from SunPad fcdc1411 SunPadStickView: radial clamp and positive-up Y.
// Adds explicit contact ownership across interruption/reset.
#import "GalaxyPadStickView.h"
#include <cmath>
@implementation GalaxyPadStickView {
  UIView *_thumb;
  UITouch *_contact;
  float _x, _y;
}
- (instancetype)initWithFrame:(CGRect)frame {
  if ((self = [super initWithFrame:frame])) {
    self.multipleTouchEnabled = NO;
    self.backgroundColor = [UIColor colorWithWhite:1 alpha:0.12];
    self.layer.borderColor = [UIColor colorWithWhite:1 alpha:0.34].CGColor;
    self.layer.borderWidth = 2;
    self.isAccessibilityElement = YES;
    self.accessibilityLabel = @"Movement stick";
    _thumb = [[UIView alloc] init];
    _thumb.userInteractionEnabled = NO;
    _thumb.backgroundColor = [UIColor colorWithWhite:1 alpha:0.32];
    [self addSubview:_thumb];
  }
  return self;
}
- (void)layoutSubviews {
  [super layoutSubviews];
  CGFloat side = MIN(self.bounds.size.width, self.bounds.size.height);
  self.layer.cornerRadius = side/2;
  _thumb.bounds = CGRectMake(0, 0, side*0.42, side*0.42);
  _thumb.layer.cornerRadius = side*0.21;
  [self updateThumb];
}
- (void)updateThumb {
  CGFloat travel = MAX(0, MIN(self.bounds.size.width, self.bounds.size.height)*0.29-4);
  _thumb.center = CGPointMake(CGRectGetMidX(self.bounds)+_x*travel,
                             CGRectGetMidY(self.bounds)-_y*travel);
}
- (void)reset {
  _contact = nil;
  _x = _y = 0;
  [self updateThumb];
  if (self.valueChanged) self.valueChanged(0, 0);
}
- (void)updateContact {
  if (!_contact) return;
  CGPoint p = [_contact locationInView:self];
  CGFloat radius = MAX(1, MIN(self.bounds.size.width, self.bounds.size.height)/2);
  float x = (p.x-CGRectGetMidX(self.bounds))/radius;
  float y = (CGRectGetMidY(self.bounds)-p.y)/radius;
  float length = std::hypot(x, y);
  if (length > 1) { x /= length; y /= length; }
  _x = x; _y = y;
  [self updateThumb];
  if (self.valueChanged) self.valueChanged(x, y);
}
- (void)touchesBegan:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
  (void)event;
  if (!_contact) { _contact = touches.anyObject; [self updateContact]; }
}
- (void)touchesMoved:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
  (void)event;
  if (_contact && [touches containsObject:_contact]) [self updateContact];
}
- (void)touchesEnded:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
  (void)event;
  if (_contact && [touches containsObject:_contact]) [self reset];
}
- (void)touchesCancelled:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
  [self touchesEnded:touches withEvent:event];
}
@end
