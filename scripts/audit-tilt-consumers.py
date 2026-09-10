#!/usr/bin/env python3
"""Read-only exact-RMGE01 tilt call-site checks; not gameplay or ABI acceptance."""
import hashlib
from pathlib import Path
import struct

root = Path(__file__).resolve().parents[1]
data = (root / 'generated/extracted/run1/sys/main.dol').read_bytes()
digest = hashlib.sha256(data).hexdigest()
if digest != '2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09':
    raise SystemExit('Unsupported DOL identity')
header = struct.unpack_from('>64I', data)

def word(address):
    for i in range(18):
        offset, base, size = header[i], header[18+i], header[36+i]
        if offset and base <= address and address + 4 <= base + size:
            return struct.unpack_from('>I', data, offset + address-base)[0]
    raise ValueError(f'Unmapped address {address:08x}')

def branch(address, target, link=True):
    instruction = word(address)
    if instruction & 0xFC000003 != 0x48000000 | int(link):
        raise ValueError(f'Not expected relative branch at {address:08x}')
    delta = instruction & 0x03FFFFFC
    if delta & 0x02000000:
        delta -= 0x04000000
    if (address + delta) & 0xFFFFFFFF != target:
        raise ValueError(f'Wrong branch target at {address:08x}')

# Names are candidate labels from pinned Bussun USA symbols (R546).
# Raw branch opcodes/operands below are verified independently of comments.
branch(0x803302E0, 0x8033015C)  # sphere acceleration clacXY -> acceleration getter
branch(0x80330170, 0x803D21B8, False)  # core branch -> MR acceleration
branch(0x803306AC, 0x803D2904)  # plain sphere clacXY -> Nunchuk X
branch(0x803306B8, 0x803D292C)  # plain sphere clacXY -> Nunchuk Y
branch(0x803301A0, 0x803D2244)  # ball brake -> core held A
branch(0x803301F8, 0x803D25CC)  # ball jump -> core triggered A
branch(0x803327F4, 0x803332DC)  # ray updateRotate -> rotate gate
branch(0x8033281C, 0x803D21B8)  # ray updateRotate -> same core acceleration
if word(0x8033015C) != 0x800300B8:
    raise ValueError('Sphere core/sub selector offset changed')
# Tamakoro constructs the acceleration controller and stores it at actor+0x8c.
branch(0x803378E8, 0x803300B4)
# Constructor installs vtable805bbc30. Its move slot retains the shared sphere
# implementation; its axis slot replaces only clacXY.
for address, expected in [
    (0x803300D0, 0x3C80805C), (0x803300E0, 0x3884BC30),
    (0x803300F4, 0x909F0000), (0x803378EC, 0x907E008C),
    (0x805BBC38, 0x8033064C), (0x805BBC3C, 0x803301E8),
    (0x805BBC40, 0x80330228), (0x805BBC50, 0x80330230),
    (0x8033064C, 0x38C00000),
    # shared movement dynamically dispatches vtable+0x20
    (0x8033070C, 0x81830000), (0x80330710, 0x818C0020),
    (0x80330714, 0x7D8903A6), (0x80330718, 0x4E800421),
    # clacXY preserves output pointers r4/r5 in r30/r31, stores scalar axes
    (0x80330270, 0x7CBF2B78), (0x80330278, 0x7C9E2378),
    (0x803304AC, 0xD3BE0000), (0x803304B0, 0xD35F0000),
    (0x803304F8, 0x4E800020),
]:
    if word(address) != expected:
        raise ValueError(f'Tilt dispatch/output contract changed at {address:08x}')
branch(0x80330650, 0x803306D8, False)
print('PASS: exact RMGE01 tilt calls, ball vtable dispatch and axis output stores; no patch applied')
print('Full function semantics, live object state and gameplay remain unverified')
