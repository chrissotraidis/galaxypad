#!/usr/bin/env python3
"""Exact Simulator module dispatch-table mapping; not a native function extent."""
import hashlib
import json
from pathlib import Path
import struct

root = Path(__file__).resolve().parents[1]
path = root / 'generated/build/ios-simulator-module/gRMGE01_recomp.dylib'
data = path.read_bytes()
digest = hashlib.sha256(data).hexdigest()
assert digest == '3acdcddcd47812c2e2a67b8cec0cf06c17009cf1ad7f2e9dc9abd83158a1bac0'
assert struct.unpack_from('<I', data)[0] == 0xfeedfacf
commands = struct.unpack_from('<I', data, 16)[0]
cursor = 32
segments = []
for _ in range(commands):
    kind, size = struct.unpack_from('<II', data, cursor)
    assert size >= 8 and cursor+size <= len(data)
    if kind == 0x19:
        va, length, offset, file_size = struct.unpack_from('<QQQQ', data, cursor+24)
        segments.append((va, offset, file_size))
    cursor += size

def at(va, size):
    found = [(base, off) for base, off, length in segments if base <= va and va+size <= base+length]
    assert len(found) == 1
    base, off = found[0]
    return data[off+va-base:off+va-base+size]

# Exact disassembly at5f60e84..98 computes unsigned16 table entry *4 +5f60e9c.
assert at(0x5f60e84, 24) == struct.pack('<6I', 0xb00063e9, 0x912e8129,
                                      0x1000008a, 0x7868792b, 0x8b0b094a, 0xd61f0140)
table, branch_base = 0x6bddba0, 0x5f60e9c
entries = []
for guest in range(0x804b683c, 0x804b6890, 4):
    index = (guest-0x804b60a0)//4
    delta, = struct.unpack('<H', at(table+index*2, 2))
    native = branch_base+delta*4
    entries.append(dict(guest=hex(guest), native=hex(native),
                        first_word=hex(struct.unpack('<I', at(native,4))[0])))
print(json.dumps(dict(module_sha256=digest, entries=entries,
                      boundary='Entry points only, not contiguous function ranges. Optimizer may '
                               'share or outline code. Do not assign samples by min/max addresses.'), indent=2))
