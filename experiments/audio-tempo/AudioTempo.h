// SPDX-License-Identifier: GPL-3.0-or-later
// Isolated offline prototype. Not connected to GalaxyPad's mixer or controls.
#pragma once

#include <algorithm>
#include <array>
#include <atomic>
#include <cmath>
#include <cstddef>
#include <cstdint>

namespace galaxypad::experiment {

// 32 kHz stereo WSOLA ahead of a fixed-rate output resampler. Push has one
// producer, Pull one consumer. Reset requires both sides stopped, like replacing
// a sound stream. Construction/reset and all processing allocate no memory.
// Fixed input/synthesis capacity is an input-time bound, NOT wall latency at
// reduced tempo. Offline source-provenance tests separately gate actual wall age.
class AudioTempo final {
 public:
  struct Frame {float left = 0, right = 0;};
  static constexpr std::size_t SampleRate = 32000;
  static constexpr std::size_t Hop = 128;
  static constexpr std::size_t Window = Hop * 2;
  // +/-12 ms covers half a period down to about 42 Hz. A shorter search can
  // track input phase drift instead of finding the next matching bass period.
  static constexpr std::size_t Search = 384;
  static constexpr std::size_t RingSize = 4096;
  static constexpr std::size_t MaxInput = 3584;
  static constexpr std::size_t ResamplerReserve = 128;
  static constexpr std::size_t TargetInput = 2048;
  static constexpr std::uint64_t NoSource = ~std::uint64_t{};
  static_assert(MaxInput + Hop + ResamplerReserve == SampleRate * 120 / 1000);
  static_assert(std::atomic<std::uint64_t>::is_always_lock_free);

  struct Statistics {
    std::uint64_t inputAccepted = 0, inputRetired = 0, inputRejected = 0;
    std::uint64_t retainedInputDiscardedOnStall = 0, retainedInputDiscardedOnFlush = 0;
    std::uint64_t outputFrames = 0, synthesizedHops = 0, bypassHops = 0;
    std::uint64_t unityEntries = 0, unityExits = 0;
    // Counts an actual unavailable analysis window on every attempted hop.
    // No replay path increments input supply or conceals a failed request.
    std::uint64_t unavailableWindows = 0, startupFrames = 0;
    std::uint64_t maximumBufferedFrames = 0;
    double supplyRatio = 1, analysisRatio = 1;
  };

  void Reset(bool paused = false) {
    m_paused = paused;
    m_head = 0; m_rejected = 0; m_stats = {};
    ResetConsumerState(0);
  }

  // Consumer-only pause/resume flush, safe while the producer remains active.
  // Never resets or rewrites producer head. Call between Pull invocations;
  // the host emits silence while paused and flushes stale data before resuming.
  void FlushOnConsumer() {
    const auto head = m_head.load(std::memory_order_acquire);
    m_stats.retainedInputDiscardedOnFlush += head-m_tail.load(std::memory_order_relaxed);
    ResetConsumerState(head);
  }

  std::size_t Push(const Frame* source, std::size_t count) {
    if (m_paused) return 0;  // Lifecycle reset is quiescent, not concurrent.
    const auto head = m_head.load(std::memory_order_relaxed);
    const auto tail = m_tail.load(std::memory_order_acquire);
    const auto accepted = std::min<std::uint64_t>(count, MaxInput - (head - tail));
    for (std::size_t i = 0; i < accepted; ++i) m_input[(head + i) & Mask] = source[i];
    m_head.store(head + accepted, std::memory_order_release);
    if (count != accepted) m_rejected.fetch_add(count - accepted, std::memory_order_relaxed);
    return accepted;
  }

