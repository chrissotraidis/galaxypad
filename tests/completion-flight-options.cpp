#include "../patches/experiments/completion-flight-options.h"
#include "../patches/experiments/rolling/idle-wait-timing.h"
#include <cassert>

int main() {
  std::uint64_t deadline = 42;
  const char* invalid_values[] = {nullptr, "", "-1", "+1", " 1", "1 ", "1ms", "3600001", "9999999999999999999999"};
  for (const char* invalid : invalid_values) {
    assert(!galaxypad::CompletionArmDeadline(invalid, 100, deadline));
    assert(deadline == 42);
  }
  assert(galaxypad::CompletionArmDeadline("0", 100, deadline) && deadline == 100);
  assert(galaxypad::CompletionArmDeadline("120000", 100, deadline) && deadline == 120000000100ULL);
  assert(!galaxypad::CompletionArmDeadline("1", UINT64_MAX, deadline));
  galaxypad::IdleWaitTiming timer;
  unsigned clocks = 0, waits = 0, observed = 0;
  auto clock = [&]() -> std::uint64_t { return ++clocks * 10; };
  auto observer = [&](std::uint64_t start, std::uint64_t end) {
    ++observed;
    assert(start == 10 && end == 20);
  };
  timer.MeasureWithClock([&] { ++waits; }, clock, observer);
  assert(waits == 1 && clocks == 0 && observed == 0);
  timer.Configure(true);
  timer.MeasureWithClock([&] { ++waits; }, clock, observer);
  assert(waits == 2 && clocks == 2 && observed == 1 && timer.ElapsedNs() == 10);
  timer.Measure([] {}, [](std::uint64_t start, std::uint64_t end) { assert(end >= start); });
}
