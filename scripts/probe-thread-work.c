/* Private diagnostic only; never link this SPI probe into the product.
 * ABI: apple-oss-distributions/xnu bsd/sys/resource_private.h:
 * THSC_TIME_CPI=3, THSC_TIME_CPI_PER_PERF_LEVEL=4; times are Mach ticks.
 * Resolve the exported wrapper normally; no raw syscall or permission changes.
 */
#include <dlfcn.h>
#include <errno.h>
#include <inttypes.h>
#include <mach/mach_time.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/sysctl.h>
#include <time.h>

typedef struct { uint64_t instructions, cycles, user, system; } Counts;
typedef int (*ReadCounts)(unsigned, void *, size_t);
static uint64_t ns(clockid_t clock) {
  struct timespec t;
  if (clock_gettime(clock, &t)) return 0;
  return (uint64_t)t.tv_sec * 1000000000 + t.tv_nsec;
}
static int monotonic(Counts a, Counts b) {
  return b.instructions >= a.instructions && b.cycles >= a.cycles &&
         b.user >= a.user && b.system >= a.system;
}
int main(void) {
  ReadCounts read_counts = (ReadCounts)dlsym(RTLD_DEFAULT, "thread_selfcounts");
  if (!read_counts) { puts("unavailable: exported wrapper absent"); return 2; }
  mach_timebase_info_data_t tb;
  if (mach_timebase_info(&tb) || !tb.denom) return 1;
  unsigned levels = 0; size_t size = sizeof(levels);
  if (sysctlbyname("hw.nperflevels", &levels, &size, NULL, 0) ||
      levels == 0 || levels > 8) return 2;
  Counts a = {0}, b = {0}, pa[8] = {{0}}, pb[8] = {{0}};
  if (read_counts(3, &a, sizeof(a)) ||
      read_counts(4, pa, levels * sizeof(*pa))) {
    perror("thread_selfcounts"); return 2;
  }
  uint64_t cpu0 = ns(CLOCK_THREAD_CPUTIME_ID), wall0 = ns(CLOCK_MONOTONIC_RAW);
  volatile uint64_t work = 1;
  for (unsigned i = 0; i < 20000000; ++i) work = work * 1664525 + 1013904223;
  uint64_t wall1 = ns(CLOCK_MONOTONIC_RAW), cpu1 = ns(CLOCK_THREAD_CPUTIME_ID);
  if (read_counts(4, pb, levels * sizeof(*pb)) || read_counts(3, &b, sizeof(b))) {
    perror("thread_selfcounts"); return 2;
  }
  if (!monotonic(a,b) || b.instructions == a.instructions ||
      b.cycles == a.cycles || cpu1 <= cpu0 || wall1 <= wall0) return 1;
  double counted_ns = ((double)(b.user-a.user)+(b.system-a.system))*tb.numer/tb.denom;
  double ratio = counted_ns / (cpu1-cpu0);
  printf("timebase=%u/%u cpu_ns=%" PRIu64 " wall_ns=%" PRIu64
         " counted_cpu_ns=%.0f clock_ratio=%.6f instructions=%" PRIu64
         " cycles=%" PRIu64 "\n", tb.numer,tb.denom,cpu1-cpu0,wall1-wall0,
         counted_ns,ratio,b.instructions-a.instructions,b.cycles-a.cycles);
  for (unsigned i=0; i<levels; ++i) {
    if (!monotonic(pa[i],pb[i])) return 1;
    char key[64], name[128] = "unknown"; size_t n = sizeof(name);
    snprintf(key,sizeof(key),"hw.perflevel%u.name",i);
    if (sysctlbyname(key,name,&n,NULL,0)) snprintf(name,sizeof(name),"unknown");
    name[sizeof(name)-1] = 0;
    printf("level=%u name=%s instructions=%" PRIu64 " cycles=%" PRIu64
           " cpu_ns=%.0f\n",i,name,pb[i].instructions-pa[i].instructions,
           pb[i].cycles-pa[i].cycles,
           ((double)(pb[i].user-pa[i].user)+(pb[i].system-pa[i].system))*tb.numer/tb.denom);
  }
  uint64_t overhead0 = ns(CLOCK_MONOTONIC_RAW);
  for (unsigned i=0; i<1000; ++i)
    if (read_counts(4,pb,levels*sizeof(*pb))) return 2;
  printf("mean_perflevel_query_wall_ns=%.1f\n",
         (double)(ns(CLOCK_MONOTONIC_RAW)-overhead0)/1000);
  if (ratio < .9 || ratio > 1.1) {
    puts("FAIL: timebase/CPU-clock consistency outside 10% bound"); return 1;
  }
  puts("PASS: own-thread counters advance; Mach time agrees with thread CPU clock");
  return 0;
}