  void Pull(Frame* output, std::size_t count, std::uint64_t* oldestSource = nullptr) {
    if (!count) return;
    if (m_paused) {
      std::fill_n(output, count, Frame{});
      if (oldestSource) std::fill_n(oldestSource, count, NoSource);
      return;
    }
    const auto head = m_head.load(std::memory_order_acquire);
    m_epochRequested += count;
    m_windowProduced += head-m_observedHead;
    m_windowRequested += count;
    if (m_windowRequested >= SampleRate / 4) {
      if (double(m_windowProduced) / m_windowRequested >= .99)
        m_fullSpeedWindows = std::min(2u,m_fullSpeedWindows+1);
      else m_fullSpeedWindows = 0;
      m_windowRequested = 0; m_windowProduced = 0;
    }
    // Input observations use requested output duration; no clocks or locks in
    // the callback. A 60 ms estimator reacts to a 1.0 -> 0.67 speed step before
    // its cumulative deficit can consume the lookahead reserve.
    const double alpha = std::min(1., double(count) / (SampleRate * .060));
    if (count) m_supply += alpha * (double(head - m_observedHead) / count - m_supply);
    // Smooth the control rate separately from fast starvation/bypass detection.
    // Otherwise clipping the troughs of packetized supply to the minimum tempo
    // biases average consumption upward, eventually draining a healthy stream.
    const double rateAlpha = std::min(1., double(count) / (SampleRate * .100));
    m_rateEstimate += rateAlpha * (m_supply-m_rateEstimate);
    m_observedHead = head;
    const auto queued = head - m_tail.load(std::memory_order_relaxed);
    m_stats.maximumBufferedFrames = std::max<std::uint64_t>(
        m_stats.maximumBufferedFrames, queued + Hop - m_pendingIndex);
    if (!m_started) {
      // The long-term target includes retained search history; startup has no
      // such history yet. Do not add that history allowance to initial delay.
      if (queued < TargetInput - Search - Hop) {
        std::fill_n(output, count, Frame{});
        if (oldestSource) std::fill_n(oldestSource, count, NoSource);
        m_stats.startupFrames += count; return;
      }
      m_started = true;
      // Preserve initial normal-speed identity without treating an isolated
      // packet as sustained full-speed input during a slowed stream.
      m_unity = double(head-m_epochHead) / m_epochRequested >= .995;
    }
    // Queue error adjusts input advance, not sample frequency. Bounds explicitly
    // limit this prototype to slowdown compensation, rather than unbounded replay.
    m_ratio = std::clamp(m_rateEstimate + .50 * (double(queued) - TargetInput) / TargetInput,
                         .60, 1.03);
    // Stay bit-transparent at normal speed despite producer packet jitter.
    // Enter tempo processing only when real forward reserve is being drained;
    // return to bypass only after sustained supply has rebuilt that reserve.
    const auto forward = head - static_cast<std::uint64_t>(m_position);
    const auto pending = Hop-m_pendingIndex;
    const auto neededHops = count > pending ? (count-pending+Hop-1)/Hop : 0;
    const auto unityNeed = neededHops ? Window+(neededHops-1)*Hop : 0;
    const bool wasUnity = m_unity;
    if (m_unity && forward < unityNeed) m_unity = false;
    else if (!m_unity && m_fullSpeedWindows >= 2 && m_supply >= .995 &&
             forward >= TargetInput-Search-Hop) m_unity = true;
    if (wasUnity != m_unity) {
      if (m_unity) ++m_stats.unityEntries; else ++m_stats.unityExits;
    }
    const bool unity = m_unity;
    if (unity) m_ratio = 1.;
    for (std::size_t i = 0; i < count; ++i) {
      if (m_pendingIndex == Hop) {
        if (!Synthesize(unity)) {
          ++m_stats.unavailableWindows;
          // A genuine stall drains the already-held overlap once, then silence.
          // It never rewinds input, creates fake supply, or waits indefinitely.
          if (m_overlapValid) {
            for (std::size_t j = 0; j < Hop; ++j) {
              const float fade = float(Hop - 1 - j) / (Hop - 1);
              m_pending[j] = Scale(m_overlap[j], fade);
              m_pendingSource[j] = fade ? m_overlapSource[j] : NoSource;
            }
            m_overlapValid = false;
          } else {m_pending = {}; m_pendingSource.fill(NoSource);}
          m_pendingIndex = 0;
          if (!m_recovering) {
            // Old lookahead must not emerge a second late after a long stall.
            // Discard retained input explicitly once; subsequent failed requests
            // count normally while fresh input accumulates for recovery.
            const auto restart = m_head.load(std::memory_order_acquire);
            const auto oldTail = m_tail.load(std::memory_order_relaxed);
            m_stats.retainedInputDiscardedOnStall += restart-oldTail;
            m_position = double(restart);
            m_tail.store(restart,std::memory_order_release);
            m_recovering = true;
          }
        }
      }
      if (oldestSource) oldestSource[i] = m_pendingSource[m_pendingIndex];
      output[i] = m_pending[m_pendingIndex++];
    }
    m_stats.outputFrames += count;
  }

  // Call on consumer or after stopping both sides. Producer-owned values atomic.
  Statistics ReadStatistics() const {
    auto result = m_stats;
    result.inputAccepted = m_head.load(std::memory_order_acquire);
    result.inputRetired = m_tail.load(std::memory_order_relaxed);
    result.inputRejected = m_rejected.load(std::memory_order_relaxed);
    result.supplyRatio = m_supply; result.analysisRatio = m_ratio;
    return result;
  }

