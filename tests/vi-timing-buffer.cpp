#include "../patches/experiments/vi-timing-buffer.h"
#include <cassert>
#include <thread>

int main() {
  galaxypad::ViTimingBuffer<3> buffer;
  assert(buffer.Size() == 0 && buffer.Dropped() == 0);
  // No reader while the emulation writer is active; join is the publication fence.
  std::thread writer([&] {
    buffer.Record(100, 50, true, 12, 34, 56);
    buffer.Record(200, 0, false); // Failed clock is not a valid zero CPU interval.
    buffer.Record(300, 90, true);
    for (int i = 0; i < 100; ++i)
      buffer.Record(400 + i, 100 + i, true);
  });
  writer.join();
  assert(buffer.Size() == 3 && buffer.Dropped() == 100);
  assert(buffer.Data()[0].wall_ns == 100);
  assert(buffer.Data()[0].thread_cpu_ns == 50);
  assert(buffer.Data()[0].efb_elapsed_ns == 12);
  assert(buffer.Data()[0].throttle_elapsed_ns == 34);
  assert(buffer.Data()[0].idle_wait_elapsed_ns == 56);
  assert(buffer.Data()[0].cpu_clock_valid);
  assert(buffer.Data()[1].wall_ns == 200 && !buffer.Data()[1].cpu_clock_valid);
  assert(buffer.Data()[2].wall_ns == 300 && buffer.Data()[2].thread_cpu_ns == 90);
  buffer.Reset();
  assert(buffer.Size() == 0 && buffer.Dropped() == 0);
  buffer.Record(900, 700, true);
  assert(buffer.Size() == 1 && buffer.Data()[0].wall_ns == 900);
  assert(buffer.Data()[0].efb_elapsed_ns == 0);
  assert(buffer.Data()[0].throttle_elapsed_ns == 0);
  assert(buffer.Data()[0].idle_wait_elapsed_ns == 0);
}
