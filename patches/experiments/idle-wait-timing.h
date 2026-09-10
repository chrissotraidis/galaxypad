#pragma once

#include <chrono>
#include <cstdint>
#include <limits>

namespace galaxypad {

// CPU-thread writer/reader only. Configure before starting or after joining it.
// Measures elapsed time, including scheduling delay, not pure blocked time.
class IdleWaitTiming {
public:
  void Configure(bool enabled) noexcept {
    enabled_ = enabled;
    elapsed_ns_ = 0;
  }

  template<class Wait, class Clock>
  void MeasureWithClock(Wait&& wait, Clock&& clock) {
    if (!enabled_) {
      wait();
      return;
    }
    const std::uint64_t start = clock();
    wait();
    const std::uint64_t end = clock();
    if (end >= start) {
      const auto elapsed = end - start;
      const auto remaining = std::numeric_limits<std::uint64_t>::max() - elapsed_ns_;
      elapsed_ns_ += elapsed > remaining ? remaining : elapsed;
    }
  }

  template<class Wait>
  void Measure(Wait&& wait) {
    MeasureWithClock(wait, [] {
      return static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(
          std::chrono::steady_clock::now().time_since_epoch()).count());
    });
  }

  std::uint64_t ElapsedNs() const noexcept { return elapsed_ns_; }

private:
  bool enabled_ = false;
  std::uint64_t elapsed_ns_ = 0;
};
} // namespace galaxypad