 private:
  static constexpr std::size_t Mask = RingSize - 1;
  void ResetConsumerState(std::uint64_t head) {
    m_observedHead = head; m_epochHead = head; m_position = double(head); m_lastStart = head;
    m_epochRequested = 0; m_windowRequested = 0; m_windowProduced = 0; m_fullSpeedWindows = 0;
    m_pendingIndex = Hop; m_started = false; m_overlapValid = false; m_unity = true;
    m_recovering = false; m_supply = 1; m_rateEstimate = 1; m_ratio = 1;
    m_overlap = {}; m_pending = {};
    m_tail.store(head,std::memory_order_release);
  }
  static Frame Scale(Frame a, float s) {return {a.left * s, a.right * s};}
  static Frame Blend(Frame a, Frame b, float s) {
    return {a.left + (b.left - a.left) * s, a.right + (b.right - a.right) * s};
  }
  const Frame& At(std::uint64_t index) const {return m_input[index & Mask];}

  bool Synthesize(bool unity) {
    const auto head = m_head.load(std::memory_order_acquire);
    const auto tail = m_tail.load(std::memory_order_relaxed);
    const auto nominal = static_cast<std::uint64_t>(m_position);
    std::uint64_t start = nominal;
    const auto low = nominal > Search ? std::max(tail, nominal - Search) : tail;
    // A complete nominal analysis window is mandatory. Forward phase-search
    // candidates are optional: never declare starvation merely because the
    // producer has not supplied the entire positive search margin yet.
    if (head < nominal + Window) return false;
    const auto high = std::min(nominal + Search, head - Window);
    bool direct = unity && (!m_overlapValid || nominal == m_lastStart + Hop);
    if (m_overlapValid && !direct) {
      // A shared offset for both channels preserves stereo phase relationships.
      double best = -2.;
      double overlapEnergy = 1.e-20;
      for (const auto a : m_overlap) overlapEnergy += a.left*a.left + a.right*a.right;
      for (auto candidate = low; candidate <= high; ++candidate) {
        double dot = 0., energy = 1.e-20;
        for (std::size_t i = 0; i < Hop; ++i) {
          const auto a = m_overlap[i], b = At(candidate + i);
          dot += a.left*b.left + a.right*b.right;
          energy += b.left*b.left + b.right*b.right;
        }
        // Mild center preference breaks ties in quiet/periodic regions, keeping
        // analysis position independent from phase-alignment corrections.
        const double score = dot / std::sqrt(overlapEnergy * energy) -
            .0001 * std::abs(double(candidate) - m_position) / Search;
        if (score > best) {best = score; start = candidate;}
      }
    }
    for (std::size_t i = 0; i < Hop; ++i) {
      const Frame fresh = At(start + i);
      m_pending[i] = m_overlapValid && !direct ?
          Blend(m_overlap[i], fresh, float(i) / (Hop - 1)) : fresh;
      m_pendingSource[i] = m_overlapValid && !direct && i < Hop - 1 ?
          (i ? std::min(m_overlapSource[i], start+i) : m_overlapSource[i]) : start+i;
      m_overlap[i] = At(start + Hop + i);
      m_overlapSource[i] = start + Hop + i;
    }
    if (direct) ++m_stats.bypassHops; else ++m_stats.synthesizedHops;
    m_overlapValid = true; m_lastStart = start; m_pendingIndex = 0;
    m_recovering = false;
    if (unity && !direct) m_position = double(start);
    m_position += Hop * m_ratio;
    const auto next = static_cast<std::uint64_t>(m_position);
    const auto retired = next > Search ? next - Search : 0;
    m_tail.store(std::max(tail, retired), std::memory_order_release);
    return true;
  }

  alignas(64) std::array<Frame, RingSize> m_input{};
  alignas(64) std::atomic<std::uint64_t> m_head{0};
  alignas(64) std::atomic<std::uint64_t> m_tail{0};
  std::atomic<std::uint64_t> m_rejected{0};
  std::array<Frame, Hop> m_overlap{}, m_pending{};
  std::array<std::uint64_t, Hop> m_overlapSource{}, m_pendingSource{};
  std::uint64_t m_observedHead = 0, m_lastStart = 0;
  std::uint64_t m_epochHead = 0, m_epochRequested = 0, m_windowProduced = 0, m_windowRequested = 0;
  unsigned m_fullSpeedWindows = 0;
  double m_position = 0, m_supply = 1, m_rateEstimate = 1, m_ratio = 1;
  std::size_t m_pendingIndex = Hop;
  bool m_paused = false, m_started = false, m_overlapValid = false, m_unity = true;
  bool m_recovering = false;
  Statistics m_stats{};
};
}  // namespace galaxypad::experiment
