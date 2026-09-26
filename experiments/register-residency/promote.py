#!/usr/bin/env python3
"""Keep guest integer state in C locals with write-through to CPUState.

Every write to a promoted field updates both a local and CPUState, so CPUState is
always current at exits, callbacks and helpers; reads come from the local. Locals
are reloaded after the only helpers that write promoted state (fcmp writes CR,
the interpreter fallback and outlined loops may write anything) and after any
unrecognized call that receives ctx. Functions containing an unrecognized write
form are left unchanged. Memory accesses use the entry snapshot in gp_memmap.h.
"""
import re

FIELD_TYPES = {'cr': 'u32', 'xer': 'u32', 'lr': 'u32', 'ctr': 'u32', 'downcount': 's64'}
KNOWN_NO_PROMOTED_WRITES = {
    'mem_read8', 'mem_read16', 'mem_read32', 'mem_read64', 'mem_write8', 'mem_write16', 'mem_write32',
    'mem_write64', 'ppc_fp_available_inline', 'ppc_psq_load_inline', 'ppc_psq_store_inline', 'ppc_fmuls',
    'ppc_fsubs', 'ppc_fadds', 'ppc_fdivs', 'ppc_fctiw', 'ppc_frsp', 'ppc_ps_sub_op', 'ppc_fmul', 'ppc_ps_add_op',
    'ppc_fadd', 'ppc_fsub', 'ppc_ps_mul_op', 'ppc_ps_madd_op', 'ppc_ps_sum0', 'ppc_ps_muls0', 'ppc_ps_madds0',
    'ppc_frsqrte', 'ppc_fdiv', 'ppc_fma', 'ppc_ps_madds1', 'ppc_ps_sum1', 'ppc_ps_muls1', 'ppc_fres',
    'ppc_mftb', 'ppc_dcbz_l', 'ppc_fpscr_updated', 'ppc_program_exception', 'ppc_system_call_exception',
    'ppc_rfi',
}
CR_WRITERS = {'ppc_fcmp'}
FUNC_RE = re.compile(r'^((?:static )?void ((?:func|loop)_[0-9A-F]+)\(CPUState\* ctx\) \{)$', re.M)
CALL_RE = re.compile(r'\b([A-Za-z_][A-Za-z0-9_]*)\(ctx[,)]')
LMW_RE = re.compile(r'^(\s*)for \(u32 r = (\d+); r < 32; r\+\+, ea \+= 4\) ctx->gpr\[r\] = mem_read32\(ctx, ea\);$', re.M)
STMW_RE = re.compile(r'^(\s*)for \(u32 r = (\d+); r < 32; r\+\+, ea \+= 4\) mem_write32\(ctx, ea, ctx->gpr\[r\]\);$', re.M)
FIELD = r'(gpr\[(\d+)\]|cr|xer|lr|ctr|downcount)'
ASSIGN_RE = re.compile(r'ctx->' + FIELD + r' ([-+*/|&^]?)= ([^;]*);')
DEC_RE = re.compile(r'ctx->(ctr)--;')


def local(field):
    m = re.fullmatch(r'gpr\[(\d+)\]', field)
    return f'g_{m.group(1)}' if m else f'l_{field}'


def reads(text):
    text = re.sub(r'ctx->gpr\[(\d+)\]', r'g_\1', text)
    return re.sub(r'ctx->(cr|xer|lr|ctr|downcount)\b', r'l_\1', text)


def unroll(text):
    text = LMW_RE.sub(lambda m: '\n'.join(f'{m.group(1)}ctx->gpr[{r}] = mem_read32(ctx, ea); ea += 4;'
                                          for r in range(int(m.group(2)), 32)), text)
    return STMW_RE.sub(lambda m: '\n'.join(f'{m.group(1)}mem_write32(ctx, ea, ctx->gpr[{r}]); ea += 4;'
                                           for r in range(int(m.group(2)), 32)), text)


