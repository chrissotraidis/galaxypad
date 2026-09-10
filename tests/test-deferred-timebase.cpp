#include "../apple/experiments/deferred-timebase/accounting.h"
#include <array>
#include <cassert>
#include <cstdint>
#include <limits>

using galaxypad::experiments::DeferredTimebase;

// Mirrors the actual current AdvanceGuestTimebase arithmetic, including wrap.
struct Baseline
{
  std::uint64_t ticks, remainder;
  void Charge(std::uint64_t charge)
  {
    const auto total = remainder + charge;
    ticks += total / 12;
    remainder = total % 12;
  }
};

int main()
{
  constexpr auto maximum = std::numeric_limits<std::uint64_t>::max();
  const std::array<std::uint64_t, 12> charges = {
      0, 1, 11, 12, 13, 65536, 0x7fffffff, maximum/2,
      maximum-12, maximum-11, maximum-1, maximum};
  for (auto ticks : {std::uint64_t{0}, std::uint64_t{0xffffffff}, maximum})
    for (unsigned remainder = 0; remainder < 12; ++remainder)
      for (auto first : charges)
        for (auto second : charges)
          for (auto third : charges)
          {
            Baseline original{ticks, remainder};
            DeferredTimebase candidate(ticks, remainder);
            for (auto charge : {first, second, third})
            {
              original.Charge(charge);
              candidate.Charge(charge);
            }
            assert(candidate.Materialize() == original.ticks);
            assert(candidate.Remainder() == original.remainder);
          }

  std::uint32_t random = 0x12345678;
  Baseline original{maximum-20, 11};
  DeferredTimebase candidate(original.ticks, original.remainder);
  for (unsigned i = 0; i < 1000000; ++i)
  {
    random ^= random << 13; random ^= random >> 17; random ^= random << 5;
    const auto charge = random % 100000;
    original.Charge(charge);
    candidate.Charge(charge);
    if (i % 127 == 0)
    {
      assert(candidate.Materialize() == original.ticks);
      assert(candidate.Materialize() == original.ticks); // Repeated read is idempotent.
    }
    if (i % 1009 == 0)
    {
      original.ticks = (original.ticks & 0xffffffff00000000ULL) | random;
      candidate.WriteLow(random);
    }
    if (i % 1013 == 0)
    {
      original.ticks = (std::uint64_t(random) << 32) | std::uint32_t(original.ticks);
      candidate.WriteHigh(random);
    }
    if (i % 1021 == 0)
    {
      assert(candidate.Materialize() == original.ticks);
      assert(candidate.Remainder() == original.remainder);
      candidate = DeferredTimebase(original.ticks, original.remainder); // SyncIn/reset boundary.
    }
  }
  assert(candidate.Materialize() == original.ticks);
  assert(candidate.Remainder() == original.remainder);
}
