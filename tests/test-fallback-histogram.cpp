#include "../apple/experiments/fallback-pcs/histogram.h"
#include <cassert>
#include <cstdio>
#include <string>
using namespace galaxypad::diagnostics;
int main(int argc, char**)
{
  {
    uint8_t ram[0xd00]{};
    for (size_t i=0; i<sizeof(ram); ++i) ram[i]=i & 255;
    auto* output=std::tmpfile(); assert(output);
    DumpExceptionVectors(nullptr,ram,sizeof(ram));
    DumpExceptionVectors(output,nullptr,sizeof(ram));
    DumpExceptionVectors(output,ram,sizeof(ram)-1);
    assert(std::ftell(output)==0);
    DumpExceptionVectors(output,ram,sizeof(ram));
    std::rewind(output);
    char line[600]; unsigned lines=0;
    for(unsigned base : {0x500u,0x800u,0x900u,0xc00u}) {
      assert(std::fgets(line,sizeof(line),output));
      char prefix[80]; std::snprintf(prefix,sizeof(prefix),"[galaxypad-vector-ram] base=%08x bytes=",base);
      std::string expected=prefix;
      for(unsigned i=0;i<256;++i) {
        char hex[3];std::snprintf(hex,sizeof(hex),"%02x",i);expected+=hex;
      }
      expected+='\n';assert(line==expected);++lines;
    }
    assert(lines==4 && !std::fgets(line,sizeof(line),output));
    std::fclose(output);
  }
  if (argc > 1)
  {
    FallbackHistogram<> replay;
    unsigned pc, path;
    unsigned long long count;
    unsigned keys = 0;
    while (std::scanf("%x %u %llu", &pc, &path, &count) == 3)
    {
      assert(path <= 2 && count > 0);
      for (unsigned long long i = 0; i < count; ++i)
        replay.Record(pc, static_cast<FallbackPath>(path));
      ++keys;
    }
    std::printf("replayed_keys=%u events=%llu dropped=%llu\n", keys,
                static_cast<unsigned long long>(replay.total),
                static_cast<unsigned long long>(replay.dropped));
    assert(replay.dropped == 0);
    return 0;
  }
  FallbackHistogram<> histogram;
  for (unsigned i = 0; i < 10000; ++i)
    histogram.Record(0x80000500, FallbackPath::Uncovered);
  histogram.Record(0x500, FallbackPath::Uncovered);
  histogram.Record(0x80000500, FallbackPath::Forced);
  histogram.Record(0x80000500, FallbackPath::InstructionHook);
  histogram.Record(0, FallbackPath::Uncovered);
  uint64_t sum = 0;
  unsigned populated = 0;
  for (const auto& entry : histogram.entries)
  {
    sum += entry.count;
    populated += entry.count != 0;
  }
  assert(sum == 10004 && histogram.total == sum && !histogram.dropped);
  assert(populated == 5);
  FallbackHistogram<4> full;
  for (unsigned i = 0; i < 100; ++i)
    full.Record(i * 4, FallbackPath::Uncovered);
  assert(full.total == 100 && full.dropped == 96);
  full.Record(0, FallbackPath::Uncovered);
  assert(full.entries[0].count == 2 && full.dropped == 96);
  sum = 0;
  for (const auto& entry : full.entries)
    sum += entry.count;
  assert(sum + full.dropped == full.total);
  puts("fallback histogram: aliases, paths, zero PC, repeats and overflow pass");
}
