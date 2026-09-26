#define main harness_main
#include "harness.c"
#undef main
int main(void) {
  u32 seed = 77; unsigned runs = 0, evs = 0, iters = 0;
  for (unsigned i = 0; i < RAMSZ; i++) { ram_ref[i] = (u8)(rnd(&seed) % 3 == 0 ? rnd(&seed) : 0); ex_ref[i] = (u8)(rnd(&seed) % 3 == 0 ? rnd(&seed) : 0); }
  for (unsigned i = 0; i < sizeof ext0; i++) ext0[i] = (u8)rnd(&seed);
  u32 starts[] = { 0x80000000u, 0x80040000u, 0x80000000u + RAMSZ - 64, 0x80000000u + RAMSZ - 5, 0x90000000u + RAMSZ - 64, 0xC0000000u + RAMSZ - 40, 0xD0000000u + 0x100u, 0xCC000000u, 0x8FFFFFF0u };
  s64 dcs[] = { 0, 5, 200, 100000, -255, -300 };
  for (unsigned s = 0; s < sizeof starts / sizeof *starts; s++)
  for (unsigned d = 0; d < sizeof dcs / sizeof *dcs; d++)
  for (unsigned mode = 0; mode < 8; mode++)
  for (unsigned t = 0; t < 6; t++) {
    memset(&tmpl, 0, sizeof tmpl);
    tmpl.ram = ram; tmpl.ram_size = RAMSZ; tmpl.exram = (mode & 4) && t == 0 ? NULL : ex; tmpl.exram_size = RAMSZ;
    tmpl.external_read = xr; tmpl.external_write = xw;
    for (int r = 0; r < 32; r++) tmpl.gpr[r] = rnd(&seed);
    tmpl.gpr[6] = starts[s] + (rnd(&seed) % 4) * 4; tmpl.gpr[5] = t & 1 ? 0xFFFFFFFFu : rnd(&seed);
    tmpl.cr = rnd(&seed); tmpl.xer = rnd(&seed) & 0xE000007Fu; tmpl.msr = 0xA000u;
    tmpl.reserve_valid = mode & 1; tmpl.reserve_addr = tmpl.gpr[6] & ~31u;
    tmpl.downcount = dcs[d]; tmpl.pc = 0x80517F10u;
    g_mem_write_journal = (mode & 2) ? jr : NULL; mutate = (mode >> 2) & 1 ? (t & 1) : 0;
    int a = run(reference_chunk, 0), b = run(candidate_chunk, 1);
    runs++; evs += nev[0]; iters += (out[0].gpr[7] - tmpl.gpr[7]);
    if (b < 0 || a != b || memcmp(&out[0], &out[1], sizeof out[0]) || nev[0] != nev[1] || memcmp(ev[0], ev[1], nev[0] * sizeof(Ev))) {
      fprintf(stderr, "LOOP MISMATCH start=%08x dc=%lld mode=%u t=%u a=%d b=%d ev=%u/%u\n", starts[s], (long long)dcs[d], mode, t, a, b, nev[0], nev[1]); return 1; }
  }
  printf("LOOP PASS runs=%u loop_iterations=%u external_events=%u\n", runs, iters, evs);
  return 0;
}
