#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>

namespace galaxypad {

// Use distinct instances for CPU and graphics writers. No cross-thread reads;
// inspect/reset only after BOTH workers join. All timestamps use the same clock.
// Records describe observation boundaries, not an assertion that the CPU slept.
template<std::size_t Capacity = 32768>
class CompletionEvents {
public:
  enum class Kind { WaitBegin, WaitEnd, BeforeNotify, AfterNotify };
  struct Event {
    std::uint64_t wall_ns;
    std::uint64_t thread_cpu_ns;
    Kind kind;
    bool cpu_clock_valid;
  };

  // Configure before starting writers; disabling also discards the previous run.
  void Configure(bool enabled) noexcept {
    enabled_ = enabled;
    size_ = 0;
    dropped_ = 0;
  }

  template<class Clock>
  void Record(Kind kind, Clock&& clock) noexcept {
    if (!enabled_)
      return;
    if (size_ == Capacity) {
      if (dropped_ != std::numeric_limits<std::uint64_t>::max())
        ++dropped_;
      return; // Also avoid clock calls once full.
    }
    Event event = clock();
    event.kind = kind;
    events_[size_++] = event;
  }

  std::size_t Size() const noexcept { return size_; }
  std::uint64_t Dropped() const noexcept { return dropped_; }
  const Event* Data() const noexcept { return events_.data(); }

private:
  static_assert(Capacity > 0);
  std::array<Event, Capacity> events_{};
  bool enabled_ = false;
  std::size_t size_ = 0;
  std::uint64_t dropped_ = 0;
};
} // namespace galaxypad
