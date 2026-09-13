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
      @"Authorization: Bearer sentinel-bearer", @"api_key=sentinel-key",
      @"password=\"sentinel secret phrase\"", @"contact=sentinel@example.invalid",
      @"C:\\Users\\sentinel name\\private game.wbfs",
      @"/Users/sentinel name/Private Folder/file.dat",
      @"12345678-1234-1234-1234-123456789abc", @"00000000-0000000000000000",
      @"0123456789012345678901234567890123456789",
      @"192.168.12.45", @"fe80::1234:abcd:5678:abcd", @"ab:cd:ef:12:34:56"
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
    assert([GalaxyPadRedactedString(@"2026-09-13T09:18:08.432Z lifecycle paused")
      isEqualToString:@"2026-09-13T09:18:08.432Z lifecycle paused"]);
    NSDictionary *draft = GalaxyPadDiagnosticsIssueDraft(@{
      @"problem": @"Audio & video + freeze? #1 = 50% 🎮",
      @"context": @"日本語のエリア", @"frequency": @"Sometimes"},
      @"state=paused dmaUnderruns=12 frames=60");
    NSURL *issueURL = GalaxyPadDiagnosticsIssueURL(draft);
    assert(issueURL && [issueURL.host isEqualToString:@"github.com"]);
    assert([issueURL.path isEqualToString:@"/chrissotraidis/galaxypad/issues/new"]);
    NSURLComponents *components = [NSURLComponents componentsWithURL:issueURL resolvingAgainstBaseURL:NO];
    assert(components.queryItems.count == 2 && !components.fragment);
    assert(![components.percentEncodedQuery containsString:@"+"]);
    assert([components.percentEncodedQuery containsString:@"%2B"]);
    assert([components.queryItems[0].value isEqualToString:draft[@"title"]]);
    assert([components.queryItems[1].value isEqualToString:draft[@"body"]]);
    assert([draft[@"body"] containsString:@"dmaUnderruns=12"]);
    assert([draft[@"body"] containsString:@"日本語のエリア"]);
    assert([draft[@"body"] containsString:@"Sometimes"]);
    assert(!GalaxyPadDiagnosticsIssueURL(@{}));
    assert(!GalaxyPadDiagnosticsIssueURL(@{@"title": @"x", @"body": @""}));
    NSDictionary *empty = GalaxyPadDiagnosticsIssueDraft(@{}, @"");
    assert([empty[@"title"] isEqualToString:@"[Bug]: GalaxyPad problem"]);
    assert(GalaxyPadDiagnosticsIssueURL(empty));
    NSString *huge = [@"🎮日本語👨‍👩‍👧‍👦&+=%?#" stringByPaddingToLength:20000
      withString:@"🎮日本語👨‍👩‍👧‍👦&+=%?#" startingAtIndex:0];
    NSDictionary *bounded = GalaxyPadDiagnosticsIssueDraft(@{
      @"problem": huge, @"context": huge, @"frequency": huge}, huge);
    assert([bounded[@"title"] dataUsingEncoding:NSUTF8StringEncoding]);
    assert([bounded[@"body"] dataUsingEncoding:NSUTF8StringEncoding]);
    assert(GalaxyPadDiagnosticsIssueURL(bounded).absoluteString.length <= 7500);
    assert(GalaxyPadDiagnosticsIssueURL(bounded));
    NSString *allSecrets = [secrets componentsJoinedByString:@"\n"];
    NSDictionary *privateDraft = GalaxyPadDiagnosticsIssueDraft(@{
      @"problem": allSecrets, @"context": allSecrets, @"frequency": allSecrets}, allSecrets);
    assert(![privateDraft.description containsString:@"sentinel"]);
    assert(![privateDraft.description containsString:@"Private Folder"]);
    assert(![privateDraft.description containsString:@"123456789abc"]);
    if (argc == 2) {
      testRoot = @(argv[1]);
      assert([testRoot isAbsolutePath]);
      GalaxyPadDiagnosticsStart();
      GalaxyPadLogRuntimeEvent(@"warning", @"runtime", @"RAW-GUEST-SENTINEL /private/disc/main.dol");
      GalaxyPadLogRuntimeEvent(@"error", @"core", @"boot_failed");
      assert([GalaxyPadKnownRuntimeEvent(@"core", @"boot_failed EVENT-SECRET")
        isEqualToString:@"runtime details omitted for privacy"]);
      NSString *queueFull = @"Granule Queue has completely filled and audio samples are being dropped. ";
      for (unsigned i = 0; i < 12; ++i) {
        GalaxyPadLogRuntimeEvent(@"warning", @"audio", [queueFull stringByAppendingString:
          @"token=EVENT-SECRET /private/disc/main.dol guest=0xDEADBEEF"]);
      }
      GalaxyPadLogRuntimeEvent(@"warning", @"audio", @"unknown audio event EVENT-SECRET");
      GalaxyPadLogRuntimeEvent(@"error", @"audio", @"needed_frames would overflow m_scratch_buffer: EVENT-SECRET");
      GalaxyPadLogRuntimeEvent(@"error", @"video", @"Failed to parse shader /private/shader.metal EVENT-SECRET");
      GalaxyPadLogRuntimeEvent(@"warning", @"video", @"Failed to start shader compiler worker thread. EVENT-SECRET");
      GalaxyPadLogRuntimeEvent(@"error", @"host-gpu", @"Failed to compile compute pipeline /private/shader.metal EVENT-SECRET");
      GalaxyPadLogRuntimeEvent(@"error", @"powerpc", @"IntCPU: Unknown instruction DEADBEEF at PC = EVENT-SECRET");
      // A phrase in the wrong category, and arbitrary fallback text, must not
      // become diagnoses or leak raw data. No hashes of unknown messages.
      assert([GalaxyPadKnownRuntimeEvent(@"powerpc", queueFull) isEqualToString:@"runtime details omitted for privacy"]);
      assert([GalaxyPadKnownRuntimeEvent(@"powerpc", @"fallback EVENT-SECRET") isEqualToString:@"runtime details omitted for privacy"]);
      assert([GalaxyPadKnownRuntimeEvent(@"audio", @"") isEqualToString:@"runtime details omitted for privacy"]);
      GalaxyPadLog(@"controller raw_buttons=1234 menu=1 options=0");
      GalaxyPadLog(@"simulator input accepted buttons=1234 pointer=(0.1,0.2)");
      NSError *error = nil;
      NSURL *reportURL = GalaxyPadDiagnosticsReportURL(@"test",
        @{@"problem": @"token=REPORT-SECRET /Users/example/private.wbfs"}, @"state=paused", &error);
      assert(reportURL && !error);
      assert([reportURL.path hasPrefix:[testRoot stringByAppendingString:@"/"]]);
      NSString *report = [NSString stringWithContentsOfURL:reportURL encoding:NSUTF8StringEncoding error:&error];
      assert(!error && [report containsString:@"state=paused"]);
      assert([report containsString:@"runtime details omitted"]);
      assert([report containsString:@"category=core count=1 message=boot_failed"]);
      assert([report containsString:@"category=audio count=12 message=audio_granule_queue_full_samples_dropped"]);
      assert([report containsString:@"category=audio count=1 message=runtime details omitted"]);
      for (NSString *code in @[@"audio_resampling_scratch_buffer_overflow", @"shader_parse_failure",
          @"shader_compiler_worker_failure", @"shader_compute_pipeline_compile_failure", @"powerpc_unknown_instruction"])
        assert([report containsString:code]);
      NSString *runtimeLog = [NSString stringWithContentsOfFile:GalaxyPadDiagnosticsLogPath()
        encoding:NSUTF8StringEncoding error:nil];
      assert([runtimeLog containsString:@"count=10 message=audio_granule_queue_full_samples_dropped"]);
      assert(![runtimeLog containsString:@"count=12 message=audio_granule_queue_full_samples_dropped"]);
      for (NSString *forbidden in @[@"RAW-GUEST-SENTINEL", @"REPORT-SECRET", @"EVENT-SECRET", @"DEADBEEF", @"shader.metal", @"private.wbfs", @"main.dol", @"github.com", @"raw_buttons", @"pointer=("])
        assert(![report containsString:forbidden]);
      // A blocked writer cannot create an unbounded queue or block the caller.
      dispatch_suspend(GalaxyPadPerformanceLogQueue());
      GalaxyPadLogPerformanceWindow(@[@"async frames=60 /Users/test/ASYNC-SECRET.bin"]);
      GalaxyPadLogPerformanceWindow(@[@"DROPPED-WINDOW-SENTINEL"]);
      dispatch_resume(GalaxyPadPerformanceLogQueue());
      dispatch_sync(GalaxyPadPerformanceLogQueue(), ^{});
      runtimeLog = [NSString stringWithContentsOfFile:GalaxyPadDiagnosticsLogPath()
        encoding:NSUTF8StringEncoding error:nil];
      assert([runtimeLog containsString:@"async frames=60"]);
      assert([runtimeLog containsString:@"performance windows dropped=1 reason=writer_busy"]);
      assert(![runtimeLog containsString:@"ASYNC-SECRET"]);
      assert(![runtimeLog containsString:@"DROPPED-WINDOW-SENTINEL"]);
      // Force a size-boundary crossing without emitting megabytes to NSLog.
      NSData *padding = [NSMutableData dataWithLength:1024 * 1024];
      assert([padding writeToFile:GalaxyPadDiagnosticsLogPath() atomically:YES]);
      GalaxyPadLog(@"rotation sentinel");
      NSDictionary *attributes = [NSFileManager.defaultManager attributesOfItemAtPath:GalaxyPadDiagnosticsLogPath() error:&error];
      assert(!error && attributes.fileSize < 4096);
      attributes = [NSFileManager.defaultManager attributesOfItemAtPath:GalaxyPadDiagnosticsPreviousLogPath() error:&error];
      assert(!error && attributes.fileSize == 1024 * 1024);
      // Export failure must return nil/error, never a usable stale file URL.
      testRoot = [testRoot stringByAppendingPathComponent:@"blocked-by-file"];
      assert([@"file" writeToFile:testRoot atomically:YES encoding:NSUTF8StringEncoding error:nil]);
      error = nil;
      assert(!GalaxyPadDiagnosticsReportURL(@"test", @{}, @"", &error));
      assert(error);
    }
    puts("GalaxyPad diagnostic redaction and bounded formatting checks pass");
  }
}
