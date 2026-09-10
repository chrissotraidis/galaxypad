#pragma once
#include "completion-events.h"
#include <chrono>
#include <cstdio>
#include <memory>
#include <string>
#include <time.h>

namespace galaxypad {
class CompletionRecorder {
public:
  using Buffer = CompletionEvents<>;
  using Kind = Buffer::Kind;
  enum class Result { Disabled, Saved, OpenFailed, WriteFailed };

  // No writer may be running during configuration or export.
  void Configure(const char* path) {
    buffers_.reset();
    path_ = path ? path : "";
    finished_ = false;
    result_ = Result::Disabled;
    if (!path_.empty()) {
      buffers_ = std::make_unique<Buffers>();
      buffers_->cpu.Configure(true);
      buffers_->graphics.Configure(true);
    }
  }

  bool Enabled() const noexcept { return buffers_ && !finished_; }

  // CPU and graphics have separate writers/storage. Shared configuration is
  // immutable while either writer runs; never sample the other thread's buffer.
  template<class Clock>
  void RecordCPUWithClock(Kind kind, Clock&& clock) noexcept {
    if (Enabled()) buffers_->cpu.Record(kind, clock);
  }
  template<class Clock>
  void RecordGraphicsWithClock(Kind kind, Clock&& clock) noexcept {
    if (Enabled()) buffers_->graphics.Record(kind, clock);
  }
  void RecordCPU(Kind kind) noexcept { RecordCPUWithClock(kind, ReadClock); }
  void RecordGraphics(Kind kind) noexcept { RecordGraphicsWithClock(kind, ReadClock); }

  // Both writers MUST have joined. One exclusive-create file, two ordered
  // streams; row order across streams deliberately does not imply time order.
  Result FlushAfterJoin() noexcept {
    if (finished_ || !buffers_) return result_;
    finished_ = true;
    auto* file = std::fopen(path_.c_str(), "wx");
    if (!file) return result_ = Result::OpenFailed;
    bool ok = std::fprintf(file, "# cpu_dropped=%llu graphics_dropped=%llu\nstream,kind,wall_ns,thread_cpu_ns,cpu_clock_valid\n",
        static_cast<unsigned long long>(buffers_->cpu.Dropped()),
        static_cast<unsigned long long>(buffers_->graphics.Dropped())) >= 0;
    auto write = [&](const Buffer& buffer, const char* stream) {
      for (std::size_t i = 0; i < buffer.Size() && ok; ++i) {
        const auto& e = buffer.Data()[i];
        const char* kind = e.kind == Kind::WaitBegin ? "wait_begin" :
                           e.kind == Kind::WaitEnd ? "wait_end" :
                           e.kind == Kind::BeforeNotify ? "before_notify" : "after_notify";
        ok = std::fprintf(file, "%s,%s,%llu,%llu,%u\n", stream, kind,
            static_cast<unsigned long long>(e.wall_ns),
            static_cast<unsigned long long>(e.thread_cpu_ns), e.cpu_clock_valid ? 1u : 0u) >= 0;
      }
    };
    write(buffers_->cpu, "cpu");
    write(buffers_->graphics, "graphics");
    if (std::fclose(file) != 0) ok = false;
    return result_ = ok ? Result::Saved : Result::WriteFailed;
  }

private:
  static Buffer::Event ReadClock() noexcept {
    auto wall = std::chrono::steady_clock::now().time_since_epoch();
    timespec cpu{};
    bool valid = false;
#ifdef CLOCK_THREAD_CPUTIME_ID
    valid = clock_gettime(CLOCK_THREAD_CPUTIME_ID, &cpu) == 0;
#endif
    return {static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(wall).count()),
            valid ? static_cast<std::uint64_t>(cpu.tv_sec)*1'000'000'000 +
                        static_cast<std::uint64_t>(cpu.tv_nsec) : 0, Kind::WaitBegin, valid};
  }
  struct Buffers { Buffer cpu, graphics; };
  std::unique_ptr<Buffers> buffers_;
  std::string path_;
  bool finished_ = false;
  Result result_ = Result::Disabled;
};
} // namespace galaxypad
