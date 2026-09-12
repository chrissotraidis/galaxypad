// SPDX-License-Identifier: GPL-3.0-or-later
// Direct adaptation of SunPad apple/ios/SunPadGameOverlay.mm at
// fcdc1411e483a86ca80ec82e7cd53839c51ff865. Reference menu, controls and editor.
// Galaxy-specific: normalized Wii input, tilt stick and viewport pointer;
// no Sunshine timing patches, analog FLUDD trigger or GameCube camera mapping.
#import "GalaxyPadGameOverlay.h"

#import "../shared/GalaxyPadSettings.h"
#import "../shared/GalaxyPadDiagnostics.h"
#include "../shared/GalaxyPadControlSize.h"

#import <GameController/GameController.h>
#import <QuartzCore/QuartzCore.h>

#include <algorithm>
#include <cmath>

// UIControl's documented context-menu callbacks preserve UIButton's own menu
// implementation while letting the game host clear input without pausing its runtime.
@interface GalaxyPadMenuButton : UIButton
@property(nonatomic, copy) void (^visibilityChanged)(BOOL visible);
@end
@implementation GalaxyPadMenuButton
- (void)contextMenuInteraction:(UIContextMenuInteraction *)interaction
    willDisplayMenuForConfiguration:(UIContextMenuConfiguration *)configuration
    animator:(id<UIContextMenuInteractionAnimating>)animator {
    if (self.visibilityChanged) self.visibilityChanged(YES);
    [super contextMenuInteraction:interaction willDisplayMenuForConfiguration:configuration animator:animator];
}
- (void)contextMenuInteraction:(UIContextMenuInteraction *)interaction
    willEndForConfiguration:(UIContextMenuConfiguration *)configuration
    animator:(id<UIContextMenuInteractionAnimating>)animator {
    [super contextMenuInteraction:interaction willEndForConfiguration:configuration animator:animator];
    // Release the gameplay gate when dismissal begins. On iPadOS the supplied
    // animator completion is not guaranteed for every primary-action UIMenu
    // dismissal, which otherwise leaves touch and controller input blocked.
    if (self.visibilityChanged) self.visibilityChanged(NO);
}
@end

@interface GalaxyPadReferenceStickView : UIView
@property(nonatomic, copy) void (^valueChanged)(float x, float y);
@property(nonatomic, readonly) BOOL active;
- (void)applyBaseColor:(UIColor *)baseColor thumbColor:(UIColor *)thumbColor;
- (void)reset;
@end

@implementation GalaxyPadReferenceStickView {
    UIView *_thumb;
    float _valueX, _valueY;
    BOOL _active;
    UITouch *_contact;
}

- (instancetype)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        self.multipleTouchEnabled = NO;
        self.backgroundColor = [UIColor colorWithWhite:1.0 alpha:0.12];
        self.layer.borderColor = [UIColor colorWithWhite:1.0 alpha:0.34].CGColor;
        self.layer.borderWidth = 2.0;
        _thumb = [[UIView alloc] initWithFrame:CGRectZero];
        _thumb.backgroundColor = [UIColor colorWithWhite:1.0 alpha:0.32];
        _thumb.userInteractionEnabled = NO;
        [self addSubview:_thumb];
    }
    return self;
}

- (void)layoutSubviews {
    [super layoutSubviews];
    CGFloat side = std::min(self.bounds.size.width, self.bounds.size.height);
    self.layer.cornerRadius = side * 0.5;
    CGFloat thumbDiameter = side * 0.42;
    _thumb.bounds = CGRectMake(0, 0, thumbDiameter, thumbDiameter);
    _thumb.layer.cornerRadius = thumbDiameter * 0.5;
    [self updateThumbCenter];
}

- (void)updateThumbCenter {
    CGFloat half = self.bounds.size.width * 0.5;
    CGFloat maxTravel = half - _thumb.bounds.size.width * 0.5 - 3.0;
    _thumb.center = CGPointMake(half + _valueX * maxTravel,
                                half - _valueY * maxTravel);
}

- (void)setValueX:(float)x y:(float)y {
    _valueX = x;
    _valueY = y;
    [self updateThumbCenter];
}

- (BOOL)active {
    return _active;
}

- (void)applyBaseColor:(UIColor *)baseColor thumbColor:(UIColor *)thumbColor {
    self.backgroundColor = baseColor;
    _thumb.backgroundColor = thumbColor;
}

- (void)reset {
    // A held pre-reset contact must not become a new press after a menu,
    // controller handoff, or application interruption ends.
    _contact = nil;
    _active = NO;
    _valueX = _valueY = 0.0f;
    [self updateThumbCenter];
    if (self.valueChanged)
        self.valueChanged(0.0f, 0.0f);
}

- (void)handleTouch:(UITouch *)touch {
    CGPoint p = [touch locationInView:self];
    CGPoint center = CGPointMake(CGRectGetMidX(self.bounds), CGRectGetMidY(self.bounds));
    CGFloat radius = std::max<CGFloat>(1.0, std::min(self.bounds.size.width,
                                                     self.bounds.size.height) * 0.5);
    CGFloat dx = (p.x - center.x) / radius;
    CGFloat dy = (p.y - center.y) / radius;
    CGFloat length = hypot(dx, dy);
    if (length > 1.0) {
        dx /= length;
        dy /= length;
    }
    CGFloat thumbRadius = _thumb.bounds.size.width * 0.5;
    CGFloat travel = std::max<CGFloat>(0.0, radius - thumbRadius - 4.0);
    _thumb.center = CGPointMake(center.x + dx * travel, center.y + dy * travel);
    // BellPad: positive Y is up (negate UIKit's down-positive coordinate).
    _valueX = (float)dx;
    _valueY = (float)(-dy);
    _active = YES;
    if (self.valueChanged)
        self.valueChanged(_valueX, _valueY);
}

- (void)touchesBegan:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
    (void)event;
    if (_contact) return;
    _contact = touches.anyObject;
    if (_contact) [self handleTouch:_contact];
}

- (void)touchesMoved:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
    (void)event;
    if (_contact && [touches containsObject:_contact]) [self handleTouch:_contact];
}

- (void)touchesEnded:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
    (void)event;
    if (_contact && [touches containsObject:_contact]) [self reset];
}

- (void)touchesCancelled:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
    (void)event;
    if (_contact && [touches containsObject:_contact]) [self reset];
}

@end

@interface GalaxyPadGameButton : UIButton
@property(nonatomic, assign) uint32_t inputMask;
@property(nonatomic, copy) BOOL (^activateInput)(void);
@property(nonatomic) NSUInteger activationGeneration;
@end

@implementation GalaxyPadGameButton
- (BOOL)accessibilityActivate {
    return self.enabled && !self.hidden && self.activateInput ? self.activateInput() : NO;
}
@end

static CGRect GalaxyPadFrameAtNormalizedCenter(CGRect safe, CGFloat x, CGFloat y,
                                             CGFloat width, CGFloat height) {
    return CGRectMake(CGRectGetMinX(safe) + x * safe.size.width - width * 0.5,
                      CGRectGetMinY(safe) + y * safe.size.height - height * 0.5,
                      width, height);
}

// Keep the original persisted key names so layouts created while the D-pad
// grouping was experimental continue to work after grouping becomes standard.
static NSString *const GalaxyPadExperimentalDPadOriginKey = @"GalaxyPadExperimentalDPadOrigin";
static NSString *const GalaxyPadExperimentalDPadScaleKey = @"GalaxyPadExperimentalDPadScale";

static BOOL GalaxyPadUsesPhoneLayoutDefaults(UIView *view) {
    return view.traitCollection.userInterfaceIdiom == UIUserInterfaceIdiomPhone;
}

static CGFloat GalaxyPadDefaultSizeScaleForControl(UIView *view, NSString *identifier) {
    return GalaxyPadUsesPhoneLayoutDefaults(view) && [identifier isEqualToString:@"B"]
        ? 1.158457040786743
        : 1.0;
}

@interface GalaxyPadDPadEditorGroup : UIView
@end

@implementation GalaxyPadDPadEditorGroup
@end

@interface GalaxyPadPassThroughView : UIView
@end

@implementation GalaxyPadPassThroughView
- (UIView *)hitTest:(CGPoint)point withEvent:(UIEvent *)event {
    UIView *hit = [super hitTest:point withEvent:event];
    for (UIView *view = hit; view != nil && view != self; view = view.superview) {
        if ([view isKindOfClass:UIControl.class])
            return hit;
    }
    return nil;
}
@end

@interface GalaxyPadGameOverlay () <UIGestureRecognizerDelegate>
@end

@implementation GalaxyPadGameOverlay {
    UIButton *_menuButton;          // the three-dot menu
    UIButton *_pauseButton;
    UIView *_pauseOverlay;
    UIView *_pauseCard;
    UILabel *_pauseTitleLabel;
    UILabel *_pauseDetailLabel;
    UIButton *_pauseBackButton;
    GalaxyPadReferenceStickView *_moveStick;
    GalaxyPadReferenceStickView *_tiltStick;
    GalaxyPadDPadEditorGroup *_experimentalDPadGroup;
    NSMutableArray<GalaxyPadGameButton *> *_buttons;
    NSMutableArray<UIGestureRecognizer *> *_editGestures;

    UIView *_settingsPanel;
    UISlider *_opacitySlider;
    UISlider *_sizeSlider;
    UISlider *_selectedSizeSlider;
    UISwitch *_hideControlsSwitch;
    UISwitch *_editLayoutSwitch;
    UIButton *_resetLayoutButton;
    UIView *_editorBar;
    UILabel *_editorHintLabel;
    __weak UIView *_selectedControl;

    galaxypad::InputState _touchState;
    UITouch *_pointerContact;
    BOOL _touchControlsHidden;
    uint32_t _accessibilityButtons;
    NSUInteger _accessibilityEpoch;
    BOOL _editingLayout;
    BOOL _menuVisible;
    BOOL _pauseVisible;
}

- (instancetype)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        self.userInteractionEnabled = YES;
        self.multipleTouchEnabled = YES;
        _gameplayAvailable = YES;
        [self buildMenuButton];
        [self buildPauseMenu];
        [self buildTouchControls];
        [self buildSettingsPanel];
        [self applySettings];
        [self observeControllerConnection];
    }
    return self;
}

- (void)dealloc {
    [[NSNotificationCenter defaultCenter] removeObserver:self];
}

#pragma mark - Three-dot menu

- (void)buildMenuButton {
    GalaxyPadMenuButton *menuButton = [GalaxyPadMenuButton buttonWithType:UIButtonTypeCustom];
    _menuButton = menuButton;
    __weak GalaxyPadGameOverlay *weakSelf = self;
    menuButton.visibilityChanged = ^(BOOL visible) {
        GalaxyPadGameOverlay *overlay = weakSelf;
        if (!overlay) return;
        [overlay clearTouchInput];
        overlay->_menuVisible = visible;
        if (overlay.nativeUIChanged) overlay.nativeUIChanged();
    };
    UIImageSymbolConfiguration *symbol =
        [UIImageSymbolConfiguration configurationWithPointSize:19.0
                                                        weight:UIImageSymbolWeightBold];
    UIImage *ellipsis = [UIImage systemImageNamed:@"ellipsis" withConfiguration:symbol];
    [_menuButton setImage:ellipsis forState:UIControlStateNormal];
    _menuButton.accessibilityLabel = @"Menu";
    _menuButton.accessibilityIdentifier = @"galaxypad.menu";
    _menuButton.showsMenuAsPrimaryAction = YES;
    if (@available(iOS 15.0, *))
        _menuButton.changesSelectionAsPrimaryAction = NO;
    _menuButton.menu = [self buildMenu];

    UIButtonConfiguration *configuration =
        [UIButtonConfiguration plainButtonConfiguration];
    configuration.image = ellipsis;
    configuration.baseForegroundColor = UIColor.whiteColor;
    configuration.contentInsets = NSDirectionalEdgeInsetsZero;
    configuration.cornerStyle = UIButtonConfigurationCornerStyleCapsule;

    UIBackgroundConfiguration *background =
        [UIBackgroundConfiguration clearConfiguration];
    background.backgroundColor = [UIColor colorWithWhite:0.06 alpha:0.72];
    background.cornerRadius = 20.0;
    background.strokeColor = [UIColor colorWithWhite:1.0 alpha:0.30];
    background.strokeWidth = 1.0;
    configuration.background = background;

    // Keep the primary-action menu transition on one circular appearance.
    // Otherwise iPadOS can synthesize a rectangular selected state while the
    // menu is being dismissed.
    _menuButton.automaticallyUpdatesConfiguration = NO;
    _menuButton.configuration = configuration;
    _menuButton.tintColor = UIColor.whiteColor;
    _menuButton.backgroundColor = UIColor.clearColor;
    _menuButton.layer.borderWidth = 0.0;
    [self addSubview:_menuButton];
    _pauseButton = [UIButton buttonWithType:UIButtonTypeSystem];
    UIButtonConfiguration *pause = [UIButtonConfiguration filledButtonConfiguration];
    pause.title = @"Pause";
    pause.image = [UIImage systemImageNamed:@"pause.fill"];
    pause.imagePadding = 6;
    pause.baseBackgroundColor = [UIColor colorWithWhite:0.06 alpha:0.72];
    pause.baseForegroundColor = UIColor.whiteColor;
    _pauseButton.configuration = pause;
    _pauseButton.accessibilityIdentifier = @"galaxypad.pause";
    _pauseButton.accessibilityLabel = @"Pause game";
    [_pauseButton addTarget:self action:@selector(presentPause) forControlEvents:UIControlEventTouchUpInside];
    [self addSubview:_pauseButton];
}

