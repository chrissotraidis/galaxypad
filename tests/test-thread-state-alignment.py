from pathlib import Path
import importlib.util

path=Path(__file__).resolve().parents[1]/'scripts/align-thread-state.py'
spec=importlib.util.spec_from_file_location('alignment',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
rows=[dict(start_ns=a,end_ns=b,valid=v,run_state=s) for a,b,v,s in
      ((0,3,1,3),(4,5,1,1),(6,7,0,None),(8,10,1,3),(11,14,1,1))]
result=module.observe(rows,2,12)
assert result['samples']==3 and result['invalid']==1
assert result['states']=={'1':1,'3':1}
assert result['boundary_overlaps']==2
assert result['max_snapshot_gap_ms']==4/1e6
assert result['max_query_ms']==2/1e6
empty=module.observe([],2,12)
assert empty['states']=={} and empty['max_snapshot_gap_ms']==10/1e6
assert module.observe(rows,4,10)['samples']==3
assert result['priorities']=={} and result['priority_unknown']==2
rows[1]['priority']=31
rows[2]['priority']=99 # Invalid samples must not contribute.
rows[3]['priority']=31
result=module.observe(rows,2,12)
assert result['priorities']=={'31':2} and result['priority_unknown']==0
assert module.observe(rows,5,8)['priorities']=={}
rows[1].update(policy=1,base_priority=31,max_priority=63)
rows[2].update(policy=99,base_priority=99,max_priority=99)
assert module.observe(rows,2,12)['scheduling']=={
    'policy':{'1':1},'base_priority':{'31':1},'max_priority':{'63':1}}
import tempfile
with tempfile.TemporaryDirectory() as directory:
    fixture=Path(directory)/'states.csv'
    fixture.write_text('start_ns,end_ns,valid,run_state,priority\n0,1,1,1,31\n2,3,0,,\n')
    parsed=module.read_states(fixture)
    assert parsed[0]['priority']==31 and parsed[1]['priority'] is None
    fixture.write_text('start_ns,end_ns,valid,run_state\n0,1,1,1\n')
    assert module.read_states(fixture)[0]['priority'] is None
    fixture.write_text('start_ns,end_ns,valid,run_state,priority,policy,base_priority,max_priority\n'
                       '0,1,1,1,0,1,31,63\n2,3,0,,,,,,,\n')
    parsed=module.read_states(fixture)
    assert parsed[0]['priority']==0 and parsed[0]['policy']==1
    assert parsed[0]['base_priority']==31 and parsed[0]['max_priority']==63
    assert all(parsed[1][key] is None for key in ('policy','base_priority','max_priority'))
print('Thread-state containment, straddles, invalid snapshots and uncovered gaps pass')
