// Bounded read-only system thermal/power snapshots. No activity assertion or QoS change.
// Nominal/false may also mean unsupported; neither proves absence of throttling.
#import <Foundation/Foundation.h>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <thread>

int main(int argc, char** argv) {
  if (argc != 2) { std::fprintf(stderr, "Usage: thermal-state-probe SECONDS (1..120)\n"); return 2; }
  char* end = nullptr;
  const long seconds = std::strtol(argv[1], &end, 10);
  if (!*argv[1] || *end || seconds < 1 || seconds > 120) return 2;
  using Clock = std::chrono::steady_clock;
  const auto start = Clock::now();
  std::puts("# thermal: 0=nominal_or_unsupported,1=fair,2=serious,3=critical; low_power=0 may be unsupported; no frequency inference");
  std::puts("start_ns,end_ns,thermal_state,low_power_mode");
  for (long sample = 0; sample <= seconds; ++sample) {
    std::this_thread::sleep_until(start + std::chrono::seconds(sample));
    @autoreleasepool {
      auto now = [] { return std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now().time_since_epoch()).count(); };
      const auto begin = now();
      NSProcessInfo* info = NSProcessInfo.processInfo;
      const long thermal = (long)info.thermalState;
      const int lowPower = info.lowPowerModeEnabled ? 1 : 0;
      const auto finish = now();
      if (thermal < 0 || thermal > 3) { std::fprintf(stderr, "Unknown thermal value %ld\n", thermal); return 1; }
      std::printf("%lld,%lld,%ld,%d\n", (long long)begin, (long long)finish, thermal, lowPower);
      std::fflush(stdout);
    }
  }
}
