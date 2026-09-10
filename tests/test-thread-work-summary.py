import copy
import importlib.util
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('summary',root/'scripts/summarize-thread-work.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
stamps=list(range(0,701,100)); rows=[]
for i,t in enumerate(stamps):
    for level in range(2):
        rows.append(dict(vi_ns=t,before_ns=t+1,after_ns=t+2,error=0,level=level,
                         instructions=i*100,cycles=i*50,user_mach=i*3,system_mach=i))
meta=dict(dropped=0,levels=2,numerator=125,denominator=3,config_error=0)
def run(r=rows,s=stamps,d=meta,drop=0,start=50,end=650,cap=None):
    return m.summarize(r,s,d,drop,start,end,cap)
result=run()
assert result['vi_count_range']==[5,5] and result['selected_samples']==6
assert result['totals']['instructions']==1000
assert result['thread_cpu_ns']==40*125/3
assert result['levels'][0]['cpu_time_share']==.5
assert result['omitted_boundary_ns']==[51,48]
def rejects(**kwargs):
    try: run(**kwargs)
    except ValueError: return
    raise AssertionError(f'Invalid trace accepted: {kwargs}')
for key,value in [('levels',0),('denominator',0),('numerator',0),('config_error',38),('dropped',-1)]:
    d=dict(meta); d[key]=value; rejects(d=d)
rejects(s=stamps[:-1]); rejects(start=701,end=800)
rejects(start=50,end=150); rejects(r=rows[:-1])
for key,value in [('error',45),('instructions',0),('before_ns',9999),('level',1),('cycles',-1)]:
    r=copy.deepcopy(rows); r[6][key]=value; rejects(r=r)
d=dict(meta,dropped=4)
r=copy.deepcopy(rows)
for row in r[6:8]: row['after_ns']=10000
rejects(r=r)
rejects(d=d); rejects(d=d,cap=7); rejects(drop=1)
assert run(d=d,drop=4,cap=8)['recording']['retained_tail_margin_ns']==50
rejects(d=d,cap=8,end=750)
print('Thread summary validates exact VI pairing, query bounds, topology, errors/resets, Mach conversion and complete prefix coverage')
