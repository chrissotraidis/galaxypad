// SPDX-License-Identifier: GPL-3.0-or-later
#import <Foundation/Foundation.h>
#include "GalaxyPadControllerMapping.h"
@interface GalaxyPadControllerMappingStore : NSObject
+ (galaxypad::ControllerMapping)mapping;
+ (void)setMapping:(galaxypad::ControllerMapping)mapping;
+ (void)reset;
@end
