#!/usr/bin/env python3
"""Join sampled module offsets to exact llvm-objdump instructions.

Counts are sampled-PC attribution, not instruction costs or dynamic counts.
The caller must verify that the disassembly matches the traced binary.
"""
import argparse
from collections import Counter
import json
import re


def load_origin(instructions, pc, globals_by_address=None):
    """Conservative local proof only; never infer guest/CPU state from a register name."""
    op, args = instructions[pc]
    if not op.startswith('ld'):
        raise ValueError('Expected a load')
    if '[sp' in args:
        return 'stack'
    previous = instructions.get(pc - 4, ('', ''))
    # Resolve the numeric page+offset, not objdump's nearest-symbol annotation.
    # Caller supplies symbols from the same verified binary as the instructions.
    page = re.fullmatch(r'(x\d+), (0x[0-9a-f]+)(?: <[^>]+>)?', previous[1])
    load = re.fullmatch(r'[xw]\d+, \[(x\d+)(?:, #(0x[0-9a-f]+))?\]', args)
    if (globals_by_address and op in ('ldr', 'ldrb') and previous[0] == 'adrp' and
            page and load and page[1] == load[1]):
        address = int(page[2], 16) + int(load[2] or '0', 16)
        if op == 'ldr' and globals_by_address.get(address) == '_g_mem_write_journal':
            return 'memory_write_journal_global_adjacent'
        if op == 'ldrb' and globals_by_address.get(address) == '_g_ppc_lazy_fp_enabled':
            return 'lazy_fp_global_adjacent'
    # LLVM's compact PC-relative jump table: loaded halfword is scaled and
    # added to an ADR code base, then branched to. Require the entire local form.
    if op == 'ldrh' and args == 'w11, [x9, x8, lsl #1]':
        a, b, c = (instructions.get(pc + n, ('', '')) for n in (-12, -8, -4))
        d, e = (instructions.get(pc + n, ('', '')) for n in (4, 8))
        if (a[0] == 'adrp' and a[1].startswith('x9, ') and
                b[0] == 'add' and re.fullmatch(r'x9, x9, #0x[0-9a-f]+', b[1]) and
                c[0] == 'adr' and c[1].startswith('x10, ') and
                d == ('add', 'x10, x10, x11, lsl #2') and e == ('br', 'x10')):
            return 'pc_relative_branch_table'
    return 'unresolved'


def family(op):
    if op in ('fmov', 'fcvt', 'fcvtzs', 'fcvtzu', 'scvtf', 'ucvtf'):
        return 'fp_move_or_conversion'
    if op in ('bl', 'blr'):
        return 'call'
    if op in ('b', 'br', 'ret', 'cbz', 'cbnz', 'tbz', 'tbnz') or op.startswith('b.'):
        return 'branch'
    if op.startswith(('ld', 'st')):
        return 'load' if op.startswith('ld') else 'store'
    if op.startswith('f'):
        return 'scalar_fp'
    return 'integer_or_other'


def classify(summary, assembly, names, details=False, weight_field='samples'):
    if weight_field not in ('samples', 'cycles'):
        raise ValueError('Weight field must be samples or cycles')
    instructions = {}
    for line in assembly.splitlines():
        match = re.match(r'^\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+(\S+)\s*(.*)', line)
        if match:
            address, op, args = match.groups()
            instructions[int(address, 16)] = (op, args)
    result = {}
    for name in names:
        counts, offsets, pcs = Counter(), Counter(), Counter()
        total = 0
        for row in summary['addresses']:
            if row['name'] != name:
                continue
            pc = int(row['raw_offset'], 16) & ~3
            if pc not in instructions:
                raise ValueError(f'Missing instruction for {name} at {pc:#x}')
            op, args = instructions[pc]
            weight = row[weight_field]
            if weight < 0:
                raise ValueError('Negative instruction weight')
            total += weight
            pcs[pc] += weight
            counts[family(op)] += weight
            # Mechanical base-register grouping; not automatic CPU-field proof.
            if family(op) in ('load', 'store'):
                match = re.search(r'\[x19(?:, #(0x[0-9a-f]+))?\]', args)
                if match:
                    offsets[match.group(1) or '0x0'] += weight
        result[name] = dict({weight_field: total}, families=dict(counts),
                            x19_memory_offsets=dict(offsets.most_common()))
        if details:
            result[name]['instructions'] = [
                dict({weight_field: weight}, offset=hex(pc), opcode=instructions[pc][0],
                     operands=instructions[pc][1])
                for pc, weight in pcs.most_common()]
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('summary')
    parser.add_argument('assembly')
    parser.add_argument('names', nargs='+')
    parser.add_argument('--details', action='store_true',
                        help='Include weighted aligned instruction sites, not inferred costs')
    args = parser.parse_args()
    with open(args.summary) as source:
        summary = json.load(source)
    with open(args.assembly) as source:
        assembly = source.read()
    print(json.dumps(classify(summary, assembly, args.names, args.details), indent=2))
