// Host-only empty-pair screen. Not a calibration of the Simulator CPU thread.
#include "../apple/experiments/run-cost/sampler.h"
#include <algorithm>
#include <iostream>
#include <limits>

int main()
{
  using galaxypad::diagnostics::ThreadCpuNs;
  std::uint64_t sum = 0, minimum = std::numeric_limits<std::uint64_t>::max();
  std::uint64_t maximum = 0, zero = 0;
  for (unsigned i = 0; i < 10000; ++i)
  {
    const auto start = ThreadCpuNs();
    const auto end = ThreadCpuNs();
    if (!start || end < start)
      return 1;
    const auto duration = end - start;
    sum += duration;
    minimum = std::min(minimum, duration);
    maximum = std::max(maximum, duration);
    zero += duration == 0;
  }
  std::cout << "pairs=10000 mean_ns=" << double(sum) / 10000 << " min_ns=" << minimum
            << " max_ns=" << maximum << " zero_pairs=" << zero << '\n';
}
