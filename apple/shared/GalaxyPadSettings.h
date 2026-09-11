// SPDX-License-Identifier: GPL-3.0-or-later
// Adapted from SunPad fcdc1411e483a86ca80ec82e7cd53839c51ff865,
// apple/shared/SunPadSettings.h. Galaxy uses native Wii widescreen;
// Sunshine timing experiments and GameCube camera settings are not imported.
#pragma once

#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

typedef NS_ENUM(NSInteger, GalaxyPadAspectRatioMode) {
    GalaxyPadAspectRatioOriginal = 0,
    GalaxyPadAspectRatioWidescreen = 1,
    GalaxyPadAspectRatioFillScreen = 2,
};

/* Persisted GalaxyPad settings shared by macOS, iOS, and iPadOS. Stored in
 * NSUserDefaults so each platform keeps the same user-facing options.
 */
@interface GalaxyPadSettings : NSObject

+ (instancetype)sharedSettings;

/* Render-resolution scale. 1 = native Wii EFB, 2..4 = multiplier. */
@property(nonatomic, assign) NSInteger renderScale;
- (float)renderScaleFloat;

/* Output aspect ratio. Native 4:3 is the iPad default. This affects game rendering, never
 * touch-control layout. */
@property(nonatomic, assign) GalaxyPadAspectRatioMode aspectRatioMode;

/* Optional developer performance overlay. Off by default for normal play. */
@property(nonatomic, assign) BOOL showFPSCounter;
/* Main game output; independent of the unfinished Wii Remote speaker route. */
@property(nonatomic, assign) NSInteger mainVolume; // 0..100, default 100
@property(nonatomic, assign) BOOL mainAudioMuted;

/* Touch-control presentation. */
@property(nonatomic, assign) BOOL hideTouchControlsWhenControllerConnected;
@property(nonatomic, assign) CGFloat controlOpacity;   // 0.25..1
@property(nonatomic, assign) CGFloat controlSizeScale; // 0.70..1.35
@property(nonatomic, assign) BOOL editingControlLayout;
/* Touch tilt only; movement and physical-controller axes remain unchanged. */
@property(nonatomic, assign) CGFloat touchTiltSensitivity; // 0.5..1.5, default 1
@property(nonatomic, assign) BOOL touchTiltInvertY;

/* Per-control size overrides (1.0 = default), keyed by control identifier. */
- (CGFloat)sizeScaleForControl:(NSString *)identifier;
- (void)setSizeScale:(CGFloat)scale forControl:(NSString *)identifier;
- (void)resetControlSizeScales;

/* Save/load the retained game-data path (Application Support on mobile). */
@property(nonatomic, copy, nullable) NSString *retainedGameDataPath;

/* Extracted game tree (sys/ + files/) produced from the retained image. */
@property(nonatomic, copy, nullable) NSString *extractedGameRoot;

- (void)synchronize;

@end

NS_ASSUME_NONNULL_END
