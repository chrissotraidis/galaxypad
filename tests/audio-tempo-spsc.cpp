// SPDX-License-Identifier: GPL-3.0-or-later
// Ring ownership stress, not an audio-rate or latency fixture.
#include "../experiments/audio-tempo/AudioTempo.h"
#include <array>
#include <atomic>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <thread>

int main() {
  using Tempo = galaxypad::experiment::AudioTempo;
  Tempo tempo;
  std::atomic<bool> stop{false};
  std::thread producer([&] {
    std::array<Tempo::Frame,128> block;
    std::uint64_t ordinal = 0;
    while (!stop.load(std::memory_order_acquire)) {
      for (std::size_t i=0;i<block.size();++i) {
        const float value = float(int((ordinal+i)%1024)-512)/1024;
        block[i] = {value,-value};
      }
      // Deliberately backpressure/retry: test rejection accounting and ring
      // ownership under contention, not real producer scheduling or sound.
      const auto accepted = tempo.Push(block.data(),block.size());
      ordinal += accepted;
      if (!accepted) std::this_thread::yield();
    }
  });
  std::array<Tempo::Frame,341> output;
  std::uint64_t rendered = 0;
  for (unsigned i=0;i<2048;) {
    const auto before = tempo.ReadStatistics();
    if (before.inputAccepted-before.inputRetired < Tempo::TargetInput+512) {
      std::this_thread::yield(); continue;
    }
    tempo.Pull(output.data(),output.size());
    for (const auto frame:output) {
      assert(std::isfinite(frame.left) && frame.left == -frame.right);
      assert(std::abs(frame.left) <= .5f);
    }
    // Exercise consumer-only flush against a live producer. This must never
    // rewrite the producer's monotonically increasing publication index.
    if (i && i%127 == 0) {
      const auto beforeFlush = tempo.ReadStatistics().inputAccepted;
      tempo.FlushOnConsumer();
      assert(tempo.ReadStatistics().inputAccepted >= beforeFlush);
    }
    rendered += output.size(); ++i;
  }
  stop.store(true,std::memory_order_release); producer.join();
  const auto stats = tempo.ReadStatistics();
  assert(stats.unavailableWindows == 0);
  assert(stats.inputRetired <= stats.inputAccepted);
  std::printf("SPSC ownership PASS: rendered=%llu accepted=%llu retired=%llu rejected=%llu\n",
      (unsigned long long)rendered,(unsigned long long)stats.inputAccepted,
      (unsigned long long)stats.inputRetired,(unsigned long long)stats.inputRejected);
}
