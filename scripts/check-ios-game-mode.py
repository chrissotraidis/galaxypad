#!/usr/bin/env python3
"""Validate Game Mode opt-in metadata; this cannot detect active system state."""
import argparse
import plistlib
from pathlib import Path


def validate(info):
    for key in ('LSSupportsGameMode', 'GCSupportsGameMode', 'UIRequiresFullScreen'):
        if info.get(key) is not True:
            raise ValueError(f'{key} must be a Boolean true in the packaged app')
    if info.get('LSApplicationCategoryType') != 'public.app-category.adventure-games':
        raise ValueError('GalaxyPad game category is missing or incorrect')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plist', type=Path)
    args = parser.parse_args()
    try:
        validate(plistlib.loads(args.plist.read_bytes()))
    except (ValueError, OSError) as error:
        parser.exit(1, f'Game Mode metadata: {error}\n')
    print('Game Mode opt-in metadata verified; active system state is not inferred.')
