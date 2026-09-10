#!/usr/bin/env python3
"""Inventory source boundaries that an offline ARM64 exporter must replace.

This is a conservative textual inventory, not relocation discovery or proof
that arbitrary reference JIT output is relocatable.
"""
from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parents[1]
directory = root / 'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/JitArm64'
patterns = {
    'host_pointer_materialization': r'\bMOVP2R\s*\(',
    'host_helper_call': r'\b(?:ABI_CallFunction\w*|QuickCallFunction)\s*\(',
    'runtime_code_mutation_or_cache': r'\b(?:ScopedJITPageWriteAndNoExecute|WriteProtect|ClearCache|FinalizeBlock|BackPatch)\b',
    'live_state_references': r'\bm_ppc_state\.',
}
records, sources = [], {}
for path in sorted(directory.glob('*')):
    if path.suffix not in ('.h', '.cpp'):
        continue
    relative = str(path.relative_to(root))
    sources[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        if line.lstrip().startswith('//'):
            continue
        for category, pattern in patterns.items():
            if re.search(pattern, line):
                records.append(dict(category=category, file=relative,
                                    line=line_number, text=line.strip()))
print(json.dumps(dict(source_sha256=sources,
                      categories={name: sum(r['category'] == name for r in records)
                                  for name in patterns},
                      sites=records, limitation=__doc__.strip()), indent=2))
