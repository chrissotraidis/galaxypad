// Diagnostic-only, CPU-thread-owned interpreter-step census.
#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdio>

namespace galaxypad::diagnostics
{
enum class FallbackPath : uint32_t { Uncovered, Forced, InstructionHook };

// CPU-thread physical RAM snapshot, not an instruction-cache observation.
inline void DumpExceptionVectors(std::FILE* output, const uint8_t* ram, size_t size)
{
  if (!output || !ram || size < 0xd00)
    return;
  for (uint32_t base : {0x500u, 0x800u, 0x900u, 0xc00u})
  {
    std::fprintf(output, "[galaxypad-vector-ram] base=%08x bytes=", base);
    for (size_t offset = 0; offset < 256; ++offset)
      std::fprintf(output, "%02x", static_cast<unsigned>(ram[base + offset]));
    std::fputc('\n', output);
  }
}

template <size_t Capacity = 32768> struct FallbackHistogram
{
  static_assert(Capacity && (Capacity & (Capacity - 1)) == 0);
  struct Entry
  {
    uint32_t pc = 0;
    FallbackPath path = FallbackPath::Uncovered;
    uint64_t count = 0;
  };
  std::array<Entry, Capacity> entries{};
  uint64_t total = 0;
  uint64_t dropped = 0;

  // No allocation, guest-memory reads, output or unbounded collision scans.
  // Keep PC aliases distinct; normalization belongs in offline analysis.
  void Record(uint32_t pc, FallbackPath path)
  {
    ++total;
    uint32_t hash = (pc >> 2) ^ (static_cast<uint32_t>(path) * 0x9e3779b9u);
    hash ^= hash >> 16;
    hash *= 0x7feb352du;
    hash ^= hash >> 15;
    hash *= 0x846ca68bu;
    hash ^= hash >> 16;
    const size_t index = hash & (Capacity - 1);
    constexpr size_t probes = Capacity < 16 ? Capacity : 16;
    for (size_t probe = 0; probe < probes; ++probe)
    {
      auto& entry = entries[(index + probe) & (Capacity - 1)];
      if (!entry.count)
      {
        entry = {pc, path, 1};
        return;
      }
      if (entry.pc == pc && entry.path == path)
      {
        ++entry.count;
        return;
      }
    }
    ++dropped;
  }
};
}
