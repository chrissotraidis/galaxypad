#include "core/cpu.h"
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
void reference_chunk(CPUState*);
void candidate_chunk(CPUState*);
extern const unsigned gp_entries[]; extern const unsigned gp_entry_count;
#define RAMSZ 0x100000u
static u8 ram_ref[RAMSZ], ex_ref[RAMSZ], ram[RAMSZ], ex[RAMSZ], ext0[65536], ext[65536];
typedef struct { u32 pc, ea, size, kind, cr, xer, rv, ra; u64 value; s64 dc; u32 gpr[32]; } Ev;
static Ev ev[2][4096]; static unsigned nev[2], side, mutate; static jmp_buf stop;
static void rec(CPUState* c, u32 ea, u32 size, u64 v, u32 kind) {
  if (nev[side] == 4096) longjmp(stop, 1);
  Ev* e = &ev[side][nev[side]++]; memset(e, 0, sizeof *e);
  e->pc = c->pc; e->ea = ea; e->size = size; e->value = v; e->kind = kind; e->cr = c->cr; e->xer = c->xer;
  e->dc = c->downcount; e->rv = c->reserve_valid; e->ra = c->reserve_addr; memcpy(e->gpr, c->gpr, sizeof e->gpr);
#ifdef GP_CALLBACK_CONTRACT
  /* Runtime MMIO hooks never write guest integer registers; mutate only state they may touch. */
  if (mutate && nev[side] % 5 == 0) { c->exception ^= 1; c->fpr[3] += 1.0; c->reserve_valid = !c->reserve_valid; c->reserve_addr = ea; }
#else
  if (mutate && nev[side] % 5 == 0) { c->gpr[12] ^= 3; c->xer ^= 0x80000000u; c->reserve_valid = !c->reserve_valid; c->reserve_addr = ea; }
#endif
}
static u64 xr(CPUState* c, u32 ea, u8 size) { u64 v = 0; for (unsigned i = 0; i < size; i++) v = (v << 8) | ext[(ea + i) & 0xFFFF]; rec(c, ea, size, v, 0); return v; }
static void xw(CPUState* c, u32 ea, u64 v, u8 size) { rec(c, ea, size, v, 1); for (unsigned i = 0; i < size; i++) ext[(ea + i) & 0xFFFF] = (u8)(v >> (8 * (size - i - 1))); }
static void jr(u32 off, u32 size, void* user) { rec((CPUState*)user, off, size, 0, 2); }
static u32 rnd(u32* s) { *s ^= *s << 13; *s ^= *s >> 17; *s ^= *s << 5; return *s; }
static u32 pick(u32* s) {
  u32 k = rnd(s) % 12, o = rnd(s) % RAMSZ;
  switch (k) {
  case 0: case 1: case 2: return 0x80000000u + o;
  case 3: return 0xC0000000u + o;
  case 4: case 5: return 0x90000000u + o;
  case 6: return 0xD0000000u + o;
  case 7: return 0x80000000u + RAMSZ - (rnd(s) % 16);
  case 8: return 0x90000000u + RAMSZ - (rnd(s) % 16);
  case 9: return 0xCC000000u + (rnd(s) & 0xFFFF);
  case 10: return rnd(s) % 64;
  default: return rnd(s);
  }
}
static CPUState tmpl, out[2];
static int run(void (*f)(CPUState*), unsigned s) {
  side = s; nev[s] = 0; memcpy(ram, ram_ref, RAMSZ); memcpy(ex, ex_ref, RAMSZ); memcpy(ext, ext0, sizeof ext);
  out[s] = tmpl; g_mem_write_journal_user = &out[s];
  int capped = setjmp(stop); if (!capped) f(&out[s]);
  static u8 r2[2][RAMSZ], e2[2][RAMSZ], x2[2][65536];
  memcpy(r2[s], ram, RAMSZ); memcpy(e2[s], ex, RAMSZ); memcpy(x2[s], ext, sizeof ext);
  if (s == 1) {
    if (memcmp(r2[0], r2[1], RAMSZ) || memcmp(e2[0], e2[1], RAMSZ) || memcmp(x2[0], x2[1], sizeof ext)) return -1;
  }
  return capped;
}
int main(int argc, char** argv) {
  unsigned trials = argc > 1 ? (unsigned)atoi(argv[1]) : 3, runs = 0, capped = 0, evs = 0, jn = 0; u32 seed = 0x9E3779B9u;
  for (unsigned i = 0; i < RAMSZ; i++) { ram_ref[i] = (u8)rnd(&seed); ex_ref[i] = (u8)rnd(&seed); }
  for (unsigned i = 0; i < sizeof ext0; i++) ext0[i] = (u8)rnd(&seed);
  for (unsigned e = 0; e < gp_entry_count; e++)
  for (unsigned mode = 0; mode < 8; mode++)
  for (unsigned t = 0; t < trials; t++) {
    memset(&tmpl, 0, sizeof tmpl);
    tmpl.ram = ram; tmpl.ram_size = RAMSZ; tmpl.exram = (mode & 4) && t == 0 ? NULL : ex; tmpl.exram_size = RAMSZ;
    tmpl.external_read = xr; tmpl.external_write = xw;
    for (int r = 0; r < 32; r++) tmpl.gpr[r] = pick(&seed);
    tmpl.gpr[1] = 0x80000000u + 0x80000u + (rnd(&seed) % 0x4000) * 8u;
    for (int r = 0; r < 32; r++) { u64 b = ((u64)rnd(&seed) << 32) | rnd(&seed); if (r & 1) { float f = (float)(int)(rnd(&seed) % 2000 - 1000) / 7.0f; tmpl.fpr[r] = (f64)f; tmpl.ps1[r] = (f64)f * 0.5; } else { memcpy(&tmpl.fpr[r], &b, 8); tmpl.ps1[r] = (f64)(int)rnd(&seed) / 3.0; } }
    tmpl.cr = rnd(&seed); tmpl.xer = rnd(&seed) & 0xE000007Fu; tmpl.lr = pick(&seed); tmpl.ctr = rnd(&seed) % 40;
    tmpl.msr = 0x2000u | 0x8000u; for (int g = 0; g < 8; g++) tmpl.gqr[g] = rnd(&seed) & 0x3F073F07u;
    tmpl.reserve_valid = (mode & 1) ? 1 : 0; tmpl.reserve_addr = (mode & 1) ? pick(&seed) & ~31u : 0;
    tmpl.downcount = (s64)(rnd(&seed) % 4000) - 300; tmpl.pc = gp_entries[e];
    g_mem_write_journal = (mode & 2) ? jr : NULL; mutate = (mode >> 2) & 1 ? (t & 1) : 0;
    int a = run(reference_chunk, 0), b = run(candidate_chunk, 1);
    runs++; capped += a > 0; evs += nev[0];
    if (b < 0 || a != b || memcmp(&out[0], &out[1], sizeof out[0]) || nev[0] != nev[1] || memcmp(ev[0], ev[1], nev[0] * sizeof(Ev))) {
      unsigned k = 0; for (; k < nev[0] && k < nev[1] && !memcmp(&ev[0][k], &ev[1][k], sizeof(Ev)); k++);
      fprintf(stderr, "MISMATCH entry=%08x mode=%u trial=%u a=%d b=%d events %u/%u first-diff=%u state=%d\n", gp_entries[e], mode, t, a, b, nev[0], nev[1], k, memcmp(&out[0], &out[1], sizeof out[0]) != 0);
      return 1;
    }
    for (unsigned k = 0; k < nev[0]; k++) jn += ev[0][k].kind == 2;
  }
  printf("PASS entries=%u runs=%u capped=%u events=%u journal_events=%u\n", gp_entry_count, runs, capped, evs, jn);
  return 0;
}
