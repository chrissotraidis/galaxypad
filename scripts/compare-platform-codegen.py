#!/usr/bin/env python3
"""Compare exact sampled chunk code in retained native and Simulator modules.

Static counts and raw encoding agreement only; no relocation normalization,
semantic equivalence, dynamic frequency, or runtime-speed inference.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT/'generated/modules-scale-r387/RMGE01/2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09-c4cbfba1bd04990b/gRMGE01_recomp.dylib'
SIMULATOR = ROOT/'generated/build/ios-simulator-module/gRMGE01_recomp.dylib'
EXPECTED = ('c0021b9f2fad3acc3746b6a582b46935e2f7b60bc38434ad7d485564957c7939',
            '3acdcddcd47812c2e2a67b8cec0cf06c17009cf1ad7f2e9dc9abd83158a1bac0')


def parse(lines, names):
    chunks, active = {}, None
    for line in lines:
        header = re.match(r'^[0-9a-f]+ <_([^>]+)>:$', line.strip())
        if header:
            active = header[1] if header[1] in names else None
            if active:
                if active in chunks:
                    raise ValueError('Duplicate symbol: '+active)
                chunks[active] = []
            continue
        ins = re.match(r'^\s*([0-9a-f]+):\s+([0-9a-f]{8})\s+(\S+)', line)
        if active and ins:
            chunks[active].append((ins[2], ins[3]))
    if set(chunks) != set(names) or any(not rows for rows in chunks.values()):
        raise ValueError('Missing or empty requested symbols')
    return chunks


def compare(native, simulator):
    if set(native) != set(simulator):
        raise ValueError('Symbol sets differ')
    result = {}
    for name in sorted(native):
        a, b = native[name], simulator[name]
        result[name] = dict(native_instructions=len(a), simulator_instructions=len(b),
            same_opcode_sequence=[op for _, op in a] == [op for _, op in b],
            same_encoding_sequence=a == b,
            raw_encoding_matches_at_same_index=sum(x[0] == y[0] for x,y in zip(a,b)),
            native_opcodes=dict(Counter(op for _,op in a)),
            simulator_opcodes=dict(Counter(op for _,op in b)))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    profile = args.profile.read_bytes()
    summary = json.loads(profile)
    if summary['address_binary'] != 'gRMGE01_recomp.dylib':
        raise ValueError('Unexpected profile binary')
    names = {r['name'] for r in summary['addresses']
             if re.fullmatch(r'func_[0-9A-Fa-f]{8}',r['name'])}
    if not names:
        raise ValueError('No sampled chunks')
    decoded, identities, commands = [], [], []
    for module, expected in zip((NATIVE,SIMULATOR),EXPECTED):
        actual = hashlib.sha256(module.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError('Module identity changed: '+str(module))
        identities.append(dict(path=str(module), sha256=actual))
        cmd = ['xcrun','llvm-objdump','--disassemble-symbols='+
               ','.join('_'+n for n in sorted(names)),str(module)]
        commands.append(cmd)
        print('Inspecting', module, flush=True)
        with subprocess.Popen(cmd,stdout=subprocess.PIPE,text=True) as process:
            decoded.append(parse(process.stdout,names))
            if process.wait() != 0:
                raise RuntimeError('Disassembly failed')
    chunks = compare(*decoded)
    totals = dict(chunks=len(chunks),
        native_instructions=sum(r['native_instructions'] for r in chunks.values()),
        simulator_instructions=sum(r['simulator_instructions'] for r in chunks.values()),
        equal_opcode_sequences=sum(r['same_opcode_sequence'] for r in chunks.values()),
        equal_encoding_sequences=sum(r['same_encoding_sequence'] for r in chunks.values()),
        equal_raw_words_at_same_index=sum(r['raw_encoding_matches_at_same_index'] for r in chunks.values()))
    report = dict(modules=identities,profile_sha256=hashlib.sha256(profile).hexdigest(),
                  commands=commands,totals=totals,chunks=chunks,
                  boundary=__doc__)
    with args.output.open('x') as out:
        json.dump(report,out,indent=2)
        out.write('\n')
    print(json.dumps(totals,indent=2))


if __name__ == '__main__':
    main()
