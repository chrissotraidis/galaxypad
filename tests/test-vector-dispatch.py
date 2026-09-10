"""Actual Dolphin dispatch tables with operation-body spies, NOT guest semantics.

Optional --benchmark measures dispatch alone; excludes fetch, MMU, HLE, actual
operation bodies and the chassis. Never interpret its output as game speed.
"""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
core = root/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC'
tables = (core/'Interpreter/Interpreter_Tables.cpp').read_text()
tables = re.sub(r'^#include.*$', '', tables, flags=re.M)
gekko = (core/'Gekko.h').read_text()
start = gekko.index('union UGeckoInstruction')
end = gekko.index('\n};', start) + 3
instruction = gekko[start:end]
names = sorted(set(re.findall(r'Interpreter::(\w+)', tables)) -
               {'Instruction', 'GetInterpreterOp', 'RunInterpreterOp',
                'RunTable4', 'RunTable19', 'RunTable31', 'RunTable59', 'RunTable63'})
spies = '\n'.join(
    f'[[gnu::noinline]] static void {name}(Interpreter& i, UGeckoInstruction w) '
    f'{{ i.observed = {index + 1}; i.word = w.hex; }}'
    for index, name in enumerate(names))
program = r'''
#include <array>
#include <cassert>
#include <cstdint>
#include <chrono>
#include <iostream>
#include <vector>
using u32 = std::uint32_t;
#define ASSERT(x) assert(x)
INSTRUCTION
struct Interpreter {
  using Instruction = void(*)(Interpreter&, UGeckoInstruction);
  unsigned observed = 0, word = 0;
  SPIES
  static Instruction GetInterpreterOp(UGeckoInstruction);
  static void RunInterpreterOp(Interpreter&, UGeckoInstruction);
  static void RunTable4(Interpreter&, UGeckoInstruction);
  static void RunTable19(Interpreter&, UGeckoInstruction);
  static void RunTable31(Interpreter&, UGeckoInstruction);
  static void RunTable59(Interpreter&, UGeckoInstruction);
  static void RunTable63(Interpreter&, UGeckoInstruction);
};
TABLES
#include "apple/experiments/vector-execution/dispatch.h"
using namespace galaxypad::vector_experiment;
struct Entry {u32 pc, word;};
volatile std::uint64_t sink = 0;
int main(int argc, char**) {
  Dispatch<Interpreter, UGeckoInstruction> dispatch;
  std::vector<Entry> entries;
  for (u32 pc = 0; pc < 0x1000; ++pc) {
    auto expected = Expected(pc);
    if (!expected) {assert(!dispatch.Lookup(pc, UGeckoInstruction{0})); continue;}
    UGeckoInstruction word{expected->word};
    auto op = dispatch.Lookup(pc, word);
    assert(op && op == Interpreter::GetInterpreterOp(word));
    Interpreter baseline, candidate;
    Interpreter::RunInterpreterOp(baseline, word);
    op(candidate, word);
    assert(baseline.observed == candidate.observed && baseline.word == candidate.word);
    for (unsigned bit = 0; bit < 32; ++bit)
      assert(!dispatch.Lookup(pc, UGeckoInstruction{word.hex ^ (u32{1} << bit)}));
    entries.push_back({pc, word.hex});
  }
  assert(entries.size() == 121);
  if (argc < 2) return 0;
  // Same entries, same spy bodies, ABBA order. No representative game weighting.
  for (bool candidate : {false, true, true, false}) {
    Interpreter state;
    std::uint64_t checksum = 0;
    const auto start = std::chrono::steady_clock::now();
    for (unsigned repeat = 0; repeat < 200000; ++repeat)
      for (auto entry : entries) {
        UGeckoInstruction word{entry.word};
        if (candidate) {
          auto op = dispatch.Lookup(entry.pc, word);
          if (op) op(state, word);
          else Interpreter::RunInterpreterOp(state, word);
        } else Interpreter::RunInterpreterOp(state, word);
        checksum += state.observed + state.word;
      }
    const auto ns = std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::steady_clock::now() - start).count();
    sink = checksum;
    std::cout << (candidate ? "guarded" : "baseline") << " ns/dispatch="
              << double(ns) / (200000 * entries.size()) << " checksum=" << checksum << '\n';
  }
}
'''.replace('INSTRUCTION', instruction).replace('SPIES', spies).replace('TABLES', tables)
with tempfile.TemporaryDirectory(prefix='galaxypad-vector-dispatch-') as directory:
    cpp = Path(directory)/'test.cpp'
    binary = Path(directory)/'test'
    cpp.write_text(program)
    flags = ['-O3'] if '--benchmark' in sys.argv else ['-O2', '-fsanitize=address,undefined']
    subprocess.run(['clang++', '-std=c++20', *flags, '-I', str(root), str(cpp),
                    '-o', str(binary)], check=True)
    subprocess.run([str(binary)] + (['benchmark'] if '--benchmark' in sys.argv else []),
                   check=True)
print('Actual dispatch-table operation identity passes; operation bodies are spies, not semantics')
