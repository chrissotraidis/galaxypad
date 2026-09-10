// Diagnostic microbenchmark, not a game-performance acceptance test.
#include "../patches/experiments/completion-flight-recorder.h"
#include <chrono>
#include <cstdio>
#include <limits>

using Recorder = galaxypad::CompletionFlightRecorder;
using Clock = std::chrono::steady_clock;

__attribute__((noinline)) void CPU(Recorder& recorder, std::uint64_t i) {
  recorder.CPUWait(i * 100, i * 100 + 10);
}
__attribute__((noinline)) void Graphics(Recorder& recorder) {
  recorder.GraphicsBoundary(true);
  recorder.GraphicsBoundary(false);
}
__attribute__((noinline)) void Baseline(Recorder&, std::uint64_t i) {
  asm volatile("" : : "r"(i) : "memory");
}

template<class Tick>
double Measure(Recorder& recorder, Tick tick) {
  constexpr std::uint64_t count = 2'000'000;
  auto start = Clock::now();
  for (std::uint64_t i = 0; i < count; ++i) tick(recorder, i);
  return std::chrono::duration<double, std::nano>(Clock::now()-start).count()/count;
}

int main() {
  Recorder recorder;
  std::puts("trial,mode,cpu_pair_ns,graphics_pair_ns,baseline_ns");
  for (int trial = 0; trial < 6; ++trial) {
    // Alternate order. Configure allocates outside the measured interval.
    for (int index = 0; index < 2; ++index) {
      const bool enabled = (trial + index) % 2;
      // No FlushAfterJoin: this benchmark never writes an output file.
      recorder.Configure(enabled ? "benchmark-unused" : nullptr,
                         std::numeric_limits<std::uint64_t>::max(), 20'000'000);
      const double baseline = Measure(recorder, Baseline);
      const double cpu = Measure(recorder, CPU);
      const double graphics = Measure(recorder, [](Recorder& r, std::uint64_t) { Graphics(r); });
      std::printf("%d,%s,%.3f,%.3f,%.3f\n", trial, enabled ? "enabled" : "disabled",
                  cpu, graphics, baseline);
    }
  }
}
