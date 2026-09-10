#include "../patches/experiments/vi-timing-recorder.h"
#include <cassert>
#include <fstream>
#include <iterator>
#include <thread>
#include <csignal>
#include <sys/resource.h>

int main(int argc, char** argv) {
  assert(argc == 2);
  using Recorder = galaxypad::ViTimingRecorder;
  const std::string path = std::string(argv[1]) + "/timing.csv";
  Recorder recorder;
  int calls = 0;
  auto clock = [&]() noexcept {
    ++calls;
    return Recorder::Buffer::Sample{100, 0, false, 25, 30, 40, 50, 60, 70};
  };
  recorder.Configure(nullptr);
  assert(!recorder.Enabled());
  recorder.RecordWithClock(clock);
  assert(calls == 0 && recorder.FlushAfterJoin() == Recorder::Result::Disabled);
  recorder.Configure("");
  recorder.RecordWithClock(clock);
  assert(calls == 0);
  recorder.Configure(path.c_str());
  assert(recorder.Enabled());
  std::thread writer([&] { recorder.RecordWithClock(clock); recorder.Record(); });
  writer.join();
  assert(calls == 1);
  assert(!std::ifstream(path).good()); // No file until post-join export.
  assert(recorder.FlushAfterJoin() == Recorder::Result::Saved);
  assert(recorder.FlushAfterJoin() == Recorder::Result::Saved);
  std::ifstream input(path);
  const std::string data((std::istreambuf_iterator<char>(input)), {});
  assert(data.find("# dropped=0\nwall_ns,thread_cpu_ns,cpu_clock_valid,efb_elapsed_ns,throttle_elapsed_ns,idle_wait_elapsed_ns,dvd_wait_elapsed_ns,gather_wait_elapsed_ns,wakeup_elapsed_ns\n100,0,0,25,30,40,50,60,70\n") == 0);
  assert(!recorder.Enabled());
  recorder.RecordWithClock(clock);
  assert(calls == 1); // Finished sessions cannot acquire more samples.
  recorder.Configure(path.c_str());
  assert(recorder.FlushAfterJoin() == Recorder::Result::OpenFailed);
  std::ifstream original(path);
  assert(std::string((std::istreambuf_iterator<char>(original)), {}) == data);
  recorder.Configure((std::string(argv[1])+"/missing/out.csv").c_str());
  assert(recorder.FlushAfterJoin() == Recorder::Result::OpenFailed);
  // Exercise buffered-write/fclose failure without filling the user's disk.
  recorder.Configure((std::string(argv[1])+"/limited.csv").c_str());
  recorder.RecordWithClock(clock);
  rlimit original_limit{};
  assert(getrlimit(RLIMIT_FSIZE, &original_limit) == 0);
  auto limited = original_limit;
  limited.rlim_cur = 8;
  auto old_handler = std::signal(SIGXFSZ, SIG_IGN);
  assert(setrlimit(RLIMIT_FSIZE, &limited) == 0);
  const auto result = recorder.FlushAfterJoin();
  assert(setrlimit(RLIMIT_FSIZE, &original_limit) == 0);
  std::signal(SIGXFSZ, old_handler);
  assert(result == Recorder::Result::WriteFailed);
}
