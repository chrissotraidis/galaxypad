// Print timestamps from the same C++ clock used by the VI timing recorder.
#include <chrono>
#include <cstdio>
int main() {
  const auto now = std::chrono::steady_clock::now().time_since_epoch();
  std::printf("%lld\n", static_cast<long long>(
      std::chrono::duration_cast<std::chrono::nanoseconds>(now).count()));
}
