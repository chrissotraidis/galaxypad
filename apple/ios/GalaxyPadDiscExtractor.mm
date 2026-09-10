// SPDX-License-Identifier: GPL-3.0-or-later
// Adapted from SunPadDiscExtractor at fcdc1411e483a86ca80ec82e7cd53839c51ff865.
// Galaxy adds exact image/DOL verification and checked, path-safe file exports.
#import "GalaxyPadDiscExtractor.h"
#import <CommonCrypto/CommonDigest.h>
#include "GalaxyPadDiscIdentity.h"
#include "DiscIO/DiscExtractor.h"
#include "DiscIO/Filesystem.h"
#include "DiscIO/Volume.h"
#include <array>
#include <filesystem>
#include <fstream>
namespace fs=std::filesystem;

static std::string SHA256(const fs::path& path, BOOL (^cancelled)(void)) {
  std::ifstream stream(path,std::ios::binary);
  if (!stream) return {};
  CC_SHA256_CTX context;
  CC_SHA256_Init(&context);
  std::array<char,65536> buffer;
  while (stream.read(buffer.data(),buffer.size()) || stream.gcount()) {
    if (cancelled && cancelled()) return {};
    CC_SHA256_Update(&context,buffer.data(),(CC_LONG)stream.gcount());
  }
  if (stream.bad() || !stream.eof()) return {};
  unsigned char digest[CC_SHA256_DIGEST_LENGTH];
  CC_SHA256_Final(digest,&context);
  constexpr char digits[]="0123456789abcdef";
  std::string result;
  for (unsigned char byte:digest) { result+=digits[byte>>4]; result+=digits[byte&15]; }
  return result;
}

static bool ExportChecked(const DiscIO::Volume& volume, const DiscIO::Partition& partition,
    const DiscIO::FileInfo& directory, const fs::path& target, unsigned depth,
    uint64_t& completed, uint64_t total, BOOL (^cancelled)(void), void (^progress)(NSString*,double)) {
  if (depth>128 || (cancelled && cancelled())) return false;
  std::error_code error;
  if (!fs::create_directory(target,error) || error) return false;
  for (const auto& entry:directory) {
    if (cancelled && cancelled()) return false;
    std::string name=entry.GetName();
    if (name.empty() || name=="." || name==".." || name.find('/')!=std::string::npos ||
        name.find('\\')!=std::string::npos || name.find('\0')!=std::string::npos) return false;
    auto path=target/name;
    if (entry.IsDirectory()) {
      if (!ExportChecked(volume,partition,entry,path,depth+1,completed,total,cancelled,progress)) return false;
    } else {
      if (fs::exists(path,error) || error || !DiscIO::ExportFile(volume,partition,&entry,path.string())) return false;
      if (fs::file_size(path,error)!=entry.GetSize() || error) return false;
    }
    ++completed;
    if (progress && (completed%64==0 || completed==total)) {
      double fraction=0.1+0.85*std::min(1.0,(double)completed/(double)total);
      dispatch_async(dispatch_get_main_queue(), ^{ progress(@"Extracting game data",fraction); });
    }
  }
  return true;
}

@implementation GalaxyPadDiscExtractor
+ (void)extractImageAtPath:(NSString *)imagePath toDirectory:(NSString *)destination
    progress:(void (^)(NSString*,double))progress completion:(void (^)(BOOL,NSString*))completion {
  [self extractImageAtPath:imagePath toDirectory:destination cancelled:nil progress:progress completion:completion];
}
+ (void)extractImageAtPath:(NSString *)imagePath toDirectory:(NSString *)destination
    cancelled:(BOOL (^)(void))cancelled
    progress:(void (^)(NSString*,double))progress completion:(void (^)(BOOL,NSString*))completion {
  dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED,0), ^{
    @autoreleasepool {
      NSString *failure=nil;
      try {
        auto extract=[&]() -> NSString* {
          if (cancelled && cancelled()) return @"Import cancelled.";
          fs::path image=imagePath.fileSystemRepresentation, root=destination.fileSystemRepresentation;
          std::error_code error;
          if (!fs::is_regular_file(image,error) || error || fs::file_size(image,error)!=GalaxyPadImageBytes || error)
            return @"This is not the supported exact Galaxy image.";
          if (progress) dispatch_async(dispatch_get_main_queue(), ^{ progress(@"Verifying image identity",0); });
          if (SHA256(image,cancelled)!=GalaxyPadImageSHA256) return @"Image SHA-256 does not match supported RMGE01 data.";
          if (cancelled && cancelled()) return @"Import cancelled.";
          auto volume=DiscIO::CreateVolume(image.string());
          if (!volume || volume->GetVolumeType()!=DiscIO::Platform::WiiDisc ||
              volume->GetGameID()!="RMGE01" || volume->GetRevision()!=0)
            return @"Expected a supported RMGE01 revision 0 Wii disc.";
          auto partition=volume->GetGamePartition();
          auto filesystem=volume->GetFileSystem(partition);
          if (!filesystem || !filesystem->IsValid()) return @"Could not read the Wii data partition.";
          if (!fs::create_directory(root,error) || error) return @"A new private extraction directory is required.";
          if (!DiscIO::ExportSystemData(*volume,partition,root.string())) return @"System-data extraction failed.";
          if (SHA256(root/"sys/main.dol",cancelled)!=GalaxyPadDOLSHA256) return @"Extracted DOL does not match the supported module identity.";
          uint64_t completed=0, total=std::max<uint64_t>(1,filesystem->GetRoot().GetTotalChildren());
          if (!ExportChecked(*volume,partition,filesystem->GetRoot(),root/"files",0,completed,total,cancelled,progress))
            return @"Game-data extraction failed or was incomplete.";
          return nil;
        };
        failure=extract();
      } catch (const std::exception&) { failure=@"Extraction failed; existing game data and saves are unchanged."; }
      dispatch_async(dispatch_get_main_queue(), ^{
        NSString *result=(cancelled && cancelled()) ? @"Import cancelled." : failure;
        if (!result && progress) progress(@"Extraction verified",1);
        completion(result==nil,result);
      });
    }
  });
}
@end