def transform_body(body, stats):
    body = unroll(body)
    fields = set(re.findall(r'ctx->(gpr\[\d+\]|cr|xer|lr|ctr|downcount)(?![A-Za-z0-9_])', body))
    if not fields:
        return None, set()
    out = []
    for line in body.split('\n'):
        def assign(m):
            field, op, rhs = m.group(1), m.group(3), reads(m.group(4))
            return f'ctx->{field} = ({local(field)} {op}= ({rhs}));'
        new = ASSIGN_RE.sub(assign, line)
        new = DEC_RE.sub(lambda m: f'ctx->{m.group(1)} = (--l_{m.group(1)});', new)
        # Protect write-through targets, then turn all remaining promoted accesses into local reads.
        new = re.sub(r'ctx->' + FIELD + r' = \(', lambda m: f'@@{m.group(1)}@@ = (', new)
        new = reads(new)
        if re.search(r'ctx->(gpr\[|cr\b|xer\b|lr\b|ctr\b|downcount\b)', new) or re.search(r'\b[gl]_\w+\s*([-+*/|&^]?=|\+\+|--)', new.replace('= (g_', '').replace('= (l_', '')) and '@@' not in new:
            return None, {'unhandled': line.strip()}
        new = re.sub(r'@@(gpr\[\d+\]|cr|xer|lr|ctr|downcount)@@', r'ctx->\1', new)
        new = re.sub(r'\bmem_(read|write)(8|16|32|64)\(ctx, ', r'gp_mm_\1\2(&gp_mm, ctx, ', new)
        out.append(new)
        calls = set(CALL_RE.findall(new)) - {'gp_mm_read8'}
        reload = None
        for c in calls:
            if c.startswith('gp_mm_') or c in KNOWN_NO_PROMOTED_WRITES:
                continue
            if c in CR_WRITERS and 'cr' in fields:
                reload = reload or {'cr'}
            else:
                reload = fields
                if not c.startswith('loop_') and c != 'ppc_fallback_instruction':
                    stats['unknown_calls'][c] = stats['unknown_calls'].get(c, 0) + 1
        if reload:
            indent = re.match(r'\s*', new).group(0)
            out.append(indent + ' '.join(f'{local(f)} = ctx->{f};' for f in sorted(reload)))
    decl = ['    GP_MM_DECL(ctx);']
    for f in sorted(fields, key=lambda f: (not f.startswith('gpr'), int(re.sub(r'\D', '', f) or 0), f)):
        t = 'u32' if f.startswith('gpr') else FIELD_TYPES[f]
        decl.append(f'    {t} {local(f)} = ctx->{f};')
    return '\n'.join(decl) + '\n' + '\n'.join(out), fields


def transform_chunk(text, scope='all'):
    stats = {'functions': 0, 'transformed': 0, 'unchanged': [], 'unknown_calls': {}}
    starts = list(FUNC_RE.finditer(text))
    if scope == 'loops':
        starts = [m for m in starts if m.group(2).startswith('loop_')]
    if starts:
        text = text.replace('#include "../RMGE01.h"', '#include "../RMGE01.h"\n#include "../gp_memmap.h"', 1)
        starts = list(m for m in FUNC_RE.finditer(text) if scope != 'loops' or m.group(2).startswith('loop_'))
    pieces, pos = [], 0
    for m in starts:
        a = m.end()
        b = text.index('\n}\n', a)
        stats['functions'] += 1
        body, info = transform_body(text[a:b], stats)
        pieces.append(text[pos:a])
        if body is None:
            pieces.append(text[a:b])
            if info:
                stats['unchanged'].append((m.group(2), info))
        else:
            pieces.append('\n' + body)
            stats['transformed'] += 1
        pos = b
    pieces.append(text[pos:])
    return ''.join(pieces), stats


if __name__ == '__main__':
    import argparse, json, pathlib
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=pathlib.Path, required=True, help='Generated RMGE01_generated directory')
    p.add_argument('--output', type=pathlib.Path, required=True, help='New directory for the transformed copy')
    p.add_argument('--only', nargs='*', help='Chunk file stems to transform (default: all)')
    p.add_argument('--scope', choices=('all', 'loops'), default='all',
                   help='loops: convert only outlined loop functions, leaving chunk bodies unchanged')
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    (a.output/'chunks').mkdir()
    for f in a.input.iterdir():
        if f.is_file():
            (a.output/f.name).write_bytes(f.read_bytes())
    here = pathlib.Path(__file__).resolve().parent
    (a.output/'gp_memmap.h').write_text((here/'gp_memmap.h').read_text())
    total = {'chunks': 0, 'functions': 0, 'transformed': 0, 'unchanged': [], 'unknown_calls': {}}
    for f in sorted((a.input/'chunks').glob('*.c')):
        text = f.read_text()
        if a.only is None or f.stem in a.only:
            text, s = transform_chunk(text, a.scope)
            total['chunks'] += 1
            for k in ('functions', 'transformed'):
                total[k] += s[k]
            total['unchanged'] += [[f.stem, n, i] for n, i in s['unchanged']]
            for c, n in s['unknown_calls'].items():
                total['unknown_calls'][c] = total['unknown_calls'].get(c, 0) + n
        (a.output/'chunks'/f.name).write_text(text)
    (a.output/'promote-report.json').write_text(json.dumps(total, indent=1) + '\n')
    print(json.dumps({k: (v if k != 'unchanged' else len(v)) for k, v in total.items()}))
