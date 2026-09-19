// SPDX-License-Identifier: GPL-3.0-or-later
// Adapted from SunPad fcdc1411e483a86ca80ec82e7cd53839c51ff865,
// apple/shared/SunPadSettings.mm. Reference settings persistence and editor ranges.
#import "GalaxyPadSettings.h"
#include <cmath>

@implementation GalaxyPadSettings {
    NSMutableDictionary<NSString *, NSNumber *> *_controlSizeScales;
}

+ (instancetype)sharedSettings {
    static GalaxyPadSettings *shared = nil;
    static dispatch_once_t once;
    dispatch_once(&once, ^{
        shared = [[GalaxyPadSettings alloc] init];
    });
    return shared;
}

- (instancetype)init {
    if ((self = [super init])) {
        NSDictionary *saved = [[NSUserDefaults standardUserDefaults]
            dictionaryForKey:@"GalaxyPadControlSizeScales"];
        _controlSizeScales = saved ? [saved mutableCopy] : [NSMutableDictionary dictionary];
    }
    return self;
}

- (NSInteger)renderScale {
    NSNumber *value = [[NSUserDefaults standardUserDefaults] objectForKey:@"GalaxyPadRenderScale"];
    if (value == nil)
        return 1;
    NSInteger scale = value.integerValue;
    return scale < 1 ? 1 : (scale > 4 ? 4 : scale);
}

- (void)setRenderScale:(NSInteger)renderScale {
    NSInteger clamped = renderScale < 1 ? 1 : (renderScale > 4 ? 4 : renderScale);
    [[NSUserDefaults standardUserDefaults] setInteger:clamped forKey:@"GalaxyPadRenderScale"];
}

- (float)renderScaleFloat {
    switch (self.renderScale) {
    case 1: return 1.0f;
    case 2: return 2.0f;
    case 3: return 3.0f;
    case 4: return 4.0f;
    default: return 1.0f;
    }
}

- (GalaxyPadAspectRatioMode)aspectRatioMode {
    NSNumber *saved = [[NSUserDefaults standardUserDefaults]
        objectForKey:@"GalaxyPadAspectRatioMode"];
    NSInteger mode = saved == nil ? GalaxyPadAspectRatioOriginal : saved.integerValue;
    if (mode < GalaxyPadAspectRatioOriginal || mode > GalaxyPadAspectRatioFillScreen)
        return GalaxyPadAspectRatioOriginal;
    return (GalaxyPadAspectRatioMode)mode;
}

- (void)setAspectRatioMode:(GalaxyPadAspectRatioMode)aspectRatioMode {
    NSInteger mode = aspectRatioMode;
    if (mode < GalaxyPadAspectRatioOriginal || mode > GalaxyPadAspectRatioFillScreen)
        mode = GalaxyPadAspectRatioOriginal;
    [[NSUserDefaults standardUserDefaults] setInteger:mode
                                               forKey:@"GalaxyPadAspectRatioMode"];
}

- (BOOL)showFPSCounter {
    return [[NSUserDefaults standardUserDefaults] boolForKey:@"GalaxyPadShowFPSCounter"];
}