- (void)buildPauseMenu {
    _pauseOverlay = [[UIView alloc] initWithFrame:self.bounds];
    _pauseOverlay.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    _pauseOverlay.backgroundColor = [UIColor colorWithWhite:0.0 alpha:0.46];
    _pauseOverlay.accessibilityViewIsModal = YES;
    _pauseOverlay.hidden = YES;

    _pauseCard = [[UIView alloc] initWithFrame:CGRectZero];
    _pauseCard.backgroundColor = [UIColor colorWithWhite:0.06 alpha:0.96];
    _pauseCard.layer.cornerRadius = 18.0;
    _pauseCard.layer.borderWidth = 1.0;
    _pauseCard.layer.borderColor = [UIColor colorWithWhite:1.0 alpha:0.24].CGColor;
    [_pauseOverlay addSubview:_pauseCard];

    _pauseTitleLabel = [[UILabel alloc] initWithFrame:CGRectZero];
    _pauseTitleLabel.text = @"Pause Menu";
    _pauseTitleLabel.textColor = UIColor.whiteColor;
    _pauseTitleLabel.font = [UIFont preferredFontForTextStyle:UIFontTextStyleTitle2];
    _pauseTitleLabel.textAlignment = NSTextAlignmentCenter;
    [_pauseCard addSubview:_pauseTitleLabel];

    _pauseDetailLabel = [[UILabel alloc] initWithFrame:CGRectZero];
    _pauseDetailLabel.text = @"Press controller Menu / Options again, or Back to Game, to resume.\nHold Start + for Galaxy’s original Wii pause screen, including Return to Observatory.";
    _pauseDetailLabel.textColor = [UIColor colorWithWhite:1.0 alpha:0.78];
    _pauseDetailLabel.font = [UIFont preferredFontForTextStyle:UIFontTextStyleBody];
    _pauseDetailLabel.numberOfLines = 0;
    _pauseDetailLabel.textAlignment = NSTextAlignmentCenter;
    [_pauseCard addSubview:_pauseDetailLabel];

    _pauseBackButton = [UIButton buttonWithType:UIButtonTypeSystem];
    UIButtonConfiguration *back = [UIButtonConfiguration filledButtonConfiguration];
    back.title = @"Back to Game";
    back.image = [UIImage systemImageNamed:@"play.fill"];
    back.imagePadding = 8.0;
    back.baseBackgroundColor = [UIColor colorWithRed:0.20 green:0.55 blue:0.98 alpha:1.0];
    back.baseForegroundColor = UIColor.whiteColor;
    _pauseBackButton.configuration = back;
    _pauseBackButton.accessibilityIdentifier = @"galaxypad.pause.back";
    _pauseBackButton.accessibilityLabel = @"Back to Game";
    [_pauseBackButton addTarget:self action:@selector(dismissPauseMenu) forControlEvents:UIControlEventTouchUpInside];
    [_pauseCard addSubview:_pauseBackButton];
    [self addSubview:_pauseOverlay];
}

- (void)presentPause {
    if (!self.gameplayAvailable || _pauseVisible || _menuVisible || _editingLayout || !_settingsPanel.hidden) return;
    [self reset];
    _pauseVisible = YES;
    _pauseOverlay.hidden = NO;
    [self setNeedsLayout];
    [self bringSubviewToFront:_pauseOverlay];
    if (self.nativeUIChanged) self.nativeUIChanged();
}

- (void)presentNativePause {
    [self presentPause];
}
- (BOOL)nativePauseVisible { return _pauseVisible; }
- (void)toggleNativePause {
    if (_pauseVisible) [self dismissPauseMenu];
    else [self presentPause];
}

- (void)dismissPauseMenu {
    if (!_pauseVisible) return;
    _pauseVisible = NO;
    _pauseOverlay.hidden = YES;
    [self clearTouchInput];
    if (self.nativeUIChanged) self.nativeUIChanged();
}

