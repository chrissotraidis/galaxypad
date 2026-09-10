// SPDX-License-Identifier: GPL-3.0-or-later
// SunPad-derived staged extractor; only the configured exact Galaxy image.
#import <Foundation/Foundation.h>
@interface GalaxyPadDiscExtractor : NSObject
// Caller supplies a new private staging path; existing destinations are rejected.
// Failure leaves staging for the owning import transaction to clean up.
+ (void)extractImageAtPath:(NSString *)imagePath toDirectory:(NSString *)destination
  progress:(void (^)(NSString *status, double fraction))progress
  completion:(void (^)(BOOL ok, NSString *error))completion;
// Cancellation is polled on the worker queue. The block must be thread-safe.
// A current DiscIO file export finishes before cancellation is observed.
+ (void)extractImageAtPath:(NSString *)imagePath toDirectory:(NSString *)destination
  cancelled:(BOOL (^)(void))cancelled
  progress:(void (^)(NSString *status, double fraction))progress
  completion:(void (^)(BOOL ok, NSString *error))completion;
@end
