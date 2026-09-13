// The private decoder must delegate the rejected instruction to the chassis.
// This callback models Interpreter::stwu + SingleStepInner fault delivery; no ROM.
#include "GalaxyPadTHPGuest.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned fallback_calls, raw_writes;
static int fault, eligible, decoded;
static void write_external(CPUState *s, uint32_t a, uint64_t v, uint8_t n) {
    (void)s; (void)a; (void)v; (void)n; ++raw_writes;
}
static void fallback(CPUState *s, uint32_t instruction, uint32_t pc) {
    assert(instruction==0x9421fff0u && pc==0x80452398u);
    ++fallback_calls;
    if (fault) {
        // A store fault preserves r1; SingleStepInner delivers DSI at 0x80000300.
        s->srr0=pc; s->dar=s->gpr[1]-16; s->pc=0x80000300;
    } else {
        s->gpr[1]-=16; s->pc=pc+4;
    }
    // HookInstructionFallback charges the host and SyncIn resets this accumulator.
    s->downcount=0;
}
int GalaxyPadTHPResolveGuestFrame(const CPUState *s, GalaxyPadTHPGuestFrame *f) {
    (void)s; memset(f,0,sizeof *f); return eligible;
}
int GalaxyPadTHPDecode(GalaxyPadTHPDecoder *d, const uint8_t *b, size_t n,
                      unsigned w, unsigned h, uint8_t *p[3], const size_t z[3]) {
    (void)d; (void)b; (void)n; (void)w; (void)h; (void)p; (void)z; return decoded;
}
static CPUState state(void) {
    CPUState s={0}; s.pc=0x80452398; s.lr=0x80451750; s.gpr[1]=0x80000100;
    s.external_write=write_external; s.instruction_fallback=fallback; return s;
}
int main(void) {
    CPUState s=state(); fault=1;
    assert(GalaxyPadTHPDispatchInner(&s,NULL));
    assert(fallback_calls==1 && raw_writes==0);
    assert(s.gpr[1]==0x80000100 && s.pc==0x80000300);
    assert(s.srr0==0x80452398 && s.dar==0x800000f0 && s.downcount==0);
    s=state(); fault=0;
    assert(GalaxyPadTHPDispatchInner(&s,NULL));
    assert(fallback_calls==2 && s.gpr[1]==0x800000f0 && s.pc==0x8045239c && s.downcount==0);
    s=state(); eligible=1; decoded=1;
    assert(GalaxyPadTHPDispatchInner(&s,NULL));
    assert(fallback_calls==2 && s.gpr[1]==0x80000100 && s.pc==s.lr);
    s=state(); s.pc=0x80000000; CPUState before=s;
    assert(!GalaxyPadTHPDispatchInner(&s,NULL) && !memcmp(&s,&before,sizeof s));
    s=state(); s.instruction_fallback=NULL; before=s;
    assert(!GalaxyPadTHPDispatchInner(&s,NULL) && !memcmp(&s,&before,sizeof s));
    puts("Private THP patch: fault-preserving fallback, success, cycle ownership and entry guard pass");
}
