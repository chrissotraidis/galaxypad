from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('summary',Path(__file__).resolve().parents[1]/'scripts/summarize-cross-eligibility.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def row(c,f,m,r,t):return f'[cross-island-r804] calls={c} fast={f} mode={m} range={r} ties={t}\n'
a=row(4096,4000,40,50,6);b=row(8192,8000,80,100,12)
assert module.summarize(a+b)['delta']==dict(calls=4096,fast=4000,mode=40,range=50,ties=6)
assert module.summarize((a+b).replace('r804','r807'))['diagnostic']=='r807'
window=module.summarize(a+'scene starts\n'+a+b+'ignored\n',3,4)
assert window['observations']==2 and window['line_window']==[3,4]
assert window['delta']['calls']==4096
for start,end in [(0,None),(3,2),(1,1),(999,None)]:
    try:module.summarize(a+b,start,end)
    except ValueError:pass
    else:raise AssertionError('Invalid/empty scene window accepted')
for invalid in ['',a,a+a,b+a,a+row(8192,8192,1,0,0),a+b.replace('r804','r807')]:
    try:module.summarize(invalid)
    except ValueError:pass
    else:raise AssertionError('Invalid counter window accepted')
print('Cross eligibility summary: deltas, missing data, reset and totals checks pass')
