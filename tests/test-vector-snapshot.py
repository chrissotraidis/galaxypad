from pathlib import Path
import runpy
import struct
root=Path(__file__).resolve().parents[1]
compare=runpy.run_path(str(root/'scripts/compare-vector-snapshot.py'))['compare']
dol=(root/'generated/extracted/run1/sys/main.dol').read_bytes()
lines=[]
for base in [0x500,0x800,0x900,0xc00]:
    data=bytearray(256)
    if base==0xc00: data[:28]=dol[0x4a60c8:0x4a60c8+28]
    else:
        data[:152]=dol[0x49d1e0:0x49d1e0+152]
        struct.pack_into('>I',data,0x68,0x38600000|{0x500:4,0x800:7,0x900:8}[base])
    lines.append(f'[galaxypad-vector-ram] base={base:08x} bytes={data.hex()}\n')
log=''.join(lines)
assert compare(log,dol)['all_match']
bad=log.replace('7c9043a6','60000000',1)
assert not compare(bad,dol)['all_match']
for bad in ('',log+lines[0],''.join(lines[:-1])):
    try: compare(bad,dol)
    except ValueError: pass
    else: raise AssertionError('invalid capture accepted')
print('Vector comparison: expected exception patches, mismatch and incomplete/duplicate rejection pass')
