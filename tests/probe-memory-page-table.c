/* Data-only mapping prototype. Not linked into GalaxyPad. */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "core/cpu.h"

PPCMemWriteJournal g_mem_write_journal;
void *g_mem_write_journal_user;
enum { PAGE_SHIFT = 17, PAGE_SIZE = 1 << PAGE_SHIFT, PAGE_COUNT = 1 << 15 };
#ifndef ITERATIONS
#define ITERATIONS 2000000
#endif
typedef struct {
  u8 *pointer;
  u32 offset;
} Page;
typedef struct {
  Page pages[PAGE_COUNT];
  u8 *ram, *exram;
  u32 ram_size, exram_size;
  unsigned rebuilds;
  unsigned callback_depth;
} Mapping;

static void refresh(Mapping *map, CPUState *cpu) {
  if (map->rebuilds && map->ram == cpu->ram && map->exram == cpu->exram &&
      map->ram_size == cpu->ram_size && map->exram_size == cpu->exram_size)
    return;
  memset(map->pages, 0, sizeof(map->pages));
  /* Ask the existing resolver to certify each complete page, preserving
     mapping precedence and MEM1 write-journal offsets. Partial pages fall back. */
  if (cpu->ram_size >= PAGE_SIZE && (!cpu->exram || cpu->exram_size >= PAGE_SIZE)) {
    for (u32 page = 0; page < PAGE_COUNT; ++page) {
      u32 offset = 0;
      u8 *ptr = get_ram_ptr(cpu, page << PAGE_SHIFT, PAGE_SIZE, &offset);
      map->pages[page] = (Page){ptr, offset};
    }
  }
  map->ram = cpu->ram; map->exram = cpu->exram;
  map->ram_size = cpu->ram_size; map->exram_size = cpu->exram_size;
  ++map->rebuilds;
}

static u8 *resolve_ready(Mapping *map, CPUState *cpu, u32 address, u32 size, u32 *offset) {
  if (map->callback_depth) return get_ram_ptr(cpu, address, size, offset);
  Page page = map->pages[address >> PAGE_SHIFT];
  u32 within = address & (PAGE_SIZE - 1);
  if (page.pointer && size && size <= PAGE_SIZE && within <= PAGE_SIZE - size) {
    if (offset) *offset = page.offset == (u32)-1 ? (u32)-1 : page.offset + within;
    return page.pointer + within;
  }
  return get_ram_ptr(cpu, address, size, offset);
}

static u8 *resolve(Mapping *map, CPUState *cpu, u32 address, u32 size, u32 *offset) {
  /* Deliberately validate every lookup in this oracle. Moving this refresh to
     host boundaries is NOT proved here and must not be done silently. */
  refresh(map, cpu);
  return resolve_ready(map, cpu, address, size, offset);
}

static void callback_enter(Mapping *map) { ++map->callback_depth; }
static void callback_leave(Mapping *map, CPUState *cpu) {
  assert(map->callback_depth);
  if (!--map->callback_depth) refresh(map, cpu);
}

static unsigned comparisons;
static volatile uintptr_t sink;
static __attribute__((noinline)) u8 *baseline(CPUState *cpu, u32 address) {
  return get_ram_ptr(cpu, address, 4, NULL);
}
static __attribute__((noinline)) u8 *prototype(Mapping *map, CPUState *cpu, u32 address) {
#ifdef BOUNDARY_TIMING
  /* Optimistic stable-map diagnostic only, no callbacks during timed region.
     Actual runtime boundary integration remains entirely unimplemented. */
  return resolve_ready(map, cpu, address, 4, NULL);
#else
  return resolve(map, cpu, address, 4, NULL);
#endif
}
static void timing(Mapping *map, CPUState *cpu, int candidate) {
  struct timespec start, end;
  u32 random = 29; uintptr_t sum = 0;
  clock_gettime(CLOCK_THREAD_CPUTIME_ID, &start);
  for (unsigned i = 0; i < ITERATIONS; ++i) {
    random = random * 1664525u + 1013904223u;
    u32 address = (i & 1 ? 0x80000000u : 0x90000000u) + (random & 0x1fffcu);
    sum ^= (uintptr_t)(candidate ? prototype(map, cpu, address) : baseline(cpu, address));
  }
  clock_gettime(CLOCK_THREAD_CPUTIME_ID, &end); sink = sum;
  double ns = (end.tv_sec-start.tv_sec)*1e9 + end.tv_nsec-start.tv_nsec;
  printf("%s %.3f ns/lookup (synthetic)\n",
         candidate ? "table" : "range", ns/ITERATIONS);
}
static void check(Mapping *map, CPUState *cpu, u32 address, u32 size) {
  u32 a = 0xaabbccdd, b = a;
  u8 *reference = get_ram_ptr(cpu, address, size, &a);
  u8 *candidate = resolve(map, cpu, address, size, &b);
  assert(reference == candidate && a == b);
  ++comparisons;
}

