// Isolated arithmetic throughput, not a module/CPUState/dispatch benchmark.
#include "../apple/experiments/deferred-timebase/accounting.h"
#include <array>
#include <chrono>
#include <iostream>

struct Eager
{
  std::uint64_t ticks = 0, remainder = 0;
  void Charge(std::uint64_t cycles)
  {
    const auto total = remainder + cycles;
    ticks += total / 12;
    remainder = total % 12;
  }
  std::uint64_t Materialize() { return ticks; }
};

template <typename State>
[[gnu::noinline]] std::uint64_t Run(State state, unsigned mask,
                                   const std::array<std::uint64_t, 1024>& charges)
{
  std::uint64_t checksum = 0;
  for (unsigned i = 0; i < 20000000; ++i)
  {
    state.Charge(charges[i & 1023]);
    if ((i & mask) == 0)
      checksum += state.Materialize();
  }
  return checksum + state.Materialize();
}

int main()
{
  std::array<std::uint64_t, 1024> charges{};
  std::uint32_t random = 0x12345678;
  for (auto& charge : charges)
  {
    random ^= random << 13; random ^= random >> 17; random ^= random << 5;
    charge = random % 1024;
  }
  for (unsigned mask : {0u, 7u, 63u, 1023u})
  {
    std::uint64_t baseline = 0;
    for (bool candidate : {false, true, true, false})
    {
      const auto start = std::chrono::steady_clock::now();
      const auto checksum = candidate ?
          Run(galaxypad::experiments::DeferredTimebase(0, 0), mask, charges) :
          Run(Eager{}, mask, charges);
      const auto ns = std::chrono::duration_cast<std::chrono::nanoseconds>(
          std::chrono::steady_clock::now() - start).count();
      if (!candidate) baseline = checksum;
      assert(checksum == baseline);
      std::cout << "observer_every=" << mask+1 << " candidate=" << candidate
                << " ns/charge=" << double(ns)/20000000 << " checksum=" << checksum << '\n';
    }
  }
}
