// Bracket wall-clock reads with the exact steady clock used by the VI recorder.
// Export after capture; these are observed offset bounds, not clock continuity proof.
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <thread>
#include <vector>

using Steady = std::chrono::steady_clock;
template<class Clock> static long long Now() {
  return std::chrono::duration_cast<std::chrono::nanoseconds>(
      Clock::now().time_since_epoch()).count();
}
struct Row { long long before, wall, after; };
int main(int argc, char** argv) {
  if (argc != 2) return 2;
  char* end = nullptr;
  const long seconds = std::strtol(argv[1], &end, 10);
  if (!*argv[1] || *end || seconds < 1 || seconds > 120) return 2;
  std::vector<Row> rows;
  rows.reserve(seconds * 10 + 2);
  const auto stop = Steady::now() + std::chrono::seconds(seconds);
  do {
    Row row{};
    row.before = Now<Steady>();
    row.wall = Now<std::chrono::system_clock>();
    row.after = Now<Steady>();
    rows.push_back(row);
    if (Steady::now() >= stop) break;
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
  } while (rows.size() < static_cast<size_t>(seconds * 10 + 2));
  std::puts("steady_before_ns,wall_unix_ns,steady_after_ns");
  for (const auto& row : rows)
    std::printf("%lld,%lld,%lld\n", row.before, row.wall, row.after);
  return std::ferror(stdout) ? 1 : 0;
}
