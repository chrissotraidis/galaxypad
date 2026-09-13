// SPDX-License-Identifier: GPL-3.0-or-later
// Isolated UIKit regression host; not compiled into GalaxyPad.
#import "../../apple/ios/GalaxyPadGameOverlay.h"
#import "../../apple/ios/GalaxyPadControllers.h"
#import <GameController/GameController.h>
#import <objc/runtime.h>
#import "../../apple/ios/GalaxyPadAboutViewController.h"
#import "../../apple/shared/GalaxyPadSettings.h"
#include <cstdio>
#include <cstdlib>
#include <cmath>
@interface GalaxyPadMenuButton : UIButton
- (void)contextMenuInteraction:(UIContextMenuInteraction *)interaction
    willDisplayMenuForConfiguration:(UIContextMenuConfiguration *)configuration
    animator:(id<UIContextMenuInteractionAnimating>)animator;
- (void)contextMenuInteraction:(UIContextMenuInteraction *)interaction
    willEndForConfiguration:(UIContextMenuConfiguration *)configuration
    animator:(id<UIContextMenuInteractionAnimating>)animator;
@end
@interface GalaxyPadControllers (PauseTestAccess)
- (void)publishWithSeconds:(float)seconds;
@end
// Software controller snapshots exercise the production adapter. Override
// enumeration only inside this isolated test bundle, never in GalaxyPad.
static NSArray<GCController *> *pauseTestControllers;
static NSArray<GCController *> *PauseTestControllerList(id, SEL) {
  return pauseTestControllers;
}
@interface GalaxyPadGameOverlay (TestAccess)
- (void)beginLayoutEditing;
- (void)selectControlForEditing:(UIView *)control;
- (void)toggleTiltStick;
- (void)toggleAuxiliaryButtons;
- (void)toggleTouchControls;
- (void)endLayoutEditing;
- (UIMenu *)buildMenu;
- (UIAlertController *)touchControlGuide;
- (void)toggleSettingsPanel;
- (void)resetLayout;
- (void)controlDragged:(UIPanGestureRecognizer *)drag;
- (void)stickChanged:(UIView *)stick x:(float)x y:(float)y;
- (void)setTouchTiltSensitivity:(CGFloat)value;
- (void)toggleTouchTiltInversion;
- (void)setMainVolume:(NSInteger)value;
- (void)toggleMainAudioMuted;
- (UIMenu *)audioMenu;
@end
// Exercise phone geometry even when the isolated host runs on an iPad Simulator.
@interface PhoneLayoutTestOverlay : GalaxyPadGameOverlay
@end
@implementation PhoneLayoutTestOverlay
- (UIEdgeInsets)safeAreaInsets { return UIEdgeInsetsMake(0,47,21,47); }
@end
@interface LayoutTestPan : UIPanGestureRecognizer
@property(nonatomic) UIGestureRecognizerState testState;
@property(nonatomic) CGPoint testTranslation;
@end
@implementation LayoutTestPan
- (UIGestureRecognizerState)state { return self.testState; }
- (CGPoint)translationInView:(UIView *)view { return self.testTranslation; }
- (void)setTranslation:(CGPoint)value inView:(UIView *)view { self.testTranslation=value; }
@end
static UIView *Find(UIView *root, NSString *name, BOOL identifier) {
  if ((identifier || [root isKindOfClass:UISlider.class]) &&
      [(identifier?root.accessibilityIdentifier:root.accessibilityLabel) isEqual:name]) return root;
  for (UIView *child in root.subviews) if (UIView *match=Find(child,name,identifier)) return match;
  return nil;
}
static void Check(BOOL condition,const char *message) {
  if (!condition) { fprintf(stderr,"FAIL: %s\n",message); exit(1); }
}
static void CheckControllerPauseToggle(GalaxyPadGameOverlay *overlay) {
  GCController *controller=[GCController controllerWithExtendedGamepad];
  pauseTestControllers=@[controller];
  Method enumeration=class_getClassMethod(GCController.class,@selector(controllers));
  IMP original=method_setImplementation(enumeration,(IMP)PauseTestControllerList);
  GalaxyPadControllers *adapter=[GalaxyPadControllers new];
  __block BOOL modal=NO;
  __block unsigned toggles=0;
  __block galaxypad::InputState published;
  __weak GalaxyPadControllers *weakAdapter=adapter;
  adapter.inputAllowed=^BOOL { return !modal && !overlay.blocksGameplay; };
  adapter.pauseToggleAllowed=^BOOL {
    return !modal && (!overlay.blocksGameplay || overlay.nativePauseVisible);
  };
  adapter.pauseRequested=^{ ++toggles; [overlay toggleNativePause]; [weakAdapter reset]; };
  adapter.inputChanged=^(galaxypad::InputState input) { published=input; };
  [adapter reconcile];
  auto menu=[&](float value) {
    auto button=controller.extendedGamepad.buttonOptions;
    Check(button.pressedChangedHandler!=nil,"View uses event-time pressed callbacks");
    // Deliberately leave the live snapshot released: queued short taps must use
    // the event payload, including when a timer samples zero between callbacks.
    button.pressedChangedHandler(button,value,value!=0);
    [adapter publishWithSeconds:0];
  };
  menu(0); menu(1);
  Check(toggles==1 && overlay.nativePauseVisible,"controller View opens native pause");
  menu(1);
  Check(toggles==1,"held View does not toggle repeatedly");
  [controller.extendedGamepad.leftThumbstick.xAxis setValue:0.5f];
  menu(0); menu(1);
  Check(toggles==2 && !overlay.blocksGameplay,"second View press resumes while gameplay is blocked and a stick is held");
  Check(published.buttons==0,"resume View does not leak guest Plus");
  menu(1);
  Check(toggles==2,"held resume View does not pause again");
  [controller.extendedGamepad.leftThumbstick.xAxis setValue:0];
  menu(0);
  [controller.extendedGamepad.buttonA setValue:1];
  [adapter publishWithSeconds:0];
  Check(published.buttons==galaxypad::A,"gameplay input returns after resume and release");
  [controller.extendedGamepad.buttonA setValue:0];
  modal=YES; menu(0); menu(1);
  Check(toggles==2,"View cannot escape unrelated modal UI");
  modal=NO; menu(1);
  Check(toggles==2,"held modal input cannot become a new View press");
  menu(0); menu(1);
  Check(toggles==3 && overlay.nativePauseVisible,"fresh View works after modal closes");
  menu(0);
  auto options=controller.extendedGamepad.buttonOptions;
  Check(options.pressedChangedHandler!=nil,"Options uses event-time pressed callbacks");
  options.pressedChangedHandler(options,1,YES);
  [adapter publishWithSeconds:0];
  Check(toggles==4 && !overlay.blocksGameplay,"View resumes native pause");
  pauseTestControllers=@[]; [adapter reconcile];
  method_setImplementation(enumeration,original);
  pauseTestControllers=nil;
}
static NSUInteger CountViews(UIView *root, Class type) {
  NSUInteger count=[root isKindOfClass:type] ? 1 : 0;
  for (UIView *child in root.subviews) count+=CountViews(child,type);
  return count;
}
// Synthetic contacts exercise our handlers, not Simulator multitouch delivery.
@interface OverlayTestTouch : UITouch
@property(nonatomic) CGPoint testPoint;
@end
@implementation OverlayTestTouch
- (CGPoint)locationInView:(UIView *)view { (void)view; return self.testPoint; }
@end
@interface OverlayTestViewController : UIViewController
@property(nonatomic,strong) UIViewController *capturedPresentation;
@property(nonatomic) BOOL previewing;
@end
@implementation OverlayTestViewController
- (void)presentViewController:(UIViewController *)controller animated:(BOOL)animated completion:(void (^)(void))completion {
  if (self.previewing) {
    [super presentViewController:controller animated:animated completion:completion];
    return;
  }
  self.capturedPresentation=controller;
  if (completion) completion();
}
- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  if (self.previewing) return;
  GalaxyPadAboutViewController *about=[[GalaxyPadAboutViewController alloc] init];
  [about loadViewIfNeeded];
  UITextView *aboutText=(UITextView *)Find(about.view,@"galaxypad.about.text",YES);
  Check([aboutText isKindOfClass:UITextView.class] && !aboutText.editable,
        "About is readable, not editable");
  Check(aboutText.adjustsFontForContentSizeCategory,"About supports Dynamic Type");
  Check([aboutText.text containsString:@"Private development build"] &&
        [aboutText.text containsString:@"audit is not finished"],"About preserves private/incomplete notices boundary");
  Check(about.navigationItem.rightBarButtonItem!=nil,"About has explicit dismissal");
  // This bundle's own preferences only, never the product's defaults.
  [NSUserDefaults.standardUserDefaults removePersistentDomainForName:NSBundle.mainBundle.bundleIdentifier];
  GalaxyPadSettings *displaySettings = GalaxyPadSettings.sharedSettings;
  Check(displaySettings.aspectRatioMode == GalaxyPadAspectRatioOriginal,
        "iPad-safe aspect default is 4:3");
  Check(displaySettings.hideTouchControlsWhenControllerConnected,
        "controller connection hides touch controls by default");
  [NSUserDefaults.standardUserDefaults setInteger:99 forKey:@"GalaxyPadAspectRatioMode"];
  Check(displaySettings.aspectRatioMode == GalaxyPadAspectRatioOriginal,
        "invalid aspect preference safely falls back to 4:3");
  [NSUserDefaults.standardUserDefaults removeObjectForKey:@"GalaxyPadAspectRatioMode"];
  GalaxyPadGameOverlay *overlay=[[GalaxyPadGameOverlay alloc] initWithFrame:self.view.bounds];
  [self.view addSubview:overlay];
  // Exercise the real letterboxed layout, including optional controls.
  overlay.viewportProvider=^CGRect { return CGRectMake(0,0.1031175,1,0.793765); };
  [overlay applySettings];
  [overlay toggleSettingsPanel];
  [overlay setNeedsLayout]; [overlay layoutIfNeeded];
  UIView *settingsPanel=Find(overlay,@"galaxypad.touch.settings",YES);
  UIView *resetControl=Find(overlay,@"galaxypad.touch.reset",YES);
  Check(settingsPanel && !settingsPanel.hidden && resetControl,"touch settings and reset exist");
  CGRect resetInPanel=[resetControl convertRect:resetControl.bounds toView:settingsPanel];
  if (settingsPanel.bounds.size.height>=320)
    Check(CGRectContainsRect(settingsPanel.bounds,resetInPanel),"Reset fully visible without scrolling at full panel height");
  CGRect panelSafe=UIEdgeInsetsInsetRect(overlay.bounds,overlay.safeAreaInsets);
  Check(CGRectContainsRect(panelSafe,settingsPanel.frame),"settings panel stays inside safe area");
  UIScrollView *settingsScroll=nil;
  for (UIView *view in settingsPanel.subviews)
    if ([view isKindOfClass:UIScrollView.class]) settingsScroll=(UIScrollView *)view;
  Check(settingsScroll!=nil,"touch settings retain scroll access on compact screens");
  [settingsScroll scrollRectToVisible:[resetControl convertRect:resetControl.bounds toView:settingsScroll]
                            animated:NO];
  [settingsPanel layoutIfNeeded];
  CGRect resetInScroll=[resetControl convertRect:resetControl.bounds toView:settingsScroll];
  Check(CGRectContainsRect(settingsScroll.bounds,resetInScroll),"scrolling exposes the complete Reset action");
  CGPoint resetHitPoint=[resetControl convertPoint:CGPointMake(CGRectGetMidX(resetControl.bounds),
      CGRectGetMidY(resetControl.bounds)) toView:overlay];
  UIView *resetHit=[overlay hitTest:resetHitPoint withEvent:nil];
  Check(resetHit==resetControl || [resetHit isDescendantOfView:resetControl],
        "compact touch settings Reset remains tappable after scrolling");
  [settingsScroll setContentOffset:CGPointZero animated:NO];
  [overlay toggleSettingsPanel];
  UIMenu *rootMenu=[overlay buildMenu];
  overlay.gameplayAvailable = NO;
  [overlay layoutIfNeeded];
  Check(Find(overlay,@"A",YES).hidden,"idle hides gameplay buttons");
  Check(Find(overlay,@"galaxypad.pause",YES).hidden,"idle hides game pause");
  Check(!Find(overlay,@"galaxypad.menu",YES).hidden,"idle retains native menu access");
  [overlay refreshControllerVisibility]; [overlay layoutIfNeeded];
  Check(Find(overlay,@"A",YES).hidden,"controller refresh cannot reveal idle gameplay buttons");
  overlay.gameplayAvailable = YES; [overlay layoutIfNeeded];
  Check(!Find(overlay,@"A",YES).hidden,"running restores gameplay buttons");
  Check(!Find(overlay,@"galaxypad.pause",YES).hidden,"running exposes game pause");
  UIView *menuControl=Find(overlay,@"galaxypad.menu",YES);
  UIView *pauseControl=Find(overlay,@"galaxypad.pause",YES);
  CGRect topSafe=UIEdgeInsetsInsetRect(overlay.bounds,overlay.safeAreaInsets);
  Check(fabs(CGRectGetMinY(menuControl.frame)-CGRectGetMinY(pauseControl.frame))<0.5,
        "top controls share the same vertical alignment");
  Check(CGRectGetMinY(menuControl.frame)>=CGRectGetMinY(topSafe)+19.5,
        "top controls keep the lowered iPad-safe inset");
  Check(rootMenu.children.count==8,"root menu includes the main Audio group");
  GalaxyPadSettings *audioSettings = GalaxyPadSettings.sharedSettings;
  Check(audioSettings.mainVolume==100 && !audioSettings.mainAudioMuted,"audio defaults full volume and unmuted");
  [overlay setMainVolume:50];
  [overlay toggleMainAudioMuted];
  UIMenu *audioMenu = [overlay audioMenu];
  Check(audioSettings.mainVolume==50 && audioSettings.mainAudioMuted,"mute preserves selected volume");
  Check(((UIAction *)audioMenu.children.lastObject).state==UIMenuElementStateOn,"mute menu check follows setting");
  Check(((UIAction *)((UIMenu *)audioMenu.children.firstObject).children[2]).state==UIMenuElementStateOn,
        "volume menu checks selected level");
  [overlay toggleMainAudioMuted];
  Check(audioSettings.mainVolume==50 && !audioSettings.mainAudioMuted,"unmute restores retained level");
  [overlay setMainVolume:-1]; Check(audioSettings.mainVolume==0,"volume lower bound");
  [overlay setMainVolume:101]; Check(audioSettings.mainVolume==100,"volume upper bound");
  [NSUserDefaults.standardUserDefaults setObject:@"bad" forKey:@"GalaxyPadMainVolume"];
  Check(audioSettings.mainVolume==100,"nonnumeric volume safely defaults");
  [NSUserDefaults.standardUserDefaults setDouble:NAN forKey:@"GalaxyPadMainVolume"];
  Check(audioSettings.mainVolume==100,"nonfinite volume safely defaults");
  [overlay setMainVolume:100];
  UIMenu *display=(UIMenu *)rootMenu.children.firstObject;
  Check([display.title isEqual:@"Display"],"SunPad Display group remains first");
  Check(((UIMenu *)display.children.firstObject).children.count==4,
        "all four render scales remain available under Display");
  UIMenu *aspectMenu=(UIMenu *)display.children[1];
  Check(aspectMenu.children.count==3,"all display aspect choices remain available");
  for (UIAction *action in aspectMenu.children)
    Check(!(action.attributes & UIMenuElementAttributesDisabled),"restart-required aspect remains selectable");
  Check(CountViews(overlay,UISegmentedControl.class)==0,
        "touch settings do not duplicate the render-resolution selector");
  Check([display.children[2].title isEqual:@"Show FPS Counter"],
        "FPS diagnostic is inside Display");
  Check([((UIAction *)display.children[3]).identifier isEqual:@"galaxypad.menu.performance-log"] &&
        ((UIAction *)display.children[3]).state==UIMenuElementStateOff,
        "persistent performance logging defaults off and is reachable");
  UIAction *stop=(UIAction *)rootMenu.children.lastObject;
  Check((stop.attributes & UIMenuElementAttributesDestructive) &&
        (stop.attributes & UIMenuElementAttributesDisabled),
        "Stop is destructive and disabled without a runtime handler");
  overlay.stopRequested=^{};
  UIButton *menuButton=(UIButton *)Find(overlay,@"galaxypad.menu",YES);
  stop=(UIAction *)menuButton.menu.children.lastObject;
  Check(!(stop.attributes & UIMenuElementAttributesDisabled),"Stop enabled with runtime handler");
  overlay.stopRequested=nil;
  Check(((UIAction *)menuButton.menu.children.lastObject).attributes & UIMenuElementAttributesDisabled,
        "clearing runtime handler refreshes the already attached menu");
  GalaxyPadMenuButton *nativeMenu=(GalaxyPadMenuButton *)menuButton;
  [nativeMenu contextMenuInteraction:nil willDisplayMenuForConfiguration:nil animator:nil];
  Check(overlay.nativeMenuVisible && overlay.blocksGameplay,
        "displayed native menu blocks gameplay input");
  [nativeMenu contextMenuInteraction:nil willEndForConfiguration:nil animator:nil];
  Check(!overlay.nativeMenuVisible && !overlay.blocksGameplay,
        "menu dismissal releases gameplay without animator completion");
  for (UIMenuElement *element in rootMenu.children) {
    if ([element.title isEqual:@"Game Data & Saves"]) {
      UIAction *status=(UIAction *)((UIMenu *)element).children.firstObject;
      Check([status.identifier isEqual:@"galaxypad.menu.data-status"] &&
            (status.attributes & UIMenuElementAttributesDisabled) &&
            !(status.attributes & UIMenuElementAttributesDestructive),
            "read-only data status is disabled without a host handler");
      UIAction *remove=(UIAction *)((UIMenu *)element).children.lastObject;
      Check((remove.attributes & UIMenuElementAttributesDestructive) &&
            (remove.attributes & UIMenuElementAttributesDisabled),
            "remove styling preserves disabled state without data host");
    }
  }
  UIAlertController *guide=[overlay touchControlGuide];
  Check([guide.message containsString:@"X: spin. Y: reset camera."] &&
        [guide.message containsString:@"press A or B separately"] &&
        [guide.message containsString:@"not device motion"],
        "touch guide describes face labels, independent aim/action and tilt boundary");
  Check(guide.actions.count==1 && [guide.actions.firstObject.title isEqual:@"Done"],
        "touch guide has explicit non-destructive dismissal");
  BOOL foundExtraAction=NO, foundGuideAction=NO;
  for (UIMenuElement *element in [overlay buildMenu].children) {
    if (![element isKindOfClass:UIMenu.class] || ![element.title isEqual:@"Controls"]) continue;
    for (UIMenuElement *child in ((UIMenu *)element).children) {
      if ([child isKindOfClass:UIAction.class] &&
          [((UIAction *)child).identifier isEqual:@"galaxypad.menu.touch-guide"])
        foundGuideAction=!(((UIAction *)child).attributes & UIMenuElementAttributesDisabled);
      if ([child.title isEqual:@"Show Extra Wii Buttons (1 / 2 / −)"]) {
        foundExtraAction=YES;
        Check(!(((UIAction *)child).attributes & UIMenuElementAttributesDisabled),
              "extra buttons action works without a host delegate");
      }
    }
  }
  Check(foundExtraAction,"advanced keys are reachable from Controls menu");
  Check(foundGuideAction,"touch guide is available inside Controls without a host delegate");
  [overlay setNeedsLayout]; [overlay layoutIfNeeded];
  if (self.traitCollection.userInterfaceIdiom == UIUserInterfaceIdiomPhone) {
    NSArray<NSString *> *visibleIDs=@[@"move", @"A", @"B", @"Spin", @"C", @"Z",
      @"Plus", @"D_U", @"D_D", @"D_L", @"D_R", @"galaxypad.menu"];
    CGRect safe=UIEdgeInsetsInsetRect(overlay.bounds,overlay.safeAreaInsets);
    CGRect confirmationActions=CGRectMake(CGRectGetMinX(safe)+safe.size.width*0.25,
        CGRectGetMinY(safe)+safe.size.height*0.76,safe.size.width*0.5,safe.size.height*0.18);
    Check(!CGRectIntersectsRect(Find(overlay,@"Plus",YES).frame,confirmationActions),
          "phone pause avoids observed save confirmation actions");
    for (NSUInteger i=0;i<visibleIDs.count;++i) {
      UIView *control=Find(overlay,visibleIDs[i],YES);
      Check(control && !control.hidden,"default phone control visible");
      Check(control.bounds.size.width>=44 && control.bounds.size.height>=44,
            "default phone target at least 44pt");
      Check(CGRectContainsRect(CGRectInset(safe,-0.5,-0.5),control.frame),
            "default phone control contained in safe area");
      for (NSUInteger j=i+1;j<visibleIDs.count;++j) {
        UIView *peer=Find(overlay,visibleIDs[j],YES);
        if (CGRectIntersectsRect(control.frame,peer.frame))
          fprintf(stderr,"Overlapping phone controls: %s %s (%s / %s)\n",
            visibleIDs[i].UTF8String,visibleIDs[j].UTF8String,
            NSStringFromCGRect(control.frame).UTF8String,NSStringFromCGRect(peer.frame).UTF8String);
        Check(!CGRectIntersectsRect(control.frame,peer.frame),
              "default phone visible touch targets do not overlap");
      }
    }
  }
  if (self.traitCollection.userInterfaceIdiom == UIUserInterfaceIdiomPad &&
      overlay.bounds.size.width >= 1000) {
    NSArray<NSString *> *ids = @[@"move", @"tilt", @"A", @"B", @"Spin", @"C", @"Z", @"1", @"2", @"Plus", @"−", @"D_U", @"D_D", @"D_L", @"D_R"];
    // Physical-device feedback prioritizes SunPad's thumb reach over the old
    // scene-specific HUD exclusion rectangles that forced controls inward.
    Check(CGRectGetMidX(Find(overlay,@"move",YES).frame)<overlay.bounds.size.width*0.2,
          "iPad movement is reachable from the left edge");
    Check(CGRectGetMidX(Find(overlay,@"A",YES).frame)>overlay.bounds.size.width*0.85,
          "iPad jump is reachable from the right edge");
    for (NSUInteger i=0; i<ids.count; ++i) {
      UIView *first=Find(overlay,ids[i],YES);
      Check(first!=nil,"default iPad control exists");
      Check(first.bounds.size.width>=44 && first.bounds.size.height>=44,"minimum iPad target is 44pt");
      for (NSUInteger j=i+1; j<ids.count; ++j) {
        UIView *second=Find(overlay,ids[j],YES);
        Check(second!=nil,"peer control exists");
        if (CGRectIntersectsRect(first.frame,second.frame))
          fprintf(stderr,"Overlapping iPad controls: %s %s\n",ids[i].UTF8String,ids[j].UTF8String);
        Check(!CGRectIntersectsRect(first.frame,second.frame),"default iPad controls do not overlap");
      }
    }
  }
  __block galaxypad::InputState state;
  overlay.inputChanged=^(galaxypad::InputState value) { state=value; };
  UIControl *a=(UIControl *)Find(overlay,@"A",YES);
  UIControl *b=(UIControl *)Find(overlay,@"B",YES);
  Check(a && b,"A and B controls exist");
  [a sendActionsForControlEvents:UIControlEventTouchDown];
  [(UIControl *)Find(overlay,@"galaxypad.pause",YES) sendActionsForControlEvents:UIControlEventTouchUpInside];
  Check((state.buttons & (galaxypad::A | galaxypad::Plus)) == (galaxypad::A | galaxypad::Plus),
        "visible Pause sends original Plus while preserving held touch A");
  Check(!overlay.blocksGameplay && !overlay.nativePauseVisible,"game Pause leaves runtime and input live");
  [NSRunLoop.mainRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.8]];
  Check(state.buttons==galaxypad::A,"game Pause pulse releases without clearing held touch");
  [a sendActionsForControlEvents:UIControlEventTouchUpInside];
  [overlay presentNativePause];
  Check(state.buttons==0 && overlay.blocksGameplay,"separate app pause releases and blocks input");
  UIControl *nativeResume=(UIControl *)Find(overlay,@"galaxypad.pause.back",YES);
  Check(nativeResume && !nativeResume.hidden,"native Pause has a visible Back to Game escape hatch");
  [nativeResume sendActionsForControlEvents:UIControlEventTouchUpInside];
  Check(!overlay.blocksGameplay,"Back to Game releases the pause input gate");
  CheckControllerPauseToggle(overlay);
  UIControl *pauseActivation=(UIControl *)Find(overlay,@"Plus",YES);
  Check([pauseActivation accessibilityActivate],"visible pause supports accessibility activation");
  Check(state.buttons & galaxypad::Plus,"accessibility activation presses Plus");
  [pauseActivation sendActionsForControlEvents:UIControlEventTouchDown];
  [NSRunLoop.mainRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.8]];
  Check(state.buttons & galaxypad::Plus,"accessibility release preserves held touch");
  [pauseActivation sendActionsForControlEvents:UIControlEventTouchUpInside];
  Check(!(state.buttons & galaxypad::Plus),"touch release clears remaining Plus");
  Check([pauseActivation accessibilityActivate],"second accessibility pulse starts");
  [overlay reset];
  [NSRunLoop.mainRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.8]];
  Check(state.buttons==0,"reset cancels pending accessibility pulse");
  [pauseActivation accessibilityActivate];
  [overlay toggleSettingsPanel];
  Check(state.buttons==0 && ![pauseActivation accessibilityActivate],"settings clears and blocks accessibility input");
  [overlay toggleSettingsPanel];
  [NSRunLoop.mainRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.8]];
  Check(state.buttons==0,"dismissed settings does not revive cancelled pulse");
  overlay.gameplayAvailable=NO;
  Check(![pauseActivation accessibilityActivate],"idle rejects accessibility game input");
  overlay.gameplayAvailable=YES;
  if (self.traitCollection.userInterfaceIdiom==UIUserInterfaceIdiomPhone) {
    UIView *pause=Find(overlay,@"Plus",YES);
    CGRect safe=UIEdgeInsetsInsetRect(overlay.bounds,overlay.safeAreaInsets);
    CGRect centerLane=CGRectMake(CGRectGetMinX(safe)+safe.size.width*0.4,
        CGRectGetMinY(safe)+safe.size.height*0.7,safe.size.width*0.2,safe.size.height*0.3);
    Check(!CGRectIntersectsRect(pause.frame,centerLane),"phone pause avoids lower central game content");
    Check(CGRectContainsRect(safe,pause.frame),"phone pause stays inside safe area");
    Check(pause.bounds.size.width>=44 && pause.bounds.size.height>=44,"phone pause retains minimum touch target");
    for (NSString *identifier in @[@"A",@"B",@"C",@"Z",@"Spin",@"tilt",@"1",@"2",@"−"])
      Check(!CGRectIntersectsRect(pause.frame,Find(overlay,identifier,YES).frame),
            "phone pause does not intersect action or optional button targets");
  }
  for (NSString *identifier in @[@"A", @"B", @"C", @"Z", @"Spin"]) {
    UIButton *button=(UIButton *)Find(overlay,identifier,YES);
    Check([button titleForState:UIControlStateNormal].length==1,"SunPad face buttons use one letter, no action copy");
    Check([button attributedTitleForState:UIControlStateNormal]==nil,"no multiline action text in face buttons");
  }
  if (self.traitCollection.userInterfaceIdiom==UIUserInterfaceIdiomPad && overlay.bounds.size.width>=1000) {
    for (NSString *identifier in @[@"1", @"2", @"−"]) {
      Check(Find(overlay,identifier,YES).center.y > overlay.bounds.size.height*0.5,
            "auxiliary buttons remain with lower SunPad clusters, never a top toolbar");
      UIView *aux=Find(overlay,identifier,YES);
      Check(aux.bounds.size.width==aux.bounds.size.height,
            "auxiliary keys are compact, not oversized shoulder pills");
    }
    Check(Find(overlay,@"Plus",YES).bounds.size.width>=100,
          "iPad Start has a readable labeled target");
    Check([[(UIButton *)Find(overlay,@"Plus",YES) titleForState:UIControlStateNormal] isEqual:@"Start +"],
          "Start identifies the guest plus button");

  }
  [a sendActionsForControlEvents:UIControlEventTouchDown];
  [b sendActionsForControlEvents:UIControlEventTouchDown];
  Check(state.buttons==(galaxypad::A|galaxypad::B),"UIKit button callbacks preserve A+B");
  [a sendActionsForControlEvents:UIControlEventTouchUpInside];
  Check(state.buttons==galaxypad::B,"A release preserves B");
  [b sendActionsForControlEvents:UIControlEventTouchCancel];
  Check(state.buttons==0,"B cancellation releases final button");
  overlay.viewportProvider=^CGRect { return CGRectMake(0,0.1,1,0.8); };
  OverlayTestTouch *bar=[OverlayTestTouch new];
  bar.testPoint=CGPointMake(overlay.bounds.size.width*0.5,0);
  OverlayTestTouch *pointer=[OverlayTestTouch new];
  pointer.testPoint=CGPointMake(overlay.bounds.size.width*0.5,overlay.bounds.size.height*0.5);
  [overlay touchesBegan:[NSSet setWithObject:bar] withEvent:nil];
  [overlay touchesBegan:[NSSet setWithObject:pointer] withEvent:nil];
  Check(state.pointerVisible,"letterbox contact must not steal the gameplay pointer");
  [a sendActionsForControlEvents:UIControlEventTouchDown];
  pointer.testPoint=CGPointMake(overlay.bounds.size.width*0.75,overlay.bounds.size.height*0.3);
  [overlay touchesMoved:[NSSet setWithObject:pointer] withEvent:nil];
  Check(state.buttons==galaxypad::A && state.pointerVisible &&
        std::abs(state.pointerX-0.75)<0.001 && std::abs(state.pointerY-0.25)<0.001,
        "pointer movement preserves held A and maps through gameplay viewport");
  Check(state.pointerContact,"active touch owns pointer");
  [overlay touchesEnded:[NSSet setWithObject:pointer] withEvent:nil];
  Check(state.pointerVisible && !state.pointerContact && state.buttons==galaxypad::A,
        "lift releases pointer ownership but retains touch aim and held A");
  galaxypad::InputMixer pointerMixer;
  galaxypad::InputState controllerAim; controllerAim.pointerVisible=true;
  controllerAim.pointerX=0.2f;
  pointerMixer.set(galaxypad::InputSource::Controller,controllerAim);
  pointerMixer.set(galaxypad::InputSource::Touch,state);
  Check(pointerMixer.consume().pointerX==0.2f,"lift restores right-stick aim");
  [overlay touchesBegan:[NSSet setWithObject:pointer] withEvent:nil];
  pointerMixer.set(galaxypad::InputSource::Touch,state);
  Check(std::abs(pointerMixer.consume().pointerX-0.75f)<0.001,
        "new contact takes pointer ownership again");
  [overlay touchesCancelled:[NSSet setWithObject:pointer] withEvent:nil];
  Check(!state.pointerVisible && !state.pointerContact && state.buttons==galaxypad::A,
        "pointer cancel clears contact and preserves held button");
  [a sendActionsForControlEvents:UIControlEventTouchUpInside];
  [overlay reset];
  [overlay touchesBegan:[NSSet setWithObject:pointer] withEvent:nil];
  Check(state.pointerVisible,"prepare touch aim before controller handoff");
  [overlay setTouchControlsHidden:YES animated:NO];
  Check(!state.pointerVisible,"controller handoff clears touch aim");
  [overlay touchesBegan:[NSSet setWithObject:pointer] withEvent:nil];
  Check(!state.pointerVisible,"hidden touch controls cannot reclaim controller aim");
  [overlay setTouchControlsHidden:NO animated:NO];
  [overlay touchesBegan:[NSSet setWithObject:pointer] withEvent:nil];
  Check(state.pointerVisible,"touch aim returns after controller handoff ends");
  [overlay reset];
  [a sendActionsForControlEvents:UIControlEventTouchDown];
  [overlay touchesBegan:[NSSet setWithObject:pointer] withEvent:nil];
  Check(state.buttons==galaxypad::A && state.pointerVisible,"prepare held touch before manual disable");
  [overlay toggleTouchControls];
  Check(state.buttons==0 && !state.pointerVisible && a.hidden,
        "manual disable clears button and pointer and hides controls");
  UIView *menu=Find(overlay,@"galaxypad.menu",YES);
  Check(menu && !menu.hidden && menu.userInteractionEnabled,"manual disable preserves menu escape hatch");
  [overlay touchesBegan:[NSSet setWithObject:pointer] withEvent:nil];
  Check(!state.pointerVisible,"manual disable rejects new pointer contacts");
  [overlay refreshControllerVisibility];
  Check(a.hidden,"controller refresh cannot undo manual disable");
  [overlay beginLayoutEditing];
  Check(!a.hidden,"editor can still show disabled controls");
  [overlay endLayoutEditing];
  Check(a.hidden,"leaving editor restores manual disable");
  [overlay applySettings];
  Check(a.hidden,"settings refresh preserves manual disable");
  [overlay toggleTouchControls];
  Check(!a.hidden && a.userInteractionEnabled,"manual enable restores controls");
  [overlay touchesBegan:[NSSet setWithObject:pointer] withEvent:nil];
  Check(state.pointerVisible,"pointer reacquires after manual enable");
  [overlay reset];
  UIView *two=Find(overlay,@"2",YES);
  Check(two!=nil,"Wii2 is present");
  for (NSString *identifier in @[@"1", @"2", @"−"]) {
    UIView *aux=Find(overlay,identifier,YES);
    Check(aux.hidden && !aux.userInteractionEnabled,"extra Wii keys default hidden and cannot steal pointer touches");
  }
  Check(!Find(overlay,@"Plus",YES).hidden,"pause remains in the primary layout");
  [overlay toggleAuxiliaryButtons];
  Check(!two.hidden && two.userInteractionEnabled,"advanced Wii keys remain available");
  [(UIControl *)two sendActionsForControlEvents:UIControlEventTouchDown];
  Check(state.buttons==galaxypad::Two,"extra Wii key retains its mapping");
  [overlay toggleAuxiliaryButtons];
  Check(state.buttons==0 && two.hidden,"hiding held advanced keys clears input");
  UIView *tilt=Find(overlay,@"tilt",YES);
  Check(tilt.hidden,"tilt is out of the primary gameplay layout by default");
  [overlay toggleTiltStick];
  Check(!tilt.hidden && tilt.userInteractionEnabled,"tilt is explicitly available");
  GalaxyPadSettings *tiltSettings=GalaxyPadSettings.sharedSettings;
  Check(tiltSettings.touchTiltSensitivity==1 && !tiltSettings.touchTiltInvertY,
        "touch tilt defaults preserve original response");
  [overlay stickChanged:tilt x:0.4f y:-0.6f];
  Check(std::abs(state.tiltX-0.4f)<0.001 && std::abs(state.tiltY+0.6f)<0.001,
        "default tilt preserves axes");
  [overlay setTouchTiltSensitivity:0.5];
  Check(state.tiltX==0 && state.tiltY==0,"sensitivity change releases held tilt");
  [overlay stickChanged:tilt x:0.4f y:-0.6f];
  Check(std::abs(state.tiltX-0.2f)<0.001 && std::abs(state.tiltY+0.3f)<0.001,
        "low sensitivity scales both tilt axes");
  [overlay toggleTouchTiltInversion];
  Check(state.tiltX==0 && state.tiltY==0,"inversion change releases held tilt");
  [overlay setTouchTiltSensitivity:1.5];
  [overlay stickChanged:tilt x:1 y:-1];
  Check(state.tiltX==1 && state.tiltY==1,"tilt boost saturates and Y inversion applies");
  [overlay stickChanged:Find(overlay,@"move",YES) x:0.4f y:-0.6f];
  Check(std::abs(state.moveX-0.4f)<0.001 && std::abs(state.moveY+0.6f)<0.001,
        "tilt preferences do not change movement");
  [overlay setTouchTiltSensitivity:NAN];
  Check(tiltSettings.touchTiltSensitivity==1,"invalid sensitivity restores neutral default");
  [NSUserDefaults.standardUserDefaults setObject:@"invalid" forKey:@"GalaxyPadTouchTiltSensitivity"];
  Check(tiltSettings.touchTiltSensitivity==1,"malformed persisted sensitivity is safe");
  [overlay setTouchTiltSensitivity:1];
  [overlay toggleTouchTiltInversion];
  [overlay toggleTiltStick];
  Check(tilt.hidden && !tilt.userInteractionEnabled,"hidden tilt cannot consume touches");
  CGFloat width=two.bounds.size.width;
  [overlay beginLayoutEditing];
  Check(!two.hidden && two.userInteractionEnabled,"editor exposes hidden advanced keys without changing preference");
  [overlay setNeedsLayout]; [overlay layoutIfNeeded];
  UIView *editorBar=Find(overlay,@"galaxypad.touch.editor",YES);
  UIView *doneControl=Find(overlay,@"galaxypad.touch.done",YES);
  Check(editorBar && doneControl.bounds.size.height>=44,"editor Done has at least 44pt height");
  Check(!CGRectIntersectsRect(editorBar.frame,menuButton.frame),"editor does not cover menu escape hatch");
  for (NSString *key in @[@"1", @"2", @"−", @"Plus"]) {
    UIView *extra=Find(overlay,key,YES);
    Check(!CGRectIntersectsRect(editorBar.frame,extra.frame),"editor leaves extra Wii keys selectable");
  }
  Check(!tilt.hidden,"editor still exposes tilt placement");
  [overlay selectControlForEditing:two];
  [overlay setNeedsLayout]; [overlay layoutIfNeeded];
  UISlider *slider=(UISlider *)Find(overlay,@"2 size",NO);
  Check([slider isKindOfClass:UISlider.class] && slider.enabled,"selected slider exists and enabled");
  CGPoint center=[slider convertPoint:CGPointMake(CGRectGetMidX(slider.bounds),CGRectGetMidY(slider.bounds)) toView:overlay];
  UIView *hit=[overlay hitTest:center withEvent:nil];
  Check(hit==slider || [hit isDescendantOfView:slider],"slider receives hit testing");
  slider.value=1.25;
  [slider sendActionsForControlEvents:UIControlEventValueChanged];
  [overlay layoutIfNeeded];
  Check(std::abs([GalaxyPadSettings.sharedSettings sizeScaleForControl:@"2"]-1.25)<0.001,"size stored");
  Check(std::abs(two.bounds.size.width/width-1.25)<0.01,"button geometry resizes");
  UIButton *visibility=(UIButton *)Find(overlay,@"galaxypad.touch.selected-visibility",YES);
  Check(visibility && !visibility.hidden && [visibility.currentTitle isEqual:@"Show in game"],
        "selecting a hidden Wii key offers restoration in the editor");
  Check(visibility.bounds.size.width>=44 && visibility.bounds.size.height>=44,
        "editor visibility meets minimum target size");
  [visibility sendActionsForControlEvents:UIControlEventTouchUpInside];
  Check([NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadShowAuxiliaryButtons"],
        "editor restores auxiliary keys persistently");
  [overlay endLayoutEditing];
  for (NSString *key in @[@"1",@"2",@"−"])
    Check(!Find(overlay,key,YES).hidden,"restored keys remain visible after Done");
  [overlay beginLayoutEditing];
  [overlay selectControlForEditing:two];
  [visibility sendActionsForControlEvents:UIControlEventTouchUpInside];
  [overlay endLayoutEditing];
  Check(two.hidden,"editor can hide auxiliary keys again");
  [overlay beginLayoutEditing];
  [overlay selectControlForEditing:tilt];
  Check(!visibility.hidden && [visibility.accessibilityLabel isEqual:@"Show Tilt in game"],
        "hidden tilt stick offers the same restoration action");
  [visibility sendActionsForControlEvents:UIControlEventTouchUpInside];
  [overlay endLayoutEditing];
  Check(!tilt.hidden,"restored tilt remains usable after Done");
  [overlay toggleTiltStick];
  [overlay beginLayoutEditing];
  [overlay selectControlForEditing:a];
  Check(visibility.hidden,"required gameplay controls cannot be hidden accidentally");
  [overlay selectControlForEditing:two];
  GalaxyPadSettings *settings=GalaxyPadSettings.sharedSettings;
  settings.controlOpacity=0.37;
  settings.hideTouchControlsWhenControllerConnected=NO;
  settings.controlSizeScale=1.2;
  NSUserDefaults *defaults=NSUserDefaults.standardUserDefaults;
  [defaults setObject:@{@"Plus":NSStringFromCGPoint(CGPointMake(0.6,0.7))}
              forKey:@"GalaxyPadControlOrigins"];
  [defaults setObject:NSStringFromCGPoint(CGPointMake(0.4,0.5))
              forKey:@"GalaxyPadExperimentalDPadOrigin"];
  [defaults setDouble:1.4 forKey:@"GalaxyPadExperimentalDPadScale"];
  [overlay resetLayout];
  [overlay layoutIfNeeded];
  Check(std::abs(settings.controlOpacity-0.37)<0.001,"layout reset preserves opacity");
  Check(!settings.hideTouchControlsWhenControllerConnected,"layout reset preserves controller visibility");
  Check(std::abs(settings.controlSizeScale-1)<0.001 &&
        std::abs([settings sizeScaleForControl:@"2"]-1)<0.001,"layout reset clears global and cached individual sizes");
  for (NSString *key in @[@"GalaxyPadControlOrigins",@"GalaxyPadExperimentalDPadOrigin",@"GalaxyPadExperimentalDPadScale"])
    Check([defaults objectForKey:key]==nil,"layout reset clears saved positions and D-pad size");
  [overlay beginLayoutEditing];
  [overlay layoutIfNeeded];
  UIView *pause=Find(overlay,@"Plus",YES);
  CGPoint originalCenter=pause.center;
  LayoutTestPan *pan=[LayoutTestPan new];
  [pause addGestureRecognizer:pan];
  pan.testState=UIGestureRecognizerStateBegan;
  pan.testTranslation=CGPointMake(-30,-25);
  [overlay controlDragged:pan];
  pan.testState=UIGestureRecognizerStateCancelled;
  [overlay controlDragged:pan];
  [overlay layoutIfNeeded];
  Check([defaults dictionaryForKey:@"GalaxyPadControlOrigins"][@"Plus"]==nil,
        "cancelled drag does not persist a position");
  Check(CGPointEqualToPoint(pause.center,originalCenter),"cancelled drag restores default position");
  pan.testState=UIGestureRecognizerStateBegan;
  pan.testTranslation=CGPointMake(-30,-25);
  [overlay controlDragged:pan];
  pan.testState=UIGestureRecognizerStateEnded;
  [overlay controlDragged:pan];
  NSString *savedPause=[defaults dictionaryForKey:@"GalaxyPadControlOrigins"][@"Plus"];
  Check(savedPause!=nil,"completed drag persists position");
  CGPoint savedCenter=pause.center;
  pan.testState=UIGestureRecognizerStateBegan;
  pan.testTranslation=CGPointMake(20,15);
  [overlay controlDragged:pan];
  pan.testState=UIGestureRecognizerStateCancelled;
  [overlay controlDragged:pan];
  [overlay layoutIfNeeded];
  Check([[defaults dictionaryForKey:@"GalaxyPadControlOrigins"][@"Plus"] isEqual:savedPause],
        "cancelled drag preserves prior custom position");
  Check(std::abs(pause.center.x-savedCenter.x)<0.01 && std::abs(pause.center.y-savedCenter.y)<0.01,
        "cancelled drag restores custom geometry");
  [pause removeGestureRecognizer:pan];
  [overlay resetLayout];
  puts("UIKit overlay: A+B callbacks/release, Wii2 selection, slider hit test, ValueChanged, persistence getter and resize pass");
  PhoneLayoutTestOverlay *phone=[[PhoneLayoutTestOverlay alloc] initWithFrame:CGRectMake(0,0,844,390)];
  UIViewController *phoneHost=[UIViewController new];
  [self addChildViewController:phoneHost];
  [self setOverrideTraitCollection:[UITraitCollection traitCollectionWithUserInterfaceIdiom:UIUserInterfaceIdiomPhone]
          forChildViewController:phoneHost];
  phoneHost.view.frame=phone.bounds;
  [self.view addSubview:phoneHost.view];
  [phoneHost.view addSubview:phone];
  [phoneHost didMoveToParentViewController:self];
  [phone applySettings];
  [phone beginLayoutEditing];
  [phone selectControlForEditing:Find(phone,@"2",YES)];
  [phone setNeedsLayout]; [phone layoutIfNeeded];
  UIView *phoneEditor=Find(phone,@"galaxypad.touch.editor",YES);
  UIView *phoneVisibility=Find(phone,@"galaxypad.touch.selected-visibility",YES);
  UIView *phoneSlider=Find(phone,@"2 size",NO);
  Check(phoneVisibility.bounds.size.width>=44 && phoneVisibility.bounds.size.height>=44,
        "iPhone 14 editor keeps visibility target usable");
  for (UIView *item in @[phoneVisibility,phoneSlider,Find(phone,@"galaxypad.touch.done",YES)]) {
    CGRect frame=[item convertRect:item.bounds toView:phoneEditor];
    Check(CGRectContainsRect(phoneEditor.bounds,frame),"iPhone 14 editor actions fit inside bar");
    CGPoint point=[item convertPoint:CGPointMake(CGRectGetMidX(item.bounds),CGRectGetMidY(item.bounds)) toView:phone];
    UIView *target=[phone hitTest:point withEvent:nil];
    Check(target==item || [target isDescendantOfView:item],"iPhone 14 editor actions receive touches");
  }
  CGRect phoneSafe=UIEdgeInsetsInsetRect(phone.bounds,phone.safeAreaInsets);
  for (NSString *key in @[@"move",@"tilt"])
    Check(CGRectContainsRect(phoneSafe,Find(phone,key,YES).frame),"iPhone sticks fit safe area");
  if ([NSProcessInfo.processInfo.arguments containsObject:@"--preview-phone-editor"]) {
    [overlay removeFromSuperview];
    self.view.backgroundColor=UIColor.blackColor;
    puts("GALAXYPAD_UI_TEST_PASS"); fflush(stdout);
    return;
  }
  [phoneHost willMoveToParentViewController:nil];
  [phoneHost.view removeFromSuperview];
  [phoneHost removeFromParentViewController];
  // Invoke the exact menu action through public UIControl dispatch. This proves
  // its persistence/alert handler, separately from native menu navigation.
  UIMenu *handlerDisplay=(UIMenu *)[overlay buildMenu].children.firstObject;
  UIAction *nativeAspect=(UIAction *)((UIMenu *)handlerDisplay.children[1]).children[1];
  UIControl *aspectDispatch=[UIControl new];
  [aspectDispatch addAction:nativeAspect forControlEvents:UIControlEventTouchUpInside];
  [aspectDispatch sendActionsForControlEvents:UIControlEventTouchUpInside];
  Check(GalaxyPadSettings.sharedSettings.aspectRatioMode==GalaxyPadAspectRatioWidescreen,
        "native 16:9 action persists the next-launch setting");
  Check([self.capturedPresentation isKindOfClass:UIAlertController.class] &&
        [self.capturedPresentation.title isEqual:@"Restart Required"],
        "aspect handler explains that a game restart is required");
  self.capturedPresentation=nil;
  GalaxyPadSettings.sharedSettings.aspectRatioMode=GalaxyPadAspectRatioOriginal;
  puts("GALAXYPAD_UI_TEST_PASS");
  fflush(stdout);
  if ([NSProcessInfo.processInfo.arguments containsObject:@"--preview"]) {
    self.previewing=YES;
    [overlay removeFromSuperview];
    [NSUserDefaults.standardUserDefaults removePersistentDomainForName:NSBundle.mainBundle.bundleIdentifier];
    [GalaxyPadSettings.sharedSettings resetControlSizeScales];
    GalaxyPadGameOverlay *preview=[[GalaxyPadGameOverlay alloc] initWithFrame:self.view.bounds];
    preview.viewportProvider=^CGRect { return CGRectMake(0,0.1031175,1,0.793765); };
    self.view.backgroundColor=UIColor.blackColor;
    UIView *field=[[UIView alloc] initWithFrame:CGRectMake(0,self.view.bounds.size.height*0.1031175,
        self.view.bounds.size.width,self.view.bounds.size.height*0.793765)];
    field.backgroundColor=[UIColor colorWithWhite:0.12 alpha:1];
    field.userInteractionEnabled=NO;
    [self.view addSubview:field];
    [self.view addSubview:preview];
    [preview applySettings];
    if ([NSProcessInfo.processInfo.arguments containsObject:@"--settings"])
      [preview toggleSettingsPanel];
    if ([NSProcessInfo.processInfo.arguments containsObject:@"--editor"]) {
      [preview beginLayoutEditing];
      [preview selectControlForEditing:Find(preview,@"2",YES)];
    }
    return;
  }
  exit(0);
}
- (UIInterfaceOrientationMask)supportedInterfaceOrientations { return UIInterfaceOrientationMaskLandscape; }
@end
@interface OverlayTestDelegate : UIResponder <UIApplicationDelegate>
@property(nonatomic,strong) UIWindow *window;
@end
@implementation OverlayTestDelegate
- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)options {
  (void)application; (void)options;
  self.window=[[UIWindow alloc] initWithFrame:UIScreen.mainScreen.bounds];
  self.window.rootViewController=[OverlayTestViewController new];
  [self.window makeKeyAndVisible];
  return YES;
}
@end
int main(int argc,char **argv) {
  @autoreleasepool { return UIApplicationMain(argc,argv,nil,NSStringFromClass(OverlayTestDelegate.class)); }
}
