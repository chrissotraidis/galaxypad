#pragma once
#include "completion-trigger.h"
#include <chrono>
#include <cstdio>
#include <memory>
#include <string>

namespace galaxypad {
class CompletionFlightRecorder {
public:
  using Trigger = CompletionTrigger<>;
  enum class Result { Disabled, Saved, OpenFailed, WriteFailed, InvalidConfiguration };

  // Configure before either worker starts. not_before is an absolute timestamp
  // in the steady-clock domain; runtime must log how it chose this boundary.
  void Configure(const char* path, std::uint64_t not_before, std::uint64_t threshold) {
    trigger_.reset();
    path_ = path ? path : "";
    finished_ = false;
    result_ = Result::Disabled;
    not_before_ = not_before;
    threshold_ = threshold;
    if (path_.empty()) return;
    if (!threshold) { result_ = Result::InvalidConfiguration; return; }
    trigger_ = std::make_unique<Trigger>();
    trigger_->Configure(true, not_before, threshold);
  }

  bool Enabled() const noexcept { return trigger_ && !finished_; }
  void CPUWait(std::uint64_t start, std::uint64_t end) noexcept {
    if (Enabled()) trigger_->CPUWait(start, end);
  }
  template<class Clock>
  void GraphicsWithClock(bool before, Clock&& clock) noexcept {
    if (Enabled()) trigger_->GraphicsBoundary(before, clock);
  }
  void GraphicsBoundary(bool before) noexcept {
    GraphicsWithClock(before, [] {
      auto time = std::chrono::steady_clock::now().time_since_epoch();
      // Wall-only observations deliberately avoid a thread CPU syscall at
      // each notification. Never report the unsampled CPU value as valid zero.
      return Trigger::Event{static_cast<std::uint64_t>(
          std::chrono::duration_cast<std::chrono::nanoseconds>(time).count()),
          0, Trigger::Kind::BeforeNotify, false};
    });
  }

  Result FlushAfterJoin() noexcept {
    if (finished_ || !trigger_) return result_;
    finished_ = true;
    auto* file = std::fopen(path_.c_str(), "wx");
    if (!file) return result_ = Result::OpenFailed;
    auto number = [](std::uint64_t n) { return static_cast<unsigned long long>(n); };
    bool ok = std::fprintf(file,
        "# flight_version=1 triggered=%u graphics_frozen=%u not_before_ns=%llu threshold_ns=%llu trigger_start_ns=%llu trigger_end_ns=%llu invalid_waits=%llu cpu_overwritten=%llu graphics_overwritten=%llu\nstream,kind,wall_ns,thread_cpu_ns,cpu_clock_valid\n",
        trigger_->Triggered() ? 1u : 0u, trigger_->Graphics().Frozen() ? 1u : 0u,
        number(not_before_), number(threshold_), number(trigger_->TriggerStart()),
        number(trigger_->TriggerEnd()), number(trigger_->InvalidWaits()),
        number(trigger_->CPU().Overwritten()), number(trigger_->Graphics().Overwritten())) >= 0;
    auto write = [&](const Trigger::Buffer& buffer, const char* stream) {
      for (std::size_t i = 0; i < buffer.Size() && ok; ++i) {
        const auto& e = buffer.At(i);
        using Kind = Trigger::Kind;
        const char* kind = e.kind == Kind::WaitBegin ? "wait_begin" :
                           e.kind == Kind::WaitEnd ? "wait_end" :
                           e.kind == Kind::BeforeNotify ? "before_notify" : "after_notify";
        ok = std::fprintf(file, "%s,%s,%llu,%llu,%u\n", stream, kind,
                          number(e.wall_ns), number(e.thread_cpu_ns), e.cpu_clock_valid ? 1u : 0u) >= 0;
      }
    };
    write(trigger_->CPU(), "cpu");
    write(trigger_->Graphics(), "graphics");
    if (std::fclose(file) != 0) ok = false;
    return result_ = ok ? Result::Saved : Result::WriteFailed;
  }

private:
  std::unique_ptr<Trigger> trigger_;
  std::string path_;
  std::uint64_t not_before_ = 0, threshold_ = 0;
  bool finished_ = false;
  Result result_ = Result::Disabled;
};
} // namespace galaxypad
