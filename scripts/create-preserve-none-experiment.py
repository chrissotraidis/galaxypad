#!/usr/bin/env python3
"""Copy generated C into an unselected preserve_none calling-convention experiment.

Only generated chunk functions and their pointer type change ABI. The exported
module entry points, host callbacks and GXRuntime helper functions do not.
This script never edits/selects the input tree or builds a module.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ATTRIBUTE = '__attribute__((preserve_none))'
PROTOTYPE = re.compile(r'^void (func_[0-9A-F]{8})\(CPUState\* ctx\);$', re.M)
DEFINITION = re.compile(r'^void (func_[0-9A-F]{8})\(CPUState\* ctx\) \{$', re.M)
POINTER = 'typedef void (*DolRecompFunction)(CPUState* ctx);'
GUARD = '''#if !defined(__aarch64__) || !defined(__clang__)
#error "preserve_none experiment requires AArch64 Clang"
#endif
#if !__has_attribute(preserve_none)
#error "compiler lacks preserve_none"
#endif
'''


def transform_header(text):
    if text.count(POINTER) != 1 or not PROTOTYPE.search(text):
        raise ValueError('Unknown generated header shape or already transformed')
    transformed = PROTOTYPE.sub(lambda m: f'{ATTRIBUTE} void {m[1]}(CPUState* ctx);', text)
    transformed = transformed.replace(POINTER, f'typedef {ATTRIBUTE} void (*DolRecompFunction)(CPUState* ctx);')
    return GUARD + transformed


def transform_chunk(text):
    if not DEFINITION.search(text):
        raise ValueError('Unknown chunk definition or already transformed')
    return DEFINITION.sub(lambda m: f'{ATTRIBUTE} void {m[1]}(CPUState* ctx) {{', text)


def create(source, output):
    source, output = source.resolve(), output.resolve()
    if output.exists() or source == output or source in output.parents:
        raise ValueError('Output must be a new directory outside the input tree')
    files = sorted(p for p in source.rglob('*') if p.is_file() and p.suffix in ('.h', '.c', '.txt', '.dol'))
    prepared, hashes, declarations, definitions = {}, {}, set(), set()
    for path in files:
        relative = str(path.relative_to(source))
        original = path.read_bytes()
        text = original.decode() if path.suffix != '.dol' else None
        if path.suffix == '.h' and POINTER in text:
            declarations.update(PROTOTYPE.findall(text))
            text = transform_header(text)
        elif path.suffix == '.c' and DEFINITION.search(text):
            definitions.update(DEFINITION.findall(text))
            text = transform_chunk(text)
        # The private DOL is required by module-table generation; copy its
        # verified bytes unchanged, never interpret it as text.
        prepared[relative] = text.encode() if text is not None else original
        hashes[relative] = {'source': hashlib.sha256(original).hexdigest(),
                            'candidate': hashlib.sha256(prepared[relative]).hexdigest()}
    if not definitions or definitions != declarations:
        raise ValueError('Generated declarations and definitions do not match')
    for relative, data in prepared.items():
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    manifest = {'selected': False, 'source': str(source), 'output': str(output),
                'change': 'preserve_none on generated functions and their pointer type only',
                'functions': len(definitions), 'files': hashes}
    (output / 'preserve-none-provenance.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = create(args.source, args.output)
    print(f"Prepared {manifest['functions']} functions at {manifest['output']}; selected=false")
