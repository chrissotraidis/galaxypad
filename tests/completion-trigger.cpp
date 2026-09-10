#include "../patches/experiments/completion-trigger.h"
#include <cassert>
#include <thread>

int main() {
  using T = galaxypad::CompletionTrigger<4>;
  using K = T::Kind;
  T trigger;
  int clocks = 0;
  auto clock = [&] { return T::Event{static_cast<unsigned>(++clocks), 0, K::BeforeNotify, false}; };
  trigger.Configure(false, 100, 20);
  trigger.CPUWait(100, 200);
  trigger.GraphicsBoundary(true, clock);
  assert(!trigger.Triggered() && clocks == 0);
  trigger.Configure(true, 100, 20);
  trigger.CPUWait(0, 99);
  trigger.CPUWait(90, 150); // Crossing arming boundary is excluded.
  trigger.CPUWait(100, 119);
  trigger.CPUWait(120, 119);
  assert(!trigger.Triggered() && trigger.InvalidWaits() == 1);
  trigger.CPUWait(120, 140); // Exact threshold and arming boundary are inclusive.
  trigger.CPUWait(200, 500); // First trigger is immutable.
  assert(trigger.TriggerStart() == 120 && trigger.TriggerEnd() == 140);
  assert(trigger.CPU().Size() == 4 && trigger.CPU().At(0).wall_ns == 100);
  assert(!trigger.Graphics().Frozen()); // No graphics response is not completion.
  trigger.GraphicsBoundary(true, clock);
  trigger.GraphicsBoundary(false, clock);
  trigger.GraphicsBoundary(true, clock);
  assert(trigger.Graphics().Frozen() && clocks == 2);
  assert(trigger.Graphics().At(1).kind == K::AfterNotify);

  for (int i = 0; i < 100; ++i) {
    trigger.Configure(true, 0, 20);
    std::atomic<bool> begun{false}, cpu_done{false};
    std::thread graphics([&] {
      trigger.GraphicsBoundary(true, clock);
      begun.store(true, std::memory_order_release);
      while (!cpu_done.load(std::memory_order_acquire)) std::this_thread::yield();
      trigger.GraphicsBoundary(false, clock);
    });
    std::thread cpu([&] {
      while (!begun.load(std::memory_order_acquire)) std::this_thread::yield();
      trigger.CPUWait(100, 150);
      cpu_done.store(true, std::memory_order_release);
    });
    cpu.join();
    graphics.join();
    assert(trigger.Triggered() && trigger.Graphics().Frozen());
    assert(trigger.Graphics().Size() == 2 && trigger.CPU().Size() == 2);
  }
  trigger.Configure(true, 0, 0);
  trigger.CPUWait(0, 100);
  assert(!trigger.Triggered());
}