- (UIMenu *)buildMenu {
    __weak GalaxyPadGameOverlay *weakSelf = self;
    GalaxyPadSettings *settings = [GalaxyPadSettings sharedSettings];

    UIMenu *renderMenu = [UIMenu menuWithTitle:@"Render Resolution (Next Launch)" children:@[
        [self renderAction:@"1× (Native, Recommended)" scale:1],
        [self renderAction:@"2× (Higher GPU Cost)" scale:2],
        [self renderAction:@"3×" scale:3],
        [self renderAction:@"4×" scale:4],
    ]];

    UIMenu *aspectMenu = [UIMenu menuWithTitle:@"Aspect Ratio" children:@[
        [self aspectRatioAction:@"4:3 (Restart Required)"
                           mode:GalaxyPadAspectRatioOriginal],
        [self aspectRatioAction:@"Native 16:9 (Restart Required)"
                           mode:GalaxyPadAspectRatioWidescreen],
        [self aspectRatioAction:@"Fill Screen (Experimental, Restart Required)"
                           mode:GalaxyPadAspectRatioFillScreen],
    ]];

    UIMenu *displayMenu = [UIMenu menuWithTitle:@"Display"
                                          image:[UIImage systemImageNamed:@"display"]
                                     identifier:nil
                                        options:0
                                       children:@[renderMenu, aspectMenu]];

    UIMenu *dataMenu = [UIMenu menuWithTitle:@"Game Data & Saves"
                                       image:[UIImage systemImageNamed:@"internaldrive"]
                                  identifier:nil
                                     options:0
                                    children:@[
        [UIAction actionWithTitle:@"Import or Reimport Game Data"
                            image:[UIImage systemImageNamed:@"arrow.triangle.2.circlepath"]
                       identifier:nil handler:^(__kindof UIAction *action) {
            (void)action;
            [weakSelf.delegate gameOverlayRequestsGameDataChange:weakSelf];
        }],
        [UIAction actionWithTitle:@"Import from GalaxyPad Folder"
                            image:[UIImage systemImageNamed:@"folder"]
                       identifier:nil handler:^(__kindof UIAction *action) {
            (void)action;
            [weakSelf.delegate gameOverlayRequestsGameDataFolderImport:weakSelf];
        }],
        [UIAction actionWithTitle:@"Remove Stored Game Data"
                            image:[UIImage systemImageNamed:@"trash"]
                       identifier:nil handler:^(__kindof UIAction *action) {
            (void)action;
            [weakSelf confirmGameDataRemoval];
        }],
    ]];

    UIAction *fpsAction = [UIAction actionWithTitle:@"Show FPS Counter"
                                              image:[UIImage systemImageNamed:@"speedometer"]
                                         identifier:nil
                                            handler:^(__kindof UIAction *action) {
        (void)action;
        GalaxyPadSettings *currentSettings = [GalaxyPadSettings sharedSettings];
        currentSettings.showFPSCounter = !currentSettings.showFPSCounter;
        [currentSettings synchronize];
        [weakSelf refreshMenuButton];
    }];
    fpsAction.state = settings.showFPSCounter ? UIMenuElementStateOn : UIMenuElementStateOff;

    // FPS is a display diagnostic, not a primary gameplay command. Do not copy
    // SunPad's experiment section when Galaxy has no delivered actions in it.
    displayMenu = [displayMenu menuByReplacingChildren:@[renderMenu, aspectMenu, fpsAction]];
    UIAction *loggingAction = [UIAction actionWithTitle:@"Performance Logging (Next Launch)"
      image:[UIImage systemImageNamed:@"waveform.path.ecg"] identifier:@"galaxypad.menu.performance-log"
      handler:^(__kindof UIAction *action) {
        (void)action;
        NSUserDefaults *defaults = NSUserDefaults.standardUserDefaults;
        BOOL enabled = [defaults boolForKey:@"GalaxyPadLogFrameRateWindows"];
        [defaults setBool:!enabled forKey:@"GalaxyPadLogFrameRateWindows"];
        [weakSelf refreshMenuButton];
      }];
    loggingAction.state = [NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadLogFrameRateWindows"]
      ? UIMenuElementStateOn : UIMenuElementStateOff;
    displayMenu = [displayMenu menuByReplacingChildren:@[renderMenu, aspectMenu, fpsAction, loggingAction]];

    UIAction *reportProblemAction =
        [UIAction actionWithTitle:@"Report a Problem…"
                            image:[UIImage systemImageNamed:@"exclamationmark.bubble"]
                       identifier:nil handler:^(__kindof UIAction *action) {
        (void)action;
        [weakSelf reportProblem];
    }];

    UIAction *tiltAction = [UIAction actionWithTitle:@"Show Tilt Stick (Ball / Ray)"
        image:[UIImage systemImageNamed:@"move.3d"] identifier:nil handler:^(__kindof UIAction *action) {
        (void)action;
        [weakSelf toggleTiltStick];
    }];
    tiltAction.state = [NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadShowTiltStick"]
        ? UIMenuElementStateOn : UIMenuElementStateOff;
    UIAction *auxiliaryAction = [UIAction actionWithTitle:@"Show Extra Wii Buttons (1 / 2 / −)"
        image:[UIImage systemImageNamed:@"ellipsis.circle"] identifier:nil handler:^(__kindof UIAction *action) {
        (void)action;
        [weakSelf toggleAuxiliaryButtons];
    }];
    auxiliaryAction.state = [NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadShowAuxiliaryButtons"]
        ? UIMenuElementStateOn : UIMenuElementStateOff;
    UIAction *touchAction = [UIAction actionWithTitle:@"Touch Controls"
        image:[UIImage systemImageNamed:@"hand.tap"] identifier:nil handler:^(__kindof UIAction *action) {
        (void)action;
        [weakSelf toggleTouchControls];
    }];
    touchAction.state = [NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadTouchControlsDisabled"]
        ? UIMenuElementStateOff : UIMenuElementStateOn;
    NSMutableArray<UIMenuElement *> *tiltOptions = [NSMutableArray array];
    for (NSNumber *scale in @[@0.5, @1.0, @1.5]) {
        UIAction *response = [UIAction actionWithTitle:[NSString stringWithFormat:@"Sensitivity %.1f×", scale.doubleValue]
          image:nil identifier:nil handler:^(__kindof UIAction *action) {
            (void)action;
            [weakSelf setTouchTiltSensitivity:scale.doubleValue];
          }];
        response.state = fabs(settings.touchTiltSensitivity-scale.doubleValue)<0.001
          ? UIMenuElementStateOn : UIMenuElementStateOff;
        [tiltOptions addObject:response];
    }
    UIAction *invertTilt = [UIAction actionWithTitle:@"Invert Vertical Axis" image:nil identifier:nil
      handler:^(__kindof UIAction *action) { (void)action; [weakSelf toggleTouchTiltInversion]; }];
    invertTilt.state = settings.touchTiltInvertY ? UIMenuElementStateOn : UIMenuElementStateOff;
    [tiltOptions addObject:invertTilt];
    [tiltOptions addObject:[UIAction actionWithTitle:@"Recenter" image:nil identifier:nil
      handler:^(__kindof UIAction *action) { (void)action; [weakSelf clearTouchInput]; }]];
    UIMenu *tiltResponse = [UIMenu menuWithTitle:@"Touch Tilt Stick" children:tiltOptions];
    UIMenu *controlsMenu = [UIMenu menuWithTitle:@"Controls"
                                           image:[UIImage systemImageNamed:@"gamecontroller"]
                                      identifier:nil
                                         options:0
                                        children:@[
        [UIAction actionWithTitle:@"Controller Button Mapping…"
                            image:[UIImage systemImageNamed:@"gamecontroller"]
                       identifier:nil handler:^(__kindof UIAction *action) {
            (void)action;
            [weakSelf.delegate gameOverlayRequestsControllerMapping:weakSelf];
        }],
        [UIAction actionWithTitle:@"Touch Control Settings…"
                            image:[UIImage systemImageNamed:@"hand.draw"]
                       identifier:nil handler:^(__kindof UIAction *action) {
            (void)action;
            [weakSelf toggleSettingsPanel];
        }],
        [UIAction actionWithTitle:@"Touch Control Guide…"
                            image:[UIImage systemImageNamed:@"questionmark.circle"]
                       identifier:@"galaxypad.menu.touch-guide" handler:^(__kindof UIAction *action) {
            (void)action;
            [weakSelf.window.rootViewController presentViewController:[weakSelf touchControlGuide]
                animated:YES completion:nil];
        }],
        touchAction, tiltAction, tiltResponse, auxiliaryAction,
    ]];

    // These host adapters are not delivered yet. Do not present inert actions
    // as working, or accidentally route Galaxy reports/data to SunPad.
    for (NSUInteger i=0;i<dataMenu.children.count;++i) {
        UIAction *action=(UIAction *)dataMenu.children[i];
        BOOL available=(i==0 && [self.delegate respondsToSelector:@selector(gameOverlayRequestsGameDataChange:)]) ||
            (i==1 && [self.delegate respondsToSelector:@selector(gameOverlayRequestsGameDataFolderImport:)]) ||
            (i==2 && [self.delegate respondsToSelector:@selector(gameOverlayRequestsGameDataRemoval:)]);
        action.attributes = (available ? 0 : UIMenuElementAttributesDisabled) |
            (i==2 ? UIMenuElementAttributesDestructive : 0);
    }
    UIAction *dataStatus = [UIAction actionWithTitle:@"Game Data & Save Status…"
      image:[UIImage systemImageNamed:@"info.circle"] identifier:@"galaxypad.menu.data-status"
      handler:^(__kindof UIAction *action) {
        (void)action;
        [weakSelf.delegate gameOverlayRequestsGameDataStatus:weakSelf];
      }];
    dataStatus.attributes = [self.delegate respondsToSelector:@selector(gameOverlayRequestsGameDataStatus:)]
      ? 0 : UIMenuElementAttributesDisabled;
    NSMutableArray<UIMenuElement *> *dataItems = [dataMenu.children mutableCopy];
    [dataItems insertObject:dataStatus atIndex:0];
    dataMenu = [dataMenu menuByReplacingChildren:dataItems];
    ((UIAction *)controlsMenu.children.firstObject).attributes =
      [self.delegate respondsToSelector:@selector(gameOverlayRequestsControllerMapping:)]
        ? 0 : UIMenuElementAttributesDisabled;
    reportProblemAction.attributes = self.delegate ? 0 : UIMenuElementAttributesDisabled;
    UIAction *shareLog=[UIAction actionWithTitle:@"Share Diagnostic Log"
      image:[UIImage systemImageNamed:@"square.and.arrow.up"] identifier:nil
      handler:^(__kindof UIAction *action) {
        (void)action;
        [weakSelf.delegate gameOverlayRequestsDiagnosticLog:weakSelf];
      }];
    shareLog.attributes=[self.delegate respondsToSelector:@selector(gameOverlayRequestsDiagnosticLog:)]
      ? 0 : UIMenuElementAttributesDisabled;
    for (UIAction *action in aspectMenu.children) action.attributes = UIMenuElementAttributesDisabled;
    UIAction *about=[UIAction actionWithTitle:@"About GalaxyPad"
      image:[UIImage systemImageNamed:@"info.circle"] identifier:@"galaxypad.menu.about"
      handler:^(__kindof UIAction *action) {
        (void)action;
        if ([weakSelf.delegate respondsToSelector:@selector(gameOverlayRequestsAbout:)])
          [weakSelf.delegate gameOverlayRequestsAbout:weakSelf];
      }];
    about.attributes=[self.delegate respondsToSelector:@selector(gameOverlayRequestsAbout:)]
      ? 0 : UIMenuElementAttributesDisabled;

    UIAction *stopAction = [UIAction actionWithTitle:@"Stop Game…"
        image:[UIImage systemImageNamed:@"stop.circle"] identifier:@"galaxypad.menu.stop"
        handler:^(__kindof UIAction *action) {
            (void)action;
            [weakSelf confirmStop];
        }];
    stopAction.attributes = UIMenuElementAttributesDestructive |
        (self.stopRequested ? 0 : UIMenuElementAttributesDisabled);
    NSMutableArray<UIMenuElement *> *menuItems = [@[
        displayMenu,
        controlsMenu,
        [self audioMenu],
        dataMenu,
        shareLog,
        reportProblemAction,
        about,
        stopAction,
    ] mutableCopy];
#if TARGET_OS_SIMULATOR
    if ([NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevCheckpoints"] &&
        [self.delegate respondsToSelector:@selector(gameOverlayRequestsDevelopmentCheckpoint:)]) {
      [menuItems insertObject:[UIAction actionWithTitle:@"Save Development Checkpoint"
        image:[UIImage systemImageNamed:@"square.and.arrow.down"] identifier:nil
        handler:^(__kindof UIAction *action) {
          (void)action;
          [weakSelf.delegate gameOverlayRequestsDevelopmentCheckpoint:weakSelf];
        }] atIndex:menuItems.count - 1];
      if ([self.delegate respondsToSelector:@selector(gameOverlayRequestsDevelopmentCheckpointRestore:)]) {
        [menuItems insertObject:[UIAction actionWithTitle:@"Restore Last Development Checkpoint"
          image:[UIImage systemImageNamed:@"arrow.counterclockwise"] identifier:nil
          handler:^(__kindof UIAction *action) {
            (void)action;
            [weakSelf.delegate gameOverlayRequestsDevelopmentCheckpointRestore:weakSelf];
          }] atIndex:menuItems.count - 1];
      }
    }
#endif
    return [UIMenu menuWithTitle:@"GalaxyPad" children:menuItems];
}

- (void)reportProblem {
    [self.delegate gameOverlayRequestsProblemReport:self];
}



- (UIAction *)aspectRatioAction:(NSString *)title mode:(GalaxyPadAspectRatioMode)mode {
    __weak GalaxyPadGameOverlay *weakSelf = self;
    UIAction *aspectAction = [UIAction actionWithTitle:title
                                                 image:nil
                                            identifier:nil
                                               handler:^(__kindof UIAction *action) {
        (void)action;
        [GalaxyPadSettings sharedSettings].aspectRatioMode = mode;
        [[GalaxyPadSettings sharedSettings] synchronize];
        [[[UISelectionFeedbackGenerator alloc] init] selectionChanged];
        [weakSelf refreshMenuButton];

        NSString *message = mode == GalaxyPadAspectRatioOriginal ?
            @"4:3 is selected. Restart the game to apply it." :
            @"The selected display aspect will apply on the next game launch.";
        UIAlertController *alert =
            [UIAlertController alertControllerWithTitle:@"Restart Required"
                                                message:message
                                         preferredStyle:UIAlertControllerStyleAlert];
        [alert addAction:[UIAlertAction actionWithTitle:@"OK"
                                                  style:UIAlertActionStyleDefault
                                                handler:nil]];
        [weakSelf.window.rootViewController presentViewController:alert
                                                         animated:YES
                                                       completion:nil];
    }];
    aspectAction.state = [GalaxyPadSettings sharedSettings].aspectRatioMode == mode ?
        UIMenuElementStateOn : UIMenuElementStateOff;
    return aspectAction;
}

- (UIAction *)renderAction:(NSString *)title scale:(NSInteger)scale {
    __weak GalaxyPadGameOverlay *weakSelf = self;
    UIAction *renderAction = [UIAction actionWithTitle:title
                                                 image:nil
                                            identifier:nil
                                               handler:^(__kindof UIAction *action) {
        (void)action;
        [GalaxyPadSettings sharedSettings].renderScale = scale;
        [[GalaxyPadSettings sharedSettings] synchronize];
        [[[UISelectionFeedbackGenerator alloc] init] selectionChanged];
        [weakSelf refreshMenuButton];
    }];
    renderAction.state = [GalaxyPadSettings sharedSettings].renderScale == scale ?
        UIMenuElementStateOn : UIMenuElementStateOff;
    return renderAction;
}

@synthesize stopRequested = _stopRequested;
- (void)setStopRequested:(void (^)(void))stopRequested {
    _stopRequested = [stopRequested copy];
    [self refreshMenuButton];
}

- (void)refreshMenuButton {
    _menuButton.menu = [self buildMenu];
}

- (void)confirmGameDataRemoval {
    __weak GalaxyPadGameOverlay *weakSelf = self;
    UIAlertController *alert =
        [UIAlertController alertControllerWithTitle:@"Remove Stored Game Data?"
                                            message:@"The game will stop, then its installed image and extracted files will be removed. Saves and control settings are not affected. Any prior recovery copies and original images in Files are retained."
                                     preferredStyle:UIAlertControllerStyleAlert];
    [alert addAction:[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil]];
    [alert addAction:[UIAlertAction actionWithTitle:@"Remove" style:UIAlertActionStyleDestructive
                                            handler:^(UIAlertAction *action) {
        (void)action;
        [weakSelf.delegate gameOverlayRequestsGameDataRemoval:weakSelf];
    }]];
    [self.window.rootViewController presentViewController:alert animated:YES completion:nil];
}

#pragma mark - Touch controls

- (void)buildTouchControls {
    _buttons = [NSMutableArray array];
    _editGestures = [NSMutableArray array];

    _moveStick = [self makeStick];
    _tiltStick = [self makeStick];
    _moveStick.accessibilityLabel = @"Move stick";
    _moveStick.accessibilityIdentifier = @"move";
    _tiltStick.accessibilityLabel = @"Tilt stick";
    _tiltStick.accessibilityIdentifier = @"tilt";
    [_moveStick applyBaseColor:[UIColor colorWithWhite:0.13 alpha:0.86]
                    thumbColor:[UIColor colorWithWhite:0.58 alpha:0.94]];
    [_tiltStick applyBaseColor:[UIColor colorWithRed:0.91 green:0.66 blue:0.08 alpha:0.90]
                 thumbColor:[UIColor colorWithRed:1.00 green:0.84 blue:0.25 alpha:0.98]];
    [self addSubview:_moveStick];
    [self addSubview:_tiltStick];
    [self addEditGesturesToControl:_moveStick];
    [self addEditGesturesToControl:_tiltStick];

    [self addButton:@"A" mask:galaxypad::A];
    [self addButton:@"B" mask:galaxypad::B];
    [self addButton:@"X" mask:galaxypad::Spin];
    [self addButton:@"Y" mask:galaxypad::C];
    [self addButton:@"Z" mask:galaxypad::Z];
    [self addButton:@"Start +" mask:galaxypad::Plus];
    [self addButton:@"1" mask:galaxypad::One];
    [self addButton:@"2" mask:galaxypad::Two];
    [self addButton:@"−" mask:galaxypad::Minus];
    // D-pad
    [self addButton:@"▲" mask:galaxypad::Up];
    [self addButton:@"▼" mask:galaxypad::Down];
    [self addButton:@"◀" mask:galaxypad::Left];
    [self addButton:@"▶" mask:galaxypad::Right];

    _experimentalDPadGroup = [GalaxyPadDPadEditorGroup new];
    _experimentalDPadGroup.accessibilityLabel = @"D-pad";
    _experimentalDPadGroup.accessibilityIdentifier = @"ExperimentalDPad";
    _experimentalDPadGroup.backgroundColor = UIColor.clearColor;
    _experimentalDPadGroup.layer.cornerRadius = 14.0;
    _experimentalDPadGroup.hidden = YES;
    _experimentalDPadGroup.userInteractionEnabled = NO;
    [self addSubview:_experimentalDPadGroup];
    [self addEditGesturesToControl:_experimentalDPadGroup];
}

- (GalaxyPadReferenceStickView *)makeStick {
    GalaxyPadReferenceStickView *stick = [[GalaxyPadReferenceStickView alloc] initWithFrame:CGRectMake(0, 0, 128, 128)];
    __weak GalaxyPadGameOverlay *weakSelf = self;
    __weak GalaxyPadReferenceStickView *weakStick = stick;
    stick.valueChanged = ^(float x, float y) {
        GalaxyPadReferenceStickView *strongStick = weakStick;
        if (strongStick != nil)
            [weakSelf stickChanged:strongStick x:x y:y];
    };
    return stick;
}

- (void)addButton:(NSString *)label mask:(uint32_t)mask {
    GalaxyPadGameButton *button = [GalaxyPadGameButton buttonWithType:UIButtonTypeSystem];
    [button setTitle:label forState:UIControlStateNormal];
    UIColor *fill = [UIColor colorWithWhite:0.22 alpha:0.88];
    UIColor *titleColor = UIColor.whiteColor;
    switch (mask) {
    case galaxypad::A:
        fill = [UIColor colorWithRed:0.08 green:0.56 blue:0.29 alpha:0.92];
        break;
    case galaxypad::B:
        fill = [UIColor colorWithRed:0.78 green:0.10 blue:0.13 alpha:0.92];
        break;
    case galaxypad::Spin:
    case galaxypad::C:
        fill = [UIColor colorWithWhite:0.72 alpha:0.92];
        titleColor = [UIColor colorWithWhite:0.12 alpha:1.0];
        break;
    case galaxypad::Z:
        fill = [UIColor colorWithRed:0.38 green:0.18 blue:0.58 alpha:0.94];
        break;
    case galaxypad::Plus:
        fill = [UIColor colorWithWhite:0.28 alpha:0.92];
        break;
    default:
        break;
    }
    [button setTitleColor:titleColor forState:UIControlStateNormal];
    button.titleLabel.font = [UIFont systemFontOfSize:18.0 weight:UIFontWeightBold];
    button.backgroundColor = fill;
    button.layer.cornerRadius = 28.0;
    button.layer.borderWidth = 2.0;
    button.layer.borderColor = [UIColor colorWithWhite:1.0 alpha:0.36].CGColor;
    button.accessibilityLabel = label;
    // SunPad's face is letter-only. Describe mappings to assistive technology,
    // never as extra copy crammed into the touch target.
    NSString *role = nil;
    switch (mask) {
    case galaxypad::A: role = @"Jump / Use"; break;
    case galaxypad::B: role = @"Shoot"; break;
    case galaxypad::Z: role = @"Crouch"; break;
    case galaxypad::C: role = @"Camera"; break;
    case galaxypad::Spin: role = @"Spin"; break;
    case galaxypad::Plus: role = @"Hold for in-game pause menu"; break;
    default: break;
    }
    if (role) {
        button.accessibilityLabel = [NSString stringWithFormat:@"%@, %@",label,role];
    }
    button.inputMask = mask;
    __weak GalaxyPadGameOverlay *activationOwner = self;
    __weak GalaxyPadGameButton *activationButton = button;
    button.activateInput = ^BOOL {
        return [activationOwner activateGameButton:activationButton];
    };
    button.accessibilityIdentifier = [self identifierForMask:mask];
    [button addTarget:self action:@selector(buttonDown:)
     forControlEvents:UIControlEventTouchDown];
    [button addTarget:self action:@selector(buttonUp:)
     forControlEvents:UIControlEventTouchUpInside | UIControlEventTouchUpOutside |
                            UIControlEventTouchCancel];
    [_buttons addObject:button];
    [self addSubview:button];
    [self addEditGesturesToControl:button];


}

- (void)stickChanged:(GalaxyPadReferenceStickView *)stick x:(float)x y:(float)y {
    if (_editingLayout || !_settingsPanel.hidden) return;
    if (stick == _moveStick) {
        _touchState.moveX = x; _touchState.moveY = y;
    } else {
        GalaxyPadSettings *settings = GalaxyPadSettings.sharedSettings;
        const float sensitivity = settings.touchTiltSensitivity;
        _touchState.tiltX = std::isfinite(x) ? std::clamp(x*sensitivity, -1.f, 1.f) : 0;
        _touchState.tiltY = std::isfinite(y) ? std::clamp(y*sensitivity, -1.f, 1.f) : 0;
        if (settings.touchTiltInvertY) _touchState.tiltY = -_touchState.tiltY;
    }
    [self publishInput];
}

- (void)buttonDown:(GalaxyPadGameButton *)button {
    if (_editingLayout || !_settingsPanel.hidden) return;
    _touchState.buttons |= button.inputMask;
    button.transform = CGAffineTransformMakeScale(0.92, 0.92);
    [self publishInput];
}

- (BOOL)activateGameButton:(GalaxyPadGameButton *)button {
    if (!button || !_gameplayAvailable || self.blocksGameplay || !self.window) return NO;
    const uint32_t mask = button.inputMask;
    const NSUInteger generation = ++button.activationGeneration;
    const NSUInteger epoch = _accessibilityEpoch;
    _accessibilityButtons |= mask;
    [self publishInput];
    __weak GalaxyPadGameOverlay *weakSelf = self;
    __weak GalaxyPadGameButton *weakButton = button;
    // Galaxy requires a held pause button; leave margin for emulation slowdown.
    const double duration = (mask & (galaxypad::Plus | galaxypad::Minus)) ? 0.75 : 0.15;
    [NSTimer scheduledTimerWithTimeInterval:duration repeats:NO block:^(NSTimer *timer) {
        (void)timer;
        GalaxyPadGameOverlay *owner = weakSelf;
        if (!owner || !weakButton || epoch != owner->_accessibilityEpoch ||
            generation != weakButton.activationGeneration) return;
        owner->_accessibilityButtons &= ~mask;
        [owner publishInput]; // physical contact owns a separate mask
    }];
    return YES;
}

- (void)buttonUp:(GalaxyPadGameButton *)button {
    _touchState.buttons &= ~button.inputMask;
    button.transform = CGAffineTransformIdentity;
    [self publishInput];
}


- (void)clearTouchInput {
    ++_accessibilityEpoch;
    _accessibilityButtons = 0;
    for (GalaxyPadGameButton *button in _buttons)
        button.transform = CGAffineTransformIdentity;
    [_moveStick reset];
    [_tiltStick reset];
    _pointerContact = nil;
    _touchState = {};
    if (self.inputChanged) self.inputChanged(_touchState);
}

#pragma mark - Layout

- (void)layoutSubviews {
    [super layoutSubviews];
    CGRect safe = self.bounds;
    if (@available(iOS 11.0, *)) {
        safe = UIEdgeInsetsInsetRect(safe, self.safeAreaInsets);
    }
    // BellPad's landscape layout math: scale to a reference 800x380 area on
    // phones and a fixed larger set on iPads (width >= 1000).
    BOOL pad = self.traitCollection.userInterfaceIdiom == UIUserInterfaceIdiomPad &&
               safe.size.width >= 1000.0;
    BOOL phone = GalaxyPadUsesPhoneLayoutDefaults(self);
    CGFloat baseScale = pad ? 1.0
                            : std::min<CGFloat>(1.0, std::min(safe.size.width / 800.0,
                                                              safe.size.height / 380.0));
    CGFloat controlScale = [GalaxyPadSettings sharedSettings].controlSizeScale;
    CGFloat scale = baseScale * controlScale;
    CGFloat margin = pad ? 34.0 : std::max<CGFloat>(8.0, 18.0 * baseScale);
    CGFloat stick = (pad ? 172.0 : 126.0 * baseScale) * controlScale;
    CGFloat small = (pad ? 62.0 : std::max<CGFloat>(44.0, 46.0 * baseScale)) * controlScale;
    CGFloat medium = (pad ? 76.0 : 58.0 * baseScale) * controlScale;
    CGFloat large = (pad ? 104.0 : 78.0 * baseScale) * controlScale;
    // Use the reviewed SunPad iPad geometry. User layout edits still take precedence.
    auto padFrame = [&](CGFloat x, CGFloat bottom, CGFloat w, CGFloat h) {
        return CGRectMake(CGRectGetMinX(safe) + x - w * 0.5,
                          CGRectGetMaxY(safe) - bottom - h * 0.5, w, h);
    };
    CGFloat right = CGRectGetWidth(safe);

    CGRect moveDefault = phone ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.1234722222, 0.7803490991, stick, stick) : pad ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.1310395315, 0.7905894519, stick, stick) :
        CGRectMake(CGRectGetMinX(safe) + margin,
                   CGRectGetMaxY(safe) - stick - margin, stick, stick);
    [self placeControl:_moveStick
          defaultFrame:moveDefault
            identifier:@"move"];
    CGFloat camera = (pad ? 84.0 : 86.0 * baseScale) * controlScale;
    CGRect cameraDefault = phone ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.9233055556, 0.8130067568, camera, camera) : pad ?
        padFrame(right * 0.5, 320, camera, camera) :
        CGRectMake(CGRectGetMaxX(safe) - margin - camera,
                   CGRectGetMaxY(safe) - margin - camera, camera, camera);
    [self placeControl:_tiltStick
          defaultFrame:cameraDefault
            identifier:@"tilt"];

    GalaxyPadGameButton *a = [self buttonWithMask:galaxypad::A];
    GalaxyPadGameButton *b = [self buttonWithMask:galaxypad::B];
    GalaxyPadGameButton *x = [self buttonWithMask:galaxypad::Spin];
    GalaxyPadGameButton *y = [self buttonWithMask:galaxypad::C];
    // A was not present in the captured iPhone preferences because it was not
    // moved. Keep the original phone fallback so the sparse captured layout
    // reconstructs the exact arrangement the user made.
    CGRect aDefault = pad ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.8916544656, 0.7409513961, large, large) :
        CGRectMake(CGRectGetMaxX(safe) - margin - large,
                   CGRectGetMaxY(safe) - margin - camera - large - 18.0 * scale,
                   large, large);
    [self placeControl:a
          defaultFrame:aDefault
            identifier:@"A"];
    CGRect bDefault = phone ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.83, 0.6898648649, medium, medium) : pad ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.8360175695, 0.8092037229, medium, medium) :
        CGRectMake(CGRectGetMinX(a.frame) - medium - 12.0 * scale,
                   CGRectGetMidY(a.frame) + 8.0, medium, medium);
    // Keep the familiar diagonal cluster without overlapping rectangular hit areas.
    if (pad) bDefault.origin.x = MIN(bDefault.origin.x, CGRectGetMinX(aDefault) - medium - 8.0);
    [self placeControl:b
          defaultFrame:bDefault
            identifier:@"B"];
    CGFloat spinSize = small;
    CGRect xDefault = phone ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.9034166667, 0.4258445946, small, small) : pad ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.9593704246, 0.7156153051, spinSize, spinSize) :
        CGRectMake(CGRectGetMidX(a.frame) - small * 0.5,
                   CGRectGetMinY(a.frame) - small - 10.0 * scale, small, small);
    [self placeControl:x
          defaultFrame:xDefault
            identifier:@"Spin"];
    CGRect yDefault = phone ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.837, 0.5268581081, small, small) : pad ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.9542459736, 0.7869700103, small, small) :
        CGRectMake(CGRectGetMinX(a.frame) - small - 8.0 * scale,
                   CGRectGetMinY(a.frame) - small + 8.0, small, small);
    [self placeControl:y
          defaultFrame:yDefault
            identifier:@"C"];

    // Auxiliary Wii keys are not shoulder actions. Keep their hit areas usable
    // without giving pause/settings the visual weight of jump or spin.
    CGFloat shoulderWidth = small;
    CGFloat shoulderY = CGRectGetMinY(safe) + (pad ? 92.0 : 68.0 * baseScale);
    CGRect lDefault = phone ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.36, 0.88,
                                      shoulderWidth, small) : pad ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.1281112738, 0.6633919338, shoulderWidth, small) :
        CGRectMake(CGRectGetMinX(safe) + margin, shoulderY, shoulderWidth, small);
    [self placeControl:[self buttonWithMask:galaxypad::One]
          defaultFrame:lDefault
            identifier:@"1"];
    // Pair 1/2 horizontally; neither belongs in the top HUD or action cluster.
    CGRect twoDefault = pad ? CGRectOffset(lDefault, small + 12.0, 0)
                            : CGRectOffset(lDefault,small+12.0*scale,0);
    [self placeControl:[self buttonWithMask:galaxypad::Two]
          defaultFrame:twoDefault
            identifier:@"2"];
    CGFloat rightShoulderWidth = small;
    GalaxyPadGameButton *rightShoulder = [self buttonWithMask:galaxypad::Minus];
    CGRect rDefault = phone ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.56, 0.88,
                                      rightShoulderWidth, small) : pad ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.8960468521, 0.6478800414, rightShoulderWidth, small) :
        CGRectMake(CGRectGetMaxX(safe) - margin - rightShoulderWidth, shoulderY,
                   rightShoulderWidth, small);
    [self placeControl:rightShoulder
          defaultFrame:rDefault
            identifier:@"−"];
    CGRect zDefault = phone ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.9712500000, 0.4350788288, small, small) : pad ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.8275988287, 0.7213029990, small, small) :
        CGRectMake(CGRectGetMaxX(safe) - margin - shoulderWidth - small - 12.0 * scale,
                   shoulderY, small, small);
    [self placeControl:[self buttonWithMask:galaxypad::Z]
          defaultFrame:zDefault
            identifier:@"Z"];
    CGFloat startWidth = (pad ? 116.0 : 92.0 * baseScale) * controlScale;
    // Keep pause inward of the phone action cluster, not over central Mario,
    // title prompts or dialogue. Saved editor origins still take precedence.
    CGRect startDefault = phone ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.72, 0.62, startWidth, small) : pad ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.8967789165, 0.5780765253, startWidth, small) :
        CGRectMake(CGRectGetMidX(safe) - startWidth * 0.5,
                   CGRectGetMinY(safe) + margin, startWidth, small);
    [self placeControl:[self buttonWithMask:galaxypad::Plus]
          defaultFrame:startDefault
            identifier:@"Plus"];

    CGFloat d = 44.0 * controlScale;
    CGFloat dx = CGRectGetMaxX(_moveStick.frame) + (pad ? 34.0 : 18.0 * scale);
    CGRect defaultGroupFrame = phone ?
        // Leave separation from the movement stick with full 44pt D-pad cells.
        // Saved editor origins continue to override this default.
        GalaxyPadFrameAtNormalizedCenter(safe, 0.0812777778, 0.43,
                                      3.0 * d, 3.0 * d) : pad ?
        GalaxyPadFrameAtNormalizedCenter(safe, 0.2686676428, 0.7947259566, 3.0*d, 3.0*d) :
        CGRectMake(dx, CGRectGetMidY(_moveStick.frame) - 1.5 * d, 3.0 * d, 3.0 * d);
    [self placeExperimentalDPadGroupWithDefaultFrame:defaultGroupFrame safeArea:safe];
    // Preserve SunPad's hand-reachable iPad centers; saved editor positions win.
    [self layoutExperimentalDPadButtons];

    for (GalaxyPadGameButton *button in _buttons) {
        button.layer.cornerRadius =
            std::min(button.bounds.size.width, button.bounds.size.height) * 0.5;
    }

    CGFloat settingsSide = 44.0;
    // Keep the top controls clear of the iPad safe-area edge and the title HUD.
    // This is a visual offset only; it does not change the gameplay viewport.
    CGFloat menuInset = 20.0;
    _menuButton.frame = CGRectMake(CGRectGetMaxX(safe) - settingsSide - menuInset,
                                   CGRectGetMinY(safe) + menuInset,
                                   settingsSide, settingsSide);
    _pauseButton.frame = CGRectMake(CGRectGetMinX(_menuButton.frame) - 108,
                                   CGRectGetMinY(_menuButton.frame), 100, 44);
    _pauseButton.hidden = !self.gameplayAvailable || _editingLayout;

    _pauseOverlay.frame = self.bounds;
    CGFloat pauseWidth = MIN(560.0, CGRectGetWidth(safe) - 80.0);
    CGFloat pauseHeight = 260.0;
    _pauseCard.frame = CGRectMake(CGRectGetMidX(safe) - pauseWidth * 0.5,
                                  CGRectGetMidY(safe) - pauseHeight * 0.5,
                                  pauseWidth, pauseHeight);
    _pauseTitleLabel.frame = CGRectMake(24.0, 22.0, pauseWidth - 48.0, 38.0);
    _pauseDetailLabel.frame = CGRectMake(34.0, 70.0, pauseWidth - 68.0, 82.0);
    _pauseBackButton.frame = CGRectMake(34.0, pauseHeight - 72.0, pauseWidth - 68.0, 48.0);

    [self layoutSettingsPanelInSafeArea:safe];
    CGFloat editorWidth = MIN(560.0, CGRectGetWidth(safe) - 92.0);
    CGFloat editorHeight = 60.0;
    _editorBar.frame = CGRectMake(CGRectGetMidX(safe) - editorWidth * 0.5 - 34.0,
                                  CGRectGetMinY(safe) + 12.0,
                                  editorWidth, editorHeight);
    [self updateControlAppearance];
    if (!_settingsPanel.hidden)
        [self bringSubviewToFront:_settingsPanel];
    if (!_editorBar.hidden)
        [self bringSubviewToFront:_editorBar];
    [self bringSubviewToFront:_menuButton];
    if (!_pauseOverlay.hidden)
        [self bringSubviewToFront:_pauseOverlay];
}

