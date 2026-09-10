/* Actual runtime ABI offsets for interpreting disassembly, not base-reg proof. */
#include <stddef.h>
#include <stdio.h>
#ifndef PROBE_CPU_HEADER
#define PROBE_CPU_HEADER "core/cpu.h"
#endif
#include PROBE_CPU_HEADER
#define FIELD(name) printf("%s 0x%zx %zu\n", #name, offsetof(CPUState, name), sizeof(((CPUState*)0)->name))
int main(void) {
  printf("CPUState %zu\n", sizeof(CPUState));
  FIELD(gpr); FIELD(fpr); FIELD(ps1); FIELD(pc); FIELD(lr); FIELD(fpscr); FIELD(msr);
  FIELD(downcount); FIELD(ram); FIELD(ram_size); FIELD(exram); FIELD(exram_size);
  FIELD(external_read); FIELD(external_write); FIELD(reserve_valid);
  return 0;
}
