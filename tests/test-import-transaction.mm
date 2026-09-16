// SPDX-License-Identifier: GPL-3.0-or-later
#import "../apple/ios/GalaxyPadImportTransaction.h"
#import "../apple/ios/GalaxyPadDiscExtractor.h"
#include <cassert>
#include <unistd.h>
#include <fcntl.h>
#include "fixtures/import/GalaxyPadDiscIdentity.h"

// Route production background dispatches to one serial queue. A barrier lets
// the test hold main-thread delivery until the copy worker has been released.
static dispatch_queue_t importWorkers;
static void TestImportDispatchAsync(dispatch_queue_t queue, dispatch_block_t block) {
  dispatch_async(queue==dispatch_get_main_queue()?queue:importWorkers,block);
}
#define dispatch_async TestImportDispatchAsync
#import "../apple/ios/GalaxyPadImportTransaction.mm"
#undef dispatch_async

static int extractorMode=0, extractorCalls=0;
static uint64_t fixtureBytes=GalaxyPadImageBytes;
static std::array<unsigned char,512> fixtureHeader(uint64_t bytes) {
  std::array<unsigned char,512> header{};
  memcpy(header.data(),"WBFS",4);
  uint32_t sectors=static_cast<uint32_t>(bytes>>9);
  for (int i=0;i<4;++i) header[4+i]=sectors>>(24-i*8);
  header[8]=9; header[9]=21; header[12]=1;
  return header;
}

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
  assert([NSFileManager.defaultManager attributesOfItemAtPath:image error:nil].fileSize==fixtureBytes);
  assert([NSFileManager.defaultManager createDirectoryAtPath:destination withIntermediateDirectories:NO attributes:nil error:nil]);
  assert([[@"synthetic extracted marker" dataUsingEncoding:NSUTF8StringEncoding]
    writeToFile:[destination stringByAppendingPathComponent:@"marker"] atomically:YES]);
  completion(extractorMode==2,extractorMode==2?nil:@"Synthetic extraction failure.");
}
@end

int main() {
  @autoreleasepool {
    importWorkers=dispatch_queue_create("galaxypad.import-test-workers",DISPATCH_QUEUE_SERIAL);
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
    // Test-only 32 MiB sparse source; controlled extractor checks copy/activation only.
    NSURL *image=[root URLByAppendingPathComponent:@"copy-fixture.wbfs"];
    int fd=open(image.fileSystemRepresentation,O_CREAT|O_EXCL|O_RDWR,0600);
    assert(fd>=0 && ftruncate(fd,fixtureBytes)==0 && write(fd,fixtureHeader(fixtureBytes).data(),512)==512 && close(fd)==0);
    // A busy UI may deliver progress only after the worker's enclosing block
    // has died. The queued callback must own its values, not lambda references.
    extractorMode=1;
    __block BOOL delayedDone=NO, workerRetired=NO;
    __block unsigned delayedProgress=0;
    TestSpaceImport *delayed=[[TestSpaceImport alloc] initWithRoot:root];
    [delayed prepareImage:image progress:^(NSString *message,double fraction) {
      assert(workerRetired && NSThread.isMainThread);
      assert([message isEqualToString:@"Copying selected image"] && fraction>0 && fraction<=0.25);
      ++delayedProgress;
    } completion:^(BOOL ok,NSString *message) {
      assert(!ok && [message isEqualToString:@"Synthetic extraction failure."]);
      delayedDone=YES;
    }];
    dispatch_sync(importWorkers, ^{});
    workerRetired=YES;
    NSDate *delayedDeadline=[NSDate dateWithTimeIntervalSinceNow:5];
    while (!delayedDone && delayedDeadline.timeIntervalSinceNow>0)
      [NSRunLoop.currentRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.01]];
    assert(delayedDone && delayedProgress==GalaxyPadImageBytes/(16*1024*1024));
    extractorCalls=0;
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
      // Same supported container type at different lengths must reach the
      // content verifier. Whole-container size is not a revision identity.
      fixtureBytes=GalaxyPadImageBytes+(mode>=2?512:0);
      fd=open(image.fileSystemRepresentation,O_RDWR);
      assert(fd>=0 && ftruncate(fd,fixtureBytes)==0 && write(fd,fixtureHeader(fixtureBytes).data(),512)==512 && close(fd)==0);
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
      assert([NSFileManager.defaultManager attributesOfItemAtPath:image.path error:nil].fileSize==fixtureBytes);
      NSData *unchanged=[NSData dataWithContentsOfURL:image];
      assert(unchanged.length==fixtureBytes);
      const unsigned char *bytes=(const unsigned char *)unchanged.bytes;
      assert(memcmp(bytes,fixtureHeader(fixtureBytes).data(),512)==0);
      for (NSUInteger i=512;i<unchanged.length;++i) assert(bytes[i]==0);
    }
    assert([NSFileManager.defaultManager removeItemAtURL:root error:nil]);
    puts("Import storage threshold, rejection, copy cancellation, extraction failure cleanup and activation gates passed");
  }
}
