#include "Common/BlockingLoop.h"
#include <atomic>
#include <cassert>
#include <chrono>
#include <thread>
#include <vector>

struct Observations {
  // Only the worker accesses these until join.
  std::vector<bool> boundaries;
};

void Observe(void* context, bool before) noexcept {
  static_cast<Observations*>(context)->boundaries.push_back(before);
}

void Check(bool observed) {
  Common::BlockingLoop loop;
  Common::Event entered, release;
  std::atomic<int> payloads{0};
  Observations observations;
  observations.boundaries.reserve(1024); // Test storage, not runtime instrumentation.
  loop.Prepare();
  std::thread worker([&] {
    loop.Run([&] {
      if (payloads.fetch_add(1) == 0) {
        entered.Set();
        release.Wait();
      }
    }, 0, observed ? Observe : nullptr, &observations);
  });
  assert(entered.WaitFor(std::chrono::seconds(3)));
  assert(!loop.IsDone());
  release.Set();
  loop.Wait();
  assert(loop.IsDone());
  loop.Wakeup();
  loop.Wait();
  loop.Stop();
  worker.join();
  assert(payloads.load() >= 2);
  if (!observed) {
    assert(observations.boundaries.empty());
  } else {
    assert(!observations.boundaries.empty());
    assert(observations.boundaries.size() % 2 == 0);
    for (std::size_t i = 0; i < observations.boundaries.size(); ++i)
      assert(observations.boundaries[i] == (i % 2 == 0));
  }
}

int main() {
  for (int i = 0; i < 100; ++i) {
    Check(false);
    Check(true);
  }
}
