#!/usr/bin/env python3
"""Rank guest instruction entries from a retained, source-matched coverage export.

Counts measure entry attempts, including exceptions, not completed instructions
or CPU time. A helper mentioned within an entry may execute conditionally.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('coverage', type=Path)
args = parser.parse_args()
data = json.loads(args.coverage.read_text())
source = Path(data['filenames'][0])
raw = source.read_bytes()
if hashlib.sha256(raw).hexdigest() != data['chunk_sha256']:
    raise SystemExit('Source changed since coverage export')
text = raw.decode()
name = data.get('function_name', 'func_' + source.stem.rsplit('_', 1)[1])
text = text.split('void ' + name + '(CPUState* ctx) {', 1)[1]
blocks = dict(re.findall(r'^(label_[0-9A-F]{8}:)\n(.*?)(?=^label_|\Z)',
                         text, re.M | re.S))
counts, sites, unknown = Counter(), [], []
for entry in data['instruction_entries']:
    label = entry['label']
    count = entry['count']
    if count is None:
        unknown.append(label)
        continue
    block = blocks[label]
    instruction = re.search(r'// ([0-9A-F]{8}): ([^\n]+)', block)
    if not instruction and re.search(r'loop_[0-9A-F]{8}\(ctx\)', block):
        unknown.append(label + ' outlined helper; internal execution excluded')
        continue
    if not instruction or label != 'label_' + instruction[1] + ':':
        raise SystemExit('Instruction identity mismatch: ' + label)
    mnemonic = instruction[2].split()[0]
    counts[mnemonic] += count
    sites.append(dict(pc=instruction[1], instruction=instruction[2], entries=count))
print(json.dumps(dict(source=str(source), source_sha256=data['chunk_sha256'],
                      profile_sha256=data['profile_sha256'],
                      known_entry_attempts=sum(counts.values()), unknown=unknown,
                      by_mnemonic=dict(counts.most_common()),
                      hottest_sites=sorted(sites, key=lambda row: row['entries'],
                                           reverse=True)[:40],
                      caveat=__doc__.strip()), indent=2))
