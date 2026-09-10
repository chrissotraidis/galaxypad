#!/usr/bin/env python3
"""Locate SDK-shaped templates in the exact DOL; no live-byte equivalence claim."""
from pathlib import Path
import hashlib
import json
import struct

root=Path(__file__).resolve().parents[1]
dol=(root/'generated/extracted/run1/sys/main.dol').read_bytes()
assert hashlib.sha256(dol).hexdigest()=='2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09'
word=lambda offset: struct.unpack_from('>I',dol,offset)[0]
def locate(words):
    pattern=struct.pack('>'+str(len(words))+'I',*words)
    matches=[]
    for section in range(7):
        offset,address,size=word(section*4),word(0x48+section*4),word(0x90+section*4)
        for pos in range(offset,offset+size-len(pattern)+1,4):
            if dol[pos:pos+len(pattern)]==pattern:
                matches.append((pos,address+pos-offset))
    assert len(matches)==1, 'Template must be unique in exact DOL text'
    return matches[0]
system=[0x7d30faa6,0x612a0008,0x7d50fba6,0x4c00012c,0x7c0004ac,0x7d30fba6,0x4c000064]
generic=[0x7c9043a6,0x808000c0,0x9064000c,0x7c7042a6,0x90640010,
         0x90a40014,0xa06401a2,0x60630002,0xb06401a2,0x7c600026,
         0x90640080,0x7c6802a6,0x90640084,0x7c6902a6,0x90640088,
         0x7c6102a6,0x9064008c,0x7c7a02a6,0x90640198,0x7c7b02a6,
         0x9064019c,0x7c651b78,0x60000000,0x7c6000a6,0x60630030,
         0x7c7b03a6,0x38600000,0x808000d4,0x54a507bd,0x40820014,
         0x3ca0804a,0x38a51d3c,0x7cba03a6,0x4c000064,
         0x546515ba,0x80a53000,0x7cba03a6,0x4c000064]
found={name:dict(file_offset=hex(loc[0]),address=hex(loc[1]),bytes=len(words)*4)
       for name,words in [('system_call',system),('generic_exception',generic)]
       for loc in [locate(words)]}
census=json.loads((root/'generated/fallback-pcs-r755.json').read_text())
assert census['dropped']==0
sites={int(s['pc'],16):s['count'] for s in census['sites'] if s['path']=='uncovered'}
vectors=[]
for base,name,offsets in [(0xc00,'system_call',list(range(0,28,4))),
    (0x500,'external_interrupt',list(range(0,0x78,4))+list(range(0x88,0x98,4))),
    (0x800,'floating_point_unavailable',list(range(0,0x78,4))+list(range(0x88,0x98,4))),
    (0x900,'decrementer',list(range(0,0x78,4))+list(range(0x88,0x98,4)))]:
    observed={pc-base:count for pc,count in sites.items() if base<=pc<base+0x100}
    assert set(observed)==set(offsets)
    assert len(set(observed.values()))==1
    vectors.append(dict(base=hex(base),kind=name,entries=observed[0],
                        instructions_per_entry=len(offsets),steps=sum(observed.values())))
print(json.dumps(dict(dol_sha256=hashlib.sha256(dol).hexdigest(),templates=found,
    observed_vectors=vectors,
    caveat='DOL templates and observed PC paths agree with SDK shape. Runtime vector bytes '
           'and patched exception numbers are not captured; not permission to redirect '
           'execution or skip HID0, MMU, exception, cache or cycle effects.'),indent=2))
