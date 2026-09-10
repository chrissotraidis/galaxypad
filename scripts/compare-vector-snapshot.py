#!/usr/bin/env python3
"""Compare one physical-RAM vector snapshot to exact RMGE01 DOL templates."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct

def compare(log, dol):
    if hashlib.sha256(dol).hexdigest() != '2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09':
        raise ValueError('Unsupported DOL identity')
    snapshots={}
    for match in re.finditer(r'\[galaxypad-vector-ram\] base=([0-9a-f]{8}) bytes=([0-9a-f]+)',log):
        base=int(match[1],16); data=bytes.fromhex(match[2])
        if base in snapshots or len(data)!=256:
            raise ValueError('Duplicate or truncated vector snapshot')
        snapshots[base]=data
    if set(snapshots)!={0x500,0x800,0x900,0xc00}:
        raise ValueError('Expected one snapshot of all four vector regions')
    rows=[]
    for base in sorted(snapshots):
        if base==0xc00:
            expected=dol[0x4a60c8:0x4a60c8+28]
        else:
            expected=bytearray(dol[0x49d1e0:0x49d1e0+152])
            struct.pack_into('>I',expected,0x68,0x38600000|{0x500:4,0x800:7,0x900:8}[base])
        actual=snapshots[base][:len(expected)]
        differences=[dict(offset=hex(i),expected=expected[i:i+4].hex(),actual=actual[i:i+4].hex())
                     for i in range(0,len(expected),4) if expected[i:i+4]!=actual[i:i+4]]
        rows.append(dict(base=hex(base),compared_bytes=len(expected),matches=not differences,
                         differences=differences,ram_sha256=hashlib.sha256(snapshots[base]).hexdigest()))
    return dict(vectors=rows,all_match=all(row['matches'] for row in rows),
                caveat='Physical RAM at capture start, not instruction-cache bytes or later '
                       'immutability. Match alone does not authorize native execution.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log',type=Path);parser.add_argument('dol',type=Path)
    args=parser.parse_args()
    print(json.dumps(compare(args.log.read_text(),args.dol.read_bytes()),indent=2))
