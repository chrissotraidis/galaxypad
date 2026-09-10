#pragma once
// Private host diagnostic only. No inclusion in ordinary release builds.
#ifndef GALAXYPAD_PRIVATE_THREAD_WORK
#error "Thread-work SPI requires an explicitly private diagnostic build"
#endif
#include <array>
#include <cerrno>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <dlfcn.h>
#include <limits>
#include <mach/mach_time.h>
#include <memory>
#include <string>
#include <sys/sysctl.h>

namespace galaxypad {
// Single CPU-thread writer; configure before start, export only after join.
template<std::size_t Capacity = 16384> class ThreadWorkRecorder {
public:
  struct Counts { std::uint64_t instructions{}, cycles{}, user_mach{}, system_mach{}; };
  using Reader = int (*)(unsigned, void*, std::size_t);
  struct Sample {
    std::uint64_t vi_ns{}, before_ns{}, after_ns{};
    int error{};
    std::array<Counts,8> levels{};
  };
  enum class Result { Disabled, Saved, OpenFailed, WriteFailed };
  static_assert(Capacity > 0);

  // Injected provider also permits tests without querying the kernel.
  void Configure(const char* path, Reader reader, unsigned levels,
                 unsigned numerator, unsigned denominator) {
    samples_.reset(); path_ = path ? path : ""; reader_ = reader;
    size_ = 0; dropped_ = 0; finished_ = false; result_ = Result::Disabled;
    levels_ = levels; numerator_ = numerator; denominator_ = denominator;
    config_error_ = !reader ? ENOSYS :
      (levels == 0 || levels > 8 || !numerator || !denominator ? EINVAL : 0);
    if (!path_.empty()) samples_ = std::make_unique<std::array<Sample,Capacity>>();
  }
  void ConfigureApple(const char* path) {
    // Disabled path must not resolve symbols, query sysctls or allocate.
    if (!path || !*path) { Configure(nullptr,nullptr,0,0,0); return; }
    unsigned levels = 0; std::size_t bytes = sizeof(levels);
    mach_timebase_info_data_t tb{};
    auto reader = reinterpret_cast<Reader>(dlsym(RTLD_DEFAULT,"thread_selfcounts"));
    if (sysctlbyname("hw.nperflevels",&levels,&bytes,nullptr,0)) levels = 0;
    if (mach_timebase_info(&tb)) tb = {};
    Configure(path,reader,levels,tb.numer,tb.denom);
  }
  template<class Clock> void Record(std::uint64_t vi_ns, Clock clock) noexcept {
    if (!samples_ || finished_) return;
    if (size_ == Capacity) {
      if (dropped_ != std::numeric_limits<std::uint64_t>::max()) ++dropped_;
      return; // No expensive counter query for discarded rows.
    }
    auto& sample = (*samples_)[size_++];
    sample.vi_ns = vi_ns; sample.error = config_error_;
    if (sample.error) return;
    sample.before_ns = clock(); errno = 0;
    // XNU THSC_TIME_CPI_PER_PERF_LEVEL=4; ABI uses Mach ticks, not ns.
    if (reader_(4,sample.levels.data(),levels_*sizeof(Counts))) {
      sample.error = errno ? errno : EIO;
      sample.levels = {}; // Never expose partially written failed results as valid.
    }
    sample.after_ns = clock();
  }
  void Record(std::uint64_t vi_ns) noexcept {
    Record(vi_ns, [] {
      return static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count());
    });
  }
  Result FlushAfterJoin() noexcept {
    if (!samples_ || finished_) return result_;
    finished_ = true;
    FILE* file = std::fopen(path_.c_str(),"wx");
    if (!file) return result_ = Result::OpenFailed;
    bool ok = std::fprintf(file,"# dropped=%llu levels=%u timebase=%u/%u config_error=%d\nvi_ns,before_ns,after_ns,error,level,instructions,cycles,user_mach,system_mach\n",
      static_cast<unsigned long long>(dropped_),levels_,numerator_,denominator_,config_error_) >= 0;
    const unsigned exported_levels = levels_ > 0 && levels_ <= 8 ? levels_ : 1;
    for (std::size_t i=0; i<size_ && ok; ++i) {
      const auto& s = (*samples_)[i];
      for (unsigned j=0; j<exported_levels && ok; ++j) {
        const auto& c = s.levels[j];
        ok = std::fprintf(file,"%llu,%llu,%llu,%d,%u,%llu,%llu,%llu,%llu\n",
          (unsigned long long)s.vi_ns,(unsigned long long)s.before_ns,
          (unsigned long long)s.after_ns,s.error,j,(unsigned long long)c.instructions,
          (unsigned long long)c.cycles,(unsigned long long)c.user_mach,
          (unsigned long long)c.system_mach) >= 0;
      }
    }
    if (std::fclose(file)) ok = false;
    return result_ = ok ? Result::Saved : Result::WriteFailed;
  }
  std::size_t Size() const { return size_; }
  std::uint64_t Dropped() const { return dropped_; }
  const Sample& At(std::size_t i) const { return (*samples_)[i]; }
private:
  std::unique_ptr<std::array<Sample,Capacity>> samples_;
  std::string path_;
  Reader reader_{};
  unsigned levels_{}, numerator_{}, denominator_{};
  int config_error_{};
  std::size_t size_{};
  std::uint64_t dropped_{};
  bool finished_{};
  Result result_{Result::Disabled};
};
}
