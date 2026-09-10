"""Prove normal-entry extraction preserves original dispatch and fallback text."""
from pathlib import Path
import sys

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
from normal_kernel_entry import transform
source=(root/'generated/thp-kernels-r198-exits/candidate.c').read_text()
changed=transform(source)
outer='void func_804520A0(CPUState* ctx) {'
assert source.split(outer,1)[1]==changed.split(outer,1)[1]
assert source.count('case 0x')==changed.count('case 0x')
for i,start in ((0,'804526E8'),(1,'80452B74')):
    sig=f'static __attribute__((noinline, flatten)) bool thp_kernel_{i}(CPUState* ctx) {{'
    original=source[source.index(sig):source.index('\n}\n',source.index(sig))+3]
    routed=changed[changed.index(sig):changed.index('\n}\n',changed.index(sig))+3]
    dispatch=f'\n    if (ctx->pc==0x{start}u) return thp_normal_{i}(ctx);'
    assert routed.replace(dispatch,'',1)==original
    normal_sig=sig.replace(f'thp_kernel_{i}',f'thp_normal_{i}')
    normal=changed[changed.index(normal_sig):changed.index('\n}\n',changed.index(normal_sig))+3]
    assert 'switch (ctx->pc)' not in normal
    assert normal.split(normal_sig+'\n',1)[1]==original.split('    default: return false;\n    }\n',1)[1]
try:
    transform(source+'\n')
except AssertionError:
    pass
else:
    raise AssertionError('Source pin must fail closed')
print('Both original resumes, normal instruction bodies, outer charges and entry cases preserved')
