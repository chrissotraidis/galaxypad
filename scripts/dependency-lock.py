#!/usr/bin/env python3
"""Read and verify GalaxyPad's committed dependency pins without changing sources."""
import argparse
import json
from pathlib import Path
import subprocess


def pins(root):
    lock = json.loads((root / 'config/dependencies.lock.json').read_text())
    repositories = lock['repositories']
    if repositories['recompCore']['revision'] != lock['vendorRevisions']['modernGekkoRecompCoreDolphin']:
        raise ValueError('RecompCore revision and vendor alias disagree')
    return {
        'modernGekko': (root / 'ref/ModernGekko', repositories['modernGekko']['revision']),
        'recompCore': (root / 'ref/ModernGekko/vendor/dolphin',
                       lock['vendorRevisions']['modernGekkoRecompCoreDolphin']),
        'dolRecomp': (root / 'ref/ModernGekko/vendor/dolphin/DolRecomp',
                      repositories['dolRecomp']['revision']),
    }


def verify(root):
    locked = pins(root)
    repositories = json.loads((root / 'config/dependencies.lock.json').read_text())['repositories']
    parents = {'modernGekko': (root, 'ref/ModernGekko'),
               'recompCore': (root / 'ref/ModernGekko', 'vendor/dolphin'),
               'dolRecomp': (root / 'ref/ModernGekko/vendor/dolphin', 'DolRecomp')}
    for name, (checkout, expected) in locked.items():
        parent, relative = parents[name]
        modules = parent / '.gitmodules'
        if not modules.is_file():
            raise ValueError(f'{name}: parent .gitmodules is missing')
        paths = subprocess.check_output(['git', 'config', '--file', str(modules),
                                         '--get-regexp', r'^submodule\..*\.path$'], text=True)
        matches = [line.partition(' ')[0] for line in paths.splitlines()
                   if line.partition(' ')[2] == relative]
        if len(matches) != 1:
            raise ValueError(f'{name}: .gitmodules must declare exactly one path {relative}')
        url = subprocess.check_output(['git', 'config', '--file', str(modules),
                                       '--get', matches[0][:-4] + 'url'], text=True).strip()
        if url != repositories[name]['url']:
            raise ValueError(f'{name}: .gitmodules URL does not match the dependency lock')
        entry = subprocess.check_output(['git', '-C', str(parent), 'ls-files', '--stage', '--', relative], text=True)
        fields = entry.split()
        if len(fields) != 4 or fields[:3] != ['160000', expected, '0']:
            raise ValueError(f'{name}: parent gitlink does not match locked revision {expected}')
        actual = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != expected:
            raise ValueError(f'{name}: expected {expected}, found {actual}; run bootstrap-dependencies.sh')
        # Include nested submodule dirtiness and gitlink changes. Ignored build
        # products are not source changes and are not a build-provenance claim.
        result = subprocess.run(['git', '-C', str(checkout), 'diff', '--quiet', 'HEAD',
                                 '--ignore-submodules=none'])
        if result.returncode:
            raise ValueError(f'{name}: tracked sources differ from the pinned commit')
        extra = subprocess.check_output(['git', '-C', str(checkout), 'ls-files',
                                         '--others', '--exclude-standard', '-z'])
        if extra:
            raise ValueError(f'{name}: unexpected nonignored untracked files')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--revision', choices=['modernGekko', 'recompCore', 'dolRecomp'])
    args = parser.parse_args()
    if args.revision:
        print(pins(args.root)[args.revision][1])
    else:
        try:
            verify(args.root)
        except (ValueError, subprocess.CalledProcessError) as error:
            parser.exit(1, str(error) + '\n')
        print('Pinned dependency revisions and tracked/nonignored source cleanliness verified.')


if __name__ == '__main__':
    main()
