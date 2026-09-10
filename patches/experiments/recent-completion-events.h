#pragma once
#include "completion-events.h"

namespace galaxypad {

// Single writer owns append AND freeze. A different thread may request a freeze
// through an external atomic flag, but must never mutate/read this buffer live.
template<std::size_t Capacity = 32768>
class RecentCompletionEvents {
public:
  using Kind = CompletionEvents<>::Kind;
  using Event = CompletionEvents<>::Event;

  void Configure(bool enabled) noexcept {
    enabled_ = enabled;
    frozen_ = false;
    next_ = size_ = 0;
    overwritten_ = 0;
  }

  template<class Clock>
  void Record(Kind kind, Clock&& clock) noexcept {
    if (!enabled_ || frozen_) return;
    auto event = clock();
    event.kind = kind;
    events_[next_] = event;
    next_ = (next_ + 1) % Capacity;
    if (size_ < Capacity) {
      ++size_;
    } else if (overwritten_ != std::numeric_limits<std::uint64_t>::max()) {
      ++overwritten_;
    }
  }

  void Freeze() noexcept { frozen_ = true; }
  bool Frozen() const noexcept { return frozen_; }
  std::size_t Size() const noexcept { return size_; }
  std::uint64_t Overwritten() const noexcept { return overwritten_; }

  // Read after all writers join. Caller validates index < Size(). Export in
  // this chronological order, not physical array order after wrapping.
  const Event& At(std::size_t index) const noexcept {
    return events_[((size_ == Capacity ? next_ : 0) + index) % Capacity];
  }

private:
  static_assert(Capacity > 0);
  std::array<Event, Capacity> events_{};
  std::size_t next_ = 0, size_ = 0;
  std::uint64_t overwritten_ = 0;
  bool enabled_ = false, frozen_ = false;
};
} // namespace galaxypad
