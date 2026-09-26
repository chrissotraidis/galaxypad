#pragma once
/* Constant-folded chunk lookup for modules with few contiguous runs.
   Same result as dolrecomp_find_original: runs are sorted and disjoint, so the
   first run containing the address is the one the page walk would select. */
#if DOLRECOMP_LOOKUP_RUNS <= 4
static inline __attribute__((always_inline)) DolRecompFunction gp_find_original(u32 address) {
#pragma clang loop unroll(full)
    for (u32 run = 0; run < DOLRECOMP_LOOKUP_RUNS; ++run) {
        if (address >= dolrecomp_run_start[run] && address < dolrecomp_run_end[run]) {
            u32 offset = address - dolrecomp_run_start[run];
            if ((offset & 3u) != 0u) return NULL;
            return dolrecomp_run_chunks[dolrecomp_run_base[run] + offset / dolrecomp_run_stride[run]];
        }
    }
    return NULL;
}
#else
#define gp_find_original dolrecomp_find_original
#endif
