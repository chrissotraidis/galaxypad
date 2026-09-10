#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>

namespace galaxypad {

// One CPU-thread writer. Inspect/reset only before starting or after joining it.
// Deliberately contains no clocks, allocations, locks, callbacks or file I/O.
template <std::size_t Capacity = 16384>
class ViTimingBuffer {
public:
  static_assert(Capacity > 0);
  struct Sample {
    std::uint64_t wall_ns{};
    std::uint64_t thread_cpu_ns{};
    bool cpu_clock_valid{};
    std::uint64_t efb_elapsed_ns{};
    std::uint64_t throttle_elapsed_ns{};
    std::uint64_t idle_wait_elapsed_ns{};
    std::uint64_t dvd_wait_elapsed_ns{};
    std::uint64_t gather_wait_elapsed_ns{};
    std::uint64_t wakeup_elapsed_ns{};
  };

  void Record(std::uint64_t wall_ns, std::uint64_t cpu_ns, bool cpu_valid,
              std::uint64_t efb_ns = 0, std::uint64_t throttle_ns = 0,
              std::uint64_t idle_ns = 0, std::uint64_t dvd_ns = 0, std::uint64_t gather_ns = 0, std::uint64_t wakeup_ns = 0) noexcept {
    if (size_ == Capacity) {
      if (dropped_ != std::numeric_limits<std::uint64_t>::max())
        ++dropped_;
      return;
    }
    samples_[size_++] = {wall_ns, cpu_ns, cpu_valid, efb_ns, throttle_ns, idle_ns, dvd_ns, gather_ns, wakeup_ns};
  }

  void Reset() noexcept { size_ = 0; dropped_ = 0; }
  std::size_t Size() const noexcept { return size_; }
  std::uint64_t Dropped() const noexcept { return dropped_; }
  const Sample* Data() const noexcept { return samples_.data(); }

private:
  std::array<Sample, Capacity> samples_{};
  std::size_t size_{};
  std::uint64_t dropped_{};
};

} // namespace galaxypad
