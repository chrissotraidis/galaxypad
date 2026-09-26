#include "core/cpu.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
void reference_chunk(CPUState*); void candidate_chunk(CPUState*);
static u64 xr(CPUState* c, u32 ea, u8 s){(void)c;(void)ea;(void)s;return 0;}
static void xw(CPUState* c, u32 ea, u64 v, u8 s){(void)c;(void)ea;(void)v;(void)s;}
int main(int argc, char** argv) {
  void (*f)(CPUState*) = argv[1][0]=='r' ? reference_chunk : candidate_chunk;
  unsigned calls = atoi(argv[2]);
  u8* ram = calloc(1, 0x1800000); u8* ex = calloc(1, 0x4000000);
  unsigned long long iters = 0;
  for (unsigned k = 0; k < calls; k++) {
    CPUState c; memset(&c, 0, sizeof c);
    c.ram = ram; c.ram_size = 0x1800000; c.exram = ex; c.exram_size = 0x4000000; c.external_read = xr; c.external_write = xw;
    c.gpr[5] = 0xFFFFFFFFu; c.gpr[6] = 0x80100000u + (k & 7) * 4; c.gpr[7] = 0; c.msr = 0xA000u;
    c.downcount = 2000000; c.pc = 0x80517F10u;
    f(&c); iters += c.gpr[7];
  }
  printf("iterations=%llu\n", iters); return 0; }