- (CGFloat)experimentalDPadScale {
    NSNumber *saved = [[NSUserDefaults standardUserDefaults]
        objectForKey:GalaxyPadExperimentalDPadScaleKey];
    return saved == nil ? 1.0 : std::clamp<CGFloat>(saved.doubleValue, 0.60, 1.75);
}

- (void)placeExperimentalDPadGroupWithDefaultFrame:(CGRect)defaultFrame safeArea:(CGRect)safe {
    CGFloat individualScale = [self experimentalDPadScale];
    _experimentalDPadGroup.bounds = CGRectMake(0, 0,
        defaultFrame.size.width * individualScale,
        defaultFrame.size.height * individualScale);

    NSString *savedPoint = [[NSUserDefaults standardUserDefaults]
        stringForKey:GalaxyPadExperimentalDPadOriginKey];
    CGPoint center = savedPoint.length > 0 ? CGPointFromString(savedPoint) : CGPointMake(-1.0, -1.0);
    if (center.x >= 0.0 && center.y >= 0.0) {
        center.x = CGRectGetMinX(safe) + std::clamp<CGFloat>(center.x, 0.0, 1.0) * safe.size.width;
        center.y = CGRectGetMinY(safe) + std::clamp<CGFloat>(center.y, 0.0, 1.0) * safe.size.height;
    } else {
        center = CGPointMake(CGRectGetMidX(defaultFrame), CGRectGetMidY(defaultFrame));
    }
    CGFloat halfWidth = MIN(_experimentalDPadGroup.bounds.size.width * 0.5,
                            safe.size.width * 0.5);
    CGFloat halfHeight = MIN(_experimentalDPadGroup.bounds.size.height * 0.5,
                             safe.size.height * 0.5);
    center.x = std::clamp(center.x, CGRectGetMinX(safe) + halfWidth,
                         CGRectGetMaxX(safe) - halfWidth);
    center.y = std::clamp(center.y, CGRectGetMinY(safe) + halfHeight,
                         CGRectGetMaxY(safe) - halfHeight);
    _experimentalDPadGroup.center = center;
}

