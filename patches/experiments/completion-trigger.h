#pragma once
#include "recent-completion-events.h"
#include <atomic>

namespace galaxypad {
// CPU supplies existing idle-wait timestamps, so detection requires no new
// clocks. Graphics records notification observations in its own rolling buffer.
template<std::size_t Capacity = 32768>
class CompletionTrigger {
public:
  using Buffer = RecentCompletionEvents<Capacity>;
  using Kind = typename Buffer::Kind;
  using Event = typename Buffer::Event;
  static_assert(Capacity >= 2 && Capacity % 2 == 0);

  // Before worker launch/after both joins only. not_before is an explicit
  // monotonic-clock arming boundary, not an inference that gameplay has begun.
  void Configure(bool enabled, std::uint64_t not_before, std::uint64_t threshold) noexcept {
    enabled_ = enabled && threshold > 0;
    not_before_ = not_before;
    threshold_ = threshold;
    trigger_start_ = trigger_end_ = 0;
    invalid_waits_ = 0;
    freeze_requested_.store(false, std::memory_order_relaxed);
    cpu_.Configure(enabled_);
    graphics_.Configure(enabled_);
  }

  // CPU writer only. A wait crossing the arming boundary is not eligible.
  void CPUWait(std::uint64_t start, std::uint64_t end) noexcept {
    if (!enabled_ || cpu_.Frozen()) return;
    if (end < start) { ++invalid_waits_; return; }
    cpu_.Record(Kind::WaitBegin, [=] { return Event{start, 0, Kind::WaitBegin, false}; });
    cpu_.Record(Kind::WaitEnd, [=] { return Event{end, 0, Kind::WaitEnd, false}; });
    if (start >= not_before_ && end-start >= threshold_) {
      trigger_start_ = start;
      trigger_end_ = end;
      cpu_.Freeze();
      freeze_requested_.store(true, std::memory_order_release);
    }
  }

  // Graphics writer only. Complete the notification pair before freezing.
  // If no later notification arrives, export graphics.Frozen()==false; never
  // manufacture coverage or have the CPU mutate this writer's storage.
  template<class Clock>
  void GraphicsBoundary(bool before, Clock&& clock) noexcept {
    if (!enabled_ || graphics_.Frozen()) return;
    graphics_.Record(before ? Kind::BeforeNotify : Kind::AfterNotify, clock);
    if (!before && freeze_requested_.load(std::memory_order_acquire)) graphics_.Freeze();
  }

  // All inspection below is post-both-join, including the non-atomic metadata.
  bool Triggered() const noexcept { return cpu_.Frozen(); }
  std::uint64_t TriggerStart() const noexcept { return trigger_start_; }
  std::uint64_t TriggerEnd() const noexcept { return trigger_end_; }
  std::uint64_t InvalidWaits() const noexcept { return invalid_waits_; }
  const Buffer& CPU() const noexcept { return cpu_; }
  const Buffer& Graphics() const noexcept { return graphics_; }

private:
  Buffer cpu_, graphics_;
  std::atomic<bool> freeze_requested_{false};
  bool enabled_ = false;
  std::uint64_t not_before_ = 0, threshold_ = 0;
  std::uint64_t trigger_start_ = 0, trigger_end_ = 0, invalid_waits_ = 0;
};
} // namespace galaxypad
