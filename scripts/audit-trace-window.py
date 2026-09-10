#!/usr/bin/env python3
"""Inspect retained Instruments timing without exposing captured environment data."""
import argparse
import json
import math
import plistlib
from pathlib import Path


def audit(archive):
    objects = archive['$objects']
    keys = ('_rawStartTime', '_rawEndTime', '_rawWindowStartTime', '_rawDuration')
    runs = []
    for obj in objects:
        if not isinstance(obj, dict) or not all(key in obj for key in keys):
            continue
        values = [objects[obj[k].data] if isinstance(obj[k], plistlib.UID)
                  else obj[k] for k in keys]
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in values):
            raise ValueError('Invalid trace timing values')
        start, end, window, duration = values
        if not start <= window < end or duration <= 0:
            raise ValueError('Invalid retained window ordering')
        if abs(end-window-duration) > .001:
            raise ValueError('Retained duration disagrees with window endpoints')
        runs.append(dict(recording_start_unix=start, recording_end_unix=end,
                         retained_start_unix=window, retained_seconds=duration,
                         recording_seconds=end-start,
                         discarded_prefix_seconds=window-start))
    if not runs:
        raise ValueError('No recognized retained-window metadata; do not infer timeline')
    return runs


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace', type=Path)
    args = parser.parse_args()
    with (args.trace/'form.template').open('rb') as stream:
        print(json.dumps(audit(plistlib.load(stream)), indent=2))
