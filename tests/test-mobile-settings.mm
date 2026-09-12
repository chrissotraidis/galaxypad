// SPDX-License-Identifier: GPL-3.0-or-later
#import "../apple/shared/GalaxyPadSettings.h"
#include <cassert>

// Read-only preference tests: argument-domain overrides never write user settings.
int main() {
  @autoreleasepool {
    NSUserDefaults *defaults = NSUserDefaults.standardUserDefaults;
    NSDictionary *original = [defaults volatileDomainForName:NSArgumentDomain];
    // This read-only test executable never persists preferences. Check the
    // absent-key default separately from explicit saved/argument overrides.
    assert([defaults objectForKey:@"GalaxyPadControlOpacity"] == nil);
    assert([GalaxyPadSettings new].controlOpacity == 0.55);
    NSDictionary *baseline = @{
      @"GalaxyPadRenderScale": @1,
      @"GalaxyPadAspectRatioMode": @1,
      @"GalaxyPadControlOpacity": @0.82,
      @"GalaxyPadControlSizeScale": @1,
      @"GalaxyPadControlSizeScales": @{},
    };
    [defaults setVolatileDomain:baseline forName:NSArgumentDomain];
    GalaxyPadSettings *settings = [GalaxyPadSettings new];
    assert(settings.renderScaleFloat == 1);
    assert(settings.aspectRatioMode == GalaxyPadAspectRatioWidescreen);
    assert(settings.controlOpacity == 0.82);
    assert(settings.controlSizeScale == 1);
    assert([settings sizeScaleForControl:@"A"] == 1);
    NSMutableDictionary *limits = [baseline mutableCopy];
    limits[@"GalaxyPadRenderScale"] = @99;
    limits[@"GalaxyPadAspectRatioMode"] = @99;
    limits[@"GalaxyPadControlOpacity"] = @-1;
    limits[@"GalaxyPadControlSizeScale"] = @99;
    limits[@"GalaxyPadControlSizeScales"] = @{@"A": @99, @"B": @-1};
    [defaults setVolatileDomain:limits forName:NSArgumentDomain];
    settings = [GalaxyPadSettings new];
    assert(settings.renderScale == 4);
    assert(settings.aspectRatioMode == GalaxyPadAspectRatioOriginal);
    assert(settings.controlOpacity == 0.25);
    assert(settings.controlSizeScale == 1.35);
    assert([settings sizeScaleForControl:@"A"] == 1.75);
    assert([settings sizeScaleForControl:@"B"] == 0.60);
    [defaults setVolatileDomain:original forName:NSArgumentDomain];
    puts("SunPad-derived GalaxyPad settings: getter and range checks passed");
  }
}
