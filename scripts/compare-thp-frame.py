#!/usr/bin/env python3
"""Compare private PrologueA 640x368 GX I8 planes with linear native YUV420."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("tiled", type=Path)
parser.add_argument("linear", type=Path)
args = parser.parse_args()
gx, native = args.tiled.read_bytes(), args.linear.read_bytes()
assert len(gx) == len(native) == 640 * 368 * 3 // 2
offset = 0
for name, w, h in (("Y", 640, 368), ("U", 320, 184), ("V", 320, 184)):
    # GX I8: 8x4 texels per 32-byte tile, tiles in row-major order.
    errors = []
    for y in range(h):
        for x in range(w):
            index = ((y // 4) * (w // 8) + x // 8) * 32 + (y % 4) * 8 + x % 8
            errors.append(int(gx[offset + index]) - native[offset + y * w + x])
    print(json.dumps({"plane": name, "samples": len(errors),
                      "different": sum(e != 0 for e in errors),
                      "max_absolute_error": max(map(abs, errors)),
                      "mean_absolute_error": sum(map(abs, errors)) / len(errors),
                      "mean_signed_error": sum(errors) / len(errors)}))
    offset += w * h
