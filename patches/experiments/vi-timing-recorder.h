#pragma once
#include "vi-timing-buffer.h"
#include <chrono>
#include <cstdio>
#include <memory>
#include <string>
#include <time.h>

namespace galaxypad {
class ViTimingRecorder {
public:
  using Buffer = ViTimingBuffer<>;
  enum class Result { Disabled, Saved, OpenFailed, WriteFailed };

  // Call before the writer starts. Empty/unset environment value is fully disabled.
  void Configure(const char* path) {
    buffer_.reset();
    path_ = path ? path : "";
    finished_ = false;
    result_ = Result::Disabled;
    if (!path_.empty())
      buffer_ = std::make_unique<Buffer>();
  }

  template<class Clock>
  void RecordWithClock(Clock clock) noexcept {
    if (!buffer_ || finished_)
      return;
    const auto sample = clock();
    buffer_->Record(sample.wall_ns, sample.thread_cpu_ns, sample.cpu_clock_valid,
                    sample.efb_elapsed_ns, sample.throttle_elapsed_ns, sample.idle_wait_elapsed_ns,
                    sample.dvd_wait_elapsed_ns, sample.gather_wait_elapsed_ns, sample.wakeup_elapsed_ns);
  }

  bool Enabled() const noexcept { return buffer_ && !finished_; }

  void Record(std::uint64_t efb_ns = 0, std::uint64_t throttle_ns = 0,
              std::uint64_t idle_ns = 0, std::uint64_t dvd_ns = 0, std::uint64_t gather_ns = 0, std::uint64_t wakeup_ns = 0) noexcept {
    RecordWithClock([=]() noexcept {
      const auto wall = std::chrono::steady_clock::now().time_since_epoch();
      timespec cpu{};
      bool valid = false;
#ifdef CLOCK_THREAD_CPUTIME_ID
      valid = clock_gettime(CLOCK_THREAD_CPUTIME_ID, &cpu) == 0;
#endif
      return Buffer::Sample{
          static_cast<std::uint64_t>(
              std::chrono::duration_cast<std::chrono::nanoseconds>(wall).count()),
          valid ? static_cast<std::uint64_t>(cpu.tv_sec) * 1'000'000'000 +
                      static_cast<std::uint64_t>(cpu.tv_nsec) : 0,
          valid, efb_ns, throttle_ns, idle_ns, dvd_ns, gather_ns, wakeup_ns};
    });
  }

  // Caller MUST join the writer first. Idempotent; never overwrite an existing file.
  Result FlushAfterJoin() noexcept {
    if (finished_ || !buffer_)
      return result_;
    finished_ = true;
    std::FILE* file = std::fopen(path_.c_str(), "wx");
    if (!file)
      return result_ = Result::OpenFailed;
    bool ok = std::fprintf(file, "# dropped=%llu\nwall_ns,thread_cpu_ns,cpu_clock_valid,efb_elapsed_ns,throttle_elapsed_ns,idle_wait_elapsed_ns,dvd_wait_elapsed_ns,gather_wait_elapsed_ns,wakeup_elapsed_ns\n",
                           static_cast<unsigned long long>(buffer_->Dropped())) >= 0;
    for (std::size_t i = 0; i < buffer_->Size() && ok; ++i) {
      const auto& sample = buffer_->Data()[i];
      ok = std::fprintf(file, "%llu,%llu,%u,%llu,%llu,%llu,%llu,%llu,%llu\n",
                        static_cast<unsigned long long>(sample.wall_ns),
                        static_cast<unsigned long long>(sample.thread_cpu_ns),
                        sample.cpu_clock_valid ? 1u : 0u,
                        static_cast<unsigned long long>(sample.efb_elapsed_ns),
                        static_cast<unsigned long long>(sample.throttle_elapsed_ns),
                        static_cast<unsigned long long>(sample.idle_wait_elapsed_ns),
                        static_cast<unsigned long long>(sample.dvd_wait_elapsed_ns),
                        static_cast<unsigned long long>(sample.gather_wait_elapsed_ns),
                        static_cast<unsigned long long>(sample.wakeup_elapsed_ns)) >= 0;
    }
    if (std::fclose(file) != 0)
      ok = false;
    return result_ = ok ? Result::Saved : Result::WriteFailed;
  }

private:
  std::unique_ptr<Buffer> buffer_;
  std::string path_;
  bool finished_{};
  Result result_{Result::Disabled};
};
} // namespace galaxypad
