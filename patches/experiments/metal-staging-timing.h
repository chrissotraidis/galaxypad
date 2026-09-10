// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <cstdint>
#ifdef __APPLE__
#include <mach/mach_time.h>
#endif

namespace GalaxyPadDiagnostics {
struct StagingGPUInterval {
  bool valid = false;
  double seconds = 0, startSeconds = 0, endSeconds = 0;
};
inline StagingGPUInterval ValidateStagingGPUInterval(bool completed, double start, double end) {
  if (!completed || !std::isfinite(start) || !std::isfinite(end) ||
      start <= 0 || end < start || !std::isfinite(end - start)) return {};
  return {true, end - start, start, end};
}
inline std::uint64_t StagingHostNanoseconds() {
#ifdef __APPLE__
  static const auto scale = [] {
    mach_timebase_info_data_t info{};
    mach_timebase_info(&info);
    return info;
  }();
  return static_cast<std::uint64_t>(
      static_cast<__uint128_t>(mach_absolute_time()) * scale.numer / scale.denom);
#else
  return std::chrono::duration_cast<std::chrono::nanoseconds>(
      std::chrono::steady_clock::now().time_since_epoch()).count();
#endif
}
inline const char* StagingClockDomain() {
#ifdef __APPLE__
  return "mach_absolute";
#else
  return "steady";
#endif
}
// Diagnostic only. No clocks or output without explicit opt-in. A bounded
// trace avoids unbounded private artifacts; these are CPU wall intervals,
// not GPU execution timestamps. Logging occurs after the measured operation.
template <class Operation, class Clock, class Record>
void MeasureStaging(bool enabled, Operation&& operation, Clock&& clock, Record&& record) {
  if (!enabled) { operation(); return; }
  const auto begin = clock();
  operation();
  const auto end = clock();
  record(begin, end);
}

inline std::FILE* StagingTraceFile() {
  static auto* file = [] {
    const char* path = std::getenv("GALAXYPAD_METAL_STAGING_TRACE");
    if (!path || !*path) return static_cast<std::FILE*>(nullptr);
    auto* output = std::fopen(path, "w");
    if (output) std::fputs("sample,stage,begin_ns,end_ns,gpu_valid,gpu_ms,buffer,clock,gpu_start_s,gpu_end_s\n", output);
    return output;
  }();
  return file;
}
inline std::atomic<unsigned long long>& StagingTraceCount() {
  static std::atomic<unsigned long long> count{0};
  return count;
}
class StagingCaptureGate {
  std::atomic<bool> armed{false};
  std::atomic<unsigned> polls{0};
public:
  template <class Ready>
  bool Allow(bool requiresTrigger, Ready&& ready) {
    if (!requiresTrigger || armed.load(std::memory_order_relaxed)) return true;
    // Check only every 64 staging calls before capture; never poll after arming.
    if ((polls.fetch_add(1, std::memory_order_relaxed) & 63) != 0 || !ready()) return false;
    armed.store(true, std::memory_order_relaxed);
    return true;
  }
};
inline bool StagingTraceArmed() {
  static const char* path = std::getenv("GALAXYPAD_METAL_STAGING_ARM_FILE");
  static StagingCaptureGate gate;
  return gate.Allow(path && *path, [&] {
    auto* trigger = std::fopen(path, "r");
    if (!trigger) return false;
    const bool ready = std::fgetc(trigger) == '1';
    std::fclose(trigger);
    return ready;
  });
}
template <class Operation, class GPURead>
void TraceStagingGPU(const char* stage, Operation&& operation, GPURead&& readGPU,
                     std::uintptr_t buffer = 0) {
  auto* file = StagingTraceFile();
  if (!file || !StagingTraceArmed()) { operation(); return; }
  static_assert(sizeof(unsigned long long) >= 8);
  const auto sample = StagingTraceCount().fetch_add(1, std::memory_order_relaxed);
  MeasureStaging(sample < 4096, operation, [] {
    return StagingHostNanoseconds();
  }, [&](auto begin, auto end) {
    const auto gpu = readGPU(); // after completion and outside the host interval
    std::fprintf(file, "%llu,%s,%llu,%llu,%d,%.9f,%llu,%s,%.9f,%.9f\n", sample, stage,
      static_cast<unsigned long long>(begin), static_cast<unsigned long long>(end),
      gpu.valid ? 1 : 0, gpu.seconds * 1000, static_cast<unsigned long long>(buffer),
      StagingClockDomain(), gpu.startSeconds, gpu.endSeconds);
    std::fflush(file); // survive native runtime stop without process exit
  });
}
template <class Operation>
void TraceStaging(const char* stage, Operation&& operation, std::uintptr_t buffer = 0) {
  TraceStagingGPU(stage, operation, [] { return StagingGPUInterval{}; }, buffer);
}
}
