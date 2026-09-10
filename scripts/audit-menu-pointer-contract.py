#!/usr/bin/env python3
"""Check selected USA pointer-menu call sites against the exact supported DOL.

Candidates from Bussun78f4a04 USA symbols; no patching or runtime writes.
This validates narrow instruction contracts, not complete function equivalence.
"""
import hashlib
import json
from pathlib import Path
import struct

root = Path(__file__).resolve().parents[1]
data = (root / "generated/extracted/run1/sys/main.dol").read_bytes()
identity = hashlib.sha256(data).hexdigest()
assert identity == "2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09"
header = struct.unpack_from(">64I", data)
sections = [(header[i], header[18+i], header[36+i]) for i in range(18)]


def word(address):
    for offset, base, size in sections:
        if offset and base <= address and address + 4 <= base + size:
            return struct.unpack_from(">I", data, offset + address - base)[0]
    raise ValueError(f"Unmapped DOL address {address:08x}")


def branch(address, target):
    instruction = word(address)
    assert instruction & 0xFC000003 == 0x48000001, hex(address)
    delta = instruction & 0x03FFFFFC
    if delta & 0x02000000:
        delta -= 0x04000000
    assert (address + delta) & 0xFFFFFFFF == target, hex(address)


# FileSelectItem: reject invalid selection; require pointing before A edge.
branch(0x80178EC4, 0x803FB0EC)  # live observer return address80178EC8
# Native observer has one explicit return site. Audit all direct BL callers in
# text sections; this does not claim absence of indirect calls or future RELs.
callers=[]
for offset,base,size in sections[:7]:
    if not offset: continue
    for address in range(base,base+size-3,4):
        instruction=word(address)
        if instruction & 0xFC000003 != 0x48000001: continue
        delta=instruction & 0x03FFFFFC
        if delta & 0x02000000: delta-=0x04000000
        if (address+delta)&0xFFFFFFFF == 0x803FB0EC: callers.append(address)
assert callers==[0x80178EC4], [hex(address) for address in callers]
assert word(0x80178EF4) == 0x881F0145  # lbz r0,0x145(r31)
assert word(0x80178F00) == 0x881F0144  # lbz r0,0x144(r31)
branch(0x80178F0C, 0x803D2B6C)
# ButtonPaneController: pointing Nerve check before the same A predicate.
branch(0x8034BF8C, 0x803A29B8)
branch(0x8034BF98, 0x803D2B6C)
# Menu predicate uses P1 WPad and WPadButton::testTriggerA, not held A.
assert word(0x803D2B74) == 0x38600000  # li r3,0
branch(0x803D2B7C, 0x803AB568)
branch(0x803D2B84, 0x803AB094)
# Context getter: r13 singleton -> sequence -> progress -> pointer controller.
for address, instruction in [(0x803FA3E4,0x806DC588), (0x803FA3E8,0x8063000C),
                             (0x803FA3EC,0x80630004), (0x803FA3F0,0x80630008)]:
    assert word(address)==instruction, hex(address)
branch(0x803FCC70,0x803FA3E4)
assert word(0x803FCC74)==0x806300D0
# Fixed 16-entry request pointer array [0x0c,0x4c), requester/mode record.
for address, instruction in [(0x803A9CB0,0x38C3004C),(0x803A9CB4,0x3903000C),
                             (0x803A9CD4,0x80070000),(0x803A9CFC,0x90870000),
                             (0x803A9D0C,0x90A40004),
                             (0x803A8E54,0x38A00005),(0x8017B668,0x808300BC)]:
    assert word(address)==instruction,hex(address)
branch(0x803A8E58,0x803A9CA8)
# LiveActor::isNerve loads Spine+0x50; getter prefers pending+8 to current+4.
assert word(0x80165834)==0x80630050
branch(0x80165844,0x8016FBA4)
for address, instruction in [(0x8016FBA4,0x80030008),(0x8016FBA8,0x2C000000),
                             (0x8016FBAC,0x4182000C),(0x8016FBB0,0x7C030378),
                             (0x8016FBB4,0x4E800020),(0x8016FBB8,0x80630004),
                             (0x8016FBBC,0x4E800020)]:
    assert word(address)==instruction,hex(address)
# Pointer freshness boundary: retail hit testing passes the past position (+4),
# not the current sample (+0x18), to the indirect target predicate. Retail also
# tests past in-screen byte +0x0c directly (Petari's current inline helper differs).
branch(0x803FA538,0x803858C0)
for address,instruction in [
    (0x803FA53C,0x8803000C), (0x803FA540,0x7C7F1B78),
    (0x803FA5D4,0xC03F0014), (0x803FA5DC,0x389F0064),
    (0x803FA5E0,0x38BF0004), (0x803FA5E4,0x7D8903A6),
    (0x803FA5E8,0x4E800421)]:
    assert word(address)==instruction,hex(address)
