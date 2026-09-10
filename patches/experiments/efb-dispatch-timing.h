// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>

namespace GalaxyPadDiagnostics
{
inline std::FILE* GetEFBDispatchTrace()
{
  static std::FILE* const file = [] {
    const char* path = std::getenv("GALAXYPAD_EFB_DISPATCH_TRACE");
    if (!path || !*path)
      return static_cast<std::FILE*>(nullptr);
    auto* result = std::fopen(path, "w");
    if (result)
      std::fprintf(result, "queued_ns,entered_ns,finished_ns,returned_ns,x,y,guest_pc,guest_lr\n");
    return result;
  }();
  return file;
}

inline std::uint64_t EFBDispatchNow()
{
  return std::chrono::duration_cast<std::chrono::nanoseconds>(
      std::chrono::steady_clock::now().time_since_epoch()).count();
}

// Dispatch must invoke its callback exactly once and wait for completion, as
// AsyncRequests::PushBlockingEvent does. Its future synchronizes these writes.
// Dispatch duration includes video queue/pipeline work, not just sleeping.
template <typename Dispatch, typename Read>
auto TraceEFBDispatch(Dispatch&& dispatch, Read&& read, std::uint32_t x,
                      std::uint32_t y, std::uint32_t pc, std::uint32_t lr)
{
  auto* file = GetEFBDispatchTrace();
  if (!file)
    return dispatch(read);

  std::uint64_t entered = 0, finished = 0;
  const auto queued = EFBDispatchNow();
  auto result = dispatch([&] {
    entered = EFBDispatchNow();
    auto value = read();
    finished = EFBDispatchNow();
    return value;
  });
  const auto returned = EFBDispatchNow();
  std::fprintf(file, "%llu,%llu,%llu,%llu,%u,%u,0x%08x,0x%08x\n",
               static_cast<unsigned long long>(queued),
               static_cast<unsigned long long>(entered),
               static_cast<unsigned long long>(finished),
               static_cast<unsigned long long>(returned), x, y, pc, lr);
  return result;
}
}  // namespace GalaxyPadDiagnostics
