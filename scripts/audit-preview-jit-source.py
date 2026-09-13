#!/usr/bin/env python3
"""Check the published Preview 1 source archive, without extracting or running it.

This is source identity/contract evidence, not a binary or gameplay test.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile

EXPECTED = '5996996e4e62491cb0c2cdc18b5c67afab3e693e7df75467a787569eb081c3f1'
CHECKS = {
    'JitArm64/JitAsm.cpp': [
        'IsStaticRecompFallback() && JitArm64StaticRecompEnabled()',
        'ABI_CallFunction(&StaticRecompShouldYieldAt, DISPATCHER_PC);',
        'STR(IndexType::Unsigned, DISPATCHER_PC, PPC_REG, PPCSTATE_OFF(pc));',
    ],
    'JitArm64/JitArm64_Cache.cpp': [
        '!(IsStaticRecompFallback() && JitArm64StaticRecompEnabled())',
    ],
    'StaticRecomp/StaticRecompCore.cpp': [
        '#if defined(_M_ARM_64) && !defined(__IPHONE_OS_VERSION_MIN_REQUIRED)',
    ],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    with args.archive.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if digest != EXPECTED:
        parser.error(f'Not the published Preview 1 source archive: SHA-256 {digest}')
    evidence = {}
    with tarfile.open(args.archive, 'r:gz') as archive:
        for suffix, markers in CHECKS.items():
            matches = [m for m in archive.getmembers() if m.isfile()
                       and '/macos-runtime/' in m.name and m.name.endswith('/' + suffix)]
            if len(matches) != 1:
                parser.error(f'Expected exactly one source file: {suffix}')
            data = archive.extractfile(matches[0]).read()
            source = data.decode('utf-8')
            missing = [marker for marker in markers if marker not in source]
            if missing:
                parser.error(f'Missing source contract in {suffix}: {missing}')
            evidence[suffix] = {'sha256': hashlib.sha256(data).hexdigest(),
                                'markers_present': len(markers)}
    print(json.dumps({'archive_sha256': digest, 'source_checks': evidence,
                      'scope': 'Preview 1 Mac source only; not binary execution or historical iOS proof'}, indent=2))


if __name__ == '__main__':
    main()
