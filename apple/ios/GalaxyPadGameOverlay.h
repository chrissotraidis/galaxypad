// SPDX-License-Identifier: GPL-3.0-or-later
// Adapted from SunPadGameOverlay.h at fcdc1411e483a86ca80ec82e7cd53839c51ff865.
#pragma once
#import <UIKit/UIKit.h>
#include "../shared/GalaxyPadInput.h"
@class GalaxyPadGameOverlay;
@protocol GalaxyPadGameOverlayDelegate <NSObject>
@optional
- (void)gameOverlayRequestsGameDataChange:(GalaxyPadGameOverlay *)overlay;
- (void)gameOverlayRequestsGameDataFolderImport:(GalaxyPadGameOverlay *)overlay;
- (void)gameOverlayRequestsGameDataRemoval:(GalaxyPadGameOverlay *)overlay;
- (void)gameOverlayRequestsGameDataStatus:(GalaxyPadGameOverlay *)overlay;
- (void)gameOverlayRequestsControllerMapping:(GalaxyPadGameOverlay *)overlay;
- (void)gameOverlayRequestsDiagnosticLog:(GalaxyPadGameOverlay *)overlay;
- (void)gameOverlayRequestsAbout:(GalaxyPadGameOverlay *)overlay;
- (void)gameOverlayRequestsDevelopmentCheckpoint:(GalaxyPadGameOverlay *)overlay;
- (void)gameOverlayRequestsDevelopmentCheckpointRestore:(GalaxyPadGameOverlay *)overlay;
@required
- (void)gameOverlayRequestsProblemReport:(GalaxyPadGameOverlay *)overlay;
@end
@interface GalaxyPadGameOverlay : UIView
@property(nonatomic, weak) id<GalaxyPadGameOverlayDelegate> delegate;
@property(nonatomic, copy) void (^inputChanged)(galaxypad::InputState state);
@property(nonatomic, copy) CGRect (^viewportProvider)(void);
@property(nonatomic, copy) void (^nativeUIChanged)(void);
@property(nonatomic, copy) void (^stopRequested)(void);
@property(nonatomic, readonly) BOOL blocksGameplay;
@property(nonatomic, readonly) BOOL nativeMenuVisible;
@property(nonatomic) BOOL gameplayAvailable;
- (void)setTouchControlsHidden:(BOOL)hidden animated:(BOOL)animated;
- (void)refreshControllerVisibility;
- (void)presentNativePause;
@property(nonatomic, readonly) BOOL nativePauseVisible;
- (void)toggleNativePause;
- (void)applySettings;
- (void)reset;
@end
