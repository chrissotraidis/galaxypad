#pragma once

#include <array>
#include <cstdint>
#include <cstdio>
#include <ctime>

namespace galaxypad::diagnostics
{
inline std::uint64_t ThreadCpuNs()
{
#if defined(CLOCK_THREAD_CPUTIME_ID)
  timespec time{};
  if (clock_gettime(CLOCK_THREAD_CPUTIME_ID, &time) == 0)
    return std::uint64_t(time.tv_sec) * 1000000000 + time.tv_nsec;
#endif
  return 0; // Unsupported/failed clocks invalidate measurement; never use wall time.
}

enum class RunLane : unsigned { Native, NonNativeRouting };

class RunCost
{
public:
  using Clock = std::uint64_t (*)();
  struct Totals
  {
    std::uint64_t spans = 0, selected = 0, completed = 0, ns = 0, maximum_ns = 0;
    long double squared_ns = 0;
  };

  explicit RunCost(Clock clock = ThreadCpuNs) : m_clock(clock), m_start(clock()) {}
  RunCost(const RunCost&) = delete;
  RunCost& operator=(const RunCost&) = delete;

  class Scope
  {
  public:
    Scope(RunCost* owner, RunLane lane) : m_owner(owner), m_lane(lane)
    {
      if (!owner)
        return;
      auto& totals = owner->lanes[unsigned(lane)];
      ++totals.spans;
      auto& random = owner->m_random;
      random ^= random << 13;
      random ^= random >> 17;
      random ^= random << 5;
      m_selected = (random & 255u) == 0; // Approximate 1/256 inclusion, not periodic.
      if (m_selected)
      {
        ++totals.selected;
        m_start = owner->m_clock();
      }
    }
    Scope(const Scope&) = delete;
    Scope& operator=(const Scope&) = delete;
    ~Scope()
    {
      if (!m_selected)
        return;
      const auto end = m_owner->m_clock();
      if (!m_start || end < m_start)
      {
        ++m_owner->clock_errors;
        return;
      }
      const auto elapsed = end - m_start;
      auto& totals = m_owner->lanes[unsigned(m_lane)];
      ++totals.completed;
      totals.ns += elapsed;
      totals.squared_ns += static_cast<long double>(elapsed) * elapsed;
      if (elapsed > totals.maximum_ns)
        totals.maximum_ns = elapsed;
    }
  private:
    RunCost* m_owner;
    RunLane m_lane;
    bool m_selected = false;
    std::uint64_t m_start = 0;
  };

  // Call on the SAME CPU thread after every scope has ended, before Run returns.
  void Report(std::FILE* output)
  {
    const auto end = m_clock();
    if (!m_start || end < m_start)
      ++clock_errors;
    const auto total = m_start && end >= m_start ? end - m_start : 0;
    if (!output)
      return;
    std::fprintf(output, "[galaxypad-run-cost] cpu_ns=%llu clock_errors=%llu inclusion=256\n",
                 static_cast<unsigned long long>(total),
                 static_cast<unsigned long long>(clock_errors));
    for (unsigned i = 0; i < lanes.size(); ++i)
    {
      const auto& lane = lanes[i];
      std::fprintf(output, "[galaxypad-run-cost-lane] lane=%u spans=%llu selected=%llu "
                   "completed=%llu ns=%llu squared_ns=%.0Lf maximum_ns=%llu\n", i,
                   static_cast<unsigned long long>(lane.spans),
                   static_cast<unsigned long long>(lane.selected),
                   static_cast<unsigned long long>(lane.completed),
                   static_cast<unsigned long long>(lane.ns), lane.squared_ns,
                   static_cast<unsigned long long>(lane.maximum_ns));
    }
  }

  std::array<Totals, 2> lanes{};
  std::uint64_t clock_errors = 0;
private:
  Clock m_clock;
  std::uint64_t m_start;
  std::uint32_t m_random = 0x9e3779b9;
};
} // namespace galaxypad::diagnostics
