#!/usr/bin/env python3
"""Rank contiguous FP-arithmetic spans, not CPU cost or safe fusion candidates.

Loads, stores, control flow, unknown counts and gaps end a span. Interior entries
remain possible: every span is a dataflow inspection region, not a basic block.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re


def rank(data, include_memory=False):
    source = Path(data['filenames'][0])
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != data['chunk_sha256']:
        raise ValueError('Source changed since coverage export')
    function = data['function_name']
    body = raw.decode().split('void ' + function + '(CPUState* ctx) {', 1)[1]
    blocks = dict(re.findall(r'^(label_[0-9A-F]{8}:)\n(.*?)(?=^label_|\Z)',
                             body, re.M | re.S))
    # Explicit arithmetic/move allowlist; FPSCR/CR effects still require audit.
    arithmetic = set('fadd fadds fsub fsubs fmul fmuls fdiv fdivs fmadd fmadds '
                     'fmsub fmsubs fnmadd fnmadds fnmsub fnmsubs fres frsqrte '
                     'frsp fmr fneg fabs fnabs fsel ps_add ps_sub ps_mul ps_div '
                     'ps_madd ps_msub ps_nmadd ps_nmsub ps_muls0 ps_muls1 '
                     'ps_madds0 ps_madds1 ps_sum0 ps_sum1 ps_res ps_rsqrte '
                     'ps_merge00 ps_merge01 ps_merge10 ps_merge11 ps_mr ps_neg '
                     'ps_abs ps_nabs ps_sel'.split())
    memory = set('lfs lfsu lfsx lfsux lfd lfdu lfdx lfdux '
                 'stfs stfsu stfsx stfsux stfd stfdu stfdx stfdux stfiwx '
                 'psq_l psq_lu psq_lx psq_lux psq_st psq_stu psq_stx psq_stux'.split())
    islands, current = [], []

    def finish():
        if len(current) >= 2:
            islands.append(dict(start=current[0]['pc'], end=current[-1]['pc'],
                                length=len(current),
                                entry_attempts=sum(x['count'] for x in current),
                                minimum_site_count=min(x['count'] for x in current),
                                maximum_site_count=max(x['count'] for x in current),
                                memory_observers=[x['pc'] for x in current if x['memory_observer']],
                                instructions=current.copy()))
        current.clear()

    for entry in sorted(data['instruction_entries'], key=lambda e: e['label']):
        label, count = entry['label'], entry['count']
        block = blocks[label]
        match = re.search(r'// ([0-9A-F]{8}): ([^\n]+)', block)
        if match and label != 'label_' + match[1] + ':':
            raise ValueError('Instruction identity mismatch: ' + label)
        if not match or count is None:
            finish()
            continue
        pc, instruction = match.groups()
        mnemonic = instruction.split()[0].rstrip('.')
        if mnemonic not in arithmetic and not (include_memory and mnemonic in memory):
            finish()
            continue
        if current and int(pc, 16) != int(current[-1]['pc'], 16) + 4:
            finish()
        helpers = sorted(set(re.findall(r'\b((?:ppc_|mem_|dolrecomp_)\w+)\s*\(', block)))
        current.append(dict(pc=pc, instruction=instruction, count=count, helpers=helpers,
                            memory_observer=mnemonic in memory))
    finish()
    return dict(source=str(source), source_sha256=data['chunk_sha256'],
                profile_sha256=data['profile_sha256'],
                islands=sorted(islands, key=lambda i: i['entry_attempts'], reverse=True),
                include_memory=include_memory,
                caveat=__doc__.strip() if not include_memory else
                'Memory-inclusive inspection spans, not proven routines or safe fusion candidates. '
                'Every memory observer requires alias, callback, exception and ordering proof. '
                'Every suffix remains externally enterable. Counts are historical entry attempts, not CPU cost.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('coverage', type=Path)
    parser.add_argument('--include-memory', action='store_true',
                        help='Expose larger spans and memory observers; does not authorize fusion')
    args = parser.parse_args()
    print(json.dumps(rank(json.loads(args.coverage.read_text()), args.include_memory), indent=2))
