#!/usr/bin/env python3
"""Locate an exact-input PSMTXMultVec correspondence, without installing a hook."""
import hashlib
import json
from pathlib import Path
import struct

root = Path(__file__).resolve().parents[1]
data = (root / 'generated/extracted/run1/sys/main.dol').read_bytes()
assert hashlib.sha256(data).hexdigest() == '2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09'
header = struct.unpack('>64I', data[:256])
sections = [(header[i], header[18+i], header[36+i]) for i in range(7) if header[36+i]]
# Petari mtxvec.c: psq_l f0,0(r4),0,0; psq_l f2,0(r3),0,0;
# psq_l f1,8(r4),1,0. Match opcode/register/offset bytes, not Korean addresses.
prefix = struct.pack('>3I', 0xe0040000, 0xe0430000, 0xe0248008)
matches = []
for offset, address, size in sections:
    for relative in range(0, size - 0x54 + 1, 4):
        start = offset + relative
        if data[start:start+12] == prefix and data[start+0x50:start+0x54] == bytes.fromhex('4e800020'):
            matches.append((address + relative, data[start:start+0x54]))
assert len(matches) == 1, f'Expected unique candidate, got {len(matches)}'
address, raw = matches[0]
# Full reference register/operand sequence, not merely the search prefix.
expected = (0xe0040000, 0xe0430000, 0xe0248008, 0x10820032, 0xe0630008,
            0x10a3207a, 0xe1030010, 0x10c52994, 0xe1230018, 0x11480032,
            0xf0c58000, 0x1169507a, 0xe0430020, 0x118b5b14, 0xe0630028,
            0x10820032, 0xf1858004, 0x10a3207a, 0x10c52994, 0xf0c58008,
            0x4e800020)
assert struct.unpack('>21I', raw) == expected
calls = []
for offset, base, size in sections:
    for relative in range(0, size, 4):
        word, = struct.unpack_from('>I', data, offset+relative)
        if word >> 26 != 18 or not word & 1:
            continue
        displacement = word & 0x03fffffc
        if displacement & 0x02000000:
            displacement -= 0x04000000
        pc = base+relative
        target = (displacement if word & 2 else pc+displacement) & 0xffffffff
        if target == address:
            calls.append(hex(pc))
print(json.dumps(dict(reference='ref/petari/src/RVL_SDK/mtx/mtxvec.c:PSMTXMultVec',
                      candidate_address=hex(address), size=len(raw),
                      sha256=hashlib.sha256(raw).hexdigest(),
                      instructions=[hex(w) for w in struct.unpack('>21I', raw)],
                      direct_call_sites=calls,
                      caveat='Full reference instruction words match; ABI/FP semantics and '
                             'runtime call frequency remain unverified. No hook.'), indent=2))
