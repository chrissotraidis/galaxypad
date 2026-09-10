#!/usr/bin/env python3
"""Compare isolated AC(1,0)=16 to SDK quarter-path algebra and cosine IDCT."""
import math
from pathlib import Path
import struct
import sys
def f(x):
    return struct.unpack(">f",struct.pack(">f",x))[0]
# PrologueA first-block DQT[1]=3, independently captured in R660/R661.
a=f(16*f(3*f(1.387039845)))
c4,c2,cs=map(f,(1.414213562,1.847759065,1.082392200))
t2=f(a*c2-a)
t3=f(a*c4-t2)
t4=f(t3-a*f(c2-cs))
# SDK quarter path stores odd middle outputs in this order.
sdk=[a,t2,t3,t4,-t4,-t3,-t2,-a]
sdk=[math.floor(f(f(x+1024)*0.125)) for x in sdk]
ideal=[math.floor(128+48*math.cos((2*x+1)*math.pi/16)/(4*math.sqrt(2))) for x in range(8)]
actual=list(Path(sys.argv[1]).read_bytes()[:8])
print("actual",actual,"SDK algebra",sdk,"cosine",ideal)
assert actual==sdk
assert actual==ideal[:3]+[ideal[4],ideal[3]]+ideal[5:]
print("isolated middle-pixel reversal reproduced by SDK quarter-path algebra")
