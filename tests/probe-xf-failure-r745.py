"""Decode captured R742 failure bytes, without accepting or repairing the stream."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
log = (root/'generated/ios-runtime-r742.log').read_text()
match = re.search(r'cmd2 = 0x00611600; run_offset=(\d+) available=(\d+) '
                  r'preceding_bytes=\[([^]]*)\] command_bytes=\[([^]]*)\]', log)
assert match, 'Exact failure capture missing'
data = bytes.fromhex(match[4])
assert int(match[1]) == 0 and int(match[2]) == 34 and not match[3]
assert len(data) == 32 and data[:2] == bytes.fromhex('10 00')
header = int.from_bytes(data[1:5], 'big')
assert header == 0x00611600 and header >> 16 == 97
bp = []
for offset in range(2, 32, 5):
    command = data[offset:offset+5]
    assert command[0] == 0x61
    bp.append((command[1], int.from_bytes(command[2:], 'big')))
assert bp == [(register, 0) for register in range(0x16, 0x1c)]
print('Captured XF length field=97 (invalid; maximum15).')
print('After two leading bytes: six complete BP writes, registers16..1b, data0.')
print('34 available = 2 + 32, consistent with residual bytes plus a FIFO burst,')
print('but this capture does not identify the producer or prove byte loss.')
print('Do not skip the prefix, mask the assertion, or call this a valid stream.')
