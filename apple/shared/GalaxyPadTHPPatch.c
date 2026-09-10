// Private opt-in candidate; no registration/default activation in this file.
#include "GalaxyPadTHPGuest.h"
// Returns1 only at the exact replacement entry. Rejection emulates its stwu
// and advances one instruction so subsequent dispatch cannot re-enter the patch.
int GalaxyPadTHPDispatchInner(CPUState *s,GalaxyPadTHPDecoder *decoder) {
    if(!s || s->pc!=0x80452398 || !s->external_write)return 0;
    GalaxyPadTHPGuestFrame frame;
    if(GalaxyPadTHPResolveGuestFrame(s,&frame) &&
       GalaxyPadTHPDecode(decoder,frame.packet,frame.bytes,frame.width,frame.height,
                          frame.planes,frame.sizes)) {
        s->pc=s->lr;return 1;
    }
    // Exact first instruction at80452398: stwu r1,-16(r1).
    // The generated interior entry charges the remaining26 cycles of this block.
    uint32_t old_sp=s->gpr[1],address=old_sp-16;
    // Use the chassis MMU callback, not module-private journal globals.
    if(s->reserve_valid && (((s->reserve_addr&~0x40000000u) ^
                            (address&~0x40000000u))&~31u)==0)s->reserve_valid=false;
    s->external_write(s,address,old_sp,4);
    s->gpr[1]=address;s->pc=0x8045239c;s->downcount-=1;
    return 1;
}
