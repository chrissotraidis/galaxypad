"""Private FP availability fall-through transform; not selected by any builder.

Only a closed, literal-operand arithmetic grammar is admitted. External suffix
entries retain their original check after precharge and PC materialization.
No memory operation, extra incoming branch, or unknown statement is crossed.
The caller must verify the pinned helper implementation before compiling output.
"""
import hashlib
from pathlib import Path
import re

HELPER_SHA = '554149a2e7d08783402af38e5a2b898aff476370b0e3a6af0ed4bd411aab934f'
ARITY = {'ppc_fmuls':3,'ppc_ps_add_op':3,'ppc_ps_sub_op':3,
         'ppc_ps_mul_op':3,'ppc_ps_madd_op':4,'ppc_ps_madds0':4,
         'ppc_ps_madds1':4,'ppc_ps_sum0':4,'ppc_ps_sum1':4,
         'ppc_ps_muls0':3,'ppc_ps_muls1':3}
LABEL = re.compile(r'^label_([0-9A-F]{8}):\n',re.M)
BODY = re.compile(
    r'    ctx->pc = 0x(?P<pc>[0-9A-F]{8})u;\n'
    r'    // (?P=pc): [a-z0-9_]+ +[^\n]*\n'
    r'    if \(!ppc_fp_available_inline\(ctx, 0x(?P=pc)u\)\) return;\n'
    r'    (?P<helper>ppc_[a-z0-9_]+)\(ctx, (?P<args>[^\n]+)\);\n\s*\Z')


def verify_helpers():
    path=Path(__file__).resolve().parents[1]/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core/cpu_interpreter_float.c'
    if hashlib.sha256(path.read_bytes()).hexdigest()!=HELPER_SHA:
        raise ValueError('FP helper contract needs review after source change')


def pure(body, pc):
    m=BODY.fullmatch(body)
    if not m or int(m['pc'],16)!=pc or m['helper'] not in ARITY:
        return False
    values=m['args'].split(', ')
    n=ARITY[m['helper']]
    booleans=2 if m['helper']=='ppc_ps_madd_op' else 0
    return (len(values)==n+booleans and
            all(re.fullmatch(r'\d+',v) and 0<=int(v)<32 for v in values[:n]) and
            all(v in ('true','false') for v in values[n:]))


def transform(text):
    # Outlined/multiple functions need a separately reviewed entry contract.
    if len(re.findall(r'\bvoid \w+\(CPUState\* ctx\)\s*\{',text))!=1:
        return text, []
    labels=list(LABEL.finditer(text))
    if len({m[1] for m in labels})!=len(labels):
        raise ValueError('Duplicate instruction labels')
    edits, changed=[],[]
    for i in range(1,len(labels)-1):
        before,current,after=labels[i-1:i+2]
        pc=int(current[1],16)
        if int(before[1],16)+4!=pc:
            continue
        if not pure(text[before.end():current.start()],pc-4):
            continue
        body=text[current.end():after.start()]
        if not pure(body,pc):
            continue
        target='label_'+current[1]
        if len(re.findall(r'\bgoto '+target+r';',text))!=1:
            continue
        case=re.search(r'^(?P<head>[ \t]*case 0x'+current[1]+r'u: '
                       r'(?:ctx->downcount -= \d+; )?)goto '+target+r';$',text,re.M)
        if not case or case.start()>labels[0].start():
            continue
        guard=f'if (!ppc_fp_available_inline(ctx, 0x{pc:08X}u)) return;'
        replacement=case['head']+f'ctx->pc = 0x{pc:08X}u; '+guard+' goto '+target+';'
        edits.append((case.start(),case.end(),replacement))
        needle='    '+guard+'\n'
        offset=current.end()+body.index(needle)
        edits.append((offset,offset+len(needle),''))
        changed.append(pc)
    for start,end,replacement in sorted(edits,reverse=True):
        text=text[:start]+replacement+text[end:]
    return text,changed
