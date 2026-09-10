#!/usr/bin/env python3
"""Send a leased full input snapshot to the opt-in Simulator host, then release.

Launch app with -GalaxyPadDevInputFile /absolute/path/to/input.json first.
This is host input automation, not UIKit touch or physical-controller evidence.
"""
import argparse
import json
import os
from pathlib import Path
import tempfile
import time


def publish(path, snapshot):
    now = time.time()
    value = dict(snapshot, issued=now, expires=now + 0.5)
    # Atomic replacement prevents the app from reading a partially written hold.
    descriptor, temporary = tempfile.mkstemp(prefix=".galaxypad-input-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as output:
            json.dump(value, output, allow_nan=False)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("snapshot", help='JSON full snapshot, e.g. {"buttons":3}')
    parser.add_argument("--seconds", type=float, default=0.5)
    parser.add_argument("--aim-first", type=float, default=0,
                        help="settle pointer with buttons released before the action")
    args = parser.parse_args()
    if not 0.1 <= args.seconds <= 30:
        parser.error("seconds must be between 0.1 and 30")
    if not 0 <= args.aim_first <= 5:
        parser.error("aim-first must be between 0 and 5")
    snapshot = json.loads(args.snapshot)
    if not isinstance(snapshot, dict):
        parser.error("snapshot must be an object")
    action_start = time.monotonic() + args.aim_first
    deadline = action_start + args.seconds
    try:
        while time.monotonic() < deadline:
            publish(args.path, dict(snapshot, buttons=0) if time.monotonic() < action_start else snapshot)
            time.sleep(0.1)
    finally:
        publish(args.path, {})


if __name__ == "__main__":
    main()
