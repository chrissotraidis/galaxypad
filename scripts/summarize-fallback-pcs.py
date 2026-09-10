#!/usr/bin/env python3
"""Validate one shutdown census; counts are frequency, not interpreter CPU cost."""
import argparse
import json
from pathlib import Path
import re

SUMMARY = re.compile(r'\[galaxypad-fallback-pcs\] total=(\d+) dropped=(\d+)')
SITE = re.compile(r'\[galaxypad-fallback-pc\] pc=([0-9a-fA-F]{8}) path=(\d+) count=(\d+)')
PATHS = {0: 'uncovered', 1: 'forced', 2: 'instruction_hook'}


def summarize(text):
    summaries = list(SUMMARY.finditer(text))
    if len(summaries) != 1:
        raise ValueError('Expected exactly one shutdown census; missing or mixed sessions')
    summary = summaries[0]
    total, dropped = map(int, summary.groups())
    entries, seen = [], set()
    for match in SITE.finditer(text):
        pc, path, count = int(match[1], 16), int(match[2]), int(match[3])
        if match.start() < summary.end() or path not in PATHS or count == 0:
            raise ValueError('Invalid or misplaced census entry')
        if (pc, path) in seen:
            raise ValueError('Duplicate PC/path key')
        seen.add((pc, path))
        entries.append(dict(pc=f'{pc:08x}', path=PATHS[path], count=count))
    recorded = sum(entry['count'] for entry in entries)
    if recorded + dropped != total or len(entries) > 32768:
        raise ValueError('Incomplete or inconsistent census accounting')
    # A final normal shutdown line follows the census in the actual emitter.
    if '[staticrecomp] shutdown:' not in text[summary.end():]:
        raise ValueError('Missing following core shutdown record')
    return dict(total=total, recorded=recorded, dropped=dropped,
                complete_pc_coverage=dropped == 0,
                paths={path: sum(e['count'] for e in entries if e['path'] == path)
                       for path in PATHS.values()},
                sites=sorted(entries, key=lambda e: (-e['count'], e['pc'], e['path'])),
                caveat='Whole-session step frequencies, not CPU time or matched gameplay. '
                       'PC aliases remain distinct; no vector or relocation attribution inferred.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(summarize(args.log.read_text()), indent=2))
    except ValueError as error:
        parser.exit(2, f'{error}\n')
