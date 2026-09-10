"""Only parsed read-only LINKEDIT virtual reservation may differ after unsigning."""
import ast
from pathlib import Path
import struct
source=Path(__file__).resolve().parents[1]/'scripts/build-thread-work-host.py'
tree=ast.parse(source.read_text())
function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='linkedit_reservation')
scope={'struct':struct}
exec(compile(ast.Module(body=[function],type_ignores=[]),str(source),'exec'),scope)
normalize=scope['linkedit_reservation']
def fixture(reservation):
    b=bytearray(128)
    struct.pack_into('<I',b,0,0xfeedfacf)
    struct.pack_into('<II',b,16,1,72)
    struct.pack_into('<II',b,32,0x19,72)
    b[40:56]=b'__LINKEDIT'+bytes(6)
    struct.pack_into('<Q',b,64,reservation)
    struct.pack_into('<Q',b,80,100)
    struct.pack_into('<III',b,88,1,1,0)
    return b
a=fixture(16384); b=fixture(32768)
assert normalize(a)[0]==normalize(b)[0]
b[-1]=1
assert normalize(a)[0]!=normalize(b)[0] # No content bytes ignored.
for offset,value in [(64,99),(64,16385),(88,3),(92,3),(96,1),(36,71)]:
    bad=fixture(16384)
    struct.pack_into('<I',bad,offset,value)
    try: normalize(bad)
    except AssertionError: pass
    else: raise AssertionError('Malformed/writable/sectioned LINKEDIT accepted')
print('LINKEDIT comparison permits only bounded read-only virtual reservation; content changes remain unequal')
a=fixture(16384)+bytes(16)
struct.pack_into('<II',a,16,2,96)
struct.pack_into('<II',a,104,0x1b,24)
b=bytearray(a); b[112:128]=bytes(range(16))
assert normalize(a)[0]!=normalize(b)[0]
assert normalize(a,True)[0]==normalize(b,True)[0]
b[-1]=1
assert normalize(a,True)[0]!=normalize(b,True)[0]
print('Native UUID option affects only one parsed LC_UUID; all other content remains compared')
