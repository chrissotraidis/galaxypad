/* Read-only macOS process-wide work counters; not guest or CPU-thread counts. */
#include <errno.h>
#include <inttypes.h>
#include <limits.h>
#include <libproc.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <time.h>
#include <unistd.h>

static uint64_t now_ns(void) {
  struct timespec t;
  if (clock_gettime(CLOCK_MONOTONIC_RAW, &t)) { perror("clock_gettime"); exit(1); }
  return (uint64_t)t.tv_sec * 1000000000 + t.tv_nsec;
}

int main(int argc, char **argv) {
  if (argc != 2) { fprintf(stderr, "usage: %s PID|--self-test\n", argv[0]); return 2; }
  const int self_test = strcmp(argv[1], "--self-test") == 0;
  char *end = NULL;
  errno = 0;
  long parsed = self_test ? getpid() : strtol(argv[1], &end, 10);
  if (errno || parsed <= 0 || parsed > INT_MAX || (!self_test && (!*argv[1] || *end)))
    return 2;
  struct rusage_info_v4 first = {0}, last = {0};
  uint64_t before = now_ns();
  if (proc_pid_rusage((int)parsed, RUSAGE_INFO_V4, (rusage_info_t *)&first)) {
    perror("proc_pid_rusage"); return 1;
  }
  uint64_t after = now_ns();
  if (self_test) {
    volatile uint64_t work = 1;
    for (unsigned i = 0; i < 1000000; ++i) work = work * 1664525 + 1013904223;
    if (proc_pid_rusage((int)parsed, RUSAGE_INFO_V4, (rusage_info_t *)&last)) return 1;
    if (last.ri_proc_start_abstime != first.ri_proc_start_abstime ||
        last.ri_instructions <= first.ri_instructions || last.ri_cycles <= first.ri_cycles)
      return 1;
    puts("Process instruction/cycle counters advance under bounded self-work");
    return 0;
  }
  printf("{\"pid\":%ld,\"start_abstime\":%" PRIu64 ",\"before_ns\":%" PRIu64
         ",\"after_ns\":%" PRIu64 ",\"instructions\":%" PRIu64 ",\"cycles\":%" PRIu64
         ",\"user_time\":%" PRIu64 ",\"system_time\":%" PRIu64 "}\n",
         parsed, first.ri_proc_start_abstime, before, after, first.ri_instructions,
         first.ri_cycles, first.ri_user_time, first.ri_system_time);
  return 0;
}
