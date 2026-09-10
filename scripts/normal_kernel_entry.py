"""Private normal-entry copies; original transform resumes remain byte-exact."""
import hashlib

SOURCE_SHA='98d98621d4f744ea76977a63e44f3e2e3e731f50051e4a3a800a772e05a68991'


def transform(source):
    assert hashlib.sha256(source.encode()).hexdigest()==SOURCE_SHA
    result=source
    changes=[]
    for index,start in ((0,'804526E8'),(1,'80452B74')):
        signature=f'static __attribute__((noinline, flatten)) bool thp_kernel_{index}(CPUState* ctx) {{'
        begin=result.index(signature)
        end=result.index('\n}\n',begin)+3
        original=result[begin:end]
        switch_end=original.index('    default: return false;\n    }\n')+len('    default: return false;\n    }\n')
        body=original[switch_end:]
        assert body.startswith('\nlabel_'+start+':')
        normal_signature=signature.replace(f'thp_kernel_{index}',f'thp_normal_{index}')
        normal=normal_signature+'\n'+body
        # No math, memory, entry charges, helper checks, or backedges changed.
        routed=original.replace(signature,signature+f'\n    if (ctx->pc==0x{start}u) return thp_normal_{index}(ctx);',1)
        replacement=normal+'\n'+routed
        result=result[:begin]+replacement+result[end:]
        changes.append((replacement,original))
    restored=result
    for replacement,original in reversed(changes):
        assert restored.count(replacement)==1
        restored=restored.replace(replacement,original,1)
    assert restored==source
    return result