- (void)layoutExperimentalDPadButtons {
    CGFloat cell = _experimentalDPadGroup.bounds.size.width / 3.0;
    CGPoint center = _experimentalDPadGroup.center;
    struct {
        uint32_t mask;
        CGFloat x, y;
    } placements[] = {
        {galaxypad::Up, 0.0, -1.0},
        {galaxypad::Down, 0.0, 1.0},
        {galaxypad::Left, -1.0, 0.0},
        {galaxypad::Right, 1.0, 0.0},
    };
    for (const auto &placement : placements) {
        GalaxyPadGameButton *button = [self buttonWithMask:placement.mask];
        button.bounds = CGRectMake(0, 0, cell, cell);
        button.center = CGPointMake(center.x + placement.x * cell,
                                    center.y + placement.y * cell);
    }
}

- (void)placeControl:(UIView *)control defaultFrame:(CGRect)defaultFrame identifier:(NSString *)identifier {
    NSDictionary *savedScales = [[NSUserDefaults standardUserDefaults]
        dictionaryForKey:@"GalaxyPadControlSizeScales"];
    CGFloat individualScale = savedScales[identifier] != nil
        ? [[GalaxyPadSettings sharedSettings] sizeScaleForControl:identifier]
        : GalaxyPadDefaultSizeScaleForControl(self, identifier);
    control.bounds = CGRectMake(0, 0, defaultFrame.size.width * individualScale,
                                defaultFrame.size.height * individualScale);
    NSDictionary *saved = [[NSUserDefaults standardUserDefaults]
        dictionaryForKey:@"GalaxyPadControlOrigins"];
    id savedPoint = saved[identifier];
    if (savedPoint != nil) {
        CGPoint normalized = CGPointZero;
        if ([savedPoint isKindOfClass:NSString.class])
            normalized = CGPointFromString(savedPoint);
        else if ([savedPoint isKindOfClass:NSValue.class])
            normalized = [savedPoint CGPointValue];
        normalized.x = std::clamp<CGFloat>(normalized.x, 0.0, 1.0);
        normalized.y = std::clamp<CGFloat>(normalized.y, 0.0, 1.0);
        CGRect safe = self.bounds;
        if (@available(iOS 11.0, *))
            safe = UIEdgeInsetsInsetRect(safe, self.safeAreaInsets);
        CGFloat cx = CGRectGetMinX(safe) + normalized.x * safe.size.width;
        CGFloat cy = CGRectGetMinY(safe) + normalized.y * safe.size.height;
        CGFloat halfW = MIN(control.bounds.size.width, safe.size.width) * 0.5;
        CGFloat halfH = MIN(control.bounds.size.height, safe.size.height) * 0.5;
        cx = std::clamp(cx, CGRectGetMinX(safe) + halfW, CGRectGetMaxX(safe) - halfW);
        cy = std::clamp(cy, CGRectGetMinY(safe) + halfH, CGRectGetMaxY(safe) - halfH);
        control.center = CGPointMake(cx, cy);
    } else {
        control.center = CGPointMake(CGRectGetMidX(defaultFrame), CGRectGetMidY(defaultFrame));
    }
}

- (GalaxyPadGameButton *)buttonWithMask:(uint32_t)mask {
    for (GalaxyPadGameButton *button in _buttons) {
        if (button.inputMask == mask)
            return button;
    }
    return nil;
}

- (void)layoutSettingsPanelInSafeArea:(CGRect)safe {
    CGFloat width = MIN(360.0, CGRectGetWidth(safe) - 32.0);
    BOOL compact = CGRectGetHeight(safe) < 400.0;
    CGFloat top = compact ? 12.0 : 60.0;
    CGFloat height = MIN(320.0, CGRectGetHeight(safe) - top - 12.0);
    _settingsPanel.frame = CGRectMake(CGRectGetMaxX(safe) - width - (compact ? 72.0 : 12.0),
                                      CGRectGetMinY(safe) + top,
                                      width, height);
}