- (NSInteger)mainVolume {
    id saved = [NSUserDefaults.standardUserDefaults objectForKey:@"GalaxyPadMainVolume"];
    double value = [saved isKindOfClass:NSNumber.class] ? [saved doubleValue] : 100;
    return std::isfinite(value) ? (NSInteger)MAX(0, MIN(100, value)) : 100;
}
- (void)setMainVolume:(NSInteger)value {
    [NSUserDefaults.standardUserDefaults setInteger:MAX(0, MIN(100, value)) forKey:@"GalaxyPadMainVolume"];
}
- (BOOL)mainAudioMuted {
    return [NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadMainAudioMuted"];
}
- (void)setMainAudioMuted:(BOOL)value {
    [NSUserDefaults.standardUserDefaults setBool:value forKey:@"GalaxyPadMainAudioMuted"];
}

- (GalaxyPadGyroPointerSource)gyroPointerSource {
    id saved=[NSUserDefaults.standardUserDefaults objectForKey:@"GalaxyPadGyroPointerSource"];
    NSInteger value=[saved isKindOfClass:NSNumber.class] ? [saved integerValue] : 0;
    return value>=0 && value<=2 ? (GalaxyPadGyroPointerSource)value : GalaxyPadGyroPointerOff;
}
- (void)setGyroPointerSource:(GalaxyPadGyroPointerSource)value {
    [NSUserDefaults.standardUserDefaults setInteger:value>=0 && value<=2 ? value : 0
      forKey:@"GalaxyPadGyroPointerSource"];
}
- (CGFloat)gyroPointerSensitivity {
    id saved=[NSUserDefaults.standardUserDefaults objectForKey:@"GalaxyPadGyroPointerSensitivity"];
    double value=[saved isKindOfClass:NSNumber.class] ? [saved doubleValue] : 1;
    return std::isfinite(value) ? MAX(.5,MIN(1.5,value)) : 1;
}
- (void)setGyroPointerSensitivity:(CGFloat)value {
    [NSUserDefaults.standardUserDefaults setDouble:std::isfinite(value) ? MAX(.5,MIN(1.5,value)) : 1
      forKey:@"GalaxyPadGyroPointerSensitivity"];
}
- (BOOL)gyroPointerInvertY {
    return [NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadGyroPointerInvertY"];
}
- (void)setGyroPointerInvertY:(BOOL)value {
    [NSUserDefaults.standardUserDefaults setBool:value forKey:@"GalaxyPadGyroPointerInvertY"];
}
- (CGFloat)touchTiltSensitivity {
    id saved = [NSUserDefaults.standardUserDefaults objectForKey:@"GalaxyPadTouchTiltSensitivity"];
    double value = [saved isKindOfClass:NSNumber.class] ? [saved doubleValue] : 1.0;
    return std::isfinite(value) ? MAX(0.5, MIN(1.5, value)) : 1.0;
}
- (void)setTouchTiltSensitivity:(CGFloat)value {
    [NSUserDefaults.standardUserDefaults setDouble:std::isfinite(value) ? MAX(0.5, MIN(1.5, value)) : 1.0
        forKey:@"GalaxyPadTouchTiltSensitivity"];
}
- (BOOL)touchTiltInvertY {
    return [NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadTouchTiltInvertY"];
}
- (void)setTouchTiltInvertY:(BOOL)value {
    [NSUserDefaults.standardUserDefaults setBool:value forKey:@"GalaxyPadTouchTiltInvertY"];
}

- (void)setShowFPSCounter:(BOOL)showFPSCounter {
    [[NSUserDefaults standardUserDefaults] setBool:showFPSCounter
                                            forKey:@"GalaxyPadShowFPSCounter"];
}

- (BOOL)hideTouchControlsWhenControllerConnected {
    NSNumber *value = [[NSUserDefaults standardUserDefaults] objectForKey:@"GalaxyPadHideControlsOnController"];
    return value == nil ? YES : value.boolValue;
}

- (void)setHideTouchControlsWhenControllerConnected:(BOOL)value {
    [[NSUserDefaults standardUserDefaults] setBool:value forKey:@"GalaxyPadHideControlsOnController"];
}

- (CGFloat)controlOpacity {
    NSNumber *value = [[NSUserDefaults standardUserDefaults] objectForKey:@"GalaxyPadControlOpacity"];
    if (value == nil)
        return 0.55; // Galaxy's opening/dialogue text shares the lower playfield.
    return MAX(0.25, MIN(1.0, value.doubleValue));
}

- (void)setControlOpacity:(CGFloat)controlOpacity {
    [[NSUserDefaults standardUserDefaults] setDouble:MAX(0.25, MIN(1.0, controlOpacity))
                                              forKey:@"GalaxyPadControlOpacity"];
}

- (CGFloat)controlSizeScale {
    NSNumber *value = [[NSUserDefaults standardUserDefaults] objectForKey:@"GalaxyPadControlSizeScale"];
    if (value == nil)
        return 1.0;
    return MAX(0.70, MIN(1.35, value.doubleValue));
}

- (void)setControlSizeScale:(CGFloat)controlSizeScale {
    [[NSUserDefaults standardUserDefaults] setDouble:MAX(0.70, MIN(1.35, controlSizeScale))
                                              forKey:@"GalaxyPadControlSizeScale"];
}

- (BOOL)editingControlLayout {
    return [[NSUserDefaults standardUserDefaults] boolForKey:@"GalaxyPadEditingControlLayout"];
}

- (void)setEditingControlLayout:(BOOL)editingControlLayout {
    [[NSUserDefaults standardUserDefaults] setBool:editingControlLayout forKey:@"GalaxyPadEditingControlLayout"];
}

- (CGFloat)sizeScaleForControl:(NSString *)identifier {
    NSNumber *saved = _controlSizeScales[identifier];
    if (saved == nil)
        return 1.0;
    return MAX(0.60, MIN(1.75, saved.doubleValue));
}

- (void)setSizeScale:(CGFloat)scale forControl:(NSString *)identifier {
    _controlSizeScales[identifier] = @(MAX(0.60, MIN(1.75, scale)));
    [[NSUserDefaults standardUserDefaults] setObject:_controlSizeScales
                                              forKey:@"GalaxyPadControlSizeScales"];
}

- (void)resetControlSizeScales {
    [_controlSizeScales removeAllObjects];
    [[NSUserDefaults standardUserDefaults] removeObjectForKey:@"GalaxyPadControlSizeScales"];
}

- (NSString *)retainedGameDataPath {
    return [[NSUserDefaults standardUserDefaults] stringForKey:@"GalaxyPadRetainedGameDataPath"];
}

- (void)setRetainedGameDataPath:(NSString *)retainedGameDataPath {
    if (retainedGameDataPath == nil) {
        [[NSUserDefaults standardUserDefaults] removeObjectForKey:@"GalaxyPadRetainedGameDataPath"];
    } else {
        [[NSUserDefaults standardUserDefaults] setObject:retainedGameDataPath
                                                  forKey:@"GalaxyPadRetainedGameDataPath"];
    }
}

- (NSString *)extractedGameRoot {
    return [[NSUserDefaults standardUserDefaults] stringForKey:@"GalaxyPadExtractedGameRoot"];
}

- (void)setExtractedGameRoot:(NSString *)extractedGameRoot {
    if (extractedGameRoot == nil) {
        [[NSUserDefaults standardUserDefaults] removeObjectForKey:@"GalaxyPadExtractedGameRoot"];
    } else {
        [[NSUserDefaults standardUserDefaults] setObject:extractedGameRoot
                                                  forKey:@"GalaxyPadExtractedGameRoot"];
    }
}

- (void)synchronize {
    [[NSUserDefaults standardUserDefaults] synchronize];
}

@end
