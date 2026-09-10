"""Offline exact-input lookup specialization; no dispatch/cycle policy changes."""
import hashlib

HEADER_SHA='2cf2a7c3752cd6ab93f7c41140aaa2f3c1ae477cca6587925d6a5b51c3d683b9'
START='static inline DolRecompFunction dolrecomp_find_original(u32 address) {'
END='static inline int dolrecomp_call_original('
LOOKUP='''static inline DolRecompFunction dolrecomp_find_original(u32 address) {
    if (address & 3u) return NULL;
    u32 offset = address - 0x800070A0u;
    if (offset < (0x8052D280u - 0x800070A0u))
        return dolrecomp_run_chunks[3u + (offset >> 12)];
    offset = address - 0x80004000u;
    if (offset < (0x800064E0u - 0x80004000u))
        return dolrecomp_run_chunks[offset >> 12];
    return NULL;
}

'''

def transform(source):
    if hashlib.sha256(source.encode()).hexdigest()!=HEADER_SHA:
        raise ValueError('Unexpected generated header identity')
    assert source.count(START)==1 and source.count(END)==1
    start=source.index(START);end=source.index(END,start)
    return source[:start]+LOOKUP+source[end:]
