#pragma once
#include <charconv>
#include <cstdint>
#include <cstring>
#include <limits>

namespace galaxypad {
// Explicit delay required when recording is requested. Reject whitespace,
// signs, suffixes, excessive delay and overflow; never silently arm at startup.
inline bool CompletionArmDeadline(const char* delay_ms, std::uint64_t now_ns,
                                  std::uint64_t& deadline_ns) noexcept {
  if (!delay_ms || !*delay_ms) return false;
  std::uint64_t delay = 0;
  const char* end = delay_ms + std::strlen(delay_ms);
  const auto parsed = std::from_chars(delay_ms, end, delay);
  if (parsed.ec != std::errc{} || parsed.ptr != end || delay > 3'600'000) return false;
  const auto ns = delay * 1'000'000;
  if (now_ns > std::numeric_limits<std::uint64_t>::max() - ns) return false;
  deadline_ns = now_ns + ns;
  return true;
}
} // namespace galaxypad
