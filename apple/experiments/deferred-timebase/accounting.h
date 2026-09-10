#pragma once

#include <cassert>
#include <cstdint>
#include <limits>

namespace galaxypad::experiments
{
// Arithmetic experiment only. NOT connected to CPUState or the product runtime.
// Every observer must materialize first; integration must enumerate them rather
// than treating an unobserved read/write/copy as safe.
class DeferredTimebase
{
public:
  DeferredTimebase(std::uint64_t ticks, std::uint64_t remainder)
      : m_ticks(ticks), m_pending(remainder)
  {
    assert(remainder < 12);
  }

  void Charge(std::uint64_t cycles)
  {
    constexpr auto maximum = std::numeric_limits<std::uint64_t>::max();
    // Preserve baseline uint64 addition-wrap semantics even for huge charges.
    // Normal dispatches only add pending cycles; no division or TB store.
    if (cycles > maximum - 11 || m_pending > maximum - cycles)
    {
      Materialize();
      const auto total = m_pending + cycles;
      m_ticks += total / 12;
      m_pending = total % 12;
    }
    else
    {
      m_pending += cycles;
    }
  }

  std::uint64_t Materialize()
  {
    m_ticks += m_pending / 12;
    m_pending %= 12;
    return m_ticks;
  }

  void WriteLow(std::uint32_t value)
  {
    Materialize();
    m_ticks = (m_ticks & 0xffffffff00000000ULL) | value;
  }

  void WriteHigh(std::uint32_t value)
  {
    Materialize();
    m_ticks = (std::uint64_t(value) << 32) | std::uint32_t(m_ticks);
  }

  std::uint64_t Remainder()
  {
    Materialize();
    return m_pending;
  }

private:
  std::uint64_t m_ticks;
  std::uint64_t m_pending;
};
} // namespace galaxypad::experiments
