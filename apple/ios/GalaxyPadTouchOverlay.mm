// SPDX-License-Identifier: GPL-3.0-or-later
// SunPad-derived stick/button overlay; Galaxy actions, no GC trigger carryover.
#import "GalaxyPadTouchOverlay.h"
#import "GalaxyPadStickView.h"
#include "../shared/GalaxyPadControlSize.h"
#include "../shared/GalaxyPadStickRouting.h"
@implementation GalaxyPadTouchOverlay {
  GalaxyPadStickView *_stick;
  UILabel *_stickModeLabel;
  NSMutableArray<UIButton *> *_buttons;
  galaxypad::InputState _input;
  BOOL _resetting;
  UITouch *_pointerContact;
  NSMutableDictionary<NSString *, NSString *> *_positions;
  NSMutableArray<UIGestureRecognizer *> *_editGestures;
  NSMutableDictionary<NSString *, NSNumber *> *_sizes;
}
- (instancetype)initWithFrame:(CGRect)frame {
  if ((self = [super initWithFrame:frame])) {
    self.multipleTouchEnabled = YES;
    _buttons = [NSMutableArray array];
    _positions = [[NSUserDefaults.standardUserDefaults dictionaryForKey:@"GalaxyPadControlPositions"] mutableCopy]
      ?: [NSMutableDictionary dictionary];
    _editGestures = [NSMutableArray array];
    _sizes = [[NSUserDefaults.standardUserDefaults dictionaryForKey:@"GalaxyPadControlSizes"] mutableCopy]
      ?: [NSMutableDictionary dictionary];
    _stick = [[GalaxyPadStickView alloc] init];
    _stick.accessibilityIdentifier = @"galaxypad.control.move";
    _tiltSensitivity = 1;
    _stickModeLabel = [[UILabel alloc] init];
    _stickModeLabel.text = @"Move";
    _stickModeLabel.font = [UIFont systemFontOfSize:12 weight:UIFontWeightSemibold];
    _stickModeLabel.textAlignment = NSTextAlignmentCenter;
    _stickModeLabel.textColor = UIColor.whiteColor;
    _stickModeLabel.userInteractionEnabled = NO;
    [_stick addSubview:_stickModeLabel];
    [self addSubview:_stick];
    [self addEditorGesture:_stick];
    __weak GalaxyPadTouchOverlay *weakSelf = self;
    _stick.valueChanged = ^(float x, float y) {
      GalaxyPadTouchOverlay *view = weakSelf;
      if (!view || view.editingLayout) return;
      galaxypad::routeStick(view->_input, x, y, view.tiltMode, view.tiltSensitivity, view.tiltInvertY);
      [view publish];
    };
    NSArray *names = @[@"A", @"B", @"Spin", @"Z", @"C", @"+", @"−"];
    const uint32_t bits[] = {galaxypad::A, galaxypad::B, galaxypad::Spin,
      galaxypad::Z, galaxypad::C, galaxypad::Plus, galaxypad::Minus};
    for (NSUInteger i = 0; i < names.count; ++i) {
      UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
      button.tag = bits[i];
      [button setTitle:names[i] forState:UIControlStateNormal];
      button.accessibilityLabel = names[i];
      button.accessibilityIdentifier = [@"galaxypad.control." stringByAppendingString:names[i]];
      button.backgroundColor = [UIColor colorWithWhite:0.08 alpha:0.65];
      button.layer.borderColor = [UIColor colorWithWhite:1 alpha:0.4].CGColor;
      button.layer.borderWidth = 1;
      [button addTarget:self action:@selector(down:) forControlEvents:UIControlEventTouchDown];
      [button addTarget:self action:@selector(up:) forControlEvents:
        UIControlEventTouchUpInside | UIControlEventTouchUpOutside | UIControlEventTouchCancel];
      [self addSubview:button]; [_buttons addObject:button];
      [self addEditorGesture:button];
    }
  }
  return self;
}
- (void)setTiltMode:(BOOL)tiltMode {
  [self reset];
  _tiltMode = tiltMode;
  _stick.accessibilityLabel = tiltMode ? @"Tilt stick" : @"Movement stick";
  _stickModeLabel.text = tiltMode ? @"Tilt" : @"Move";
}
- (void)setTiltSensitivity:(CGFloat)sensitivity {
  [self reset];
  _tiltSensitivity = std::isfinite(sensitivity) ? MAX(0.25, MIN(2, sensitivity)) : 1;
}
- (void)setTiltInvertY:(BOOL)invertY { [self reset]; _tiltInvertY = invertY; }
- (UIView *)hitTest:(CGPoint)point withEvent:(UIEvent *)event {
  UIView *hit = [super hitTest:point withEvent:event];
  if (hit != self) return hit;
  return CGRectContainsPoint([self gameplayViewport], point) ? self : nil;
}
- (void)addEditorGesture:(UIView *)control {
  UIPanGestureRecognizer *pan = [[UIPanGestureRecognizer alloc] initWithTarget:self action:@selector(moveControl:)];
  pan.enabled = NO;
  pan.maximumNumberOfTouches = 1;
  [control addGestureRecognizer:pan];
  [_editGestures addObject:pan];
  UIPinchGestureRecognizer *pinch = [[UIPinchGestureRecognizer alloc] initWithTarget:self action:@selector(resizeControl:)];
  pinch.enabled = NO;
  [control addGestureRecognizer:pinch];
  [_editGestures addObject:pinch];
}
- (CGFloat)sizeScaleForControl:(UIView *)control {
  id value = _sizes[control.accessibilityIdentifier];
  return galaxypad::controlScale([value isKindOfClass:NSNumber.class] ? [value doubleValue] : 1);
}
- (void)resizeControl:(UIPinchGestureRecognizer *)pinch {
  if (!self.editingLayout) return;
  [self resizeControl:pinch.view scale:[self sizeScaleForControl:pinch.view]*pinch.scale];
  pinch.scale = 1;
}
- (void)resizeControl:(UIView *)control scale:(CGFloat)scale {
  if (!self.editingLayout) return;
  [self rememberControl:control]; // preserve center when default size changes
  _sizes[control.accessibilityIdentifier] = @(galaxypad::controlScale(scale));
  [self persistPositions];
  [NSUserDefaults.standardUserDefaults setObject:_sizes forKey:@"GalaxyPadControlSizes"];
  [self setNeedsLayout];
  [self layoutIfNeeded];
}
- (CGRect)layoutArea {
  CGRect safe = UIEdgeInsetsInsetRect(self.bounds, self.safeAreaInsets);
  // Reserve the native menu/Done row, including after resizing.
  return CGRectMake(safe.origin.x+8, safe.origin.y+60,
    MAX(0, safe.size.width-16), MAX(0, safe.size.height-68));
}
- (CGPoint)clampCenter:(CGPoint)point forControl:(UIView *)control {
  CGRect safe = [self layoutArea];
  CGFloat halfW = MIN(control.bounds.size.width/2, safe.size.width/2);
  CGFloat halfH = MIN(control.bounds.size.height/2, safe.size.height/2);
  return CGPointMake(MAX(CGRectGetMinX(safe)+halfW, MIN(CGRectGetMaxX(safe)-halfW, point.x)),
    MAX(CGRectGetMinY(safe)+halfH, MIN(CGRectGetMaxY(safe)-halfH, point.y)));
}
- (void)placeSavedControl:(UIView *)control {
  id saved = _positions[control.accessibilityIdentifier];
  if ([saved isKindOfClass:NSString.class]) {
    CGPoint normalized = CGPointFromString(saved);
    if (std::isfinite(normalized.x) && std::isfinite(normalized.y)) {
      CGRect safe = [self layoutArea];
      control.center = CGPointMake(safe.origin.x + normalized.x*safe.size.width,
        safe.origin.y + normalized.y*safe.size.height);
    }
  }
  control.center = [self clampCenter:control.center forControl:control];
}
- (void)moveControl:(UIPanGestureRecognizer *)pan {
  if (!self.editingLayout) return;
  if (pan.state == UIGestureRecognizerStateBegan)
    NSLog(@"[GalaxyPad editor] drag began control=%@", pan.view.accessibilityIdentifier);
  UIView *control = pan.view;
  CGPoint delta = [pan translationInView:self];
  control.center = [self clampCenter:CGPointMake(control.center.x+delta.x, control.center.y+delta.y)
    forControl:control];
  [pan setTranslation:CGPointZero inView:self];
  [self rememberControl:control];
  if (pan.state == UIGestureRecognizerStateEnded || pan.state == UIGestureRecognizerStateCancelled) {
    [self persistPositions];
    NSLog(@"[GalaxyPad editor] drag ended control=%@", control.accessibilityIdentifier);
  }
}
- (void)rememberControl:(UIView *)control {
  CGRect safe = [self layoutArea];
  if (safe.size.width <= 0 || safe.size.height <= 0) return;
  _positions[control.accessibilityIdentifier] = NSStringFromCGPoint(CGPointMake(
    (control.center.x-safe.origin.x)/safe.size.width, (control.center.y-safe.origin.y)/safe.size.height));
}
- (void)persistPositions {
  [NSUserDefaults.standardUserDefaults setObject:_positions forKey:@"GalaxyPadControlPositions"];
}
- (NSArray<UIAccessibilityCustomAction *> *)moveActionsForControl:(UIView *)control {
  NSMutableArray *actions = [NSMutableArray array];
  NSArray *names = @[@"Move Left", @"Move Right", @"Move Up", @"Move Down"];
  const CGPoint offsets[] = {{-24,0},{24,0},{0,-24},{0,24}};
  __weak GalaxyPadTouchOverlay *weakSelf = self;
  __weak UIView *weakControl = control;
  for (NSUInteger i = 0; i < names.count; ++i) {
    CGPoint offset = offsets[i];
    [actions addObject:[[UIAccessibilityCustomAction alloc] initWithName:names[i]
      actionHandler:^BOOL(UIAccessibilityCustomAction *) {
        GalaxyPadTouchOverlay *view = weakSelf;
        UIView *target = weakControl;
        if (!view || !target || !view.editingLayout) return NO;
        target.center = [view clampCenter:CGPointMake(target.center.x+offset.x, target.center.y+offset.y)
          forControl:target];
        [view rememberControl:target];
        [view persistPositions];
        return YES;
      }]];
  }
  for (NSNumber *factor in @[@0.9, @1.1]) {
    [actions addObject:[[UIAccessibilityCustomAction alloc]
      initWithName:factor.doubleValue < 1 ? @"Make Smaller" : @"Make Larger"
      actionHandler:^BOOL(UIAccessibilityCustomAction *) {
        GalaxyPadTouchOverlay *view = weakSelf;
        UIView *target = weakControl;
        if (!view || !target || !view.editingLayout) return NO;
        [view resizeControl:target scale:[view sizeScaleForControl:target]*factor.doubleValue];
        return YES;
      }]];
  }
  return actions;
}
- (void)setEditingLayout:(BOOL)editingLayout {
  [self reset];
  _editingLayout = editingLayout;
  for (UIGestureRecognizer *pan in _editGestures) {
    pan.enabled = editingLayout;
    pan.view.accessibilityCustomActions = editingLayout ? [self moveActionsForControl:pan.view] : nil;
    pan.view.accessibilityHint = editingLayout ? @"Drag to move, pinch to resize, or use the move and size actions." : nil;
    pan.view.layer.borderWidth = editingLayout ? 3 : (pan.view == _stick ? 0 : 1);
    pan.view.layer.borderColor = (editingLayout ? UIColor.systemYellowColor :
      [UIColor colorWithWhite:1 alpha:0.4]).CGColor;
  }
}
- (void)resetLayout {
  [_positions removeAllObjects];
  [_sizes removeAllObjects];
  [NSUserDefaults.standardUserDefaults removeObjectForKey:@"GalaxyPadControlPositions"];
  [NSUserDefaults.standardUserDefaults removeObjectForKey:@"GalaxyPadControlSizes"];
  [self setNeedsLayout];
}
- (CGRect)gameplayViewport {
  CGRect normalized = self.viewportProvider ? self.viewportProvider() : CGRectZero;
  return CGRectMake(normalized.origin.x*self.bounds.size.width,
    normalized.origin.y*self.bounds.size.height, normalized.size.width*self.bounds.size.width,
    normalized.size.height*self.bounds.size.height);
}
- (void)updatePointer {
  if (!_pointerContact) return;
  CGRect viewport = [self gameplayViewport];
  CGPoint point = [_pointerContact locationInView:self];
  _input.pointerVisible = !CGRectIsEmpty(viewport) && CGRectContainsPoint(viewport, point);
  if (_input.pointerVisible) {
    _input.pointerX = (point.x-viewport.origin.x)/viewport.size.width;
    _input.pointerY = (point.y-viewport.origin.y)/viewport.size.height;
  }
  [self publish];
}
- (void)touchesBegan:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
  (void)event;
  if (self.editingLayout) return;
  if (!_pointerContact) { _pointerContact = touches.anyObject; [self updatePointer]; }
}
- (void)touchesMoved:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
  (void)event;
  if (_pointerContact && [touches containsObject:_pointerContact]) [self updatePointer];
}
- (void)touchesEnded:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
  (void)event;
  if (_pointerContact && [touches containsObject:_pointerContact]) {
    [self updatePointer];
    _pointerContact = nil; // Classic Pointer retains aim for a separate A/B press.
  }
}
- (void)touchesCancelled:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
  (void)event;
  if (_pointerContact && [touches containsObject:_pointerContact]) {
    _pointerContact = nil; _input.pointerVisible = false; [self publish];
  }
}
- (void)publish {
  if (_resetting || self.editingLayout) return;
  _input.connected = true;
  if (self.inputChanged) self.inputChanged(_input);
}
- (void)down:(UIButton *)button { _input.buttons |= (uint32_t)button.tag; [self publish]; }
- (void)up:(UIButton *)button { _input.buttons &= ~(uint32_t)button.tag; [self publish]; }
- (void)reset {
  _resetting = YES;
  _pointerContact = nil;
  [_stick reset];
  for (UIButton *button in _buttons) { [button cancelTrackingWithEvent:nil]; button.highlighted = NO; }
  _input = {};
  _resetting = NO;
  // Host already cleared its mixer; don't re-enter it from its reset callback.
}
- (void)layoutSubviews {
  [super layoutSubviews];
  CGRect safe = UIEdgeInsetsInsetRect(self.bounds, self.safeAreaInsets);
  CGFloat diameter = MIN(156, MIN(safe.size.width*0.22, safe.size.height*0.34));
  CGRect area = [self layoutArea];
  CGFloat available = MIN(area.size.width, area.size.height);
  diameter = galaxypad::controlSide(diameter, [self sizeScaleForControl:_stick], available, 84);
  _stick.frame = CGRectMake(CGRectGetMinX(safe)+20, CGRectGetMaxY(safe)-diameter-20, diameter, diameter);
  [self placeSavedControl:_stick];
  _stickModeLabel.frame = CGRectMake(0, diameter-24, diameter, 18);
  CGFloat size = MIN(66, MAX(44, safe.size.height*0.13));
  const CGFloat positions[][2] = {{0,0},{1,0},{0,1},{1,1},{2,1},{0,2},{1,2}};
  for (NSUInteger i = 0; i < _buttons.count; ++i) {
    UIButton *button = _buttons[i];
    CGFloat side = galaxypad::controlSide(size, [self sizeScaleForControl:button], available, 44);
    button.frame = CGRectMake(CGRectGetMaxX(safe)-20-size-(size+12)*positions[i][0],
      CGRectGetMaxY(safe)-20-size-(size+12)*positions[i][1], size, size);
    button.bounds = CGRectMake(0, 0, side, side);
    button.layer.cornerRadius = side/2;
    [self placeSavedControl:button];
  }
}
@end
