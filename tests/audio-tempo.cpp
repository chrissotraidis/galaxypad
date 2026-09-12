// SPDX-License-Identifier: GPL-3.0-or-later
#include "../experiments/audio-tempo/AudioTempo.h"
#include <cassert>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <new>
#include <string>
#include <vector>

static std::uint64_t allocations = 0;
void* operator new(std::size_t n) {
  ++allocations;
  if (void* p = std::malloc(n)) return p;
  throw std::bad_alloc();
}
void operator delete(void* p) noexcept {std::free(p);}
void* operator new[](std::size_t n) {return ::operator new(n);}
void operator delete[](void* p) noexcept {::operator delete(p);}

using Tempo = galaxypad::experiment::AudioTempo;
using Frame = Tempo::Frame;
using Clock = std::chrono::steady_clock;

static Frame signal(std::uint64_t index, double frequency, int kind) {
  const double t = double(index) / Tempo::SampleRate;
  const float value = .7 * std::sin(2 * 3.141592653589793 * frequency * t);
  if (kind == 1) return {value, -value};
  if (kind == 2) return {value, float(.35 * std::sin(2 * 3.141592653589793 * frequency * t + .73))};
  if (kind == 3) {
    const double phase = std::fmod(t, .5);
    const float click = phase < .004 ? .8 * std::exp(-phase / .001) : 0;
    return {click + .04f * value, click + .02f * value};
  }
  if (kind == 4) return {value, float(.7 * std::sin(2 * 3.141592653589793 * 431 * t))};
  return {value, value * .5f};
}

