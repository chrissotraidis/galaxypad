#!/usr/bin/env python3
"""Structural census of DolRecomp C output; never authorizes code generation.

Uses emitted instruction annotations, not a second PPC decoder. Unknown opcodes,
control transfers and address gaps end a window. Memory-transparent windows are
hypothetical: callbacks, faults and aliasing must be resolved before optimization.
Counts are static and cannot predict dynamic coverage or FPS.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re

ANNOTATION = re.compile(r'^\s*// ([0-9A-Fa-f]{8}):\s+(\S+)(.*)$', re.M)
FP = set('fadd fadds fsub fsubs fmul fmuls fdiv fdivs fmadd fmadds fmsub fmsubs fnmadd fnmadds fnmsub fnmsubs fneg fabs fnabs fmr frsp fres frsqrte fctiw fctiwz fsel ps_add ps_sub ps_mul ps_div ps_madd ps_msub ps_nmadd ps_nmsub ps_muls0 ps_muls1 ps_madds0 ps_madds1 ps_sum0 ps_sum1 ps_merge00 ps_merge01 ps_merge10 ps_merge11 ps_neg ps_abs ps_nabs ps_mr ps_sel ps_res ps_rsqrte'.split())
INTEGER = set('addi addis add addc adde addme addze subf subfc subfe subfme subfze neg mullw mulhw mulhwu divw divwu and andc or orc xor nand nor eqv rlwinm rlwimi rlwnm slw srw sraw srawi cntlzw extsb extsh cmp cmpl cmpi cmpli li lis mr nop'.split())
MEMORY = set('lwz lwzu lwzx lwzux lbz lbzu lbzx lbzux lhz lhzu lhzx lhzux lha lhau lhax lhaux stw stwu stwx stwux stb stbu stbx stbux sth sthu sthx sthux lfs lfsu lfsx lfsux lfd lfdu lfdx lfdux stfs stfsu stfsx stfsux stfd stfdu stfdx stfdux psq_l psq_lu psq_lx psq_lux psq_st psq_stu psq_stx psq_stux'.split())

def classify(op):
    op = op.rstrip('.')
    if op in FP:
        return 'fp'
    if op in INTEGER:
        return 'integer'
    if op in MEMORY:
        return 'memory'
    return 'barrier'

def parse(source):
    records = {}
    labels = {int(pc, 16) for pc in re.findall(r'^label_([0-9A-Fa-f]{8}):', source, re.M)}
    for m in ANNOTATION.finditer(source):
        pc = int(m[1], 16)
        if pc % 4:
            raise ValueError('unaligned instruction annotation')
        if pc not in labels:
            raise ValueError('annotation lacks corresponding emitted entry label')
        instruction = (m[2], m[3].strip())
        if pc in records and records[pc] != instruction:
            raise ValueError('conflicting instruction annotations')
        # The emitter can duplicate instructions when specializing local loops.
        records[pc] = instruction
    return [(pc, op, classify(op)) for pc, (op, _) in sorted(records.items())]

def windows(records, permit_memory):
    result, current = [], []
    def flush():
        if current:
            counts = collections.Counter(r[2] for r in current)
            if counts['fp']:
                result.append(dict(start=f'{current[0][0]:08X}', end=f'{current[-1][0]:08X}', instructions=len(current), fp=counts['fp'], memory=counts['memory']))
            current.clear()
    for record in records:
        if current and record[0] != current[-1][0] + 4:
            flush()
        if record[2] == 'barrier' or (record[2] == 'memory' and not permit_memory):
            flush()
        else:
            current.append(record)
    flush()
    return result

def summarize(spans):
    return dict(windows=len(spans), fp_in_windows=sum(s['fp'] for s in spans),
                fp_in_windows_at_least_8=sum(s['fp'] for s in spans if s['fp'] >= 8),
                max_fp=max((s['fp'] for s in spans), default=0),
                top=sorted(spans, key=lambda s: s['fp'], reverse=True)[:5])

def analyze(paths):
    chunks = []
    for path in paths:
        data = path.read_bytes()
        records = parse(data.decode())
        if not records:
            raise ValueError(f'no instruction annotations: {path}')
        chunks.append(dict(file=path.name, sha256=hashlib.sha256(data).hexdigest(),
                           counts=dict(collections.Counter(r[2] for r in records)),
                           strict=summarize(windows(records, False)),
                           memory_transparent_hypothesis=summarize(windows(records, True))))
    totals = collections.Counter()
    for chunk in chunks:
        totals.update(chunk['counts'])
    return dict(schema=1, limitation='Static straight-line windows only; every emitted instruction remains an external entry. No liveness, precision, legal-region or dynamic speedup proof.', counts=dict(totals), chunks=chunks)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('chunks', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    paths = sorted(args.chunks.glob('chunk_*.c'))
    if not paths:
        parser.error('no chunk_*.c files found')
    report = analyze(paths)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(chunks=len(paths), counts=report['counts'])))
