#include "../patches/experiments/recent-completion-events.h"
#include <atomic>
#include <cassert>
#include <thread>

int main() {
  using B = galaxypad::RecentCompletionEvents<4>;
  using K = B::Kind;
  B buffer;
  unsigned clocks = 0;
  auto clock = [&] { return B::Event{++clocks, 0, K::WaitBegin, false}; };
  buffer.Record(K::WaitBegin, clock);
  assert(clocks == 0 && buffer.Size() == 0);
  buffer.Configure(true);
  for (unsigned i = 0; i < 10; ++i)
    buffer.Record(i % 2 ? K::WaitEnd : K::WaitBegin, clock);
  assert(buffer.Size() == 4 && buffer.Overwritten() == 6);
  for (unsigned i = 0; i < 4; ++i) {
    assert(buffer.At(i).wall_ns == i + 7);
    assert(buffer.At(i).kind == (i % 2 ? K::WaitEnd : K::WaitBegin));
  }
  buffer.Freeze();
  buffer.Record(K::WaitBegin, clock);
  assert(clocks == 10 && buffer.At(0).wall_ns == 7 && buffer.Frozen());
  buffer.Configure(true);
  assert(!buffer.Frozen() && buffer.Size() == 0 && buffer.Overwritten() == 0);

  // Only the owner freezes its buffer. Release/acquire communicates a request,
  // never publishes a live array for concurrent inspection or copying.
  std::atomic<bool> request{false};
  std::thread writer([&] {
    buffer.Record(K::BeforeNotify, clock);
    while (!request.load(std::memory_order_acquire)) std::this_thread::yield();
    buffer.Record(K::AfterNotify, clock);
    buffer.Freeze();
    buffer.Record(K::BeforeNotify, clock);
  });
  request.store(true, std::memory_order_release);
  writer.join();
  assert(buffer.Frozen() && buffer.Size() == 2 && clocks == 12);
  assert(buffer.At(0).kind == K::BeforeNotify && buffer.At(1).kind == K::AfterNotify);
  buffer.Configure(false);
  buffer.Record(K::WaitBegin, clock);
  assert(buffer.Size() == 0 && clocks == 12);
}