int main(void) {
  Mapping *map = calloc(1, sizeof(*map)); assert(map);
  u8 *a = malloc(4 * PAGE_SIZE), *b = malloc(4 * PAGE_SIZE);
  u8 *c = malloc(4 * PAGE_SIZE); assert(a && b && c);
  CPUState cpu = {0};
  const u32 bases[] = {0, 0x80000000, 0x90000000, 0xc0000000, 0xd0000000,
                       0xe0000000, 0xffffffff};
  const u32 widths[] = {1, 2, 4, 8};
  u32 random = 73;
  for (unsigned mode = 0; mode < 6; ++mode) {
    cpu.ram = mode & 1 ? b : a;
    cpu.ram_size = mode == 4 ? 64 : 3 * PAGE_SIZE + 13;
    cpu.exram = mode == 2 ? NULL : c;
    cpu.exram_size = mode == 5 ? 64 : 2 * PAGE_SIZE + 7;
    for (unsigned trial = 0; trial < 100000; ++trial) {
      random = random * 1664525u + 1013904223u;
      check(map, &cpu, random, widths[trial & 3]);
    }
    for (unsigned base = 0; base < 7; ++base)
      for (u32 boundary = 0; boundary <= 4 * PAGE_SIZE; boundary += PAGE_SIZE)
        for (int delta = -16; delta < 24; ++delta)
          for (unsigned width = 0; width < 4; ++width)
            check(map, &cpu, bases[base] + boundary + delta, widths[width]);
    for (unsigned width = 0; width < 4; ++width)
      for (int delta = -16; delta < 24; ++delta) {
        check(map, &cpu, 0x80000000u + cpu.ram_size + delta, widths[width]);
        check(map, &cpu, 0x90000000u + cpu.exram_size + delta, widths[width]);
      }
  }
  printf("%u pointer/journal-offset comparisons passed; %u mapping rebuilds\n",
         comparisons, map->rebuilds);
  cpu.ram = a; cpu.ram_size = 3 * PAGE_SIZE;
  cpu.exram = c; cpu.exram_size = 3 * PAGE_SIZE; refresh(map, &cpu);
  u8 *acquired = resolve_ready(map, &cpu, 0x80000000u, 4, NULL);
  assert(acquired == a);
  callback_enter(map); cpu.ram = b;
  assert(resolve_ready(map, &cpu, 0x80000000u, 4, NULL) == b);
  callback_enter(map); cpu.ram = c;
  assert(resolve_ready(map, &cpu, 0x80000000u, 4, NULL) == c);
  callback_leave(map, &cpu); cpu.ram = b;
  assert(resolve_ready(map, &cpu, 0x80000000u, 4, NULL) == b);
  callback_leave(map, &cpu);
  assert(resolve_ready(map, &cpu, 0x80000000u, 4, NULL) == b);
  /* A journal callback cannot redirect the already-acquired current store. */
  write_be32(acquired, 37); assert(read_be32(a) == 37);
  assert(acquired != resolve_ready(map, &cpu, 0x80000000u, 4, NULL));
  puts("Nested boundary invalidation and acquired-pointer ordering passed");
#ifdef TIMING
#ifdef BOUNDARY_TIMING
  puts("Boundary-only stable-map diagnostic; no runtime integration or callback cost");
#else
  puts("Per-access mapping validation diagnostic");
#endif
  cpu.ram = a; cpu.ram_size = 3 * PAGE_SIZE;
  cpu.exram = c; cpu.exram_size = 3 * PAGE_SIZE;
  refresh(map, &cpu);
#ifdef REVERSE_ORDER
  timing(map, &cpu, 1); timing(map, &cpu, 0);
  timing(map, &cpu, 0); timing(map, &cpu, 1);
#else
  timing(map, &cpu, 0); timing(map, &cpu, 1);
  timing(map, &cpu, 1); timing(map, &cpu, 0);
#endif
#endif
  free(a); free(b); free(c); free(map);
}
