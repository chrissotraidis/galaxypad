#include "../apple/experiments/vector-execution/plan.h"

#include <cassert>
#include <fstream>
#include <iterator>
#include <vector>

using namespace galaxypad::vector_experiment;

int main(int argc, char** argv)
{
  assert(argc == 2);
  std::ifstream stream(argv[1], std::ios::binary);
  const std::vector<unsigned char> dol{std::istreambuf_iterator<char>(stream), {}};
  assert(dol.size() > 0x4a60c8 + 28);
  auto read = [&](std::size_t offset) {
    return (std::uint32_t{dol[offset]} << 24) |
           (std::uint32_t{dol[offset + 1]} << 16) |
           (std::uint32_t{dol[offset + 2]} << 8) | dol[offset + 3];
  };
  unsigned accepted = 0, returns = 0;
  for (std::uint32_t pc = 0; pc < 0x1000; ++pc)
  {
    const auto base = pc & ~std::uint32_t{0xff};
    const auto offset = pc & 0xff;
    const bool system = base == 0xc00;
    const bool generic = base == 0x500 || base == 0x800 || base == 0x900;
    const bool supported = !(pc & 3) && ((system && offset < 28) ||
                                                       (generic && offset < 152));
    assert(Expected(pc).has_value() == supported);
    if (!supported)
    {
      assert(!Recognize(pc, 0x4c000064));
      continue;
    }
    auto word = read((system ? 0x4a60c8 : 0x49d1e0) + offset);
    if (generic && offset == 0x68)
      word |= base == 0x500 ? 4 : base == 0x800 ? 7 : 8;
    const auto instruction = Recognize(pc, word);
    assert(instruction && instruction->word == word);
    assert(instruction->index == offset / 4 && instruction->system_call == system);
    returns += instruction->ReturnsFromInterrupt();
    ++accepted;
    // RAM could still contain the expected word: only the supplied fetch counts.
    for (unsigned bit = 0; bit < 32; ++bit)
      assert(!Recognize(pc, word ^ (std::uint32_t{1} << bit)));
    assert(!Recognize(pc, 0));
    assert(!Recognize(pc | 0x80000000, word));
    assert(!Recognize(pc | 0xc0000000, word));
    assert(!Recognize(pc | 0xfff00000, word));
    assert(Recognize(pc, word)); // Refusal leaves no poisoned cache/state.
  }
  assert(accepted == 121 && returns == 7);
  assert(!Expected(0xffffffff));
}
