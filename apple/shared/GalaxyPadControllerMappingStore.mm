// SPDX-License-Identifier: GPL-3.0-or-later
// Versioned app-local persistence adapted from SunPadControllerMappingStore,
// SunPad fcdc1411e483a86ca80ec82e7cd53839c51ff865.
#import "GalaxyPadControllerMappingStore.h"
static NSString *const key=@"GalaxyPadControllerButtonMappingV1";
@implementation GalaxyPadControllerMappingStore
+ (galaxypad::ControllerMapping)mapping {
  NSArray *saved=[NSUserDefaults.standardUserDefaults arrayForKey:key];
  galaxypad::ControllerMapping mapping;
  if (saved.count!=5) return mapping;
  for (unsigned i=0;i<5;++i) {
    id value=saved[i];
    if (![value isKindOfClass:NSNumber.class] || !std::isfinite([value doubleValue]) || [value doubleValue]<0 ||
        [value doubleValue]>4 || [value doubleValue]!=[value unsignedIntValue]) return {};
    mapping.physical[i]=[value unsignedIntValue];
  }
  return mapping.valid()?mapping:galaxypad::ControllerMapping{};
}
+ (void)setMapping:(galaxypad::ControllerMapping)mapping {
  if (!mapping.valid()) mapping={};
  NSMutableArray *saved=[NSMutableArray arrayWithCapacity:5];
  for (unsigned value:mapping.physical) [saved addObject:@(value)];
  [NSUserDefaults.standardUserDefaults setObject:saved forKey:key];
}
+ (void)reset { [NSUserDefaults.standardUserDefaults removeObjectForKey:key]; }
@end
