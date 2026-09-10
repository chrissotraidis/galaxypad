#!/usr/bin/env python3
"""Private exact-DOL THP boundary evidence; names are reference correspondences.

No patches, hooks, game launch, or input modification. Reports raw byte hashes
and branch destinations to stdout; keep output under ignored generated/.
"""
import hashlib
import json
from pathlib import Path
import struct

root = Path(__file__).resolve().parents[1]
data = (root/'generated/extracted/run1/sys/main.dol').read_bytes()
assert hashlib.sha256(data).hexdigest() == '2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09'
words = struct.unpack('>64I', data[:256])
sections = [(words[i], words[18+i], words[36+i]) for i in range(18) if words[36+i]]

def region(address, size):
    matches = [(off, va) for off, va, length in sections if va <= address and address+size <= va+length]
    assert len(matches) == 1
    off, va = matches[0]
    return data[off+address-va:off+address-va+size]

entries = [
    # Reference RMGK01 names are correspondences, not addresses to hook blindly.
    # Each RMGE01 range is checked against the exact supported DOL below.
    ('video_decode', 0x804514ec, 0x2c0),
    ('read_frame_header', 0x804517ac, 0x134),
    ('read_scan_header', 0x804518e0, 0x114),
    ('read_quantization', 0x804519f4, 0x398),
    ('read_huffman', 0x80451d8c, 0x3c4),
    ('prepare_bitstream', 0x80452150, 0x248),
    ('decompress_yuv', 0x80452398, 0x104),
    ('row512', 0x8045249c, 0x24c),
    ('inverse_dct_no_y', 0x804526e8, 0x48c),
    ('inverse_dct_y8', 0x80452b74, 0x494),
    ('row640', 0x80453008, 0x250),
    ('row_nxn', 0x80453258, 0x25c),
    ('huffman_y', 0x804534b4, 0x65c),
    ('huffman_u', 0x80453b10, 0x688),
    ('huffman_v', 0x80454198, 0x688),
    ('initialize', 0x80454820, 0x9c),
    ('audio_decode', 0x804548bc, 0x494),
]
result = []
for name, start, size in entries:
    raw = region(start, size)
    instructions = struct.unpack('>'+str(size//4)+'I', raw)
    assert instructions[-1] == 0x4e800020, (name, 'expected final blr')
    calls, outside, conditional, indirect = [], [], [], []
    for index, instruction in enumerate(instructions):
        pc = start+4*index
        opcode = instruction>>26
        if opcode == 18:
            displacement = instruction & 0x03fffffc
            if displacement & 0x02000000:
                displacement -= 0x04000000
            target = (displacement if instruction&2 else pc+displacement)&0xffffffff
            if instruction&1:
                calls.append(dict(pc=hex(pc), target=hex(target)))
            elif not start <= target < start+size:
                outside.append(dict(pc=hex(pc), target=hex(target)))
        elif opcode == 16:
            displacement = instruction & 0xfffc
            if displacement & 0x8000:
                displacement -= 0x10000
            target = (displacement if instruction&2 else pc+displacement)&0xffffffff
            edge = dict(pc=hex(pc), target=hex(target), link=bool(instruction&1))
            conditional.append(edge)
            if instruction&1:
                calls.append(edge)
            elif not start <= target < start+size:
                outside.append(edge)
        elif opcode == 19 and (instruction>>1)&1023 in (16, 528):
            indirect.append(dict(pc=hex(pc), register='lr' if (instruction>>1)&1023 == 16 else 'ctr',
                                 link=bool(instruction&1), bo=(instruction>>21)&31))
    if name.startswith('inverse_dct'):
        assert not calls and not outside
        assert indirect == [dict(pc=hex(start+size-4), register='lr', link=False, bo=20)]
    result.append(dict(reference_name=name, start=hex(start), size=size,
                       sha256=hashlib.sha256(raw).hexdigest(), calls=calls,
                       outside_direct_branches=outside, conditional_branches=conditional,
                       indirect_branches=indirect))
by_name = {item['reference_name']: item for item in result}
for name, expected in (
    ('video_decode', '8573a49a6cb7b069206289b877cda05a8492588d503eaeb4616d493ab12056a2'),
    ('decompress_yuv', '9f3d32a0928d77d0d1a761e4ba784e125ae8fba5f99063d446a3367d5cd15464'),
):
    assert by_name[name]['sha256'] == expected
    assert not by_name[name]['outside_direct_branches']
assert dict(pc='0x8045174c', target='0x80452398') in by_name['video_decode']['calls']
assert {call['target'] for call in by_name['decompress_yuv']['calls']} == {
    '0x80452150', '0x8045249c', '0x80453008', '0x80453258'}
print(json.dumps(result, indent=2))
