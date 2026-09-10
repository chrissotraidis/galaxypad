// SPDX-License-Identifier: GPL-3.0-or-later
// Redirect only this test translation unit's directories into a supplied temp
// root; no app/user diagnostic directory is accessed by integration checks.
#import <Foundation/Foundation.h>
static NSString *testRoot;
static NSArray<NSString *> *TestDirectories(NSSearchPathDirectory directory,
    NSSearchPathDomainMask domain, BOOL expand) {
  (void)directory; (void)domain; (void)expand;
  return @[testRoot];
}
#define NSSearchPathForDirectoriesInDomains TestDirectories
#import "../apple/shared/GalaxyPadDiagnostics.mm"
#undef NSSearchPathForDirectoriesInDomains
#include <cassert>
int main(int argc, char **argv) {
  @autoreleasepool {
    NSArray<NSString *> *secrets = @[
      @"/Users/diagnostic-test/private/game.wbfs",
      @"file:///private/test/save.bin",
      @"https://user:credential@example.invalid/private",
      @"token=sentinel-token", @"password:sentinel-password",
      @"Authorization: Bearer sentinel-bearer", @"api_key=sentinel-key"
    ];
    for (NSString *secret in secrets) {
      NSString *result = GalaxyPadRedactedString(secret);
      assert(![result isEqualToString:secret]);
      assert(![result containsString:@"sentinel"]);
      assert(![result containsString:@"credential"]);
      assert(![result containsString:@"game.wbfs"]);
      assert(![result containsString:@"save.bin"]);
    }
    NSString *ownPath = [NSHomeDirectory() stringByAppendingPathComponent:@"secret/save.bin"];
    assert(![GalaxyPadRedactedString(ownPath) containsString:@"save.bin"]);
    assert([GalaxyPadSingleLine(@"  ready\npaused\rresumed  ", 100)
      isEqualToString:@"ready paused resumed"]);
    assert(GalaxyPadSingleLine([@"x" stringByPaddingToLength:10000 withString:@"x" startingAtIndex:0], 100).length <= 101);
    assert([GalaxyPadRedactedString(@"frames=60 scale=1 state=paused")
      isEqualToString:@"frames=60 scale=1 state=paused"]);
    if (argc == 2) {
      testRoot = @(argv[1]);
      assert([testRoot isAbsolutePath]);
      GalaxyPadDiagnosticsStart();
      GalaxyPadLogRuntimeEvent(@"warning", @"runtime", @"RAW-GUEST-SENTINEL /private/disc/main.dol");
      NSError *error = nil;
      NSURL *reportURL = GalaxyPadDiagnosticsReportURL(@"test",
        @{@"problem": @"token=REPORT-SECRET /Users/example/private.wbfs"}, @"state=paused", &error);
      assert(reportURL && !error);
      assert([reportURL.path hasPrefix:[testRoot stringByAppendingString:@"/"]]);
      NSString *report = [NSString stringWithContentsOfURL:reportURL encoding:NSUTF8StringEncoding error:&error];
      assert(!error && [report containsString:@"state=paused"]);
      assert([report containsString:@"runtime details omitted"]);
      for (NSString *forbidden in @[@"RAW-GUEST-SENTINEL", @"REPORT-SECRET", @"private.wbfs", @"main.dol", @"github.com"])
        assert(![report containsString:forbidden]);
      // Force a size-boundary crossing without emitting megabytes to NSLog.
      NSData *padding = [NSMutableData dataWithLength:1024 * 1024];
      assert([padding writeToFile:GalaxyPadDiagnosticsLogPath() atomically:YES]);
      GalaxyPadLog(@"rotation sentinel");
      NSDictionary *attributes = [NSFileManager.defaultManager attributesOfItemAtPath:GalaxyPadDiagnosticsLogPath() error:&error];
      assert(!error && attributes.fileSize < 4096);
      attributes = [NSFileManager.defaultManager attributesOfItemAtPath:GalaxyPadDiagnosticsPreviousLogPath() error:&error];
      assert(!error && attributes.fileSize == 1024 * 1024);
    }
    puts("GalaxyPad diagnostic redaction and bounded formatting checks pass");
  }
}
