// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once

#include <cstdint>
#include <cstdlib>

namespace GalaxyPadDiagnostics
{
struct EFBReadContext
{
  std::uint32_t pc = 0;
  std::uint32_t lr = 0;
};

// Zero means unattributed, not a mirrored/interpreter-state guess.
inline thread_local EFBReadContext s_efb_read_context;

inline bool IsEFBReadContextEnabled()
{
  static const bool enabled = [] {
    const char* path = std::getenv("GALAXYPAD_EFB_TRACE");
    return path && *path;
  }();
  return enabled;
}

class ScopedEFBReadContext final
{
public:
  ScopedEFBReadContext(std::uint32_t pc, std::uint32_t lr)
      : m_enabled(IsEFBReadContextEnabled())
  {
    if (m_enabled)
    {
      m_previous = s_efb_read_context;
      s_efb_read_context = {pc, lr};
    }
  }

  ~ScopedEFBReadContext()
  {
    if (m_enabled)
      s_efb_read_context = m_previous;
  }

  ScopedEFBReadContext(const ScopedEFBReadContext&) = delete;
  ScopedEFBReadContext& operator=(const ScopedEFBReadContext&) = delete;

private:
  const bool m_enabled;
  EFBReadContext m_previous;
};

inline EFBReadContext CurrentEFBReadContext()
{
  return s_efb_read_context;
}
}  // namespace GalaxyPadDiagnostics
