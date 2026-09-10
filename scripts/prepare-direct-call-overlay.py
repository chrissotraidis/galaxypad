#!/usr/bin/env python3
"""Prepare all eligible caller chunks in a new diagnostic-only overlay."""
import argparse
from bisect import bisect_right
import hashlib
import importlib.util
import json
from pathlib import Path
import re

spec = importlib.util.spec_from_file_location('chunk', Path(__file__).with_name('prepare-direct-call-chunk.py'))
chunk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chunk)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('generated', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    generated = args.generated.resolve(strict=True)
    output = args.output.resolve()
    if output.exists() or output.is_relative_to(generated):
        parser.error('Output must be a new directory outside the generated tree')
    files = sorted((generated / 'chunks').glob('chunk_*.c'),
                   key=lambda p: int(p.stem.rsplit('_', 1)[1], 16))
    if not files:
        parser.error('No generated chunks')
    starts = [int(p.stem.rsplit('_', 1)[1], 16) for p in files]
    entries = []
    hashes = []
    for path in files:
        raw = path.read_bytes()
        hashes.append(hashlib.sha256(raw).hexdigest())
        entries.append(set(dict(chunk.ENTRY.findall(raw.decode()))))
    output.mkdir(parents=True, exist_ok=False)
    transfer = Path(__file__).resolve().parents[1] / 'apple/experiments/guarded-direct-calls/transfer.h'
    records = []
    for index, path in enumerate(files):
        def resolve(target):
            address = int(target, 16)
            if not 0x80000000 <= address < 0x81800000:
                return None
            dest = bisect_right(starts, address) - 1
            if dest < 0 or dest == index or target not in entries[dest]:
                return None
            return f'func_{starts[dest]:08X}'

        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != hashes[index]:
            raise RuntimeError(f'Source changed during preparation: {path}')
        text, count = chunk.transform(raw.decode(), resolve)
        record = dict(source=str(path), source_sha256=hashes[index], sites=count)
        if count:
            include = re.search(r'^#include "\.\./([^"/]+\.h)"$', text, re.M)
            if not include:
                raise ValueError(f'Missing generated header: {path}')
            header = (generated / include.group(1)).resolve(strict=True)
            text = text.replace(include.group(0),
                                f'#include "{header}"\n#include "{transfer}"', 1)
            destination = output / path.name
            with destination.open('x') as stream:
                stream.write(text)
            record.update(override=str(destination),
                          override_sha256=hashlib.sha256(text.encode()).hexdigest())
        records.append(record)
    report = dict(generated=str(generated), chunks=len(files),
                  changed_chunks=sum(bool(r['sites']) for r in records),
                  guarded_sites=sum(r['sites'] for r in records), files=records,
                  caveat='Static eligible sites, not dynamic coverage or speedup.')
    # Written last: absent manifest means preparation did not complete.
    with (output / 'manifest.json').open('x') as stream:
        json.dump(report, stream, indent=2)
    print(json.dumps({k:v for k,v in report.items() if k != 'files'}, indent=2))


if __name__ == '__main__':
    main()
