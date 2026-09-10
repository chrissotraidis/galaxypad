#!/usr/bin/env python3
"""Verify the retained R825 compile-only experiment, not runtime correctness."""
from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parents[1]
out = root/'generated/state-alias-codegen-r825-final'
report = json.loads((out/'report.json').read_text())
assert len(report['chunks']) == 3
for chunk, row in report['chunks'].items():
    base = out/chunk.removesuffix('.c')
    control = (base/'control'/chunk).read_text()
    candidate = (base/'hypothetical_restrict'/chunk).read_text()
    expected, count = re.subn(r'(\b(?:func|loop)_[0-9A-Fa-f]+\(CPUState\*) ctx\)',
                              r'\1 __restrict ctx)', control)
    assert count == row['restricted_definitions'] and count > 0
    assert candidate == expected
    words = []
    for variant in ('control', 'hypothetical_restrict'):
        path = base/variant
        assert hashlib.sha256((path/chunk).read_bytes()).hexdigest() == row['variants'][variant]['source_sha256']
        assert hashlib.sha256((path/'DO-NOT-RUN.dylib').read_bytes()).hexdigest() == row['variants'][variant]['binary_sha256']
        asm = (path/'chunk.asm').read_text()
        code = re.findall(r'^\s*[0-9a-f]+:\s+([0-9a-f]{8})\s+\S+', asm, re.M)
        assert len(code) == row['variants'][variant]['instructions']
        assert '<_func_'+chunk.removesuffix('.c').split('_')[-1]+'>:' in asm
        words.append(code)
    assert words[0] == words[1], 'Static instruction encodings differ'
    assert (base/'control/build.log').read_text() == (base/'hypothetical_restrict/build.log').read_text()
    print(chunk, len(words[0]), 'identical instruction encodings; annotation-only source diff')
print('Compile-only identity proven; no candidate executed and no performance claim')
