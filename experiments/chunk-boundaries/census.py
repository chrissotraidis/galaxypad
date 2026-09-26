#!/usr/bin/env python3
"""Read-only generated-C cut census; weights are NOT cut execution counts."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--compile-commands', type=Path, required=True)
    ap.add_argument('--module', type=Path, required=True)
    ap.add_argument('--profile', type=Path, required=True)
    ap.add_argument('--sample', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    commands = json.loads(args.compile_commands.read_text())
    sources = sorted({Path(c['file']) for c in commands
                      if re.fullmatch(r'chunk_.*\.c', Path(c['file']).name)})
    if not sources:
        raise ValueError('No generated chunks in compile commands')
    if not any(f'-fprofile-instr-use={args.profile.resolve()}' in c['command']
               for c in commands):
        raise ValueError('Requested profile is not referenced by compile commands')
    uuids = re.findall(r'UUID: ([0-9A-F-]+)', subprocess.check_output(
        ['xcrun', 'dwarfdump', '--uuid', str(args.module)], text=True))
    sample = args.sample.read_text()
    sampled_uuids = re.findall(r'\+gRMGE01_recomp\.dylib .*?<([0-9A-F-]+)>', sample)
    if len(uuids) != 1 or sampled_uuids != uuids:
        raise ValueError('Module UUID does not match sample binary image')
    # sample's final flat table is self observations, unlike its call tree.
    samples = {m[1]: int(m[2]) for m in re.finditer(
        r'^\s+(func_[0-9A-F]{8})  \(in gRMGE01_recomp\.dylib\)\s+(\d+)\s*$',
        sample, re.M)}
    if not samples:
        raise ValueError('No generated functions in sample flat table')
    profile = subprocess.check_output(['xcrun', 'llvm-profdata', 'show',
        '--all-functions', str(args.profile)], text=True)
    counts = {m[1]: int(m[2]) for m in re.finditer(
        r'^  (func_[0-9A-F]{8}):\n    Hash: .*\n    Counters: \d+\n'
        r'    Function count: (\d+)', profile, re.M)}
    if not counts:
        raise ValueError('No generated function counts in profile')
    chunks = {}
    targets = set()
    inventory = []
    for path in sources:
        text = path.read_text()
        entry = re.search(r'void (func_([0-9A-F]{8}))\(CPUState\* ctx\)', text)
        if not entry:
            raise ValueError(f'Unrecognized chunk entry: {path}')
        # Use instruction annotations, not every PC store or suffix-switch entry.
        instructions = list(re.finditer(r'^    // ([0-9A-F]{8}):\s+(\S+)(.*)$', text, re.M))
        for inst in instructions:
            if inst[2] in {'b', 'bl', 'bc', 'bcl'}:
                targets.update(int(x, 16) for x in re.findall(r'0x([0-9A-F]{8})', inst[3]))
        tail = re.search(r'\n    ctx->pc = 0x([0-9A-F]{8})u;\n    return;\nreturn_dispatch_', text)
        before = [i for i in instructions if tail and i.start() < tail.start()]
        last = before[-1] if before else None
        chunks[int(entry[2], 16)] = dict(path=str(path), name=entry[1], text=text,
            tail=tail, last=last)
        inventory.append(dict(path=str(path), sha256=sha(path)))
    rows = []
    barriers = {'b', 'bl', 'bc', 'bcl', 'bclr', 'bclrl', 'bcctr', 'bcctrl',
                'blr', 'bctr', 'sc', 'rfi', 'tw', 'twi', 'icbi', 'dcbi', 'dcbf', 'dcbst'}
    for start, chunk in chunks.items():
        tail, last = chunk['tail'], chunk['last']
        if not tail or not last:
            continue
        next_pc = int(tail[1], 16)
        if int(last[1], 16) != next_pc - 4 or next_pc not in chunks:
            continue
        successor = chunks[next_pc]
        rows.append(dict(source=chunk['path'], function=chunk['name'],
            cut_pc=f'0x{next_pc:08X}', predecessor_pc=f'0x{next_pc-4:08X}',
            predecessor_opcode=last[2], next_function=successor['name'],
            tail_line=chunk['text'][:tail.start()].count('\n') + 2,
            explicit_direct_target=next_pc in targets,
            potential_straight_line_cut=last[2] not in barriers and next_pc not in targets,
            source_self_samples=samples.get(chunk['name'], 0),
            destination_self_samples=samples.get(successor['name'], 0),
            source_profile_entries=counts.get(chunk['name']),
            destination_profile_entries=counts.get(successor['name'])))
    rows.sort(key=lambda r: (r['potential_straight_line_cut'],
        r['source_self_samples'] + r['destination_self_samples']), reverse=True)
    report = dict(module_sha256=sha(args.module), module_uuid=uuids[0],
        profile_sha256=sha(args.profile), sample_sha256=sha(args.sample),
        compile_commands_sha256=sha(args.compile_commands),
        chunk_count=len(chunks), adjacent_cuts=len(rows),
        potential_straight_line_cuts=sum(r['potential_straight_line_cut'] for r in rows),
        limitations=['Syntactic screen, not exhaustive PPC CFG proof: indirect targets remain unknown.',
            'Function entry counts and self samples are not tail-edge frequencies or removable cost.',
            'PGO training and sample observation cover different windows; do not combine as rates.',
            'UUID checks sample identity; compile commands and current sources are not immutable build receipts.',
            'No cut is removed; timing, callback, stop and exception semantics require separate proof.'],
        source_inventory=inventory, cuts=rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k: v for k, v in report.items() if k not in {'source_inventory', 'cuts'}}, indent=2))
    print(json.dumps(rows[:12], indent=2))


if __name__ == '__main__':
    main()
