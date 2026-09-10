#!/usr/bin/env python3
"""Attribute retained top-20 chunk samples using exact installed disassembly.

Read-only; no timing run or automatic identification of removable work.
Disassembly is processed one chunk at a time, not retained as huge text files.
"""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[1]
module = root/'generated/macos/GalaxyPad.app/Contents/MacOS/gRMGE01_recomp.dylib'
with module.open('rb') as stream:
    digest = hashlib.file_digest(stream, 'sha256').hexdigest()
assert digest == '1fb635f71b8ca6afab01fccb1b06a0a5e2b6ddd5a1aec4bb8ef629af3201dc7a'
profile_path = root/'generated/fprf-site-r423.json'
profile = json.loads(profile_path.read_text())
assert profile['samples'] == 28822 and profile['address_binary'] == module.name
spec = importlib.util.spec_from_file_location('classifier', root/'scripts/classify-cpu-instructions.py')
classifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classifier)
selected = [row for row in profile['leaves'] if row['name'].startswith('func_')][:20]
families, offsets, opcodes = Counter(), Counter(), Counter()
load_origins = Counter()
symbols = subprocess.check_output(['xcrun', 'nm', '-n', str(module)], text=True)
globals_by_address = {int(m[1],16):m[2] for line in symbols.splitlines()
    if (m := re.fullmatch(r'([0-9a-f]+) [a-zA-Z] (_g_mem_write_journal)', line))}
assert len(globals_by_address) == 1
chunks = []
for row in selected:
    name = row['name']
    assembly = subprocess.check_output(['xcrun','llvm-objdump',
        '--disassemble-symbols=_'+name,str(module)],text=True)
    data = classifier.classify(profile,assembly,[name],details=True)[name]
    parsed = {}
    for line in assembly.splitlines():
        match = re.match(r'\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+(\S+)\s*(.*)',line)
        if match:
            parsed[int(match[1],16)] = (match[2],match[3])
    assert data['samples'] == row['samples']
    families.update(data['families'])
    offsets.update(data['x19_memory_offsets'])
    for instruction in data['instructions']:
        opcodes[instruction['opcode']] += instruction['samples']
        if not instruction['opcode'].startswith('ld'):
            continue
        pc = int(instruction['offset'],16)
        category = classifier.load_origin(parsed, pc, globals_by_address)
        load_origins[category] += instruction['samples']
    chunks.append({'name':name,'assembly_sha256':hashlib.sha256(assembly.encode()).hexdigest(),**data})
total = sum(row['samples'] for row in chunks)
assert total == sum(families.values()) == sum(opcodes.values())
print(json.dumps({'module_sha256':digest,
    'profile_sha256':hashlib.sha256(profile_path.read_bytes()).hexdigest(),
    'selected_samples':total,'cpu_samples':profile['samples'],
    'families':dict(families.most_common()),'opcodes':dict(opcodes.most_common()),
    'load_origins':dict(load_origins.most_common()),
    'x19_offsets':dict(offsets.most_common()),'chunks':chunks,
    'boundary':'Top20 chunks only. PC samples are not executed-instruction counts, removable time, or FPS predictions. x19 offsets require separate base-register/ABI proof.'},indent=2))