#pragma mark - Settings panel

- (void)buildSettingsPanel {
    _settingsPanel = [UIView new];
    _settingsPanel.accessibilityIdentifier = @"galaxypad.touch.settings";
    _settingsPanel.backgroundColor = [UIColor colorWithWhite:0.035 alpha:0.94];
    _settingsPanel.layer.cornerRadius = 16.0;
    _settingsPanel.layer.borderWidth = 1.0;
    _settingsPanel.layer.borderColor = [UIColor colorWithWhite:1.0 alpha:0.22].CGColor;
    _settingsPanel.hidden = YES;
    [self addSubview:_settingsPanel];

    UILabel *title = [UILabel new];
    title.text = @"Touch Control Settings";
    title.textColor = UIColor.whiteColor;
    title.font = [UIFont systemFontOfSize:18.0 weight:UIFontWeightBold];

    UIButton *close = [UIButton buttonWithType:UIButtonTypeCustom];
    UIImageSymbolConfiguration *closeSymbol =
        [UIImageSymbolConfiguration configurationWithPointSize:16.0
                                                        weight:UIImageSymbolWeightBold];
    [close setImage:[UIImage systemImageNamed:@"xmark" withConfiguration:closeSymbol]
           forState:UIControlStateNormal];
    close.tintColor = UIColor.whiteColor;
    close.backgroundColor = [UIColor colorWithWhite:1.0 alpha:0.14];
    close.layer.cornerRadius = 16.0;
    close.accessibilityLabel = @"Close touch control settings";
    [close addTarget:self action:@selector(closeSettingsPanel)
      forControlEvents:UIControlEventTouchUpInside];

    UIStackView *header = [[UIStackView alloc] initWithArrangedSubviews:@[title, close]];
    header.translatesAutoresizingMaskIntoConstraints = NO;
    header.axis = UILayoutConstraintAxisHorizontal;
    header.alignment = UIStackViewAlignmentCenter;
    header.spacing = 12.0;
    [_settingsPanel addSubview:header];


    _opacitySlider = [UISlider new];
    _opacitySlider.minimumValue = 0.25;
    _opacitySlider.maximumValue = 1.0;
    _opacitySlider.value = [GalaxyPadSettings sharedSettings].controlOpacity;
    _opacitySlider.accessibilityLabel = @"Control opacity";
    [_opacitySlider addTarget:self action:@selector(opacityChanged:)
             forControlEvents:UIControlEventValueChanged];

    _sizeSlider = [UISlider new];
    _sizeSlider.minimumValue = 0.70;
    _sizeSlider.maximumValue = 1.35;
    _sizeSlider.value = [GalaxyPadSettings sharedSettings].controlSizeScale;
    _sizeSlider.accessibilityLabel = @"Control size";
    [_sizeSlider addTarget:self action:@selector(sizeChanged:)
          forControlEvents:UIControlEventValueChanged];

    _selectedSizeSlider = [UISlider new];
    _selectedSizeSlider.minimumValue = 0.60;
    _selectedSizeSlider.maximumValue = 1.75;
    _selectedSizeSlider.value = 1.0;
    _selectedSizeSlider.enabled = NO;
    _selectedSizeSlider.accessibilityLabel = @"Selected control size";
    [_selectedSizeSlider addTarget:self action:@selector(selectedSizeChanged:)
                   forControlEvents:UIControlEventValueChanged];

    _hideControlsSwitch = [UISwitch new];
    _hideControlsSwitch.on = [GalaxyPadSettings sharedSettings].hideTouchControlsWhenControllerConnected;
    _hideControlsSwitch.accessibilityLabel = @"Hide touch controls when controller connected";
    [_hideControlsSwitch addTarget:self action:@selector(hideChanged:)
                  forControlEvents:UIControlEventValueChanged];

    _editLayoutSwitch = [UISwitch new];
    _editLayoutSwitch.on = NO;
    _editLayoutSwitch.accessibilityLabel = @"Move touch controls";
    [_editLayoutSwitch addTarget:self action:@selector(editLayoutChanged:)
                forControlEvents:UIControlEventValueChanged];

    _resetLayoutButton = [UIButton buttonWithType:UIButtonTypeSystem];
    _resetLayoutButton.accessibilityIdentifier = @"galaxypad.touch.reset";
    [_resetLayoutButton setTitle:@"Reset This Device Layout" forState:UIControlStateNormal];
    [_resetLayoutButton setTitleColor:UIColor.whiteColor forState:UIControlStateNormal];
    _resetLayoutButton.titleLabel.font = [UIFont systemFontOfSize:15.0 weight:UIFontWeightSemibold];
    _resetLayoutButton.backgroundColor = [UIColor colorWithWhite:0.18 alpha:0.88];
    _resetLayoutButton.layer.cornerRadius = 10.0;
    [_resetLayoutButton addTarget:self action:@selector(confirmResetLayout)
    forControlEvents:UIControlEventTouchUpInside];

    UIStackView *stack = [[UIStackView alloc] initWithArrangedSubviews:@[
        [self settingsRowWithTitle:@"Opacity" control:_opacitySlider],
        [self settingsRowWithTitle:@"All sizes" control:_sizeSlider],
        [self settingsRowWithTitle:@"Hide on controller" control:_hideControlsSwitch],
        [self settingsRowWithTitle:@"Move controls" control:_editLayoutSwitch],
        _resetLayoutButton,
    ]];
    stack.translatesAutoresizingMaskIntoConstraints = NO;
    stack.axis = UILayoutConstraintAxisVertical;
    stack.spacing = 6.0;

    UIScrollView *scroll = [UIScrollView new];
    scroll.translatesAutoresizingMaskIntoConstraints = NO;
    scroll.alwaysBounceVertical = NO;
    scroll.showsVerticalScrollIndicator = YES;
    [_settingsPanel addSubview:scroll];
    [scroll addSubview:stack];
    [NSLayoutConstraint activateConstraints:@[
        [header.leadingAnchor constraintEqualToAnchor:_settingsPanel.leadingAnchor constant:16.0],
        [header.trailingAnchor constraintEqualToAnchor:_settingsPanel.trailingAnchor constant:-12.0],
        [header.topAnchor constraintEqualToAnchor:_settingsPanel.topAnchor constant:8.0],
        [header.heightAnchor constraintEqualToConstant:48.0],
        [close.widthAnchor constraintEqualToConstant:44.0],
        [close.heightAnchor constraintEqualToConstant:44.0],
        [scroll.leadingAnchor constraintEqualToAnchor:_settingsPanel.leadingAnchor],
        [scroll.trailingAnchor constraintEqualToAnchor:_settingsPanel.trailingAnchor],
        [scroll.topAnchor constraintEqualToAnchor:header.bottomAnchor constant:2.0],
        [scroll.bottomAnchor constraintEqualToAnchor:_settingsPanel.bottomAnchor],
        [stack.leadingAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.leadingAnchor constant:16.0],
        [stack.trailingAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.trailingAnchor constant:-16.0],
        [stack.topAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.topAnchor constant:8.0],
        [stack.bottomAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.bottomAnchor constant:-8.0],
        [stack.widthAnchor constraintEqualToAnchor:scroll.frameLayoutGuide.widthAnchor constant:-32.0],
        [_resetLayoutButton.heightAnchor constraintEqualToConstant:44.0],
    ]];

    _editorBar = [GalaxyPadPassThroughView new];
    _editorBar.accessibilityIdentifier = @"galaxypad.touch.editor";
    _editorBar.backgroundColor = [UIColor colorWithWhite:0.035 alpha:0.95];
    _editorBar.layer.cornerRadius = 16.0;
    _editorBar.layer.borderWidth = 1.0;
    _editorBar.layer.borderColor =
        [UIColor colorWithRed:1.0 green:0.78 blue:0.20 alpha:0.95].CGColor;
    _editorBar.hidden = YES;
    [self addSubview:_editorBar];

    _editorHintLabel = [UILabel new];
    _editorHintLabel.text = @"Drag controls • tap one to resize";
    _editorHintLabel.textColor = UIColor.whiteColor;
    _editorHintLabel.font = [UIFont systemFontOfSize:14.0 weight:UIFontWeightSemibold];
    _editorHintLabel.adjustsFontSizeToFitWidth = YES;
    _editorHintLabel.minimumScaleFactor = 0.75;

    UIButton *done = [UIButton buttonWithType:UIButtonTypeSystem];
    [done setTitle:@"Done" forState:UIControlStateNormal];
    [done setTitleColor:UIColor.whiteColor forState:UIControlStateNormal];
    done.titleLabel.font = [UIFont systemFontOfSize:15.0 weight:UIFontWeightBold];
    done.backgroundColor = [UIColor colorWithRed:0.12 green:0.48 blue:0.82 alpha:1.0];
    done.layer.cornerRadius = 10.0;
    done.accessibilityLabel = @"Finish moving touch controls";
    done.accessibilityIdentifier = @"galaxypad.touch.done";
    [done addTarget:self action:@selector(finishLayoutEditing)
      forControlEvents:UIControlEventTouchUpInside];

    UIStackView *editorStack = [[UIStackView alloc]
        initWithArrangedSubviews:@[_editorHintLabel, _selectedSizeSlider, done]];
    editorStack.translatesAutoresizingMaskIntoConstraints = NO;
    editorStack.axis = UILayoutConstraintAxisHorizontal;
    editorStack.alignment = UIStackViewAlignmentCenter;
    editorStack.spacing = 12.0;
    [_editorBar addSubview:editorStack];
    [_editorHintLabel setContentCompressionResistancePriority:UILayoutPriorityDefaultLow
                                                     forAxis:UILayoutConstraintAxisHorizontal];
    [_selectedSizeSlider setContentCompressionResistancePriority:UILayoutPriorityDefaultHigh
                                                         forAxis:UILayoutConstraintAxisHorizontal];
    [NSLayoutConstraint activateConstraints:@[
        [editorStack.leadingAnchor constraintEqualToAnchor:_editorBar.leadingAnchor constant:14.0],
        [editorStack.trailingAnchor constraintEqualToAnchor:_editorBar.trailingAnchor constant:-10.0],
        [editorStack.topAnchor constraintEqualToAnchor:_editorBar.topAnchor constant:8.0],
        [editorStack.bottomAnchor constraintEqualToAnchor:_editorBar.bottomAnchor constant:-8.0],
        [_selectedSizeSlider.widthAnchor constraintGreaterThanOrEqualToConstant:150.0],
        [done.widthAnchor constraintEqualToConstant:68.0],
        [done.heightAnchor constraintEqualToConstant:44.0],
    ]];
}

- (UIView *)settingsRowWithTitle:(NSString *)title control:(UIView *)control {
    UILabel *label = [UILabel new];
    label.text = title;
    label.textColor = UIColor.whiteColor;
    label.font = [UIFont systemFontOfSize:14.0 weight:UIFontWeightMedium];
    [control setContentHuggingPriority:UILayoutPriorityDefaultLow forAxis:UILayoutConstraintAxisHorizontal];
    [label setContentHuggingPriority:UILayoutPriorityDefaultHigh forAxis:UILayoutConstraintAxisHorizontal];
    UIStackView *row = [[UIStackView alloc] initWithArrangedSubviews:@[label, control]];
    row.axis = UILayoutConstraintAxisHorizontal;
    row.spacing = 12.0;
    row.alignment = UIStackViewAlignmentCenter;
    [row.heightAnchor constraintGreaterThanOrEqualToConstant:44.0].active = YES;
    return row;
}

- (void)toggleSettingsPanel {
    if (_editingLayout)
        [self finishLayoutEditing];
    if (_settingsPanel.hidden) {
        [self clearTouchInput];
        _settingsPanel.hidden = NO;
        [self bringSubviewToFront:_settingsPanel];
        [self bringSubviewToFront:_menuButton];
    } else {
        [self closeSettingsPanel];
    }
    if (self.nativeUIChanged) self.nativeUIChanged();
}

