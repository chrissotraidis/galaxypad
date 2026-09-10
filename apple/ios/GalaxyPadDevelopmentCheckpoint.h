// SPDX-License-Identifier: GPL-3.0-or-later
// Private development-state identity, not a replacement for in-game saves.
#pragma once
#import <Foundation/Foundation.h>
#import <CommonCrypto/CommonDigest.h>

static NSString *GalaxyPadCheckpointHash(NSString *path) {
  NSDictionary *attributes = [NSFileManager.defaultManager attributesOfItemAtPath:path error:nil];
  if (![attributes[NSFileType] isEqual:NSFileTypeRegular] ||
      [attributes[NSFileSize] unsignedLongLongValue] > 1024ULL*1024*1024) return nil;
  NSInputStream *stream = [NSInputStream inputStreamWithFileAtPath:path];
  [stream open];
  CC_SHA256_CTX context;
  CC_SHA256_Init(&context);
  uint8_t bytes[65536];
  NSInteger count;
  while ((count = [stream read:bytes maxLength:sizeof(bytes)]) > 0)
    CC_SHA256_Update(&context, bytes, (CC_LONG)count);
  [stream close];
  if (count < 0) return nil;
  unsigned char digest[CC_SHA256_DIGEST_LENGTH];
  CC_SHA256_Final(digest, &context);
  NSMutableString *result = [NSMutableString string];
  for (unsigned char byte : digest) [result appendFormat:@"%02x", byte];
  return result;
}

static NSDictionary *GalaxyPadCheckpointIdentity(NSString *module, NSString *user) {
  NSString *appHash = GalaxyPadCheckpointHash(NSBundle.mainBundle.executablePath);
  NSString *moduleHash = GalaxyPadCheckpointHash(module);
  NSString *saveHash = GalaxyPadCheckpointHash([user stringByAppendingPathComponent:
      @"Wii/title/00010000/524d4745/data/GameData.bin"]);
  if (!appHash || !moduleHash || !saveHash) return nil;
  return @{@"app": appHash, @"module": moduleHash, @"nandSave": saveHash};
}

static BOOL GalaxyPadCheckpointIdentityMatches(NSDictionary *saved, NSDictionary *current) {
  return [saved isKindOfClass:NSDictionary.class] && current &&
    [saved isEqualToDictionary:current];
}

static BOOL GalaxyPadCheckpointFilenameValid(NSString *name) {
  if (![name isKindOfClass:NSString.class] || ![name.pathExtension isEqualToString:@"sav"])
    return NO;
  return [[NSUUID alloc] initWithUUIDString:name.stringByDeletingPathExtension] != nil &&
         [name.lastPathComponent isEqualToString:name];
}
