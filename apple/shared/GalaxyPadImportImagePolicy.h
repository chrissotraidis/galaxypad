// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <algorithm>
#include <array>
#include <cstdint>
#include <istream>

namespace galaxypad {
// Single-disc WBFS only. Allow container padding/layout differences, while
// bounding the private copy and rejecting other formats before copying them.
inline constexpr uint64_t maxImportImageBytes = 5ULL << 30;
inline bool supportedImportContainer(std::istream& input, uint64_t bytes) {
  std::array<unsigned char,512> header{};
  if (bytes<512 || bytes>maxImportImageBytes ||
      !input.read(reinterpret_cast<char*>(header.data()),header.size()) ||
      header[0]!='W' || header[1]!='B' || header[2]!='F' || header[3]!='S') return false;
  // DiscIO uses these fields as shift counts and allocation sizes. Check them
  // before opening an untrusted container, including truncated/split inputs.
  const unsigned hdShift=header[8], wbfsShift=header[9];
  if (hdShift<9 || hdShift>20 || wbfsShift<15 || wbfsShift>26 || wbfsShift<hdShift)
    return false;
  const uint64_t sectors=(uint64_t(header[4])<<24)|(uint64_t(header[5])<<16)|
                         (uint64_t(header[6])<<8)|header[7];
  if ((sectors<<hdShift)!=bytes || header[12]==0) return false;
  return std::all_of(header.begin()+13,header.end(),[](unsigned char slot){return slot==0;});
}
inline uint64_t requiredImportBytes(uint64_t imageBytes) {
  // Up to one Wii disc of extracted data plus filesystem headroom. Preserve
  // the previous 9 GiB minimum and account for larger WBFS containers.
  return std::max<uint64_t>(9ULL << 30, imageBytes + (5ULL << 30));
}
}
