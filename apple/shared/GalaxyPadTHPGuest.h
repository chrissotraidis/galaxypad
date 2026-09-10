// Exact-RMGE01 candidate. Caller must verify DOL identity before enabling.
#pragma once
#include "GalaxyPadTHPDecoder.h"
#include "moderngekko/cpu_state.h"
typedef struct GalaxyPadTHPGuestFrame {
    const uint8_t *packet;
    size_t bytes;
    unsigned width,height;
    uint8_t *planes[3];
    size_t sizes[3];
} GalaxyPadTHPGuestFrame;
// Read-only eligibility check at the inner decompression entry. No guessed
// packet length: derive it from the active player's valid read-buffer header.
int GalaxyPadTHPResolveGuestFrame(const CPUState *,GalaxyPadTHPGuestFrame *);
int GalaxyPadTHPDispatchInner(CPUState *,GalaxyPadTHPDecoder *);
