/* Controlled child for frontend UI tests; never executes game code. */
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
static volatile sig_atomic_t stopped;
static void stop(int signal_number) { (void)signal_number; stopped = 1; }
int main(void) {
  signal(SIGTERM, stop);
  const char *mode = getenv("GALAXYPAD_PROGRESS_TEST");
  const int delay = mode && mode[0] == 'c' ? 120 : 30;
  for (int i = 0; i < delay && !stopped; ++i) sleep(1);
  if (stopped) { puts("TEST child terminated gracefully"); return 0; }
  if (mode && mode[0] == 'f') { puts("TEST intentional failure"); return 7; }
  puts("[staticrecomp] module loaded: TEST readiness marker only"); fflush(stdout);
  for (int i = 0; i < 5 && !stopped; ++i) sleep(1);
  return 0;
}
