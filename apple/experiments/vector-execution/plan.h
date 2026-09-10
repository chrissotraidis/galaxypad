#pragma once

#include <array>
#include <cstdint>
#include <optional>

namespace galaxypad::vector_experiment
{
// RMGE01 DOL 2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09.
// Recognition only: no cached guest bytes, fetches, execution or state mutation.
// A caller must compare the CURRENT authoritative instruction-cache fetch, not RAM.
inline constexpr std::array<std::uint32_t, 7> kSystemCall = {
    0x7d30faa6, 0x612a0008, 0x7d50fba6, 0x4c00012c,
    0x7c0004ac, 0x7d30fba6, 0x4c000064};
inline constexpr std::array<std::uint32_t, 38> kGeneric = {
    0x7c9043a6, 0x808000c0, 0x9064000c, 0x7c7042a6, 0x90640010,
    0x90a40014, 0xa06401a2, 0x60630002, 0xb06401a2, 0x7c600026,
    0x90640080, 0x7c6802a6, 0x90640084, 0x7c6902a6, 0x90640088,
    0x7c6102a6, 0x9064008c, 0x7c7a02a6, 0x90640198, 0x7c7b02a6,
    0x9064019c, 0x7c651b78, 0x60000000, 0x7c6000a6, 0x60630030,
    0x7c7b03a6, 0x38600000, 0x808000d4, 0x54a507bd, 0x40820014,
    0x3ca0804a, 0x38a51d3c, 0x7cba03a6, 0x4c000064,
    0x546515ba, 0x80a53000, 0x7cba03a6, 0x4c000064};

struct Instruction
{
  std::uint32_t word;
  std::uint32_t index;
  bool system_call;
  // Both generic branches contain rfi. Never continue a vector plan past it.
  constexpr bool ReturnsFromInterrupt() const { return word == 0x4c000064; }
};

// All interior entries, including the unobserved default-handler branch.
// Deliberately no cached-address alias normalization or guest-memory access.
constexpr std::optional<Instruction> Expected(std::uint32_t pc)
{
  if ((pc & 3) != 0)
    return std::nullopt;
  const auto base = pc & ~std::uint32_t{0xff};
  const auto index = (pc & 0xff) / 4;
  if (base == 0xc00 && index < kSystemCall.size())
    return Instruction{kSystemCall[index], index, true};
  std::uint32_t exception = 0;
  switch (base)
  {
  case 0x500: exception = 4; break;
  case 0x800: exception = 7; break;
  case 0x900: exception = 8; break;
  default: return std::nullopt;
  }
  if (index >= kGeneric.size())
    return std::nullopt;
  const auto word = index == 0x68 / 4 ? kGeneric[index] | exception : kGeneric[index];
  return Instruction{word, index, false};
}

constexpr std::optional<Instruction> Recognize(std::uint32_t pc,
                                              std::uint32_t fetched_word)
{
  const auto expected = Expected(pc);
  if (!expected || expected->word != fetched_word)
    return std::nullopt;
  return expected;
}
}  // namespace galaxypad::vector_experiment
