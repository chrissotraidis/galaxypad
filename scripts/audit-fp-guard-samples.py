#!/usr/bin/env python3
"""Read-only join of retained R422 samples and exact R423 guard assembly.

This counts sampled instruction addresses, not cycles removable by a patch.
Only contiguous explicit lazy-FP + MSR guard sequences are classified.
"""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / 'generated/macos/GalaxyPad.app/Contents/MacOS/gRMGE01_recomp.dylib'
EXPECTED = '1fb635f71b8ca6afab01fccb1b06a0a5e2b6ddd5a1aec4bb8ef629af3201dc7a'


def guards(text):
    instructions = []
    for line in text.splitlines():
        match = re.match(r'\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+(.+)', line)
        if match:
            instructions.append((int(match[1], 16), match[2]))
    found = []
    for index, (address, instruction) in enumerate(instructions):
        if 'adrp' not in instruction or '<_g_ppc_lazy_fp_enabled>' not in instruction:
            continue
        window = instructions[index:index + 8]
        # Follow only the adjacent fixed instruction sequence, never through a
        # control-flow target or unrelated load that merely shares an offset.
        for length in (6, 7):
            part = window[:length]
            if len(part) != length or any(p[0] != address + n * 4 for n, p in enumerate(part)):
                continue
            body = '\n'.join(p[1] for p in part)
            if (re.search(r'tbz\s+w\d+, #0xd,', part[-1][1])
                    and re.search(r'ldr\s+w\d+, \[x(?:0|19), #0x298\]', part[-2][1])
                    and 'ldrb' in body and 'b.ne' in body and 'cmp' in body):
                found.append([p[0] for p in part])
                break
    return found


def main():
    with MODULE.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if digest != EXPECTED:
        raise SystemExit('Installed module differs from profiled R422/R423 identity')
    profile_path = ROOT / 'generated/fprf-site-r423.json'
    profile = json.loads(profile_path.read_text())
    result = {'module_sha256': digest, 'cpu_samples': profile['samples'], 'chunks': []}
    for suffix, name in [('800180', 'func_800180A0'), ('804b60', 'func_804B60A0')]:
        asm_path = ROOT / f'generated/fprf-{suffix}-r423.asm'
        text = asm_path.read_text()
        if f'<_{name}>:' not in text:
            raise SystemExit('Unexpected assembly function')
        sequences = guards(text)
        pcs = {pc for sequence in sequences for pc in sequence}
        samples = [entry for entry in profile['addresses'] if entry['name'] == name]
        hits = sum(entry['samples'] for entry in samples
                   if int(entry['raw_offset'], 16) & ~3 in pcs)
        total = sum(entry['samples'] for entry in samples)
        result['chunks'].append(dict(name=name, sequences=len(sequences),
            classified_guard_samples=hits, chunk_samples=total,
            cpu_sample_percent=round(100 * hits / profile['samples'], 4),
            assembly_sha256=hashlib.sha256(text.encode()).hexdigest()))
    result['boundary'] = ('Explicit recognized guard sequences in two chunks only; '
        'unmatched shapes excluded. No dynamic-count, whole-module, removable-time '
        'or speedup claim. External entry and callback semantics remain mandatory.')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