int main(int argc, char** argv) {
  assert(argc == 8);
  const double ratio = std::atof(argv[1]), frequency = std::atof(argv[3]);
  const int callback = std::atoi(argv[2]), kind = std::atoi(argv[4]);
  const std::string scenario = argv[5], path = argv[6];
  const bool trace = std::getenv("GALAXYPAD_TEMPO_TRACE") != nullptr;
  const double seconds = std::atof(argv[7]);
  assert(callback > 0 && callback <= 1024 && ratio >= .5 && ratio <= 1);
  {
    Tempo capacity;
    std::array<Frame, Tempo::RingSize> source{};
    assert(capacity.Push(source.data(), source.size()) == Tempo::MaxInput);
    auto stats = capacity.ReadStatistics();
    assert(stats.inputAccepted == Tempo::MaxInput);
    assert(stats.inputRejected == source.size() - Tempo::MaxInput);
    assert(stats.inputRetired == 0);
    capacity.Pull(nullptr,0);
    assert(capacity.ReadStatistics().inputRetired == 0);
    capacity.Reset(true);
    assert(capacity.Push(source.data(), source.size()) == 0);
  }
  Tempo tempo;
  std::vector<Frame> input(callback * 8), output(callback), pcm;
  std::vector<std::uint64_t> provenance(callback), inputBirth;
  inputBirth.reserve(std::size_t(seconds * Tempo::SampleRate + callback));
  pcm.reserve(std::size_t(seconds * Tempo::SampleRate + callback));
  std::uint64_t inputIndex = 0, pushNs = 0, pullNs = 0, maxPullNs = 0;
  std::uint64_t maxWallAge = 0;
  std::uint64_t lastInputFrame = Tempo::NoSource, maxDeliveryGap = 0;
  std::uint64_t reportedStarvations = 0;
  double pendingInput = 0;
  bool resetOnce = false;
  bool flushOnce = false;
  std::size_t pauseOutputErrors = 0;
  const auto start = Clock::now();
  for (std::size_t frame = 0; frame < seconds * Tempo::SampleRate; frame += callback) {
    const double time = double(frame) / Tempo::SampleRate;
    if (scenario == "flush" && time >= 3 && !flushOnce) {
      const auto acceptedBefore = tempo.ReadStatistics().inputAccepted;
      tempo.FlushOnConsumer();
      assert(tempo.ReadStatistics().inputAccepted == acceptedBefore);
      flushOnce = true;
    }
    const bool paused = scenario == "reset" && time >= 3 && time < 4;
    if (paused && !resetOnce) {tempo.Reset(true); resetOnce = true;}
    if (scenario == "reset" && resetOnce && time >= 4) {
      tempo.Reset(); resetOnce = false; inputIndex = 0; pendingInput = 0; inputBirth.clear();
    }
    const auto callbackIndex = frame / callback;
    const auto gapBegin = (3*Tempo::SampleRate+callback-1)/callback;
    const auto missingCallbacks = std::max<std::size_t>(1,(Tempo::SampleRate*64/1000)/callback-1);
    bool stalled = (scenario == "stall" && time >= 3 && time < 4) ||
                   (scenario == "gap" && callbackIndex >= gapBegin &&
                    callbackIndex < gapBegin+missingCallbacks) || paused;
    double actualRatio = ratio;
    if (scenario == "changing" || scenario == "recover")
      actualRatio = time < 2 ? 1 : time < 5 ? ratio : scenario == "recover" ? 1 : .85;
    pendingInput += stalled ? 0 : callback * actualRatio;
    // Release a producer burst every three callbacks, preserving real supply.
    bool release = scenario == "bursty6" ? (frame / callback) % 6 == 0 :
                   scenario != "bursty" || (frame / callback) % 3 == 0;
    const auto supplied = release ? static_cast<std::size_t>(pendingInput) : 0;
    pendingInput -= supplied;
    if (supplied) {
      if (lastInputFrame != Tempo::NoSource) maxDeliveryGap = std::max(maxDeliveryGap,frame-lastInputFrame);
      lastInputFrame = frame;
    }
    assert(supplied <= input.size());
    for (std::size_t i = 0; i < supplied; ++i) {
      input[i] = signal(inputIndex++, frequency, kind); inputBirth.push_back(frame);
    }
    const auto beforeAlloc = allocations;
    auto before = Clock::now(); const auto accepted = tempo.Push(input.data(), supplied);
    auto middle = Clock::now(); tempo.Pull(output.data(), callback, provenance.data()); auto after = Clock::now();
    if (scenario != "stall") {
      const auto observed = tempo.ReadStatistics();
      if (trace && time < .6) std::fprintf(stderr,"step %.3f %.3f %.3f %llu %llu unity_entries=%llu unity_exits=%llu\n",time,
          observed.supplyRatio,observed.analysisRatio,(unsigned long long)observed.inputAccepted,
          (unsigned long long)observed.inputRetired,(unsigned long long)observed.unityEntries,
          (unsigned long long)observed.unityExits);
      if (observed.unavailableWindows > reportedStarvations && reportedStarvations < 5)
        std::fprintf(stderr,"unexpected starvation t=%.6f supply=%.6f analysis=%.6f accepted=%llu retired=%llu count=%llu\n",
          time,observed.supplyRatio,observed.analysisRatio,(unsigned long long)observed.inputAccepted,
          (unsigned long long)observed.inputRetired,(unsigned long long)observed.unavailableWindows);
      reportedStarvations = observed.unavailableWindows;
    }
    assert(allocations == beforeAlloc);
    assert(accepted == supplied);
    pushNs += std::chrono::duration_cast<std::chrono::nanoseconds>(middle-before).count();
    const auto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(after-middle).count();
    pullNs += elapsed; maxPullNs = std::max<std::uint64_t>(maxPullNs, elapsed);
    if (paused) for (auto f:output) pauseOutputErrors += f.left != 0 || f.right != 0;
    for (std::size_t i=0;i<std::size_t(callback);++i) if (provenance[i] != Tempo::NoSource) {
      assert(provenance[i] < inputBirth.size());
      maxWallAge = std::max<std::uint64_t>(maxWallAge,frame+i-inputBirth[provenance[i]]);
      if (scenario == "recover" && time >= 6.5) {
        const auto expected = signal(provenance[i],frequency,kind);
        assert(output[i].left == expected.left && output[i].right == expected.right);
      }
    }
    pcm.insert(pcm.end(),output.begin(),output.end());
  }
  const auto stats = tempo.ReadStatistics();
  assert(stats.inputRejected == 0 && pauseOutputErrors == 0);
  assert(stats.maximumBufferedFrames + Tempo::ResamplerReserve <= Tempo::SampleRate * .120);
  // Raw input count stays independent of synthesis output count.
  assert(stats.inputRetired <= stats.inputAccepted);
  if (scenario != "stall") assert(stats.unavailableWindows == 0);
  else assert(stats.unavailableWindows > 0);
  if (scenario == "recover") assert(stats.unityEntries == 1);
  if (ratio == 1 && (scenario == "steady" || scenario == "bursty" || scenario == "bursty6")) {
    assert(stats.synthesizedHops == 0);
    for (std::size_t i = stats.startupFrames; i < pcm.size(); ++i) {
      const auto expected = signal(i-stats.startupFrames, frequency, kind);
      assert(pcm[i].left == expected.left && pcm[i].right == expected.right);
    }
  }
  std::ofstream file(path, std::ios::binary);
  file.write(reinterpret_cast<const char*>(pcm.data()),pcm.size()*sizeof(Frame));
  assert(file.good());
  std::printf("{\"ratio\":%.9f,\"callback\":%d,\"frames\":%zu,\"input_accepted\":%llu,"
      "\"input_retired\":%llu,\"retained_input_discarded_on_stall\":%llu,\"retained_input_discarded_on_flush\":%llu,"
      "\"unity_entries\":%llu,\"unity_exits\":%llu,\"unavailable_windows\":%llu,\"startup_frames\":%llu,"
      "\"maximum_buffered_frames\":%llu,\"bypass_hops\":%llu,\"synthesized_hops\":%llu,"
      "\"supply_ratio\":%.9f,\"analysis_ratio\":%.9f,\"push_ns\":%llu,\"pull_ns\":%llu,"
      "\"max_pull_ns\":%llu,\"max_wall_age_ms\":%.6f,\"max_input_delivery_gap_ms\":%.6f,\"processing_realtime_fraction\":%.9f}\n",
      ratio,callback,pcm.size(),(unsigned long long)stats.inputAccepted,
      (unsigned long long)stats.inputRetired,(unsigned long long)stats.retainedInputDiscardedOnStall,
      (unsigned long long)stats.retainedInputDiscardedOnFlush,
      (unsigned long long)stats.unityEntries,(unsigned long long)stats.unityExits,
      (unsigned long long)stats.unavailableWindows,
      (unsigned long long)stats.startupFrames,(unsigned long long)stats.maximumBufferedFrames,
      (unsigned long long)stats.bypassHops,(unsigned long long)stats.synthesizedHops,
      stats.supplyRatio,stats.analysisRatio,(unsigned long long)pushNs,(unsigned long long)pullNs,
      (unsigned long long)maxPullNs,maxWallAge*1000./Tempo::SampleRate,maxDeliveryGap*1000./Tempo::SampleRate,
      (pushNs+pullNs)/1.e9/(pcm.size()/double(Tempo::SampleRate)));
}
