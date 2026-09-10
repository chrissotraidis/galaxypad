#!/usr/bin/env python3
"""Private diagnostic: compare largest frame errors to a double cosine IDCT.

Mathematical reference only: does not model Wii floating-point/store semantics.
"""
import argparse
import math
from pathlib import Path
import re
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("original", type=Path)
parser.add_argument("native", type=Path)
parser.add_argument("coefficients", type=Path)
parser.add_argument("quantization", type=Path)
args = parser.parse_args()
gx, native = args.original.read_bytes(), args.native.read_bytes()
assert len(gx) == len(native) == 353280
blocks = [[int(v) for v in s.split(",")] for s in re.findall(
    r"coefficients=([^\n]+)", args.coefficients.read_text())]
quant = [[int(v) for v in s.split(",")] for s in re.findall(
    r"quant \d+ values=([^\n]+)", args.quantization.read_text())]
assert len(blocks) == 5520 and len(quant) == 6
offset = 0
cos = [[(1 / math.sqrt(2) if u == 0 else 1) * math.cos((2*x+1)*u*math.pi/16)
        for u in range(8)] for x in range(8)]
for p, (w, h) in enumerate(((640,368),(320,184),(320,184))):
    worst = []
    for y in range(h):
        for x in range(w):
            index = ((y//4)*(w//8)+x//8)*32+(y%4)*8+x%8
            a,b = gx[offset+index],native[offset+y*w+x]
            worst.append((abs(a-b),x,y,a,b))
    for error,x,y,a,b in sorted(worst,reverse=True)[:4]:
        bx,by = x//8,y//8
        if p == 0:
            component = (by%2)*2+bx%2
            block = ((by//2)*40+bx//2)*6+component
        else:
            component = 3+p
            block = (by*40+bx)*6+component
        q = quant[component]
        theoretical = 128 + sum(blocks[block][v*8+u]*q[v*8+u]*cos[x%8][u]*cos[y%8][v]
                                for v in range(8) for u in range(8))/4
        pixel = min(255,max(0,math.floor(theoretical)))
        print(f"plane={p} x={x} y={y} block={block} original={a} native={b} "
              f"cosine={theoretical:.6f} floor={pixel} original_error={a-pixel} native_error={b-pixel}")
    offset += w*h
