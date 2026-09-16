#!/usr/bin/env python3
"""Conservative structural audit, not permission to replace guest functions.

Consumes DolRecomp annotations, retaining exact PCs. A candidate must have a
closed acyclic CFG, only ordinary integer/FP/memory operations, and normal blr
returns. Memory aliasing, ABI compliance and timing remain unproven.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import importlib.util

spec = importlib.util.spec_from_file_location('region_census', Path(__file__).with_name('analyze-region-feasibility.py'))
region = importlib.util.module_from_spec(spec)
spec.loader.exec_module(region)
REGISTER_OPS = set('mflr mtlr mfctr mtctr mfcr mtcrf mcrf crand crandc creqv crnand crnor cror crorc crxor addic subfic ori oris xori xoris andi andis'.split())


def parse_sources(paths):
    code, inputs = {}, []
    for path in paths:
        raw = path.read_bytes()
        source = raw.decode()
        region.parse(source)  # Require corresponding exact-entry labels.
        inputs.append(dict(file=path.name, sha256=hashlib.sha256(raw).hexdigest()))
        for match in region.ANNOTATION.finditer(source):
            pc = int(match[1], 16)
            item = (match[2], match[3].strip())
            if pc in code and code[pc] != item:
                raise ValueError(f'conflicting instruction at {pc:08X}')
            code[pc] = item
    return code, inputs


def target(operands):
    match = re.search(r'0x([0-9a-fA-F]{8})$', operands)
    return int(match[1], 16) if match else None


def audit(code, max_instructions=512, allow_calls=False):
    entries = {target(args) for op, args in code.values() if op == 'bl'} - {None}
    incoming = collections.defaultdict(set)
    for pc, (op, args) in code.items():
        if op in ('b', 'bc', 'bl') and target(args) is not None:
            incoming[target(args)].add(pc)
    candidates, rejected = [], collections.Counter()
    for entry in sorted(entries):
        seen, edges, pending, reason = set(), {}, [entry], None
        calls = set()
        while pending and reason is None:
            pc = pending.pop()
            if pc in seen:
                continue
            if pc not in code:
                reason = 'missing_instruction'
                break
            if pc != entry and pc in entries:
                reason = 'another_call_entry'
                break
            seen.add(pc)
            if len(seen) > max_instructions:
                reason = 'size_limit'
                break
            op, args = code[pc]
            if op == 'blr':
                successors = []
            elif op in ('b', 'bc'):
                address = target(args)
                if address is None:
                    reason = 'unparsed_branch'
                    break
                successors = [address] + ([pc + 4] if op == 'bc' else [])
            elif op == 'bl':
                if not allow_calls:
                    reason = 'nested_call'
                    break
                address = target(args)
                if address is None:
                    reason = 'unparsed_branch'
                    break
                calls.add(address)
                successors = [pc + 4]
            elif region.classify(op) != 'barrier' or op.rstrip('.') in REGISTER_OPS or op in ('lmw', 'stmw'):
                successors = [pc + 4]
            else:
                reason = 'system_indirect_or_unknown'
                break
            edges[pc] = successors
            pending.extend(successors)
        if reason is None:
            # Kahn's algorithm rejects cycles, including forward-edge cycles.
            indegree = dict.fromkeys(seen, 0)
            for successors in edges.values():
                for successor in successors:
                    indegree[successor] += 1
            ready = [pc for pc, count in indegree.items() if count == 0]
            visited = 0
            while ready:
                pc = ready.pop()
                visited += 1
                for successor in edges[pc]:
                    indegree[successor] -= 1
                    if indegree[successor] == 0:
                        ready.append(successor)
            if visited != len(seen):
                reason = 'loop'
            elif any(incoming[pc] - seen for pc in seen - {entry}):
                reason = 'external_interior_branch'
            elif any(pc != entry and pc - 4 in code and pc - 4 not in seen
                     and code[pc - 4][0] not in ('b', 'blr', 'bctr', 'rfi')
                     for pc in seen):
                reason = 'external_interior_fallthrough'
        if reason:
            rejected[reason] += 1
        else:
            counts = collections.Counter(region.classify(code[pc][0]) for pc in seen)
            candidates.append(dict(entry=f'{entry:08X}', instructions=len(seen),
                                   memory=counts['memory'], fp=counts['fp'],
                                   calls=[f'{pc:08X}' for pc in sorted(calls)],
                                   pcs=[f'{pc:08X}' for pc in sorted(seen)]))
    return dict(call_targets=len(entries), rejected=dict(rejected), candidates=candidates)


def closed_calls(candidates):
    """Least fixed point: an unavailable callee or recursion cannot qualify."""
    available = {candidate['entry']: candidate for candidate in candidates}
    closed = set()
    while True:
        added = {entry for entry, candidate in available.items()
                 if entry not in closed and set(candidate['calls']) <= closed}
        if not added:
            break
        closed.update(added)
    return [available[entry] for entry in sorted(closed)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('chunks', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    paths = sorted(args.chunks.glob('chunk_*.c'))
    if not paths:
        parser.error('no generated chunks')
    code, inputs = parse_sources(paths)
    report = audit(code)
    call_audit = audit(code, allow_calls=True)
    call_candidates = closed_calls(call_audit['candidates'])
    report['closed_call_regions'] = dict(
        candidates=call_candidates,
        unresolved_or_recursive=len(call_audit['candidates']) - len(call_candidates),
        rejected=call_audit['rejected'],
        unique_instructions=len({pc for c in call_candidates for pc in c['pcs']}))
    unique = {pc for candidate in report['candidates'] for pc in candidate['pcs']}
    report.update(schema=1, inputs=inputs, total_instructions=len(code),
                  unique_candidate_instructions=len(unique),
                  limitation='Static acyclic direct-call leaf candidates only. No dynamic coverage, ABI, memory, interrupt, exception, indirect-entry or performance proof. Preserve arbitrary-entry fallback.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ('call_targets', 'rejected', 'total_instructions', 'unique_candidate_instructions')}))
    print(f"candidates={len(report['candidates'])}")
    print(f"closed_call_regions={len(call_candidates)} instructions={report['closed_call_regions']['unique_instructions']}")


if __name__ == '__main__':
    main()
