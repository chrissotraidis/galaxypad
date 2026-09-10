#include "../patches/experiments/idle-wait-timing.h"
#include <cassert>
#include <limits>
#include <stdexcept>
#include <thread>

int main() {
  galaxypad::IdleWaitTiming timer;
  int waits = 0, clocks = 0;
  auto wait = [&] { ++waits; };
  auto clock = [&]() -> std::uint64_t { return ++clocks * 10; };
  timer.MeasureWithClock(wait, clock);
  assert(waits == 1 && clocks == 0 && timer.ElapsedNs() == 0);
  timer.Configure(true);
  std::thread writer([&] {
    timer.MeasureWithClock(wait, clock);
    timer.MeasureWithClock(wait, clock);
  });
  writer.join();
  assert(waits == 3 && clocks == 4 && timer.ElapsedNs() == 20);
  int index = 0;
  timer.MeasureWithClock(wait, [&]() -> std::uint64_t { return index++ == 0 ? 100 : 99; });
  assert(waits == 4 && timer.ElapsedNs() == 20);
  index = 0;
  timer.MeasureWithClock(wait, [&]() -> std::uint64_t {
    return index++ == 0 ? 0 : std::numeric_limits<std::uint64_t>::max();
  });
  timer.MeasureWithClock(wait, clock);
  assert(timer.ElapsedNs() == std::numeric_limits<std::uint64_t>::max());
  timer.Configure(false);
  const int before = clocks;
  timer.MeasureWithClock(wait, clock);
  assert(clocks == before && timer.ElapsedNs() == 0);
  timer.Configure(true);
  timer.Measure(wait); // Exercise production steady clock; no minimum duration assumption.
  int throws = 0;
  try {
    timer.Measure([&] { ++throws; throw std::runtime_error("wait failure"); });
    assert(false);
  } catch (const std::runtime_error&) {
    assert(throws == 1);
  }
}
