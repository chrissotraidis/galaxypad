// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>

namespace galaxypad::wiimote {
// RMGE01 main.dol SHA-256 must also be checked by the host before enabling
// this port policy. These are data writes only, on the emulated CPU thread.
inline constexpr char kDOLSHA256[] =
    "2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09";
inline constexpr std::uint32_t kSDA = 0x806A4CA0;
inline constexpr std::uint32_t kSleepAddress = 0x806A316A;
inline constexpr std::uint32_t kSetterAddress = 0x804D8A98;
inline constexpr std::array<std::uint32_t, 13> kSetterWords = {
    0x9421FFF0, 0x7C0802A6, 0x90010014, 0x93E1000C, 0x7C7F1B78,
    0x4BFCF63D, 0x9BEDE4CA, 0x4BFCF65D, 0x80010014, 0x83E1000C,
    0x7C0803A6, 0x38210010, 0x4E800020};

// WPAD's zero-minute setting disables guest idle disconnection. Galaxy sets
// five or fifteen minutes when a scene starts. A virtual Wii Remote has no
// physical battery to conserve; physical Xbox ownership remains independent.
// Return the old policy only when changed. Unknown code/state is intact.
inline std::optional<std::uint8_t> DisableGuestAutoSleep(
    std::uint8_t* mem1, std::size_t mem1Size, std::uint32_t r13) {
  constexpr std::size_t setterOffset = kSetterAddress - 0x80000000u;
  constexpr std::size_t sleepOffset = kSleepAddress - 0x80000000u;
  if (!mem1 || r13 != kSDA || mem1Size <= sleepOffset ||
      mem1Size < setterOffset + kSetterWords.size() * 4) return std::nullopt;
  const auto minutes = mem1[sleepOffset];
  if (minutes != 5 && minutes != 15) return std::nullopt;
  for (std::size_t i = 0; i < kSetterWords.size(); ++i) {
    const auto* p = mem1 + setterOffset + i * 4;
    const std::uint32_t word = (std::uint32_t(p[0]) << 24) |
        (std::uint32_t(p[1]) << 16) | (std::uint32_t(p[2]) << 8) | p[3];
    if (word != kSetterWords[i]) return std::nullopt;
  }
  mem1[sleepOffset] = 0;
  return minutes;
}
} // namespace galaxypad::wiimote
