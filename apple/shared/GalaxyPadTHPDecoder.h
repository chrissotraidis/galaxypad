// Private candidate; not wired into either application target.
#pragma once
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef struct GalaxyPadTHPDecoder GalaxyPadTHPDecoder;
GalaxyPadTHPDecoder *GalaxyPadTHPDecoderCreate(void);
void GalaxyPadTHPDecoderDestroy(GalaxyPadTHPDecoder *decoder);
// CPU-thread-owned, non-reentrant. Decode one complete THP video packet (not
// container frame header/audio). No destination writes on failure. Returns1
// only after validated 8x4 GX I8 tiling; otherwise0, allowing the guest fallback.
int GalaxyPadTHPDecode(GalaxyPadTHPDecoder *decoder,const uint8_t *packet,size_t bytes,
                      unsigned width,unsigned height,uint8_t *planes[3],
                      const size_t capacities[3]);
#ifdef __cplusplus
}
#endif
