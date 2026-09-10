#include "../patches/experiments/completion-events.h"
#include <cassert>
#include <thread>

int main() {
  using Buffer = galaxypad::CompletionEvents<2>;
  using Kind = Buffer::Kind;
  Buffer cpu, graphics;
  int cpu_clocks = 0, graphics_clocks = 0;
  auto cpu_clock = [&] {
    ++cpu_clocks;
    return Buffer::Event{100, 20, Kind::BeforeNotify, false};
  };
  cpu.Record(Kind::WaitBegin, cpu_clock);
  assert(cpu.Size() == 0 && cpu_clocks == 0);
  cpu.Configure(true);
  graphics.Configure(true);
  std::thread cpu_writer([&] {
    cpu.Record(Kind::WaitBegin, cpu_clock);
    cpu.Record(Kind::WaitEnd, cpu_clock);
    for (int i = 0; i < 10; ++i)
      cpu.Record(Kind::WaitEnd, cpu_clock);
  });
  std::thread graphics_writer([&] {
    auto clock = [&] {
      ++graphics_clocks;
      return Buffer::Event{90, 10, Kind::WaitBegin, true};
    };
    graphics.Record(Kind::BeforeNotify, clock);
    graphics.Record(Kind::AfterNotify, clock);
  });
  cpu_writer.join();
  graphics_writer.join();
  assert(cpu.Size() == 2 && cpu.Dropped() == 10 && cpu_clocks == 2);
  assert(graphics.Size() == 2 && graphics.Dropped() == 0 && graphics_clocks == 2);
  assert(cpu.Data()[0].kind == Kind::WaitBegin && cpu.Data()[1].kind == Kind::WaitEnd);
  assert(!cpu.Data()[0].cpu_clock_valid && cpu.Data()[0].wall_ns == 100);
  assert(graphics.Data()[0].kind == Kind::BeforeNotify);
  assert(graphics.Data()[1].kind == Kind::AfterNotify && graphics.Data()[1].cpu_clock_valid);
  cpu.Configure(false);
  cpu.Record(Kind::WaitBegin, cpu_clock);
  assert(cpu.Size() == 0 && cpu.Dropped() == 0 && cpu_clocks == 2);
}
