#include "../patches/experiments/completion-recorder.h"
#include <cassert>
#include <fstream>
#include <iterator>
#include <thread>
#include <csignal>
#include <sys/resource.h>

std::string Read(const std::string& path) {
  std::ifstream input(path);
  return std::string(std::istreambuf_iterator<char>(input), {});
}

int main(int argc, char** argv) {
  assert(argc == 2);
  using R = galaxypad::CompletionRecorder;
  using K = R::Kind;
  R recorder;
  int clocks = 0;
  auto clock = [&] { ++clocks; return R::Buffer::Event{100, 20, K::WaitBegin, false}; };
  recorder.Configure(nullptr);
  recorder.RecordCPUWithClock(K::WaitBegin, clock);
  recorder.RecordGraphicsWithClock(K::BeforeNotify, clock);
  assert(clocks == 0 && recorder.FlushAfterJoin() == R::Result::Disabled);
  const std::string path = std::string(argv[1])+"/completion.csv";
  recorder.Configure(path.c_str());
  std::thread cpu([&] {
    recorder.RecordCPUWithClock(K::WaitBegin, clock);
    recorder.RecordCPU(K::WaitEnd);
  });
  std::thread graphics([&] {
    recorder.RecordGraphics(K::BeforeNotify);
    recorder.RecordGraphics(K::AfterNotify);
  });
  cpu.join();
  graphics.join();
  assert(!std::ifstream(path).good());
  assert(recorder.FlushAfterJoin() == R::Result::Saved);
  const auto data = Read(path);
  assert(data.find("# cpu_dropped=0 graphics_dropped=0\n") == 0);
  assert(data.find("cpu,wait_begin,100,20,0\n") != std::string::npos);
  assert(data.find("graphics,before_notify,") != std::string::npos);
  assert(data.find("graphics,after_notify,") != std::string::npos);
  recorder.RecordCPUWithClock(K::WaitBegin, clock);
  assert(clocks == 1 && !recorder.Enabled());
  assert(recorder.FlushAfterJoin() == R::Result::Saved && Read(path) == data);
  recorder.Configure(path.c_str());
  assert(recorder.FlushAfterJoin() == R::Result::OpenFailed && Read(path) == data);
  recorder.Configure((std::string(argv[1])+"/missing/file.csv").c_str());
  assert(recorder.FlushAfterJoin() == R::Result::OpenFailed);
  recorder.Configure((std::string(argv[1])+"/limited.csv").c_str());
  recorder.RecordCPU(K::WaitBegin);
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
