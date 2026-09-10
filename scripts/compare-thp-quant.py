#!/usr/bin/env python3
"""Compare diagnostic THP AAN-scaled float tables to native integer DQT values."""
import argparse
from pathlib import Path
import re
import struct

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("original", type=Path)
parser.add_argument("native", type=Path)
args = parser.parse_args()
original = re.findall(r"quant \d+ bits=([^\n]+)", args.original.read_text())
native = re.findall(r"quant \d+ values=([^\n]+)", args.native.read_text())
assert len(original) == len(native) == 6
def f32(x):
    return struct.unpack(">f", struct.pack(">f", x))[0]
# Reference THP header defines f64 elements initialized with float literals.
scale = list(map(f32, (1.0, 1.387039845, 1.306562965, 1.175875602,
                      1.0, 0.785694958, 0.541196100, 0.275899379)))
bad = 0
for block, (a, b) in enumerate(zip(original, native)):
    bits = [int(x, 16) for x in a.split(",")]
    values = [int(x) for x in b.split(",")]
    assert len(bits) == len(values) == 64
    expected = [struct.unpack(">I", struct.pack(">f", q * scale[i//8] * scale[i%8]))[0]
                for i, q in enumerate(values)]
    count = sum(x != y for x, y in zip(bits, expected))
    print(f"block={block} differing_scaled_table_entries={count}/64")
    bad += count
print(f"total differing entries={bad}/384")
raise SystemExit(bool(bad))
