from pathlib import Path
import importlib.util

path=Path(__file__).resolve().parents[1]/'scripts/align-host-pressure.py'
spec=importlib.util.spec_from_file_location('pressure',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
a=dict(start_ns=0,end_ns=1,valid=1,**{k:0 for k in module.COUNTERS})
b=dict(start_ns=20,end_ns=21,valid=1,**{k:0 for k in module.COUNTERS})
b.update(cpu_user_ticks=1,cpu_system_ticks=1,cpu_idle_ticks=6,swapins=2)
r=module.bracket([a,b],4,15)
assert r['covered'] and r['bracket_ms']==21/1e6
assert r['snapshot_freshness']=='unknown_kernel_cache'
assert r['aggregate_idle_percent']==75 and r['deltas']['swapins']==2
assert not module.bracket([a,b],0,15)['covered']
b['valid']=0
assert module.bracket([a,b],4,15)['valid'] is False
b['valid']=1;a['cpu_idle_ticks']=7
assert module.bracket([a,b],4,15)['aggregate_idle_percent'] is None
assert module.bracket([a,b],4,15)['deltas']['cpu_idle_ticks'] is None
print('Host bracket bounds, missing coverage, invalid counters and reset guards pass')
