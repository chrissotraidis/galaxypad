// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <algorithm>
#include <atomic>
#include <cstdint>

namespace galaxypad::audio {
struct OutputSnapshot {
  bool available;
  std::uint64_t callbacks, requestedFrames, frames, nonzeroFrames, shortCallbacks;
  std::uint32_t peak;
};

// One RemoteIO callback writer. Start is called only before starting that audio
// unit, never while a callback is active. Readers are main-thread diagnostics.
class OutputCounters {
 public:
  void Start(bool enabled) {
    enabled_.store(false, std::memory_order_release);
    callbacks_=0; requested_=0; frames_=0; nonzero_=0; short_=0; peak_=0;
    enabled_.store(enabled, std::memory_order_release);
  }
  void Record(const std::int16_t* stereo, std::uint32_t requested,
              std::uint32_t available) {
    if (!enabled_.load(std::memory_order_acquire)) return;
    const auto frames = stereo ? std::min(requested, available) : 0u;
    std::uint64_t nonzero=0;
    std::uint32_t peak=0;
    for (std::uint32_t i=0; i<frames; ++i) {
      const int left=stereo[2ull*i], right=stereo[2ull*i+1];
      const auto value=static_cast<std::uint32_t>(std::max(left<0?-left:left,
                                                        right<0?-right:right));
      nonzero += value!=0;
      peak=std::max(peak,value);
    }
    callbacks_.fetch_add(1,std::memory_order_relaxed);
    requested_.fetch_add(requested,std::memory_order_relaxed);
    frames_.fetch_add(frames,std::memory_order_relaxed);
    nonzero_.fetch_add(nonzero,std::memory_order_relaxed);
    if(frames<requested)short_.fetch_add(1,std::memory_order_relaxed);
    // Single writer: no retry loop or audio-thread mutex required.
    peak_.store(std::max(peak,peak_.load(std::memory_order_relaxed)),std::memory_order_relaxed);
  }
  OutputSnapshot Read() const {
    return {enabled_.load(std::memory_order_acquire),
            callbacks_.load(std::memory_order_relaxed),requested_.load(std::memory_order_relaxed),
            frames_.load(std::memory_order_relaxed),nonzero_.load(std::memory_order_relaxed),
            short_.load(std::memory_order_relaxed),peak_.load(std::memory_order_relaxed)};
  }
 private:
  static_assert(std::atomic<std::uint64_t>::is_always_lock_free);
  static_assert(std::atomic<std::uint32_t>::is_always_lock_free);
  static_assert(std::atomic<bool>::is_always_lock_free);
  std::atomic<bool> enabled_{false};
  std::atomic<std::uint64_t> callbacks_{0},requested_{0},frames_{0},nonzero_{0},short_{0};
  std::atomic<std::uint32_t> peak_{0};
};
inline OutputCounters outputCounters;
} // namespace galaxypad::audio
