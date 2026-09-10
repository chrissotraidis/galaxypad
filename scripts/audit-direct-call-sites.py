#!/usr/bin/env python3
"""Census generated direct BL sites; static counts are not execution frequencies."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


def classify(source):
    result = Counter()
    next_instruction = re.compile(r'\n(?:label_[0-9A-Fa-f]+:|\s*// [0-9A-Fa-f]{8}:)')
    for match in re.finditer(r'// ([0-9A-Fa-f]{8}): bl\s+0x([0-9A-Fa-f]{8})\s*\n', source):
        boundary = next_instruction.search(source, match.end())
        body = source[match.end():boundary.start()] if boundary else source[match.end():]
        pc, target = (int(value, 16) for value in match.groups())
        continuation = (pc + 4) & 0xffffffff
        if not re.search(rf'ctx->lr\s*=\s*0x{continuation:08X}u;', body, re.I):
            raise ValueError(f'Unrecognized link-register assignment at {pc:08x}')
        if re.search(r'func_[0-9a-f]+\(ctx\)', body, re.I):
            kind = 'direct_cross_chunk'
        elif re.search(rf'goto label_{target:08X};', body, re.I):
            kind = 'local_goto'
        elif (re.search(rf'ctx->pc\s*=\s*0x{target:08X}u;', body, re.I)
              and re.search(r'\breturn;', body)):
            kind = 'return_to_chassis'
        else:
            raise ValueError(f'Unrecognized BL shape at {pc:08x}')
        result[kind] += 1
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('generated_directory', type=Path)
    args = parser.parse_args()
    files = sorted((args.generated_directory / 'chunks').glob('chunk_*.c'))
    if not files:
        parser.error('No generated chunk C files found')
    totals = Counter()
    manifest = hashlib.sha256()
    for path in files:
        raw = path.read_bytes()
        manifest.update(path.name.encode() + b'\0' + hashlib.sha256(raw).digest())
        totals.update(classify(raw.decode()))
    print(json.dumps(dict(chunk_files=len(files), source_manifest_sha256=manifest.hexdigest(),
                          direct_bl_sites=sum(totals.values()), shapes=dict(totals),
                          caveat='Static direct BL sites only. Not indirect calls, dynamic counts, '
                                 'cost attribution, or proof of guarded-call eligibility.'), indent=2))


if __name__ == '__main__':
    main()
