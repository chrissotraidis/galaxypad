"""Isolated exact-emitted Huffman tail fusion, never a module selection."""
import hashlib
import re

SOURCE_SHA = 'e6aa915816ee2a89534f75c4d59dd0c145f7a5d0162c3e1a15b2ebe33b996dcc'
START, END = '80453AAC', '80453AEC'


def parts(source):
    normalized = re.sub(r'^#include ".*RMGE01.h"$', '#include "../RMGE01.h"', source, flags=re.M)
    assert hashlib.sha256(normalized.encode()).hexdigest() == SOURCE_SHA
    body = source.split('label_'+START+':', 1)[1].split('label_'+END+':', 1)[0]
    # Keep the original memory helpers, callback order, labels and cycle charges.
    # Only remove the unrelated incoming external-switch edges in this copy.
    assert set(re.findall(r'goto label_([0-9A-F]+);', body)) == {'80453AC8', '80453AE4', '80453AF0'}
    body = body.replace('goto label_80453AF0;', 'return false;')
    helper = 'static inline bool galaxy_huffman_tail(CPUState* ctx) {\n'+body+'\nreturn true;\n}\n'
    return helper


def transform(source):
    helper = parts(source)
    anchor = 'void func_804530A0(CPUState* ctx) {'
    assert source.count(anchor) == 1
    result = source.replace(anchor, helper+'\n'+anchor)
    # Normal leader enters the helper; all other original instruction entries
    # remain unchanged. The original backedge handles yielding and target PC.
    start = 'label_'+START+':'
    result = result.replace(start, start+'\n    if (galaxy_huffman_tail(ctx)) goto label_'+END+';\n    goto label_80453AF0;', 1)
    return result