- (void)closeSettingsPanel {
    _settingsPanel.hidden = YES;
    if (_editingLayout)
        [self finishLayoutEditing];
    if (self.nativeUIChanged) self.nativeUIChanged();
}

- (void)opacityChanged:(UISlider *)slider {
    [GalaxyPadSettings sharedSettings].controlOpacity = slider.value;
    [[GalaxyPadSettings sharedSettings] synchronize];
    [self setNeedsLayout];
}

- (void)sizeChanged:(UISlider *)slider {
    [GalaxyPadSettings sharedSettings].controlSizeScale = slider.value;
    [[GalaxyPadSettings sharedSettings] synchronize];
    [self setNeedsLayout];
}

- (void)hideChanged:(UISwitch *)switcher {
    [GalaxyPadSettings sharedSettings].hideTouchControlsWhenControllerConnected = switcher.on;
    [[GalaxyPadSettings sharedSettings] synchronize];
    [self applyControllerVisibility];
}


- (void)editLayoutChanged:(UISwitch *)switcher {
    if (switcher.on)
        [self beginLayoutEditing];
    else
        [self endLayoutEditing];
}

- (void)finishLayoutEditing {
    _editLayoutSwitch.on = NO;
    [self endLayoutEditing];
}

- (void)confirmResetLayout {
    __weak GalaxyPadGameOverlay *weakSelf = self;
    UIAlertController *alert =
        [UIAlertController alertControllerWithTitle:@"Reset Touch Control Layout?"
                                            message:@"All control positions and sizes, including the grouped D-pad, return to their defaults."
                                     preferredStyle:UIAlertControllerStyleAlert];
    [alert addAction:[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil]];
    [alert addAction:[UIAlertAction actionWithTitle:@"Reset" style:UIAlertActionStyleDestructive
                                            handler:^(UIAlertAction *action) {
        (void)action;
        [weakSelf resetLayout];
    }]];
    [self.window.rootViewController presentViewController:alert animated:YES completion:nil];
}

- (void)resetLayout {
    NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
    [defaults removeObjectForKey:GalaxyPadExperimentalDPadOriginKey];
    [defaults removeObjectForKey:GalaxyPadExperimentalDPadScaleKey];
    [defaults removeObjectForKey:@"GalaxyPadControlOrigins"];
    [defaults removeObjectForKey:@"GalaxyPadControlSizeScales"];
    [defaults removeObjectForKey:@"GalaxyPadControlSizeScale"];
    // Reset geometry only, as promised by the confirmation. Preserve appearance
    // and controller-visibility preferences.
    [[GalaxyPadSettings sharedSettings] resetControlSizeScales];
    [[GalaxyPadSettings sharedSettings] synchronize];
    [self applySettings];
    [self setNeedsLayout];
}

#pragma mark - Layout editing (drag + persist)

- (void)addEditGesturesToControl:(UIView *)control {
    UIPanGestureRecognizer *drag = [[UIPanGestureRecognizer alloc]
        initWithTarget:self action:@selector(controlDragged:)];
    drag.enabled = NO;
    drag.cancelsTouchesInView = YES;
    drag.delegate = self;
    [control addGestureRecognizer:drag];
    [_editGestures addObject:drag];

    UITapGestureRecognizer *tap = [[UITapGestureRecognizer alloc]
        initWithTarget:self action:@selector(controlSelected:)];
    tap.enabled = NO;
    tap.cancelsTouchesInView = YES;
    [control addGestureRecognizer:tap];
    [_editGestures addObject:tap];
}

- (NSArray<UIView *> *)gameplayControls {
    NSMutableArray<UIView *> *controls = [NSMutableArray arrayWithArray:_buttons];
    if (_moveStick != nil) [controls addObject:_moveStick];
    if (_tiltStick != nil) [controls addObject:_tiltStick];
    return controls;
}

- (BOOL)isDPadButton:(UIView *)control {
    if (![control isKindOfClass:GalaxyPadGameButton.class])
        return NO;
    uint32_t mask = ((GalaxyPadGameButton *)control).inputMask;
    return mask == galaxypad::Up || mask == galaxypad::Down ||
           mask == galaxypad::Left || mask == galaxypad::Right;
}

- (BOOL)isEditableControl:(UIView *)control {
    if (control == _experimentalDPadGroup)
        return YES;
    if ([self isDPadButton:control])
        return NO;
    return YES;
}

- (void)toggleTiltStick {
    [self clearTouchInput];
    NSUserDefaults *defaults = NSUserDefaults.standardUserDefaults;
    [defaults setBool:![defaults boolForKey:@"GalaxyPadShowTiltStick"] forKey:@"GalaxyPadShowTiltStick"];
    [self updateControlAppearance];
    _menuButton.menu = [self buildMenu];
}

- (void)setMainVolume:(NSInteger)value {
    [self clearTouchInput];
    GalaxyPadSettings.sharedSettings.mainVolume = value;
    [self refreshMenuButton];
}
- (void)toggleMainAudioMuted {
    [self clearTouchInput];
    GalaxyPadSettings *settings = GalaxyPadSettings.sharedSettings;
    settings.mainAudioMuted = !settings.mainAudioMuted;
    [self refreshMenuButton];
}
- (UIMenu *)audioMenu {
    __weak GalaxyPadGameOverlay *weakSelf = self;
    GalaxyPadSettings *settings = GalaxyPadSettings.sharedSettings;
    NSMutableArray<UIMenuElement *> *levels = [NSMutableArray array];
    for (NSNumber *level in @[@0, @25, @50, @75, @100]) {
        UIAction *action = [UIAction actionWithTitle:[NSString stringWithFormat:@"%@%%", level]
            image:nil identifier:nil handler:^(__kindof UIAction *unused) {
                (void)unused; [weakSelf setMainVolume:level.integerValue];
            }];
        action.state = settings.mainVolume == level.integerValue ? UIMenuElementStateOn : UIMenuElementStateOff;
        [levels addObject:action];
    }
    UIAction *mute = [UIAction actionWithTitle:@"Mute Game Audio" image:[UIImage systemImageNamed:@"speaker.slash"]
        identifier:@"galaxypad.menu.mute" handler:^(__kindof UIAction *unused) {
            (void)unused; [weakSelf toggleMainAudioMuted];
        }];
    mute.state = settings.mainAudioMuted ? UIMenuElementStateOn : UIMenuElementStateOff;
    return [UIMenu menuWithTitle:@"Audio" image:[UIImage systemImageNamed:@"speaker.wave.2"]
        identifier:nil options:0 children:@[
            [UIMenu menuWithTitle:[NSString stringWithFormat:@"Main Volume · %ld%%", (long)settings.mainVolume]
                children:levels], mute]];
}

- (void)setTouchTiltSensitivity:(CGFloat)value {
    [self clearTouchInput];
    GalaxyPadSettings.sharedSettings.touchTiltSensitivity = value;
    [self refreshMenuButton];
}
- (void)toggleTouchTiltInversion {
    [self clearTouchInput];
    GalaxyPadSettings *settings = GalaxyPadSettings.sharedSettings;
    settings.touchTiltInvertY = !settings.touchTiltInvertY;
    [self refreshMenuButton];
}

- (void)toggleAuxiliaryButtons {
    // Release any held key before its view stops receiving touch-up events.
    [self clearTouchInput];
    NSUserDefaults *defaults = NSUserDefaults.standardUserDefaults;
    [defaults setBool:![defaults boolForKey:@"GalaxyPadShowAuxiliaryButtons"]
               forKey:@"GalaxyPadShowAuxiliaryButtons"];
    [self updateControlAppearance];
    _menuButton.menu = [self buildMenu];
}

- (void)toggleTouchControls {
    [self clearTouchInput];
    NSUserDefaults *defaults = NSUserDefaults.standardUserDefaults;
    [defaults setBool:![defaults boolForKey:@"GalaxyPadTouchControlsDisabled"]
               forKey:@"GalaxyPadTouchControlsDisabled"];
    [self applyControllerVisibility];
    [self updateControlAppearance];
    _menuButton.menu = [self buildMenu];
}

