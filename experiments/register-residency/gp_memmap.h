#pragma once
/* Experiment v2: entry snapshot of the invariant guest RAM map. Every miss,
   active journal or live reservation takes the unchanged original helper out of line. */
#define GP_AI static inline __attribute__((always_inline))
#define GP_COLD static __attribute__((noinline, cold))
typedef struct { u8* ram; u32 ram_lim; u8* exram; u32 exram_lim; } GpMemMap;
/* lim = size - 8 keeps one bound valid for every width <= 8 (sizes >= 8 at runtime). */
#define GP_MM_DECL(c) const GpMemMap gp_mm = { (c)->ram, (c)->ram_size - 8u, \
    (g_mem_write_journal == NULL && (c)->exram) ? (c)->exram : NULL, (c)->exram_size - 8u }
GP_AI u8* gp_fast_ptr(const GpMemMap* mm, u32 addr) {
    u32 m = addr & ~0x40000000u;
    u32 o2 = m - 0x90000000u;
    if (__builtin_expect(mm->exram != NULL && o2 <= mm->exram_lim, 1)) return mm->exram + o2;
    return NULL;
}
GP_AI u8* gp_fast_ptr1(const GpMemMap* mm, u32 addr) {
    u32 m = addr & ~0x40000000u;
    u32 o1 = m - 0x80000000u;
    if (o1 <= mm->ram_lim) return mm->ram + o1;
    return NULL;
}
#define GP_RD(N, T, BE) GP_COLD T gp_slow_read##N(CPUState* c, u32 a) { return mem_read##N(c, a); } \
  GP_AI T gp_mm_read##N(const GpMemMap* mm, CPUState* c, u32 a) { \
    u8* p = gp_fast_ptr(mm, a); if (p) return BE(p); \
    if (mm->exram == NULL || (((a & ~0x40000000u) - 0x90000000u) > mm->exram_lim + 8u)) { p = gp_fast_ptr1(mm, a); if (p) return BE(p); } \
    return gp_slow_read##N(c, a); }
#define GP_WR(N, T, BE) GP_COLD void gp_slow_write##N(CPUState* c, u32 a, T v) { mem_write##N(c, a, v); } \
  GP_AI void gp_mm_write##N(const GpMemMap* mm, CPUState* c, u32 a, T v) { \
    if (__builtin_expect(mm->exram != NULL && !c->reserve_valid, 1)) { \
      u8* p = gp_fast_ptr(mm, a); if (p) { BE(p, v); return; } \
      if ((((a & ~0x40000000u) - 0x90000000u) > mm->exram_lim + 8u)) { p = gp_fast_ptr1(mm, a); if (p) { BE(p, v); return; } } } \
    gp_slow_write##N(c, a, v); }
static inline u8 gp_rd8(const u8* p){return *p;}
static inline void gp_wr8(u8* p,u8 v){*p=v;}
GP_RD(8, u8, gp_rd8) GP_RD(16, u16, read_be16) GP_RD(32, u32, read_be32) GP_RD(64, u64, read_be64)
GP_WR(8, u8, gp_wr8) GP_WR(16, u16, write_be16) GP_WR(32, u32, write_be32) GP_WR(64, u64, write_be64)