# movement first copies current info to past, then samples/updates current info.
branch(0x8038500C,0x80385034)
branch(0x80385014,0x8038513C)
branch(0x8038501C,0x803852BC)
for address,instruction in [
    (0x803850CC,0x889D0020), (0x803850D0,0x80DD0018),
    (0x803850D4,0x80BD001C), (0x803850E8,0x90DD0004),
    (0x803850EC,0x90BD0008), (0x803850F0,0x989D000C),
    (0x80385348,0x809F0040), (0x8038534C,0x981F0020),
    (0x80385350,0x387F0018)]:
    assert word(address)==instruction,hex(address)
branch(0x80385354,0x800AD510)  # copy new position to current info
for address,instruction in [(0x800AD510,0xC0240000),(0x800AD514,0xC0040004),
                             (0x800AD518,0xD0230000),(0x800AD51C,0xD0030004),
                             (0x800AD520,0x4E800020)]:
    assert word(address)==instruction,hex(address)  # exact two-float copy body
# Screen-position accessor independently returns the same past-position address.
branch(0x803ABD7C,0x8044E33C)  # WPadPointer reset -> KPAD position parameters
for address,instruction in [(0x8044E33C,0x1C031BF8),(0x8044E340,0x3C608062),
                             (0x8044E344,0x3863D340),(0x8044E348,0x7C630214),
                             (0x8044E34C,0xD0230084),(0x8044E350,0xD0430088),
                             (0x8044E354,0x4E800020),
                             (0x8044E59C,0x1C031BF8),(0x8044E5A4,0x3C608062),
                             (0x8044E5B4,0x3863D340),(0x8044E5C4,0x7FE30214),
                             (0x8044E5C8,0xD09F00B8),(0x8044E5D0,0xD07F00BC),
                             (0x8044E624,0xEC03F024),(0x8044E628,0xD01F00C0)]:
    assert word(address)==instruction,hex(address)
# These identify fields, not complete SDK equivalence or a valid inverse mapping.
assert word(0x8044FB88)==0x801E1BE8  # lwz r0,0x1be8(r30): position-filter mode
# Retail WPAD parser flips camera Y before KPAD: 767 - decoded sensor row.
for address,instruction in [(0x804DF030,0x22F702FF),(0x804DF1B4,0x218C02FF),
                             (0x804DF1F4,0x218C02FF)]:
    assert word(address)==instruction,hex(address)
for address,instruction in [(0x8044FA6C,0xC05E1B58),(0x8044FA70,0xC01E00B4),
    (0x8044FA7C,0xC0BE1B54),(0x8044FA84,0xC09E00B0),
    (0x8044FA90,0xC0FE00F4),(0x8044FA98,0xC0DE0100),
    (0x8044FAA0,0xC09E00F8),(0x8044FAA4,0xC03E0104),
    (0x8044FAB8,0xC09E00AC),(0x8044FAC4,0xC03E00A8),
    (0x8044FB60,0xC03E0020),(0x8044FB64,0xC01E0024)]:
    assert word(address)==instruction,hex(address)  # conversion/filter input loads
for address,instruction in [(0x80386000,0x806DC588),(0x80386004,0x80630020),
                             (0x80386008,0x80630030),(0x803858C0,0x1C040074),
                             (0x803858C4,0x80630004),(0x803858C8,0x7C630214),
                             (0x803FB120,0x38A00000)]:
    assert word(address)==instruction,hex(address)  # director chain and P1 channel
branch(0x803FB5D8,0x803858C0)
assert word(0x803FB5E0)==0x38630004
branch(0x803F6B50,0x803FDEDC)  # aspect predicate; screen-space width is not EFB width
for address,instruction in [(0x803F6B54,0x2C030000),(0x803F6B58,0x38600260),
                             (0x803F6B5C,0x41820008),(0x803F6B60,0x38600340)]:
    assert word(address)==instruction,hex(address)
print(json.dumps({"dol_sha256": identity, "status": "narrow call-site contracts verified",
    "file_item_pointing_offset": "0x144", "file_item_invalid_offset": "0x145",
    "menu_a_edge_predicate": "0x803d2b6c",
    "hit_test_position_offset": "0x4 (past), not 0x18 (current)",
    "hit_test_in_screen_offset": "0xc (past)",
    "warning": "Not full equivalence, runtime target identity, or Direct Touch acceptance"}, indent=2))
