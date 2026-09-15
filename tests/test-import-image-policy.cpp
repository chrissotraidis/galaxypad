// SPDX-License-Identifier: GPL-3.0-or-later
#include "../apple/shared/GalaxyPadImportImagePolicy.h"
#include <cassert>
#include <sstream>
std::string header(uint64_t bytes) {
  std::string h(512,'\0'); h.replace(0,4,"WBFS");
  for(int i=0;i<4;++i) h[4+i]=(bytes>>9)>>(24-i*8);
  h[8]=9; h[9]=21; h[12]=1; return h;
}
bool accepts(const std::string& h,uint64_t bytes) {
  std::istringstream input(h);return galaxypad::supportedImportContainer(input,bytes);
}
int main() {
  for(uint64_t bytes:{512ULL,3508535296ULL,3508535808ULL,5ULL<<30}) {
    assert(accepts(header(bytes),bytes));
    assert(galaxypad::requiredImportBytes(bytes)>=bytes+(5ULL<<30));
  }
  for(uint64_t bytes:{0ULL,511ULL,(5ULL<<30)+512}) assert(!accepts(header(bytes),bytes));
  auto good=header(3508535296ULL);
  for(size_t size:{0,4,511}) assert(!accepts(good.substr(0,size),3508535296ULL));
  for(auto field:{0,8,9,12,13}) {
    auto bad=good;bad[field]=static_cast<char>((field==0||field==12)?0:255);
    assert(!accepts(bad,3508535296ULL));
  }
  assert(!accepts(good,3508535808ULL)); // split/truncated or inconsistent header
  assert(galaxypad::requiredImportBytes(3508535296ULL)==(9ULL<<30));
}