- (void)updateControlAppearance {
    BOOL hidden = (_touchControlsHidden || !_gameplayAvailable) && !_editingLayout;
    CGFloat alpha = _editingLayout ? 1.0 : [GalaxyPadSettings sharedSettings].controlOpacity;
    BOOL groupedDPad = YES;
    for (UIView *control in [self gameplayControls]) {
        uint32_t mask = [control isKindOfClass:GalaxyPadGameButton.class]
            ? ((GalaxyPadGameButton *)control).inputMask : 0;
        BOOL auxiliary = mask == galaxypad::One || mask == galaxypad::Two ||
                         mask == galaxypad::Minus;
        BOOL controlHidden = hidden || (control == _tiltStick && !_editingLayout &&
            ![NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadShowTiltStick"]);
        controlHidden |= auxiliary && !_editingLayout &&
            ![NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadShowAuxiliaryButtons"];
        control.hidden = controlHidden;
        control.userInteractionEnabled = !controlHidden;
        control.alpha = controlHidden ? 0.0 : alpha;
        UIColor *border = [UIColor colorWithWhite:1.0 alpha:0.68];
        CGFloat borderWidth = 1.0;
        if (_editingLayout && !(groupedDPad && [self isDPadButton:control])) {
            border = control == _selectedControl
                ? [UIColor colorWithRed:0.20 green:0.78 blue:1.0 alpha:1.0]
                : [UIColor colorWithRed:1.0 green:0.78 blue:0.20 alpha:0.95];
            borderWidth = control == _selectedControl ? 4.0 : 3.0;
        }
        control.layer.borderColor = border.CGColor;
        control.layer.borderWidth = borderWidth;
    }

    BOOL showDPadGroup = _editingLayout && !hidden;
    _experimentalDPadGroup.hidden = !showDPadGroup;
    _experimentalDPadGroup.userInteractionEnabled = showDPadGroup;
    _experimentalDPadGroup.alpha = showDPadGroup ? 1.0 : 0.0;
    _experimentalDPadGroup.layer.borderColor =
        (_selectedControl == _experimentalDPadGroup ?
            [UIColor colorWithRed:0.20 green:0.78 blue:1.0 alpha:1.0] :
            [UIColor colorWithRed:1.0 green:0.78 blue:0.20 alpha:0.95]).CGColor;
    _experimentalDPadGroup.layer.borderWidth =
        _selectedControl == _experimentalDPadGroup ? 4.0 : 3.0;
    if (showDPadGroup)
        [self bringSubviewToFront:_experimentalDPadGroup];
}

- (void)beginLayoutEditing {
    _editingLayout = YES;
    _settingsPanel.hidden = YES;
    _editorBar.hidden = NO;
    _selectedControl = nil;
    _selectedSizeSlider.enabled = NO;
    _selectedSizeSlider.value = 1.0;
    _editorHintLabel.text = @"Drag controls • tap one to resize";
    [self clearTouchInput];
    for (UIGestureRecognizer *gesture in _editGestures)
        gesture.enabled = [self isEditableControl:gesture.view];
    [self updateControlAppearance];
    [self setNeedsLayout];
    if (self.nativeUIChanged) self.nativeUIChanged();
}

- (void)endLayoutEditing {
    [self clearTouchInput];
    _editingLayout = NO;
    _editorBar.hidden = YES;
    for (UIGestureRecognizer *gesture in _editGestures)
        gesture.enabled = NO;
    _selectedControl = nil;
    _selectedSizeSlider.enabled = NO;
    _selectedSizeSlider.value = 1.0;
    _editorHintLabel.text = @"Drag controls • tap one to resize";
    [self applyControllerVisibility];
    [self updateControlAppearance];
    [self setNeedsLayout]; // Discard any unfinished drag using saved/default geometry.
    if (self.nativeUIChanged) self.nativeUIChanged();
}

- (NSString *)identifierForMask:(uint32_t)mask {
    switch (mask) {
    case galaxypad::A: return @"A";
    case galaxypad::B: return @"B";
    case galaxypad::Spin: return @"Spin";
    case galaxypad::C: return @"C";
    case galaxypad::Z: return @"Z";
    case galaxypad::Plus: return @"Plus";
    case galaxypad::One: return @"1";
    case galaxypad::Two: return @"2";
    case galaxypad::Minus: return @"−";
    case galaxypad::Up: return @"D_U";
    case galaxypad::Down: return @"D_D";
    case galaxypad::Left: return @"D_L";
    case galaxypad::Right: return @"D_R";
    default: return @"";
    }
}

- (void)controlDragged:(UIPanGestureRecognizer *)drag {
    if (!_editingLayout || drag.view == nil)
        return;
    if (drag.state == UIGestureRecognizerStateCancelled ||
        drag.state == UIGestureRecognizerStateFailed) {
        [self setNeedsLayout]; // No preference write: restore the last committed layout.
        return;
    }
    UIView *control = drag.view;
    if (drag.state == UIGestureRecognizerStateBegan)
        [self selectControlForEditing:control];
    CGPoint translation = [drag translationInView:self];
    CGPoint center = CGPointMake(control.center.x + translation.x,
                                 control.center.y + translation.y);
    [drag setTranslation:CGPointZero inView:self];

    CGRect safe = self.bounds;
    if (@available(iOS 11.0, *))
        safe = UIEdgeInsetsInsetRect(safe, self.safeAreaInsets);
    CGFloat halfWidth = MIN(control.bounds.size.width * 0.5, safe.size.width * 0.5);
    CGFloat halfHeight = MIN(control.bounds.size.height * 0.5, safe.size.height * 0.5);
    center.x = std::clamp(center.x, CGRectGetMinX(safe) + halfWidth,
                          CGRectGetMaxX(safe) - halfWidth);
    center.y = std::clamp(center.y, CGRectGetMinY(safe) + halfHeight,
                          CGRectGetMaxY(safe) - halfHeight);
    control.center = center;
    if (control == _experimentalDPadGroup)
        [self layoutExperimentalDPadButtons];

    if (drag.state == UIGestureRecognizerStateEnded) {
        NSString *identifier = control.accessibilityIdentifier;
        if (identifier.length == 0 || safe.size.width <= 0.0 || safe.size.height <= 0.0)
            return;
        CGPoint normalized = CGPointMake(
            (center.x - CGRectGetMinX(safe)) / safe.size.width,
            (center.y - CGRectGetMinY(safe)) / safe.size.height);
        if (control == _experimentalDPadGroup) {
            [[NSUserDefaults standardUserDefaults]
                setObject:NSStringFromCGPoint(normalized)
                   forKey:GalaxyPadExperimentalDPadOriginKey];
        } else {
            NSMutableDictionary *saved = [[[NSUserDefaults standardUserDefaults]
                dictionaryForKey:@"GalaxyPadControlOrigins"] mutableCopy];
            if (saved == nil)
                saved = [NSMutableDictionary dictionary];
            saved[identifier] = NSStringFromCGPoint(normalized);
            [[NSUserDefaults standardUserDefaults] setObject:saved forKey:@"GalaxyPadControlOrigins"];
        }
        [[GalaxyPadSettings sharedSettings] synchronize];
    }
}

- (void)controlSelected:(UITapGestureRecognizer *)tap {
    if (tap.state == UIGestureRecognizerStateEnded)
        [self selectControlForEditing:tap.view];
}

- (void)selectControlForEditing:(UIView *)control {
    if (!_editingLayout || control.accessibilityIdentifier.length == 0)
        return;
    _selectedControl = control;
    _selectedSizeSlider.value = control == _experimentalDPadGroup ?
        [self experimentalDPadScale] :
        [[GalaxyPadSettings sharedSettings] sizeScaleForControl:control.accessibilityIdentifier];
    _selectedSizeSlider.enabled = YES;
    _selectedSizeSlider.accessibilityLabel = [NSString stringWithFormat:@"%@ size",
                                               control.accessibilityLabel];
    _editorHintLabel.text = [NSString stringWithFormat:@"%@ size", control.accessibilityLabel];
    [self updateControlAppearance];
}

- (void)selectedSizeChanged:(UISlider *)slider {
    NSString *identifier = _selectedControl.accessibilityIdentifier;
    if (!_editingLayout || identifier.length == 0)
        return;
    // Editor-only diagnostic: no gameplay coordinates or input payloads.
    NSLog(@"[GalaxyPad editor] sizeChanged control=%@ value=%.3f tracking=%d",
          identifier, slider.value, slider.tracking);
    if (_selectedControl == _experimentalDPadGroup) {
        [[NSUserDefaults standardUserDefaults]
            setDouble:std::clamp<double>(slider.value, 0.60, 1.75)
               forKey:GalaxyPadExperimentalDPadScaleKey];
    } else {
        [[GalaxyPadSettings sharedSettings] setSizeScale:slider.value forControl:identifier];
    }
    [[GalaxyPadSettings sharedSettings] synchronize];
    [self setNeedsLayout];
}

#pragma mark - Settings application

- (void)applySettings {
    [self refreshMenuButton];
    GalaxyPadSettings *settings = [GalaxyPadSettings sharedSettings];
    [[NSUserDefaults standardUserDefaults] removeObjectForKey:@"GalaxyPadEditingControlLayout"];
    _opacitySlider.value = settings.controlOpacity;
    _sizeSlider.value = settings.controlSizeScale;
    _hideControlsSwitch.on = settings.hideTouchControlsWhenControllerConnected;
    _editLayoutSwitch.on = NO;
    [[NSUserDefaults standardUserDefaults]
        removeObjectForKey:@"GalaxyPadExperimentalTouchControls"];
    [_resetLayoutButton setTitle:@"Reset This Device Layout"
                        forState:UIControlStateNormal];
    [self endLayoutEditing];
    [self setNeedsLayout];
}

- (void)setTouchControlsHidden:(BOOL)hidden animated:(BOOL)animated {
    if (hidden && !_touchControlsHidden) [self clearTouchInput];
    _touchControlsHidden = hidden;
    [UIView animateWithDuration:animated ? 0.25 : 0.0 animations:^{
        [self setNeedsLayout];
        [self layoutIfNeeded];
    }];
}

- (void)setGameplayAvailable:(BOOL)available {
    if (_gameplayAvailable == available) return;
    _gameplayAvailable = available;
    if (!available) [self clearTouchInput];
    [self setNeedsLayout];
}

- (void)applyControllerVisibility {
    BOOL controllerConnected = NO;
#if !TARGET_OS_SIMULATOR
    // Only real hardware controllers hide the touch controls; the Simulator
    // can report virtual controllers that would hide them during testing.
    for (GCController *controller in GCController.controllers) {
        if (controller.extendedGamepad != nil) {
            controllerConnected = YES;
            break;
        }
    }
#endif
    BOOL manuallyDisabled = [NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadTouchControlsDisabled"];
    BOOL autoHide = [GalaxyPadSettings sharedSettings].hideTouchControlsWhenControllerConnected;
    BOOL shouldHide = !_editingLayout && (manuallyDisabled || (controllerConnected && autoHide));
    [self setTouchControlsHidden:shouldHide animated:YES];
    if (controllerConnected)
        [self clearTouchInput];
    GalaxyPadLog(@"controller visibility connected=%d auto_hide=%d manually_disabled=%d hidden=%d",
        controllerConnected, autoHide, manuallyDisabled, _touchControlsHidden);
}

- (void)refreshControllerVisibility {
    [self applyControllerVisibility];
}

- (void)observeControllerConnection {
    [[NSNotificationCenter defaultCenter] addObserver:self
                                             selector:@selector(applyControllerVisibility)
                                                 name:GCControllerDidConnectNotification
                                               object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self
                                             selector:@selector(applyControllerVisibility)
                                                 name:GCControllerDidDisconnectNotification
                                               object:nil];
    [self applyControllerVisibility];
}


- (void)publishInput {
    if (self.blocksGameplay) return;
    _touchState.connected = true;
    auto state = _touchState;
    state.buttons |= _accessibilityButtons;
    if (self.inputChanged) self.inputChanged(state);
}
- (void)reset { [self clearTouchInput]; }
- (BOOL)blocksGameplay { return _menuVisible || _pauseVisible || _editingLayout || !_settingsPanel.hidden; }
- (BOOL)nativeMenuVisible { return _menuVisible; }
- (UIAlertController *)touchControlGuide {
    UIAlertController *guide = [UIAlertController alertControllerWithTitle:@"Touch Controls"
      message:@"Left stick: move. A: jump / use / swim / grab Pull Stars. B: shoot Star Bits. X: spin. Y: reset camera. Z: crouch / dive. D-pad: camera view.\n\n"
               "Drag on the game to aim; press A or B separately. Hold A + B at the title screen. Touch aim currently drives a virtual Wii Remote and may not align with your finger.\n\n"
               "Hold Start + for Galaxy’s pause menu (longer during slowdowns). The top Pause button pauses immediately.\n\n"
               "Ball / ray: enable Show Tilt Stick in Controls (not device motion)."
      preferredStyle:UIAlertControllerStyleAlert];
    [guide addAction:[UIAlertAction actionWithTitle:@"Done" style:UIAlertActionStyleCancel handler:nil]];
    return guide;
}

- (void)confirmStop {
    UIAlertController *alert = [UIAlertController alertControllerWithTitle:@"Stop Game?"
      message:@"Unsaved progress will be lost. Existing saves will be kept."
      preferredStyle:UIAlertControllerStyleAlert];
    [alert addAction:[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil]];
    __weak GalaxyPadGameOverlay *weakSelf = self;
    [alert addAction:[UIAlertAction actionWithTitle:@"Stop Game" style:UIAlertActionStyleDestructive
      handler:^(UIAlertAction *action) {
        (void)action;
        if (weakSelf.stopRequested) weakSelf.stopRequested();
      }]];
    [self.window.rootViewController presentViewController:alert animated:YES completion:nil];
}
- (CGRect)gameplayViewport {
    CGRect n = self.viewportProvider ? self.viewportProvider() : CGRectZero;
    return CGRectMake(n.origin.x * self.bounds.size.width, n.origin.y * self.bounds.size.height,
                      n.size.width * self.bounds.size.width, n.size.height * self.bounds.size.height);
}
- (void)updatePointer {
    if (!_pointerContact) return;
    CGRect viewport = [self gameplayViewport];
    CGPoint point = [_pointerContact locationInView:self];
    _touchState.pointerVisible = !CGRectIsEmpty(viewport) && CGRectContainsPoint(viewport, point);
    if (_touchState.pointerVisible) {
        _touchState.pointerX = (point.x - viewport.origin.x) / viewport.size.width;
        _touchState.pointerY = (point.y - viewport.origin.y) / viewport.size.height;
    }
    [self publishInput];
}
- (void)touchesBegan:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
    (void)event;
    // Controller auto-hide owns the pointer too: a new screen contact must
    // not replace controller aim after the handoff cleared the old touch.
    if (!_gameplayAvailable || self.blocksGameplay || _touchControlsHidden || _pointerContact ||
        [NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadTouchControlsDisabled"]) return;
    const CGRect viewport = [self gameplayViewport];
    if (CGRectIsEmpty(viewport)) return;
    // A resting finger in letterboxing is not a pointer owner. Choose a real
    // playfield contact even when UIKit delivers both contacts in one set.
    for (UITouch *touch in touches) {
        if (CGRectContainsPoint(viewport, [touch locationInView:self])) {
            _pointerContact = touch;
            [self updatePointer];
            break;
        }
    }
}
- (void)touchesMoved:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
    (void)event;
    if (_pointerContact && [touches containsObject:_pointerContact]) [self updatePointer];
}
- (void)touchesEnded:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
    (void)event;
    if (_pointerContact && [touches containsObject:_pointerContact]) {
        [self updatePointer]; _pointerContact = nil;
    }
}
- (void)touchesCancelled:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
    (void)event;
    if (_pointerContact && [touches containsObject:_pointerContact]) {
        _pointerContact = nil; _touchState.pointerVisible = false; [self publishInput];
    }
}
@end
