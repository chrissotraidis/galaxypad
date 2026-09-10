// Diagnostic module extension. Not part of CPUState or the shipping module ABI.
#ifndef GALAXYPAD_DIRECT_CALL_BINDING_H
#define GALAXYPAD_DIRECT_CALL_BINDING_H
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif
typedef struct CPUState CPUState;
// Called on the guest CPU thread at a completed segment boundary. The host
// commits that segment's cycles exactly once and validates target before true.
typedef int (*GalaxyPadDirectBoundary)(CPUState* state, uint32_t target);
enum { GALAXYPAD_DIRECT_CALL_BINDING_VERSION = 1 };

// Bind before CPU execution; clear before teardown. No concurrent rebinding.
// An unsupported version clears any prior binding and returns false.
__attribute__((visibility("default")))
int galaxypad_bind_direct_calls_v1(uint32_t version, GalaxyPadDirectBoundary boundary);

// Missing binding/state always takes the original return-to-chassis path.
// This callback is necessary, not sufficient: generated code must also preserve
// replacement routing, depth limits, early returns and continuation checks.
int galaxypad_direct_call_boundary(CPUState* state, uint32_t target);
#ifdef __cplusplus
}
#endif
#endif
