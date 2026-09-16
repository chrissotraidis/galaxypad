// SPDX-License-Identifier: GPL-3.0-or-later
// Adapted staging boundary from SunPad; checked copy, verification and activation.
#import "GalaxyPadImportTransaction.h"
#import "GalaxyPadDiscExtractor.h"
#include "../shared/GalaxyPadImportActivation.h"
#include "../shared/GalaxyPadImportImagePolicy.h"
#include <atomic>
#include <array>
#include <fstream>

@implementation GalaxyPadImportTransaction {
  NSURL *_root;
  NSString *_stageName;
  BOOL _used;
  BOOL _preparing;
  BOOL _verified;
  BOOL _previousDataRetained;
  BOOL _ownsUnactivatedStage;
  std::atomic_bool _cancelled;
}
- (instancetype)initWithRoot:(NSURL *)root {
  if ((self=[super init])) { _root=[root copy]; _cancelled.store(false); }
  return self;
}
- (BOOL)preparing { return _preparing; }
- (BOOL)verified { return _verified; }
- (BOOL)previousDataRetained { return _previousDataRetained; }
- (uint64_t)availableImportBytes {
  std::error_code error;
  auto space=std::filesystem::space(_root.fileSystemRepresentation,error);
  return error || space.available==static_cast<std::uintmax_t>(-1) ? 0 : space.available;
}
- (void)cancel {
  NSAssert(NSThread.isMainThread,@"Import must be owned by main thread");
  _cancelled.store(true);
  _verified=NO;
}
- (void)prepareImage:(NSURL *)source progress:(void (^)(NSString *,double))progress
    completion:(void (^)(BOOL,NSString *))completion {
  NSAssert(NSThread.isMainThread,@"Import must be owned by main thread");
  if (_used || !_root.isFileURL || !source.isFileURL) {
    completion(NO,@"A fresh local import transaction is required."); return;
  }
  _used=YES;
  _preparing=YES;
  _stageName=[@"GameData.import-" stringByAppendingString:NSUUID.UUID.UUIDString];
  NSURL *stage=[_root URLByAppendingPathComponent:_stageName isDirectory:YES];
  NSURL *image=[stage URLByAppendingPathComponent:@"RMGE01.wbfs"];
  NSURL *extracted=[stage URLByAppendingPathComponent:@"RMGE01" isDirectory:YES];
  // Keep security-scoped access alive through the worker copy only.
  BOOL scoped=[source startAccessingSecurityScopedResource];
  dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED,0), ^{
    @autoreleasepool {
      NSString *failure=nil;
      BOOL ownsStage=NO;
      try {
        namespace fs=std::filesystem;
        auto copy=[&]() -> NSString * {
          if (self->_cancelled.load()) return @"Import cancelled.";
          fs::path root=self->_root.fileSystemRepresentation;
          fs::path input=source.fileSystemRepresentation;
          std::error_code ec;
          if (!fs::is_directory(fs::symlink_status(root,ec)) || ec)
            return @"Private game-data directory is unavailable.";
          if (!fs::is_regular_file(input,ec) || ec)
            return @"Select a local RMGE01 revision 0 WBFS image.";
          const uint64_t imageBytes=fs::file_size(input,ec);
          std::ifstream header(input,std::ios::binary);
          if (ec || !galaxypad::supportedImportContainer(header,imageBytes))
            return @"Select a single-disc WBFS image (up to 5 GiB). ISO and split WBFS imports are not supported.";
          const uint64_t required=galaxypad::requiredImportBytes(imageBytes);
          // Preflight is not a reservation; writes still check for ENOSPC.
          if ([self availableImportBytes] < required)
            return [NSString stringWithFormat:@"Import needs at least %llu GiB of available storage for the private copy, extraction and headroom. Existing game data and saves are unchanged.",
              (unsigned long long)((required+(1ULL<<30)-1)>>30)];
          if (!fs::create_directory(stage.fileSystemRepresentation,ec) || ec)
            return @"Could not create private import staging.";
          ownsStage=YES;
          std::ifstream in(input,std::ios::binary);
          std::ofstream out(image.fileSystemRepresentation,std::ios::binary);
          if (!in || !out) return @"Could not copy the selected image.";
          std::array<char,65536> buffer;
          uint64_t copied=0;
          while (in.read(buffer.data(),buffer.size()) || in.gcount()) {
            if (self->_cancelled.load()) return @"Import cancelled.";
            copied+=in.gcount();
            if (copied>imageBytes) return @"Selected image changed during import.";
            out.write(buffer.data(),in.gcount());
            if (!out) return @"Image copy failed; check available storage.";
            if (progress && copied%(16*1024*1024)==0) {
              double fraction=0.25*(double)copied/imageBytes;
              // Snapshot the lambda's reference before it escapes into a block.
              // Otherwise the callback reads the released worker's capture slot.
              void (^notify)(NSString *,double)=[progress copy];
              dispatch_async(dispatch_get_main_queue(), ^{ notify(@"Copying selected image",fraction); });
            }
          }
          out.close();
          if (!out || in.bad() || !in.eof() || copied!=imageBytes)
            return @"Image copy was incomplete.";
          return nil;
        };
        failure=copy();
      } catch (const std::exception&) { failure=@"Private image copy failed."; }
      if (scoped) [source stopAccessingSecurityScopedResource];
      dispatch_async(dispatch_get_main_queue(), ^{
        self->_ownsUnactivatedStage=ownsStage;
        void (^finish)(BOOL,NSString *)=^(BOOL ok,NSString *message) {
          BOOL accepted=ok && !self->_cancelled.load();
          // Never remove a stage while a copy/extractor worker is still using it.
          // Only this transaction's newly created tree is eligible for cleanup.
          if (!accepted && ownsStage) {
            // Large partial imports must not freeze UIKit during cleanup.
            dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY,0), ^{
              BOOL removed=[NSFileManager.defaultManager removeItemAtURL:stage error:nil];
              dispatch_async(dispatch_get_main_queue(), ^{
                self->_preparing=NO;
                if (removed) self->_ownsUnactivatedStage=NO;
                NSString *reason=self->_cancelled.load()?@"Import cancelled.":message;
                completion(NO,removed?reason:[reason stringByAppendingString:@" Private staging cleanup is still needed."]);
              });
            });
            return;
          }
          self->_preparing=NO;
          self->_verified=accepted;
          completion(accepted,self->_cancelled.load()?@"Import cancelled.":message);
        };
        if (failure || self->_cancelled.load()) { finish(NO,failure); return; }
        [GalaxyPadDiscExtractor extractImageAtPath:image.path toDirectory:extracted.path
          cancelled:^BOOL { return self->_cancelled.load(); }
          progress:^(NSString *status,double fraction) {
            if (progress) progress(status,0.25+0.75*fraction);
          } completion:finish];
      });
    }
  });
}
- (void)discardUnactivatedStage:(void (^)(BOOL,NSString *))completion {
  NSAssert(NSThread.isMainThread,@"Import must be owned by main thread");
  if (_preparing || !_ownsUnactivatedStage ||
      !galaxypad::validImportStageName(_stageName.UTF8String)) {
    completion(NO,@"No idle unactivated stage is available to discard."); return;
  }
  _preparing=YES; // Retain exclusive ownership until removal completion.
  _verified=NO;
  _cancelled.store(true);
  NSURL *stage=[_root URLByAppendingPathComponent:_stageName isDirectory:YES];
  dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY,0), ^{
    std::error_code ec;
    // Refuse a replaced/symlink root; never follow it into a different tree.
    BOOL safeRoot=std::filesystem::is_directory(std::filesystem::symlink_status(
      self->_root.fileSystemRepresentation,ec)) && !ec;
    BOOL removed=safeRoot && [NSFileManager.defaultManager removeItemAtURL:stage error:nil];
    dispatch_async(dispatch_get_main_queue(), ^{
      self->_preparing=NO;
      if (removed) self->_ownsUnactivatedStage=NO;
      completion(removed,removed?nil:@"Private staging could not be removed; cleanup is still needed.");
    });
  });
}
- (BOOL)activateWithRuntimeStopped:(BOOL)stopped error:(NSString **)error {
  NSAssert(NSThread.isMainThread,@"Import must be owned by main thread");
  if (!_verified || _preparing || _cancelled.load() || !stopped) {
    if (error) *error=@"Verified import and a stopped game are required.";
    return NO;
  }
  auto result=galaxypad::activateImport(_root.fileSystemRepresentation,_stageName.UTF8String,stopped);
  if (result.error) {
    if (error) *error=@"Could not activate import; previous data is unchanged.";
    return NO;
  }
  _verified=NO; // A transaction cannot exchange the directories twice.
  _ownsUnactivatedStage=NO; // Stage now either vanished or contains prior data.
  _previousDataRetained=result.previousDataRetained;
  return YES;
}
@end
