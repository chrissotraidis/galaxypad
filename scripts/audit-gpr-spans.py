#!/usr/bin/env python3
"""Read-only census of strictly recognized, callback-free GPR spans.

Reuses the existing integer-body recognizer. External labels remain entries;
this is not permission to remove them or a dynamic performance estimate.
"""
import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

spec = importlib.util.spec_from_file_location('gaps', Path(__file__).with_name('audit-fprf-gaps.py'))
gaps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gaps)


def spans(text):
    start = text.find('\nvoid func_')
    if start < 0:
        return []
    text = text[start:]
    labels = list(gaps.adjacent.LABEL.finditer(text))
    result, pending = [], []
    for index, label in enumerate(labels):
        address = int(label[1], 16)
        end = labels[index + 1].start() if index + 1 < len(labels) else len(text)
        operation = gaps.integer_gap(text[label.end():end], address)
        if pending and (not operation or address != pending[-1] + 4):
            result.append(pending)
            pending = []
        if operation:
            pending.append(address)
    if pending:
        result.append(pending)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('generated', type=Path)
    args = parser.parse_args()
    files = sorted((args.generated / 'chunks').glob('chunk_*.c'))
    if not files:
        parser.error('No generated chunks')
    histogram, records = Counter(), []
    for path in files:
        raw = path.read_bytes()
        found = spans(raw.decode())
        histogram.update(map(len, found))
        long = [dict(start=f'{s[0]:08X}', end=f'{s[-1]:08X}', instructions=len(s))
                for s in found if len(s) >= 8]
        if long:
            records.append(dict(file=path.name, sha256=hashlib.sha256(raw).hexdigest(), spans=long))
    print(json.dumps(dict(chunks=len(files), length_histogram=dict(sorted(histogram.items())),
                         recognized_instructions=sum(k*v for k, v in histogram.items()),
                         instructions_in_spans_at_least_8=sum(k*v for k, v in histogram.items() if k >= 8),
                         files=records,
                         caveat='Conservative static census; no dynamic coverage, liveness or speed proof.'), indent=2))


if __name__ == '__main__':
    main()
