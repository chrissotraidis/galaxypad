from pathlib import Path
import runpy
import struct
api = runpy.run_path(str(Path(__file__).resolve().parents[1]/'scripts/map-fallback-image-ranges.py'))
parse, classify = api['text_ranges'], api['classify']
dol = bytearray(0x104)
for offset,value in [(0,0x100),(0x48,0x80004000),(0x90,4)]:
    struct.pack_into('>I',dol,offset,value)
ranges = parse(dol)
assert ranges == [(0x80004000,0x80004004)]
assert classify(0x80004000,ranges,0x81201000)=='dol_text'
assert classify(0x80004004,ranges,0x81201000)=='outside_initial_text_ranges'
assert classify(0x81200000,ranges,0x81201000)=='initial_apploader_range'
assert classify(0x81201000,ranges,0x81201000)=='outside_initial_text_ranges'
assert classify(0xc00,ranges,0x81201000)=='low_memory_unattributed'
assert classify(0x91f0cb14,ranges,0x81201000)=='outside_initial_text_ranges'
for bad in (dol[:20],dol[:-1]):
    try: parse(bad)
    except ValueError: pass
    else: raise AssertionError('accepted truncated image')
print('Fallback image ranges: exact boundaries, unknowns and truncation checks pass')
