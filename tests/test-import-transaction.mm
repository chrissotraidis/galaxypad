// SPDX-License-Identifier: GPL-3.0-or-later
#import "../apple/ios/GalaxyPadImportTransaction.h"
#import "../apple/ios/GalaxyPadDiscExtractor.h"
#include <cassert>
#include <unistd.h>
#include <fcntl.h>
#include "fixtures/import/GalaxyPadDiscIdentity.h"

static int extractorMode=0, extractorCalls=0;

@interface TestSpaceImport : GalaxyPadImportTransaction
@end
@implementation TestSpaceImport
- (uint64_t)availableImportBytes { return 9ULL << 30; }
@end
@interface LowSpaceImport : TestSpaceImport
@end
@implementation LowSpaceImport
- (uint64_t)availableImportBytes { return (9ULL << 30)-1; }
@end

// A controlled extractor isolates transaction behavior, not Wii extraction.
@implementation GalaxyPadDiscExtractor
+ (void)extractImageAtPath:(NSString *)image toDirectory:(NSString *)destination
    progress:(void (^)(NSString *,double))progress completion:(void (^)(BOOL,NSString *))completion {
  (void)image; (void)destination; (void)progress; (void)completion; abort();
}
+ (void)extractImageAtPath:(NSString *)image toDirectory:(NSString *)destination
    cancelled:(BOOL (^)(void))cancelled progress:(void (^)(NSString *,double))progress
    completion:(void (^)(BOOL,NSString *))completion {
  (void)progress;
  assert(extractorMode!=0 && NSThread.isMainThread);
  assert(!cancelled());
  ++extractorCalls;
  assert([NSFileManager.defaultManager attributesOfItemAtPath:image error:nil].fileSize==GalaxyPadImageBytes);
  assert([NSFileManager.defaultManager createDirectoryAtPath:destination withIntermediateDirectories:NO attributes:nil error:nil]);
  assert([[@"synthetic extracted marker" dataUsingEncoding:NSUTF8StringEncoding]
    writeToFile:[destination stringByAppendingPathComponent:@"marker"] atomically:YES]);
  completion(extractorMode==2,extractorMode==2?nil:@"Synthetic extraction failure.");
}
@end

