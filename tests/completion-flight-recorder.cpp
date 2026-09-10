#include "../patches/experiments/completion-flight-recorder.h"
#include <cassert>
#include <fstream>
#include <iterator>
#include <thread>
#include <csignal>
#include <sys/resource.h>

std::string Read(const std::string& path) {
  std::ifstream file(path);
  return {std::istreambuf_iterator<char>(file), {}};
}

int main(int argc, char** argv) {
  assert(argc == 2);
  using R = galaxypad::CompletionFlightRecorder;
  R recorder;
  int clocks = 0;
  auto clock = [&] { ++clocks; return R::Trigger::Event{150, 0, R::Trigger::Kind::BeforeNotify, false}; };
  recorder.Configure(nullptr, 100, 20);
  recorder.GraphicsWithClock(true, clock);
  assert(clocks == 0 && recorder.FlushAfterJoin() == R::Result::Disabled);
  const std::string path = std::string(argv[1])+"/flight.csv";
  recorder.Configure(path.c_str(), 100, 0);
  assert(!recorder.Enabled() && recorder.FlushAfterJoin() == R::Result::InvalidConfiguration);
  recorder.Configure(path.c_str(), 100, 20);
  std::atomic<bool> cpu_done{false};
  std::thread cpu([&] {
    recorder.CPUWait(0, 99); // Long startup wait cannot trigger.
    recorder.CPUWait(100, 140);
    cpu_done.store(true, std::memory_order_release);
  });
  std::thread graphics([&] {
    recorder.GraphicsWithClock(true, clock);
    while (!cpu_done.load(std::memory_order_acquire)) std::this_thread::yield();
    recorder.GraphicsWithClock(false, clock);
    recorder.GraphicsWithClock(true, clock);
  });
  cpu.join(); graphics.join();
  assert(clocks == 2 && !std::ifstream(path).good());
  assert(recorder.FlushAfterJoin() == R::Result::Saved);
  auto data = Read(path);
  assert(data.find("triggered=1 graphics_frozen=1 not_before_ns=100 threshold_ns=20 trigger_start_ns=100 trigger_end_ns=140") != std::string::npos);
  assert(data.find("cpu,wait_end,140,0,0") != std::string::npos);
  recorder.GraphicsWithClock(true, clock);
  assert(clocks == 2 && recorder.FlushAfterJoin() == R::Result::Saved);
  recorder.Configure(path.c_str(), 100, 20);
  assert(recorder.FlushAfterJoin() == R::Result::OpenFailed && Read(path) == data);
  recorder.Configure((std::string(argv[1])+"/untriggered.csv").c_str(), 100, 20);
  recorder.CPUWait(100, 119);
  assert(recorder.FlushAfterJoin() == R::Result::Saved);
  assert(Read(std::string(argv[1])+"/untriggered.csv").find("triggered=0 graphics_frozen=0") != std::string::npos);
  recorder.Configure((std::string(argv[1])+"/no-graphics.csv").c_str(), 100, 20);
  recorder.CPUWait(100, 140);
  assert(recorder.FlushAfterJoin() == R::Result::Saved);
  assert(Read(std::string(argv[1])+"/no-graphics.csv").find("triggered=1 graphics_frozen=0") != std::string::npos);
  recorder.Configure((std::string(argv[1])+"/limited.csv").c_str(), 100, 20);
  recorder.CPUWait(100, 140);
  rlimit original{};
  assert(getrlimit(RLIMIT_FSIZE, &original) == 0);
  auto limit = original;
  limit.rlim_cur = 8;
  auto handler = std::signal(SIGXFSZ, SIG_IGN);
  assert(setrlimit(RLIMIT_FSIZE, &limit) == 0);
  const auto result = recorder.FlushAfterJoin();
  assert(setrlimit(RLIMIT_FSIZE, &original) == 0);
  std::signal(SIGXFSZ, handler);
  assert(result == R::Result::WriteFailed);
}
