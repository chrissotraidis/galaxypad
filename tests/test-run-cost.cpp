#include "../apple/experiments/run-cost/sampler.h"
#include <cassert>

using namespace galaxypad::diagnostics;
std::uint64_t now = 100, reads = 0;
std::uint64_t Clock() { ++reads; return now; }

int main()
{
  { RunCost::Scope disabled(nullptr, RunLane::Native); }
  assert(reads == 0);
  RunCost cost(Clock);
  for (unsigned i = 0; i < 1000000; ++i)
  {
    RunCost::Scope span(&cost, RunLane(i & 1));
    now += i & 1 ? 200 : 100;
    if (i & 2)
      continue; // Destructor must also account for early branch exits.
  }
  for (unsigned i = 0; i < 2; ++i)
  {
    const auto& lane = cost.lanes[i];
    assert(lane.spans == 500000 && lane.selected > 1700 && lane.selected < 2200);
    assert(lane.completed == lane.selected);
    assert(lane.ns == lane.selected * (i ? 200 : 100));
    assert(lane.maximum_ns == (i ? 200 : 100));
    assert(lane.squared_ns == lane.selected * (i ? 40000 : 10000));
  }
  assert(reads == 1 + 2 * (cost.lanes[0].selected + cost.lanes[1].selected));
  assert(cost.clock_errors == 0);
  cost.Report(nullptr);
  RunCost broken(Clock);
  now = 0;
  for (unsigned i = 0; i < 10000; ++i)
  {
    RunCost::Scope span(&broken, RunLane::Native);
  }
  assert(broken.clock_errors == broken.lanes[0].selected);
  assert(broken.lanes[0].completed == 0);
  broken.Report(nullptr);
  assert(broken.clock_errors == broken.lanes[0].selected + 1);
}