int main() {
  @autoreleasepool {
    char pattern[]="/tmp/galaxypad-transaction-test.XXXXXX";
    assert(mkdtemp(pattern));
    NSURL *root=[NSURL fileURLWithFileSystemRepresentation:pattern isDirectory:YES relativeToURL:nil];
    NSURL *source=[root URLByAppendingPathComponent:@"tiny.wbfs"];
    NSData *sentinel=[@"original unchanged" dataUsingEncoding:NSUTF8StringEncoding];
    assert([sentinel writeToURL:source atomically:YES]);
    for (int cancelled=0;cancelled<2;++cancelled) {
      GalaxyPadImportTransaction *transaction=[[TestSpaceImport alloc] initWithRoot:root];
      NSString *error=nil;
      assert(![transaction activateWithRuntimeStopped:YES error:&error] && error);
      if (cancelled) [transaction cancel];
      __block BOOL done=NO;
      [transaction prepareImage:source progress:nil completion:^(BOOL ok,NSString *message) {
        assert(!ok && message.length && !transaction.preparing && !transaction.verified);
        if (cancelled) assert([message isEqualToString:@"Import cancelled."]);
        done=YES;
      }];
      NSDate *deadline=[NSDate dateWithTimeIntervalSinceNow:5];
      while (!done && deadline.timeIntervalSinceNow>0)
        [NSRunLoop.currentRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.01]];
      assert(done);
      __block BOOL rejected=NO;
      [transaction prepareImage:source progress:nil completion:^(BOOL ok,NSString *message) {
        assert(!ok && message.length); rejected=YES;
      }];
      assert(rejected);
      assert([[NSData dataWithContentsOfURL:source] isEqualToData:sentinel]);
      assert([NSFileManager.defaultManager contentsOfDirectoryAtURL:root
        includingPropertiesForKeys:nil options:0 error:nil].count==1);
    }
    // Test-only 32 MiB sparse source; production identity and extractor unchanged.
    NSURL *image=[root URLByAppendingPathComponent:@"copy-fixture.wbfs"];
    int fd=open(image.fileSystemRepresentation,O_CREAT|O_EXCL|O_RDWR,0600);
    assert(fd>=0 && ftruncate(fd,GalaxyPadImageBytes)==0 && close(fd)==0);
    // Deterministic capacity rejection, no real disk filling or staging writes.
    NSUInteger beforeCount=[NSFileManager.defaultManager contentsOfDirectoryAtURL:root
      includingPropertiesForKeys:nil options:0 error:nil].count;
    LowSpaceImport *lowSpace=[[LowSpaceImport alloc] initWithRoot:root];
    __block BOOL lowSpaceDone=NO;
    [lowSpace prepareImage:image progress:nil completion:^(BOOL ok,NSString *message) {
      assert(!ok && [message containsString:@"9 GiB"] && !lowSpace.preparing && !lowSpace.verified);
      lowSpaceDone=YES;
    }];
    NSDate *spaceDeadline=[NSDate dateWithTimeIntervalSinceNow:5];
    while (!lowSpaceDone && spaceDeadline.timeIntervalSinceNow>0)
      [NSRunLoop.currentRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.01]];
    assert(lowSpaceDone && extractorCalls==0);
    assert([NSFileManager.defaultManager contentsOfDirectoryAtURL:root
      includingPropertiesForKeys:nil options:0 error:nil].count==beforeCount);
    NSURL *save=[root URLByAppendingPathComponent:@"save-sentinel"];
    assert([sentinel writeToURL:save atomically:YES]);
    for (int mode=0;mode<4;++mode) {
      extractorMode=mode>=2?2:mode;
      extractorCalls=0;
      GalaxyPadImportTransaction *transaction=[[TestSpaceImport alloc] initWithRoot:root];
      __block BOOL done=NO, sawCopy=NO;
      [transaction prepareImage:image progress:^(NSString *message,double fraction) {
        assert(NSThread.isMainThread && [message isEqualToString:@"Copying selected image"]);
        assert(fraction>0 && fraction<=0.25);
        sawCopy=YES;
        if (mode==0) [transaction cancel];
      } completion:^(BOOL ok,NSString *message) {
        assert(NSThread.isMainThread && !transaction.preparing);
        assert(ok==(mode>=2) && transaction.verified==ok);
        if (!ok) assert(message.length);
        done=YES;
      }];
      __block BOOL workerDiscardRejected=NO;
      [transaction discardUnactivatedStage:^(BOOL ok,NSString *message) {
        assert(!ok && message.length); workerDiscardRejected=YES;
      }];
      assert(workerDiscardRejected);
      NSDate *deadline=[NSDate dateWithTimeIntervalSinceNow:10];
      while (!done && deadline.timeIntervalSinceNow>0)
        [NSRunLoop.currentRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.01]];
      assert(done && sawCopy && extractorCalls==(mode==0?0:1));
      if (mode==2) {
        NSString *error=nil;
        assert(![transaction activateWithRuntimeStopped:NO error:&error]);
        assert(transaction.verified);
        assert([transaction activateWithRuntimeStopped:YES error:&error]);
        assert(!transaction.verified && !transaction.previousDataRetained);
        assert(![transaction activateWithRuntimeStopped:YES error:&error]);
        assert([NSFileManager.defaultManager fileExistsAtPath:
          [[root URLByAppendingPathComponent:@"GameData/RMGE01/marker"] path]]);
        __block BOOL rejected=NO;
        [transaction discardUnactivatedStage:^(BOOL ok,NSString *message) {
          assert(!ok && message.length); rejected=YES;
        }];
        assert(rejected);
      }
      if (mode==3) {
        [transaction cancel]; // Verified-but-cancelled must remain discardable.
        assert(!transaction.verified);
        __block BOOL discarded=NO;
        [transaction discardUnactivatedStage:^(BOOL ok,NSString *message) {
          assert(ok && !message && !transaction.preparing && NSThread.isMainThread);
          discarded=YES;
        }];
        NSDate *limit=[NSDate dateWithTimeIntervalSinceNow:5];
        while (!discarded && limit.timeIntervalSinceNow>0)
          [NSRunLoop.currentRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.01]];
        assert(discarded);
        assert([NSFileManager.defaultManager fileExistsAtPath:
          [[root URLByAppendingPathComponent:@"GameData/RMGE01/marker"] path]]);
      }
      for (NSString *entry in [NSFileManager.defaultManager contentsOfDirectoryAtPath:root.path error:nil])
        assert(![entry hasPrefix:@"GameData.import-"]);
      assert([[NSData dataWithContentsOfURL:save] isEqualToData:sentinel]);
      assert([NSFileManager.defaultManager attributesOfItemAtPath:image.path error:nil].fileSize==GalaxyPadImageBytes);
      NSData *unchanged=[NSData dataWithContentsOfURL:image];
      assert(unchanged.length==GalaxyPadImageBytes);
      const unsigned char *bytes=(const unsigned char *)unchanged.bytes;
      for (NSUInteger i=0;i<unchanged.length;++i) assert(bytes[i]==0);
    }
    assert([NSFileManager.defaultManager removeItemAtURL:root error:nil]);
    puts("Import storage threshold, rejection, copy cancellation, extraction failure cleanup and activation gates passed");
  }
}
