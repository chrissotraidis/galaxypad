/* Isolated experiment only; no runtime source/default change. */
#include "core/types.h"
#include <inttypes.h>
#include <stdio.h>
#include <time.h>

__attribute__((noinline)) static u64 reference(u32 x) {
    return convert_to_double(x);
}
__attribute__((noinline)) static u64 candidate(u32 x) {
    u32 exponent = (x >> 23) & 255u;
    if (exponent - 1u < 254u)
        return ((u64)(x & 0x80000000u) << 32) |
               (((u64)(x & 0x7fffffffu) << 29) + (896ull << 52));
    return convert_to_double(x);
}

int main(void) {
    /* Exhaust every binary32 encoding, including signed zeros and NaN payloads. */
    for (u64 i = 0; i <= UINT32_MAX; ++i) {
        u64 a = reference((u32)i), b = candidate((u32)i);
        if (a != b) {
            fprintf(stderr, "Mismatch at %08" PRIx32 "\n", (u32)i);
            return 1;
        }
    }
    puts("All 4294967296 binary32 encodings match the pinned reference.");
    for (unsigned trial = 0; trial < 4; ++trial) {
        double seconds[2];
        u64 sums[2];
        for (unsigned step = 0; step < 2; ++step) {
            unsigned which = step ^ (trial & 1u);
            u64 (*volatile fn)(u32) = which ? candidate : reference;
            u32 x = 0x12345678u;
            u64 sum = 0;
            clock_t start = clock();
            for (unsigned i = 0; i < 10000000u; ++i) {
                x = x * 1664525u + 1013904223u;
                sum ^= fn(x);
            }
            seconds[which] = (double)(clock() - start) / CLOCKS_PER_SEC;
            sums[which] = sum;
        }
        if (sums[0] != sums[1]) return 1;
        printf("trial=%u reference=%.6f candidate=%.6f ratio=%.3f checksum=%" PRIx64 "\n",
               trial, seconds[0], seconds[1], seconds[1]/seconds[0], sums[0]);
    }
    return 0;
}
