#!/usr/bin/env python3
"""Prepare a private old-PGO ThinLTO layout experiment without compiling/linking.

The output command reuses the verified control build's existing objects and
changes only the output location and LLVM extended-TSP block-placement option.
No command is executed except Ninja's read-only command inventory. Execute the
JSON argument vector explicitly only when a full-module link is authorized.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'generated/build/ios-simulator-pgo-use-20260912'
PROFILE = ROOT / 'generated/runtime/ipad-iteration-1/pgo-profile-route-20260912/current-input.profdata'
BASELINE_SHA = '90e24dfb4e96597686b8fccf09bb55efdcbd7d059dd3ff710a9f32fab26f353f'
PROFILE_SHA = '784f47e4904a36319b7805cd7807091d1d486ccc4cacc09f4785636d3949ca54'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True,
                        help='New private directory for command and future module')
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        parser.error('Output directory already exists; preserve prior evidence')
    baseline = BUILD / 'gRMGE01_recomp.dylib'
    if sha(baseline) != BASELINE_SHA or sha(PROFILE) != PROFILE_SHA:
        parser.error('Control module or old PGO profile changed')
    lines = subprocess.check_output(
        ['ninja', '-C', str(BUILD), '-t', 'commands', 'gRMGE01_recomp.dylib'],
        text=True).splitlines()
    argv = shlex.split(lines[-1])
    if argv[:2] != [':', '&&'] or argv[-2:] != ['&&', ':']:
        parser.error('Unexpected CMake link-command wrappers')
    argv = argv[2:-2]
    if '&&' in argv or '-dynamiclib' not in argv or '-flto=thin' not in argv:
        parser.error('Unexpected link command or missing ThinLTO')
    profiles = {item for item in argv if item.startswith('-fprofile-instr-use=')}
    if profiles != {'-fprofile-instr-use=' + str(PROFILE)}:
        parser.error('Link profile differs from verified old profile')
    if argv[argv.index('-o') + 1] != 'gRMGE01_recomp.dylib':
        parser.error('Unexpected original module destination')
    objects = [(BUILD / item).resolve() for item in argv if item.endswith('.o')]
    if len(objects) < 1322 or any(not p.is_file() or BUILD not in p.parents for p in objects):
        parser.error('Expected existing module object set is incomplete')
    argv[argv.index('-o') + 1] = str(output / 'gRMGE01_recomp.dylib')
    argv.insert(argv.index('-dynamiclib') + 1,
                '-Wl,-mllvm,-enable-ext-tsp-block-placement')
    output.mkdir(parents=True)
    # Preserve sizes/mtime evidence so an executor can detect concurrent rebuilds.
    inputs = [{'path': str(p), 'bytes': p.stat().st_size,
               'mtime_ns': p.stat().st_mtime_ns} for p in objects]
    manifest = {'cwd': str(BUILD), 'argv': argv, 'baseline_sha256': BASELINE_SHA,
                'profile_sha256': PROFILE_SHA, 'objects': inputs,
                'status': 'prepared; module link has not run',
                'scope': 'old profile and source unchanged; final ThinLTO block layout only'}
    (output / 'relink.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Prepared {len(objects)} existing objects; no compile or link: {output / "relink.json"}')


if __name__ == '__main__':
    main()
