// Private opt-in candidate; no registration/default activation in this file.
#include "GalaxyPadTHPGuest.h"
// Returns1 only at the exact replacement entry. Rejection executes its stwu
// through the chassis interpreter, including MMU faults and cycle charging.
int GalaxyPadTHPDispatchInner(CPUState *s,GalaxyPadTHPDecoder *decoder) {
    if(!s || s->pc!=0x80452398 || !s->instruction_fallback)return 0;
    GalaxyPadTHPGuestFrame frame;
    if(GalaxyPadTHPResolveGuestFrame(s,&frame) &&
       GalaxyPadTHPDecode(decoder,frame.packet,frame.bytes,frame.width,frame.height,
                          frame.planes,frame.sizes)) {
        s->pc=s->lr;return 1;
    }
    // Exact first instruction at80452398: stwu r1,-16(r1).
    // external_write alone does not synchronize host DSI state back to CPUState.
    // Updating r1/pc ourselves would corrupt the faulting instruction's state.
    // The callback charges this instruction; do not charge it again here.
    // Successful execution resumes at the generated interior entry; a fault
    // resumes at the interpreter's exception vector instead.
    s->instruction_fallback(s,0x9421fff0u,0x80452398u);
    return 1;
}
