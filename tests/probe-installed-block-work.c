/* Private synthetic fixture using the installed module ABI, not gameplay state.
 * No game bytes; caller must hash-check module and keep artifacts private.
 */
#include "StaticRecompABI.h"
#include <assert.h>
#include <dlfcn.h>
#include <inttypes.h>
#include <libproc.h>
#include <stdio.h>
#include <string.h>
#include <sys/resource.h>
#include <unistd.h>

static struct rusage_info_v4 snapshot(void) {
  struct rusage_info_v4 info = {0};
  assert(!proc_pid_rusage(getpid(), RUSAGE_INFO_V4, (rusage_info_t *)&info));
  return info;
}

int main(int argc, char **argv) {
  assert(argc == 2);
  void *library = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
  if (!library) { fprintf(stderr, "%s\n", dlerror()); return 1; }
  const StaticRecompModuleDesc *(*get_module)(void) = dlsym(library, "staticrecomp_get_module");
  assert(get_module);
  const StaticRecompModuleDesc *module = get_module();
  assert(module->abi_version == STATICRECOMP_ABI_VERSION);
  assert(module->cpu_abi_version == GXRUNTIME_CPU_ABI_VERSION);
  assert(module->cpu_state_size == sizeof(CPUState));
  assert(!strcmp(module->game_id, "RMGE01"));
  unsigned char ram[256] = {0};
  write_be32(ram+64, 0x3f800000); write_be32(ram+68, 0x40000000);
  write_be32(ram+72, 0x40400000); write_be32(ram+128, 0x3f000000);
  write_be32(ram+132, 0x40400000);
  CPUState initial = {0};
  initial.ram = ram; initial.ram_size = sizeof ram; initial.msr = 0x2000;
  initial.gpr[3] = 0x80000000; initial.gpr[4] = 0x80000040;
  initial.gpr[2] = 0x80000080u-9400; initial.lr = 0x81234564;
  initial.hid2 = PPC_HID2_LSQE | PPC_HID2_PSE;
  for (unsigned r=0; r<32; ++r) { initial.fpr[r] = r/17.0; initial.ps1[r] = -r/19.0; }
  for (unsigned entry=0; entry<44; ++entry) {
    CPUState s = initial; s.pc = 0x804b6278 + entry*4; s.downcount = 10000;
    assert(module->dispatch(&s, s.pc));
    assert(s.pc == initial.lr && s.downcount == 10000-(44-entry) && !s.exception);
  }
  puts("Installed module: 44 interior-entry PC/cycle/exception checks pass");
  for (unsigned run=0; run<4; ++run) {
    CPUState s = initial;
    if (module->on_state_loaded) module->on_state_loaded(&s);
    const unsigned iterations = 1000000;
    struct rusage_info_v4 before = snapshot();
    for (unsigned i=0; i<iterations; ++i) {
      s.pc=0x804b6278; s.downcount=10000; s.fpr[1]=.2; s.fpr[2]=.8;
      assert(module->dispatch(&s,s.pc));
      assert(s.pc==initial.lr && s.downcount==9956 && !s.exception);
    }
    struct rusage_info_v4 after = snapshot();
    printf("run=%u instructions_per_call=%.3f cycles_per_call=%.3f\n",run,
      (double)(after.ri_instructions-before.ri_instructions)/iterations,
      (double)(after.ri_cycles-before.ri_cycles)/iterations);
  }
  puts("Includes fixture loop/assertions and dispatch; not gameplay weighting or a speedup.");
  dlclose(library);
}
