#!/usr/bin/env python3
"""Classify observed PCs against exact image headers, not inferred relocation."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

def text_ranges(dol):
    if len(dol) < 0x100:
        raise ValueError('Truncated DOL header')
    word = lambda offset: struct.unpack_from('>I', dol, offset)[0]
    ranges = []
    for index in range(7):
        offset, address, size = word(index*4), word(0x48+index*4), word(0x90+index*4)
        if not size:
            continue
        if offset+size > len(dol) or address+size > 2**32:
            raise ValueError('Invalid DOL text extent')
        ranges.append((address, address+size))
    return ranges

def classify(pc, ranges, loader_end):
    if any(start <= pc < end for start,end in ranges):
        return 'dol_text'
    if 0x81200000 <= pc < loader_end:
        return 'initial_apploader_range'
    if pc < 0x4000:
        return 'low_memory_unattributed'
    return 'outside_initial_text_ranges'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('census', type=Path)
    parser.add_argument('sys_directory', type=Path)
    args = parser.parse_args()
    census = json.loads(args.census.read_text())
    dol = (args.sys_directory/'main.dol').read_bytes()
    loader = (args.sys_directory/'apploader.img').read_bytes()
    if len(loader) < 32:
        raise ValueError('Truncated apploader header')
    entry,size,trailer = struct.unpack_from('>III', loader, 0x10)
    if 32+size+trailer > len(loader):
        raise ValueError('Truncated apploader body')
    ranges = text_ranges(dol)
    counts = {}
    for site in census['sites']:
        category = classify(int(site['pc'],16), ranges, 0x81200000+size+trailer)
        counts[category] = counts.get(category,0)+site['count']
    print(json.dumps(dict(dol_sha256=hashlib.sha256(dol).hexdigest(),
        apploader_sha256=hashlib.sha256(loader).hexdigest(),
        dol_text_ranges=[[hex(a),hex(b)] for a,b in ranges],
        apploader_entry=hex(entry),
        initial_apploader_range=['0x81200000',hex(0x81200000+size+trailer)],
        recorded_counts=counts, dropped=census['dropped'],
        caveat='Exact virtual ranges only. No alias, relocation, vector function or CPU-cost '
               'attribution. Capture phase must be established by external scene evidence.'),indent=2))
